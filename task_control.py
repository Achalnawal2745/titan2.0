"""Cooperative cancel for long jobs (report / PPT / skill).

The mic thread sets this when you talk while a tool is running, or ESC.
Writers MUST check is_cancelled() before they save/overwrite a file.
"""
from __future__ import annotations

import threading

_CANCEL = threading.Event()
_UI_LOG = None
_UI_STATUS = None


def request_cancel(reason: str = "") -> None:
    if not _CANCEL.is_set():
        extra = f" ({reason})" if reason else ""
        print(f"[TASK] 🛑 Stop requested{extra} — will not save/overwrite")
        ui_log(f"[TASK] 🛑 Stop requested{extra}")
    _CANCEL.set()


def clear_cancel() -> None:
    _CANCEL.clear()


def is_cancelled() -> bool:
    return _CANCEL.is_set()


def set_ui_hooks(log=None, status=None) -> None:
    """log(msg), status(title, body) — Titan UI. Safe to call from worker threads."""
    global _UI_LOG, _UI_STATUS
    _UI_LOG = log
    _UI_STATUS = status


def ui_log(msg: str) -> None:
    print(msg)
    fn = _UI_LOG
    if not fn:
        return
    try:
        fn(msg)
    except Exception:
        pass


def ui_status(title: str, body: str) -> None:
    fn = _UI_STATUS
    if not fn:
        return
    try:
        fn(title, body)
    except Exception:
        pass


def stopped_message(detail: str = "File NOT written.", followup: str = "Do not restart unless they say continue.") -> str:
    """Standard 'user hit stop' response text. Was copy-pasted with slight
    wording differences into doc_edit.py and task_planner.py as _stopped();
    both now call this instead so the wording only needs to change in one
    place. Pass a tool-specific `followup` if the generic one doesn't fit."""
    return f"🛑 STOPPED by user. {detail} {followup}"
