"""
TITAN Work Pad — multi-job working notebook.

Not long-term memory (that's long_term.json).
This is the scratch + checklist Titan uses while doing real work:
  - several jobs at once
  - each job has a goal, steps (todo / doing / done / blocked), notes
  - survives reconnects / 1011 crashes
"""
from __future__ import annotations

import json
import re
import sys
from datetime import datetime
from pathlib import Path
from threading import Lock
from typing import Any


def _base_dir() -> Path:
    if getattr(sys, "frozen", False):
        return Path(sys.executable).parent
    return Path(__file__).resolve().parent.parent


PAD_JSON = _base_dir() / "memory" / "workpad.json"
PAD_MD   = _base_dir() / "memory" / "workpad.md"
_lock    = Lock()

_JOB_STATUSES  = ("active", "paused", "done")
_STEP_STATES   = ("todo", "doing", "done", "blocked")
_MAX_JOBS      = 12
_MAX_STEPS     = 24
_MAX_NOTES     = 16
_PROMPT_BUDGET = 1800   # chars injected into the live system prompt


def _now() -> str:
    return datetime.now().strftime("%Y-%m-%d %H:%M")


def _slug(text: str) -> str:
    s = re.sub(r"[^a-z0-9]+", "_", (text or "").lower()).strip("_")
    return (s[:40] or "job")


def _empty() -> dict:
    return {"updated": _now(), "jobs": []}


def load_pad() -> dict:
    if not PAD_JSON.exists():
        return _empty()
    with _lock:
        try:
            data = json.loads(PAD_JSON.read_text(encoding="utf-8"))
            if isinstance(data, dict) and isinstance(data.get("jobs"), list):
                return data
        except Exception as e:
            print(f"[WorkPad] load error: {e}")
    return _empty()


def _write(pad: dict) -> None:
    pad["updated"] = _now()
    PAD_JSON.parent.mkdir(parents=True, exist_ok=True)
    with _lock:
        PAD_JSON.write_text(json.dumps(pad, indent=2, ensure_ascii=False), encoding="utf-8")
        PAD_MD.write_text(to_markdown(pad), encoding="utf-8")


def to_markdown(pad: dict | None = None) -> str:
    pad = pad or load_pad()
    jobs = pad.get("jobs") or []
    if not jobs:
        return "# TITAN Work Pad\n\n_Empty. No jobs yet._\n"
    lines = [f"# TITAN Work Pad", f"_Updated {pad.get('updated', '')}_", ""]
    for j in jobs:
        mark = {"active": "🟢", "paused": "⏸️", "done": "✅"}.get(j.get("status"), "•")
        lines.append(f"## {mark} {j.get('title') or j.get('id')}  `{j.get('id')}`")
        if j.get("goal"):
            lines.append(f"**Goal:** {j['goal']}")
        steps = j.get("steps") or []
        if steps:
            lines.append("")
            for i, s in enumerate(steps, 1):
                st = s.get("state", "todo")
                box = {"todo": "[ ]", "doing": "[>]", "done": "[x]", "blocked": "[!]"}.get(st, "[ ]")
                extra = f" — {s['note']}" if s.get("note") else ""
                lines.append(f"{i}. {box} {s.get('text', '')}{extra}")
        notes = j.get("notes") or []
        if notes:
            lines.append("")
            lines.append("Notes:")
            for n in notes[-8:]:
                lines.append(f"- {n}")
        lines.append("")
    return "\n".join(lines).rstrip() + "\n"


