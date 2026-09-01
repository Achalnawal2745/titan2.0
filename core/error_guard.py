"""
core/error_guard.py — Loop Hygiene & Auto-Repair Guard.
Ported from DeepSeek Harness (`packages/guard`).

Provides:
1. Repeat Call Loop Detection (blocks 3x identical broken tool calls).
2. Error Classification (syntax, missing module, file not found, permission, runtime).
3. Auto-Repair Feedback Generation (guides LLM to fix the specific issue).
"""
from __future__ import annotations

import hashlib
import json
import re
from typing import Any, Dict, List, Optional, Tuple


class ErrorGuard:
    # A successful call to one of these means the world changed, so an identical
    # command afterwards is a legitimate retry, not a loop. Without this, the
    # guard blocked the normal fix cycle: `node build.js` fails -> edit the file
    # -> `node build.js` is byte-identical, so the guard refused to run it and
    # the worker could never see whether its fix worked.
    STATE_CHANGING_TOOLS = {
        "write_file", "str_replace_editor", "file_controller", "code_helper",
        "dev_agent", "python_eval",
    }

    def __init__(self, repeat_threshold: int = 3):
        self.repeat_threshold = repeat_threshold
        # Tracks tool call signatures and their outcomes
        self._history: List[Dict[str, Any]] = []

    def record_call(self, tool_name: str, args: dict, result: Any, is_error: bool) -> Tuple[bool, Optional[str]]:
        """Records a tool call.

        Returns:
            (is_loop_detected, advisory_warning)
        """
        # Canonical hash of args
        try:
            norm_args = json.dumps(args, sort_keys=True, default=str)
        except Exception:
            norm_args = str(args)
        
        sig = hashlib.sha1(f"{tool_name}:{norm_args}".encode("utf-8")).hexdigest()[:12]
        
        entry = {
            "tool": tool_name,
            "args": args,
            "sig": sig,
            "is_error": is_error,
            "result_snippet": str(result)[:200],
        }
        self._history.append(entry)

        # A successful state-changing call invalidates the failure history:
        # whatever failed before was against the OLD file contents.
        if not is_error and tool_name in self.STATE_CHANGING_TOOLS:
            for e in self._history[:-1]:
                e["is_error"] = False
            return False, None

        # Check for repeated failures with the same signature
        recent_matches = [e for e in self._history[-6:] if e["sig"] == sig and e["is_error"]]
        if len(recent_matches) >= self.repeat_threshold:
            warning = (
                f"[LOOP HYGIENE WARNING] Tool '{tool_name}' has failed {len(recent_matches)} times with identical arguments "
                "and nothing was changed in between. STOP repeating the exact same call. Analyze the error below and "
                "change your approach - edit the script, fix the parameters, or read the file to see its real contents."
            )
            return True, warning

        return False, None

    def classify_error(self, stderr_or_output: str) -> Dict[str, str]:
        """Classifies common errors and produces targeted fix suggestions."""
        text = (stderr_or_output or "").lower()
        
        if "cannot find module" in text or "no module named" in text:
            m = re.search(r"cannot find module ['\"]([^'\"]+)['\"]", stderr_or_output, re.IGNORECASE) or \
                re.search(r"no module named ['\"]([^'\"]+)['\"]", stderr_or_output, re.IGNORECASE)
            pkg = m.group(1) if m else "missing_module"
            return {
                "kind": "MISSING_MODULE",
                "package": pkg,
                "suggestion": f"Package '{pkg}' is not found. Write code that uses pre-installed libraries (e.g. python-pptx, node builtins) or verify node_modules path.",
            }

        if "syntaxerror" in text or "unexpected token" in text or "invalid syntax" in text:
            return {
                "kind": "SYNTAX_ERROR",
                "suggestion": "Code contains syntax errors or unescaped quotes. Do NOT cram code into single-line strings — write a complete script file to disk first and run it.",
            }

        if "nosuchfileordirectory" in text or "the system cannot find the file" in text or "file not found" in text:
            return {
                "kind": "FILE_NOT_FOUND",
                "suggestion": "Target file or path does not exist. Verify the real path (Desktop: C:/Users/achal/Desktop) or create the file before running scripts on it.",
            }

        if "permissiondenied" in text or "access is denied" in text or "ebusy" in text:
            return {
                "kind": "PERMISSION_ERROR",
                "suggestion": "File or resource is locked by another process (e.g. PowerPoint is currently holding the file open). Save to a new filename or close the open app.",
            }

        return {
            "kind": "RUNTIME_ERROR",
            "suggestion": "Read the traceback/stderr carefully, fix the root cause in the script, and retry once.",
        }

    def generate_auto_repair_prompt(self, tool_name: str, args: dict, stderr: str) -> str:
        """Generates a structured prompt to guide the LLM to self-heal."""
        classification = self.classify_error(stderr)
        return (
            f"[AUTO-REPAIR REQUIRED — {classification['kind']}]\n"
            f"The tool '{tool_name}' failed with the following error:\n"
            f"{stderr[:500]}\n\n"
            f"Fix Advice: {classification['suggestion']}\n"
            "Action Required: Adjust your parameters or code to resolve this error on your next tool call."
        )
