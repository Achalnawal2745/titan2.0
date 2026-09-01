"""
core/tool_pipeline.py — Guarded 4-Stage Tool Pipeline.
Ported from DeepSeek Harness (`packages/core/tools`).

Lifecycle:
1. pre_execute: Argument sanitization, shortcut path expansion (Desktop, Downloads).
2. execute: Safe execution with timeout handling.
3. post_execute: Error detection, spill-to-disk protection, error guard recording.
4. finalize: Clean structured result envelope.
"""
from __future__ import annotations

import os
from pathlib import Path
from typing import Any, Callable, Dict, Optional, Tuple

from core.error_guard import ErrorGuard
from core.spill import maybe_spill_output

# Tools whose output IS the instruction set the model must act on — spilling
# them to disk defeats the entire point, because a live-voice model under
# time pressure reliably does NOT stop to go read_file() the spilled
# original before acting. Concretely: this is why a pptx generation task
# produced a bare-bones default-template deck instead of following the
# skill's actual design guidance — load_skill's ~22KB of instructions got
# truncated to a ~270-line head, and the design rules lived further down,
# past the cut. The model literally never saw them.
NEVER_SPILL_TOOLS = {"load_skill"}

# Per-tool spill budgets (max_lines, max_chars). The global default of
# 50 lines / 2500 chars is right for a chatty `run_command`, but it crippled
# the worker on its own source files: a 155-line generator script came back as
# 12 head + 12 tail lines (~15% of it), so every str_replace_editor call was
# built from memory instead of from what it could see, failed to match, and
# burned hops re-reading narrow windows. A worker that cannot read the file it
# just wrote cannot edit that file.
#
# read_file already supports offset_lines/max_lines, so genuinely huge files can
# still be paged deliberately - these budgets only stop ordinary source files
# from being shredded when the model asked for the whole thing.
SPILL_BUDGETS = {
    "read_file": (2000, 120_000),
    "grep_search": (200, 20_000),
    "glob_search": (200, 20_000),
    "file_controller": (200, 20_000),
}


class ToolPipeline:
    def __init__(self, guard: Optional[ErrorGuard] = None):
        self.guard = guard or ErrorGuard()

    def pre_execute(self, tool_name: str, args: dict) -> dict:
        """Sanitizes arguments, expands relative OS paths (Desktop, Downloads)."""
        sanitized = dict(args or {})
        home = Path.home()

        # Path expansion helper
        for key in ("path", "destination", "file_path", "source_path", "output_path"):
            val = sanitized.get(key)
            if isinstance(val, str) and val.strip():
                val_str = val.strip()
                for folder in ("Desktop", "Downloads", "Documents"):
                    if val_str.startswith(f"{folder}/") or val_str.startswith(f"{folder}\\") or val_str.lower() == folder.lower():
                        if val_str.lower() == folder.lower():
                            sanitized[key] = str(home / folder)
                        else:
                            sub = val_str[len(folder)+1:]
                            sanitized[key] = str(home / folder / sub)
                        break
        return sanitized

    def post_execute(
        self,
        tool_name: str,
        sanitized_args: dict,
        raw_result: Any,
    ) -> Dict[str, Any]:
        """Classifies success/error, applies spill protection, and checks loop hygiene."""
        is_error = False
        result_text = str(raw_result or "")

        # Check common error indicators
        if isinstance(raw_result, dict):
            if raw_result.get("ok") is False or raw_result.get("exit_code", 0) != 0 or raw_result.get("success") is False:
                is_error = True
            if "error" in raw_result and raw_result["error"]:
                is_error = True
            if raw_result.get("stderr") and str(raw_result.get("stderr")).strip():
                is_error = True
        elif "error:" in result_text.lower() or "traceback (most recent call last)" in result_text.lower() or result_text.startswith("❌"):
            is_error = True

        # Apply Spill-to-Disk protection for large outputs — EXCEPT for
        # tools in NEVER_SPILL_TOOLS, whose full output the model must see
        # every time to actually do the task right (see comment above).
        if tool_name in NEVER_SPILL_TOOLS:
            spilled_text, was_spilled, spill_path = str(raw_result or ""), False, None
        elif tool_name in SPILL_BUDGETS:
            _lines, _chars = SPILL_BUDGETS[tool_name]
            spilled_text, was_spilled, spill_path = maybe_spill_output(
                tool_name, raw_result, max_lines=_lines, max_chars=_chars
            )
        else:
            spilled_text, was_spilled, spill_path = maybe_spill_output(tool_name, raw_result)

        # Record call in error guard
        is_loop, loop_warning = self.guard.record_call(tool_name, sanitized_args, result_text, is_error)

        final_content = spilled_text
        if is_loop and loop_warning:
            final_content = f"{loop_warning}\n\n{final_content}"
        elif is_error:
            # Generate auto-repair prompt
            repair_feedback = self.guard.generate_auto_repair_prompt(
                tool_name,
                sanitized_args,
                raw_result.get("stderr", result_text) if isinstance(raw_result, dict) else result_text,
            )
            final_content = f"{final_content}\n\n{repair_feedback}"

        return {
            "ok": not is_error,
            "is_error": is_error,
            "was_spilled": was_spilled,
            "spill_path": spill_path,
            "content": final_content,
            "raw": raw_result,
        }