def format_for_prompt(pad: dict | None = None) -> str:
    """Compact snapshot for the live system instruction."""
    pad = pad or load_pad()
    jobs = [j for j in (pad.get("jobs") or []) if j.get("status") != "done"]
    done_n = sum(1 for j in (pad.get("jobs") or []) if j.get("status") == "done")
    if not jobs and not done_n:
        return ""
    lines = ["[WORK PAD — your working notebook. Update it with the work_pad tool. Do not recite this list.]"]
    if not jobs:
        lines.append(f"(No active jobs. {done_n} finished.)")
    for j in jobs[:8]:
        title = j.get("title") or j.get("id")
        lines.append(f"JOB `{j.get('id')}` [{j.get('status','active')}] {title}")
        if j.get("goal"):
            lines.append(f"  goal: {j['goal']}")
        for i, s in enumerate(j.get("steps") or [], 1):
            lines.append(f"  {i}. [{s.get('state','todo')}] {s.get('text','')}")
        for n in (j.get("notes") or [])[-3:]:
            lines.append(f"  note: {n}")
    if done_n:
        lines.append(f"(+ {done_n} finished job(s) hidden)")
    text = "\n".join(lines)
    if len(text) > _PROMPT_BUDGET:
        text = text[: _PROMPT_BUDGET - 1] + "…"
    return text + "\n"


def _find_job(pad: dict, job: str) -> dict | None:
    if not job:
        return None
    key = job.strip().lower()
    for j in pad.get("jobs") or []:
        if str(j.get("id", "")).lower() == key:
            return j
        if str(j.get("title", "")).lower() == key:
            return j
        if key in str(j.get("title", "")).lower() or key in str(j.get("id", "")).lower():
            return j
    return None


def _unique_id(pad: dict, title: str) -> str:
    base = _slug(title)
    ids = {j.get("id") for j in pad.get("jobs") or []}
    if base not in ids:
        return base
    n = 2
    while f"{base}_{n}" in ids:
        n += 1
    return f"{base}_{n}"


