"""
core/code_runner.py — Isolated Python Code Runtime for TITAN.
Ported and adapted from DeepSeek Harness (`packages/code-runtime/code-runtime-python`).

Provides:
- One-shot Python script evaluation in an isolated subprocess.
- Clean standard output, error capture, and auto-spill integration.
"""
from __future__ import annotations

import hashlib
import os
import subprocess
import sys
import tempfile
from pathlib import Path
from typing import Any, Dict
from core.spill import maybe_spill_output


def run_python_code(code: str, timeout: int = 30) -> Dict[str, Any]:
    """Runs a Python snippet safely in a subprocess and returns execution result."""
    tmp_dir = Path(__file__).resolve().parent.parent / "scratch" / "eval"
    tmp_dir.mkdir(parents=True, exist_ok=True)
    
    digest = hashlib.sha1(code.encode("utf-8", errors="ignore")).hexdigest()[:8]
    script_path = tmp_dir / f"eval_{digest}.py"
    script_path.write_text(code, encoding="utf-8")
    
    try:
        proc = subprocess.run(
            [sys.executable, str(script_path)],
            capture_output=True,
            text=True,
            timeout=timeout,
            creationflags=getattr(subprocess, "CREATE_NO_WINDOW", 0) if os.name == "nt" else 0,
        )
        
        stdout_clean, _, _ = maybe_spill_output("py_eval_stdout", proc.stdout)
        stderr_clean, _, _ = maybe_spill_output("py_eval_stderr", proc.stderr)
        
        return {
            "success": proc.returncode == 0,
            "stdout": stdout_clean,
            "stderr": stderr_clean,
            "exit_code": proc.returncode,
        }
    except subprocess.TimeoutExpired:
        return {
            "success": False,
            "stdout": "",
            "stderr": f"Execution timed out after {timeout} seconds.",
            "exit_code": -1,
        }
    except Exception as e:
        return {
            "success": False,
            "stdout": "",
            "stderr": str(e),
            "exit_code": -1,
        }


# ── Gemini Tool Declaration ──
PYTHON_EVAL_DECLARATION = {
    "name": "python_eval",
    "description": "Execute raw Python code in an isolated runtime and return standard output, errors, and exit status.",
    "parameters": {
        "type": "OBJECT",
        "properties": {
            "code": {"type": "STRING", "description": "Complete Python script to execute"},
            "timeout": {"type": "INTEGER", "description": "Execution timeout in seconds (default 30)"},
        },
        "required": ["code"],
    },
}
