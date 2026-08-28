"""
core/spill.py — Output spill-to-disk protection engine.
Ported from DeepSeek Harness (`packages/spill`).

Prevents large tool stdout/stderr (e.g. 50+ lines or >2KB) from overflowing
the LLM's context window. Dumps raw output to a local scratch file and returns
a clean head + tail preview with a reference to the saved log file.
"""
from __future__ import annotations

import hashlib
import os
import re
from datetime import datetime
from pathlib import Path
from typing import Any, Tuple

# Thresholds
MAX_INLINE_LINES = 50
MAX_INLINE_CHARS = 2500
HEAD_LINES = 12
TAIL_LINES = 12


def _get_spill_dir() -> Path:
    base = Path(__file__).resolve().parent.parent
    spill_dir = base / "scratch" / "spill_outputs"
    spill_dir.mkdir(parents=True, exist_ok=True)
    return spill_dir


def maybe_spill_output(
    tool_name: str,
    raw_output: Any,
    max_lines: int = MAX_INLINE_LINES,
    max_chars: int = MAX_INLINE_CHARS,
) -> Tuple[str, bool, str | None]:
    """Checks if raw_output exceeds bounds. If so, saves to disk and returns a preview.

    Returns:
        (sanitized_text, was_spilled, spilled_file_path)
    """
    if raw_output is None:
        return "", False, None

    text = str(raw_output)
    lines = text.splitlines()

    # If within safe limits, return as is
    if len(lines) <= max_lines and len(text) <= max_chars:
        return text, False, None

    # Exceeds limit -> spill to disk
    spill_dir = _get_spill_dir()
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    digest = hashlib.sha1(text.encode("utf-8", errors="ignore")).hexdigest()[:8]
    clean_name = re.sub(r"[^a-zA-Z0-9_]+", "_", tool_name).strip("_") or "tool"
    spill_file = spill_dir / f"{clean_name}_{timestamp}_{digest}.log"

    try:
        spill_file.write_text(text, encoding="utf-8", errors="replace")
        spill_path_str = str(spill_file)
    except Exception as e:
        spill_path_str = f"<failed to write spill file: {e}>"

    # Construct Head + Tail preview
    head = "\n".join(lines[:HEAD_LINES])
    tail = "\n".join(lines[-TAIL_LINES:])
    omitted = len(lines) - (HEAD_LINES + TAIL_LINES)

    preview = (
        f"[OUTPUT TRUNCATED — Total {len(lines)} lines, {len(text)} bytes]\n"
        f"Full output saved to: {spill_path_str}\n"
        f"--- Output Head (first {HEAD_LINES} lines) ---\n"
        f"{head}\n"
        f"--- [... {omitted} lines omitted ...] ---\n"
        f"--- Output Tail (last {TAIL_LINES} lines) ---\n"
        f"{tail}\n"
        f"--- End of Preview ---"
    )

    return preview, True, spill_path_str