def run_work_pad(args: dict) -> dict:
    """Single entry used by the work_pad tool."""
    action = (args.get("action") or "show").strip().lower()
    job_key = (args.get("job") or args.get("job_id") or args.get("title") or "").strip()
    text = (args.get("text") or args.get("note") or args.get("goal") or "").strip()
    state = (args.get("state") or args.get("status") or "").strip().lower()
    step_ref = args.get("step")  # 1-based index or step text

    pad = load_pad()

    if action in ("show", "list", "read"):
        md = to_markdown(pad)
        return {"success": True, "action": "show", "markdown": md, "jobs": pad.get("jobs") or []}

    if action in ("add_job", "new_job", "start"):
        title = (args.get("title") or text or "Untitled").strip()
        if not title:
            return {"success": False, "error": "Need a title for the job."}
        if len(pad.get("jobs") or []) >= _MAX_JOBS:
            return {"success": False, "error": f"Pad full ({_MAX_JOBS} jobs). Archive or delete one first."}
        job = {
            "id": _unique_id(pad, title),
            "title": title,
            "goal": (args.get("goal") or "").strip(),
            "status": "active",
            "steps": [],
            "notes": [],
            "updated": _now(),
        }
        # optional first batch of steps: "a | b | c" or list
        raw_steps = args.get("steps")
        if isinstance(raw_steps, str) and raw_steps.strip():
            raw_steps = [s.strip() for s in re.split(r"[|\n;]+", raw_steps) if s.strip()]
        if isinstance(raw_steps, list):
            for s in raw_steps[:_MAX_STEPS]:
                if isinstance(s, str) and s.strip():
                    job["steps"].append({"text": s.strip(), "state": "todo"})
        pad.setdefault("jobs", []).insert(0, job)
        _write(pad)
        return {"success": True, "action": "add_job", "job": job, "markdown": to_markdown(pad)}

    job = _find_job(pad, job_key)
    if action not in ("clear_done", "archive_done") and not job and action != "show":
        if action in ("add_step", "check", "set_step", "note", "edit_job", "remove_job", "remove_step"):
            return {
                "success": False,
                "error": f"No job matching '{job_key}'.",
                "available": [j.get("id") for j in pad.get("jobs") or []],
            }

    if action == "add_step":
        if not text:
            return {"success": False, "error": "Need step text."}
        if len(job.get("steps") or []) >= _MAX_STEPS:
            return {"success": False, "error": "Too many steps on this job."}
        job.setdefault("steps", []).append({"text": text, "state": "todo"})
        job["updated"] = _now()
        _write(pad)
        return {"success": True, "action": "add_step", "job_id": job["id"], "markdown": to_markdown(pad)}

    if action in ("check", "set_step", "tick"):
        steps = job.get("steps") or []
        target = None
        if isinstance(step_ref, int) or (isinstance(step_ref, str) and str(step_ref).isdigit()):
            idx = int(step_ref) - 1
            if 0 <= idx < len(steps):
                target = steps[idx]
        if target is None and (step_ref or text):
            needle = str(step_ref or text).lower()
            for s in steps:
                if needle in s.get("text", "").lower():
                    target = s
                    break
        if target is None:
            return {"success": False, "error": "Which step? Pass step=1 or the step text."}
        new_state = state if state in _STEP_STATES else "done"
        target["state"] = new_state
        if args.get("note"):
            target["note"] = str(args["note"]).strip()
        target["at"] = _now()
        job["updated"] = _now()
        # auto-close job if every step is done
        if steps and all(s.get("state") == "done" for s in steps):
            job["status"] = "done"
        _write(pad)
        return {
            "success": True,
            "action": "set_step",
            "job_id": job["id"],
            "step": target,
            "job_status": job["status"],
            "markdown": to_markdown(pad),
        }

    if action in ("note", "add_note"):
        if not text:
            return {"success": False, "error": "Need note text."}
        notes = job.setdefault("notes", [])
        notes.append(text)
        job["notes"] = notes[-_MAX_NOTES:]
        job["updated"] = _now()
        _write(pad)
        return {"success": True, "action": "note", "job_id": job["id"], "markdown": to_markdown(pad)}

    if action in ("edit_job", "update_job"):
        if args.get("title"):
            job["title"] = str(args["title"]).strip()
        if args.get("goal") is not None:
            job["goal"] = str(args.get("goal") or "").strip()
        if state in _JOB_STATUSES:
            job["status"] = state
        elif (args.get("status") or "").lower() in _JOB_STATUSES:
            job["status"] = args["status"].lower()
        job["updated"] = _now()
        _write(pad)
        return {"success": True, "action": "edit_job", "job": job, "markdown": to_markdown(pad)}

    if action == "remove_step":
        steps = job.get("steps") or []
        idx = None
        if isinstance(step_ref, int) or (isinstance(step_ref, str) and str(step_ref).isdigit()):
            idx = int(step_ref) - 1
        elif step_ref or text:
            needle = str(step_ref or text).lower()
            for i, s in enumerate(steps):
                if needle in s.get("text", "").lower():
                    idx = i
                    break
        if idx is None or not (0 <= idx < len(steps)):
            return {"success": False, "error": "Could not find that step."}
        removed = steps.pop(idx)
        job["updated"] = _now()
        _write(pad)
        return {"success": True, "action": "remove_step", "removed": removed, "markdown": to_markdown(pad)}

    if action in ("remove_job", "delete_job"):
        pad["jobs"] = [j for j in pad.get("jobs") or [] if j is not job]
        _write(pad)
        return {"success": True, "action": "remove_job", "removed": job.get("id"), "markdown": to_markdown(pad)}

    if action in ("clear_done", "archive_done"):
        before = len(pad.get("jobs") or [])
        pad["jobs"] = [j for j in pad.get("jobs") or [] if j.get("status") != "done"]
        _write(pad)
        return {
            "success": True,
            "action": "clear_done",
            "removed": before - len(pad["jobs"]),
            "markdown": to_markdown(pad),
        }

    if action == "rewrite_steps":
        raw = args.get("steps") or text
        if isinstance(raw, str):
            raw = [s.strip() for s in re.split(r"[|\n;]+", raw) if s.strip()]
        if not isinstance(raw, list) or not raw:
            return {"success": False, "error": "Pass steps as a list or 'a | b | c'."}
        job["steps"] = [{"text": str(s).strip(), "state": "todo"} for s in raw[:_MAX_STEPS] if str(s).strip()]
        job["updated"] = _now()
        _write(pad)
        return {"success": True, "action": "rewrite_steps", "job_id": job["id"], "markdown": to_markdown(pad)}

    return {"success": False, "error": f"Unknown action '{action}'."}


# handy aliases for callers that don't want a dict
def show() -> str:
    return to_markdown()
