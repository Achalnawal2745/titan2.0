"""
TITAN Work Pad — multi-job working notebook.

Not long-term memory (that's long_term.json).
This is the scratch + checklist Titan uses while doing real work:
  - several jobs at once
  - each job has a goal, steps (todo / doing / done / blocked), notes
  - a saved RESULT so the same analysis is not redone
  - last_error so Titan can see a failure and fix it
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
WORK_LOG = _base_dir() / "memory" / "work_log.md"
_lock    = Lock()

_JOB_STATUSES  = ("active", "paused", "done")
_STEP_STATES   = ("todo", "doing", "done", "blocked")
_MAX_JOBS      = 12
_MAX_STEPS     = 24
_MAX_NOTES     = 16
_PROMPT_BUDGET = 2800


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


def _append_work_log(title: str, summary: str) -> None:
    summary = re.sub(r"\s+", " ", (summary or "")).strip()
    if not summary:
        return
    WORK_LOG.parent.mkdir(parents=True, exist_ok=True)
    line = f"- {_now()} **{title}**: {summary[:400]}\n"
    try:
        prev = WORK_LOG.read_text(encoding="utf-8") if WORK_LOG.exists() else "# TITAN work log\n\n"
        WORK_LOG.write_text(prev + line, encoding="utf-8")
    except Exception as e:
        print(f"[WorkPad] work_log: {e}")


def recent_work_log(n: int = 6) -> list[str]:
    if not WORK_LOG.exists():
        return []
    try:
        lines = [ln[2:].strip() for ln in WORK_LOG.read_text(encoding="utf-8").splitlines() if ln.startswith("- ")]
        return lines[-n:]
    except Exception:
        return []


def to_markdown(pad: dict | None = None) -> str:
    pad = pad or load_pad()
    jobs = pad.get("jobs") or []
    if not jobs:
        return "# TITAN Work Pad\n\n_Empty. No jobs yet._\n"
    lines = [f"# TITAN Work Pad", f"_Updated {pad.get('updated', '')}_", ""]
    for j in jobs:
        mark = {"active": "🟢", "doing": "🟢", "paused": "⏸️", "failed": "❌", "done": "✅"}.get(j.get("status"), "•")
        lines.append(f"## {mark} {j.get('title') or j.get('id')}  `{j.get('id')}`")
        if j.get("goal"):
            lines.append(f"**Goal:** {j['goal']}")
        if j.get("current_step") and j.get("status") == "active":
            lines.append(f"**Active Step:** `{j['current_step']}`")
        if j.get("result"):
            lines.append(f"**Result:** {j['result']}")
        if j.get("last_error"):
            lines.append(f"**Last error:** {j['last_error']}")
        steps = j.get("steps") or []
        if steps:
            lines.append("")
            for i, s in enumerate(steps, 1):
                st = s.get("state", "todo")
                box = {"todo": "[ ]", "doing": "[>]", "done": "[x]", "blocked": "[!]", "failed": "[!]"}.get(st, "[ ]")
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


def _open_jobs(pad: dict) -> list[dict]:
    return [j for j in (pad.get("jobs") or []) if j.get("status") in ("active", "paused")]


def _next_step(job: dict) -> dict | None:
    steps = job.get("steps") or []
    for s in steps:
        if s.get("state") == "doing":
            return s
    for s in steps:
        if s.get("state") in ("todo", "blocked"):
            return s
    return None


def format_for_prompt(pad: dict | None = None) -> str:
    """Compact snapshot for the live system instruction."""
    pad = pad or load_pad()
    jobs = _open_jobs(pad)
    all_jobs = pad.get("jobs") or []
    done = [j for j in all_jobs if j.get("status") == "done"]
    if not jobs and not done:
        return ""
    lines = [
        "[WORK PAD — silent notebook. Do NOT start these jobs yourself.]",
        "ONLY resume if the user just said continue / do the pending task / finish that.",
        "You may ASK once if they want to continue. Then wait. Do not run tools for leftover jobs.",
        "If they resume: reuse RESULT. Do not re-list the same files unless they said redo.",
    ]
    if not jobs:
        lines.append(f"(No active jobs. {len(done)} finished.)")
    for j in jobs[:8]:
        title = j.get("title") or j.get("id")
        lines.append(f"JOB `{j.get('id')}` [{j.get('status','active')}] {title}")
        if j.get("goal"):
            lines.append(f"  goal: {j['goal']}")
        if j.get("result"):
            lines.append(f"  RESULT (reuse, do not redo): {j['result'][:280]}")
        if j.get("last_error"):
            lines.append(f"  LAST ERROR (fix this): {j['last_error'][:180]}")
        for i, s in enumerate(j.get("steps") or [], 1):
            lines.append(f"  {i}. [{s.get('state','todo')}] {s.get('text','')}")
        nxt = _next_step(j)
        if nxt:
            lines.append(f"  NEXT: {nxt.get('text','')}")
        for n in (j.get("notes") or [])[-2:]:
            lines.append(f"  note: {n}")
    if done:
        lines.append("Finished jobs (reuse RESULT, do not start over):")
        for j in done[:4]:
            res = j.get("result") or "(no summary saved)"
            lines.append(f"  DONE `{j.get('id')}`: {res[:180]}")
    log = recent_work_log(4)
    if log:
        lines.append("Recent work log:")
        for row in log:
            lines.append(f"  - {row[:160]}")
    text = "\n".join(lines)
    if len(text) > _PROMPT_BUDGET:
        text = text[: _PROMPT_BUDGET - 1] + "…"
    return text + "\n"


def get_resume_brief() -> str:
    """
    Passive status only. NEVER tells the model to start working.
    Auto-continue was the 'tasks on a loop' bug.
    """
    pad = load_pad()
    jobs = [j for j in _open_jobs(pad) if j.get("status") == "active"]
    if not jobs:
        return ""
    j = jobs[0]
    nxt = _next_step(j)
    lines = [
        "[WORKPAD PLAN — Execute and track the steps below to finish the active task]",
        f"Job `{j.get('id')}`: {j.get('title') or ''}",
    ]
    if j.get("goal"):
        lines.append(f"Goal: {j['goal']}")
    if j.get("result"):
        lines.append(f"Saved result: {j['result'][:300]}")
    if j.get("last_error"):
        lines.append(f"Last error: {j['last_error'][:220]}")
    if nxt:
        lines.append(f"Current step to execute: [{nxt.get('state')}] {nxt.get('text')}")
    return "\n".join(lines)


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


def _new_job(pad: dict, title: str, goal: str = "", raw_steps=None) -> dict:
    job = {
        "id": _unique_id(pad, title),
        "title": title,
        "goal": (goal or "").strip(),
        "status": "active",
        "steps": [],
        "notes": [],
        "result": "",
        "last_error": "",
        "updated": _now(),
    }
    if isinstance(raw_steps, str) and raw_steps.strip():
        raw_steps = [s.strip() for s in re.split(r"[|\n;]+", raw_steps) if s.strip()]
    if isinstance(raw_steps, list):
        for s in raw_steps[:_MAX_STEPS]:
            if isinstance(s, str) and s.strip():
                job["steps"].append({"text": s.strip(), "state": "todo"})
    pad.setdefault("jobs", []).insert(0, job)
    return job


def worker_update(job_id: str, step_name: str, status: str, note: str = "") -> None:
    """Live synchronization bridge between background job workers and the workpad."""
    if not job_id:
        return
    pad = load_pad()
    job = _find_job(pad, job_id)
    if not job:
        title = job_id.replace("_", " ").capitalize()
        job = _new_job(pad, title, goal=note if status in ("start", "active") else title)
        job["id"] = job_id
    job["updated"] = _now()

    status = (status or "").lower()
    if status in ("done", "finished", "completed"):
        if step_name == "job" or not job.get("steps"):
            job["status"] = "done"
            job["current_step"] = ""
            if note:
                job["result"] = note[:900]
                _append_work_log(job.get("title") or job_id, note)
    elif status in ("failed", "error"):
        job["status"] = "failed"
        if note:
            job["last_error"] = f"{step_name}: {note}"[:400]
    elif status in ("doing", "running", "active"):
        job["status"] = "active"
        if step_name and step_name not in ("start", "job"):
            job["current_step"] = step_name

    if step_name and step_name not in ("job", "start"):
        steps = job.setdefault("steps", [])
        matched = False
        for s in steps:
            if step_name.lower() in s.get("text", "").lower():
                s["state"] = "done" if status == "done" else "doing" if status in ("doing", "running") else "blocked" if status in ("failed", "retrying") else s.get("state", "todo")
                if note:
                    s["note"] = note[:160]
                matched = True
                break
        if not matched:
            st = "done" if status == "done" else "doing" if status in ("doing", "running") else "blocked" if status in ("failed", "retrying") else "todo"
            steps.append({"text": step_name, "state": st, "note": note[:160] if note else ""})

    _write(pad)


def _looks_error(text: str) -> bool:
    t = (text or "").strip()
    if not t:
        return False
    head = t[:80].lower()
    return (
        t.startswith("❌")
        or head.startswith("error")
        or " failed" in head
        or "traceback" in t.lower()
        or "unexpected" in head
    )


def absorb_work_output(tool: str, args: dict | None, result: Any) -> None:
    """
    After a real work tool: stash a note / error / partial result on the
    newest active job so Titan does not forget and redo it.
    """
    args = args or {}
    pad = load_pad()
    jobs = [j for j in _open_jobs(pad) if j.get("status") == "active"]
    if not jobs:
        return
    job = jobs[0]
    snippet = re.sub(r"\s+", " ", str(result or "")).strip()
    if not snippet:
        return
    action = str(args.get("action") or "")
    path = str(args.get("path") or args.get("file_path") or args.get("source_path") or "")
    label = f"{tool}" + (f".{action}" if action else "") + (f" {path}" if path else "")

    if _looks_error(snippet):
        job["last_error"] = f"{label}: {snippet[:220]}"
        print(f"[WorkPad] ⛔ error saved on `{job.get('id')}`")
    else:
        job["last_error"] = ""
        # keep a running result so list/read is not repeated
        piece = f"{label}: {snippet[:220]}"
        prev = (job.get("result") or "").strip()
        if piece[:80] not in prev:
            job["result"] = (prev + " | " + piece).strip(" |")[-900:]

    notes = job.setdefault("notes", [])
    note = f"{label}: {snippet[:200]}"
    if not notes or notes[-1] != note:
        notes.append(note)
        job["notes"] = notes[-_MAX_NOTES:]
    job["updated"] = _now()
    _write(pad)


def run_work_pad(args: dict) -> dict:
    """Single entry used by the work_pad tool — flexible, forgiving action dispatch."""
    raw_action = (args.get("action") or "show").strip().lower()
    job_key = (args.get("job") or args.get("job_id") or args.get("title") or "").strip()
    text = (args.get("text") or args.get("note") or args.get("goal") or "").strip()
    state = (args.get("state") or args.get("status") or "").strip().lower()
    step_ref = args.get("step")

    pad = load_pad()

    # 1. SHOW / READ / LIST / PENDING
    if any(k in raw_action for k in ("show", "list", "read", "view", "get", "pending", "next")):
        md = to_markdown(pad)
        pending = [
            {
                "id": j.get("id"),
                "title": j.get("title"),
                "status": j.get("status"),
                "next": (_next_step(j) or {}).get("text"),
                "result": (j.get("result") or "")[:240],
                "last_error": j.get("last_error") or "",
            }
            for j in _open_jobs(pad)
        ]
        return {
            "success": True,
            "action": "show",
            "markdown": md,
            "jobs": pad.get("jobs") or [],
            "pending": pending,
            "resume": get_resume_brief(),
        }

    # 2. ERASE / CLEAR / WIPE / RESET / DELETE ALL
    if any(k in raw_action for k in ("erase", "wipe", "reset", "empty")) or (
        any(k in raw_action for k in ("clean", "clear", "delete", "remove")) and
        (job_key.lower() in ("all", "*", "everything", "pad", "workpad", "") or args.get("all") or args.get("force"))
    ):
        before = len(pad.get("jobs") or [])
        pad["jobs"] = []
        _write(pad)
        return {
            "success": True,
            "action": "erase",
            "removed": before,
            "markdown": to_markdown(pad),
            "message": "Work pad completely erased.",
        }

    # 3. DELETE / REMOVE A SPECIFIC JOB OR STEP
    if any(k in raw_action for k in ("delete", "remove", "clean")):
        job = _find_job(pad, job_key)
        if step_ref and job:
            steps = job.get("steps") or []
            idx = int(step_ref) - 1 if str(step_ref).isdigit() else None
            if idx is not None and 0 <= idx < len(steps):
                removed = steps.pop(idx)
                _write(pad)
                return {"success": True, "action": "remove_step", "removed": removed, "markdown": to_markdown(pad)}
        if job:
            pad["jobs"] = [j for j in pad.get("jobs") or [] if j is not job]
            _write(pad)
            return {"success": True, "action": "delete", "removed": job.get("id"), "markdown": to_markdown(pad)}
        else:
            before = len(pad.get("jobs") or [])
            pad["jobs"] = [j for j in pad.get("jobs") or [] if j.get("status") != "done"]
            if len(pad["jobs"]) == before:
                pad["jobs"] = []
            _write(pad)
            return {"success": True, "action": "clean", "removed": before - len(pad["jobs"]), "markdown": to_markdown(pad)}

    # 4. ADD JOB / ADD STEP / ADD NOTE
    if any(k in raw_action for k in ("add", "new", "start", "create")):
        if step_ref or "step" in raw_action:
            job = _find_job(pad, job_key) or (_open_jobs(pad)[0] if _open_jobs(pad) else None)
            if not job:
                job = _new_job(pad, job_key or "Task", goal=text)
            job.setdefault("steps", []).append({"text": text or str(step_ref), "state": "todo"})
            _write(pad)
            return {"success": True, "action": "add_step", "job_id": job["id"], "markdown": to_markdown(pad)}
        title = (args.get("title") or job_key or text or "Untitled").strip()
        existing = _find_job(pad, title)
        if existing:
            if text:
                existing["goal"] = text
            existing["status"] = "active"
            _write(pad)
            return {"success": True, "action": "add", "job": existing, "markdown": to_markdown(pad)}
        job = _new_job(pad, title, goal=text, raw_steps=args.get("steps"))
        _write(pad)
        return {"success": True, "action": "add", "job": job, "markdown": to_markdown(pad)}

    # 5. EDIT / UPDATE / CHECK / SAVE RESULT / LOG ERROR
    job = _find_job(pad, job_key) or (_open_jobs(pad)[0] if _open_jobs(pad) else None)
    if not job:
        job = _new_job(pad, job_key or "Task", goal=text)

    if any(k in raw_action for k in ("check", "tick", "complete", "done", "set")):
        steps = job.get("steps") or []
        for s in steps:
            if not step_ref or str(step_ref).lower() in s.get("text", "").lower() or str(step_ref) == str(steps.index(s)+1):
                s["state"] = state or "done"
                if text:
                    s["note"] = text
        if steps and all(s.get("state") == "done" for s in steps):
            job["status"] = "done"
        _write(pad)
        return {"success": True, "action": "edit", "job": job, "markdown": to_markdown(pad)}

    if any(k in raw_action for k in ("result", "summary", "save")):
        job["result"] = text[:900]
        job["last_error"] = ""
        if state in _JOB_STATUSES:
            job["status"] = state
        _write(pad)
        return {"success": True, "action": "save_result", "job": job, "markdown": to_markdown(pad)}

    if any(k in raw_action for k in ("error", "fail", "block")):
        job["last_error"] = text[:300]
        _write(pad)
        return {"success": True, "action": "log_error", "job": job, "markdown": to_markdown(pad)}

    # Generic edit
    if args.get("title"):
        job["title"] = args["title"]
    if text:
        job["goal"] = text
    if state in _JOB_STATUSES:
        job["status"] = state
    _write(pad)
    return {"success": True, "action": "edit", "job": job, "markdown": to_markdown(pad)}


def show() -> str:
    return to_markdown()


def track_long_task(
    phase: str,
    title: str,
    goal: str = "",
    note: str = "",
    kind: str = "",
) -> dict | None:
    """
    Called from main.py around real tools (especially smart_task).
    Puts the long job ON the pad and ticks it as the real tool runs.
    Never replaces generating the file.
    """
    title = (title or "Task").strip()[:70]
    kind = (kind or "").lower()
    if "presentation" in kind or "pptx" in kind or "deck" in kind:
        steps = "Plan slides | Build PowerPoint | Save .pptx | Open & check"
    elif "edit" in kind:
        steps = "Open file | Apply edits | Save | Open & check"
    elif any(k in kind for k in ("analy", "capstone", "project", "summar")):
        steps = "List files | Read key files | Write summary on pad | Speak short status"
    else:
        steps = "Set format (IEEE / theme) | Write sections | Save .docx | Open & check"

    try:
        if phase == "start":
            pad = load_pad()
            existing = _find_job(pad, title)
            if not existing:
                run_work_pad({
                    "action": "add_job",
                    "title": title,
                    "goal": goal or title,
                    "steps": steps,
                })
            run_work_pad({"action": "check", "job": title, "step": "1", "state": "doing"})
            run_work_pad({"action": "check", "job": title, "step": "2", "state": "doing"})
            print(f"[WorkPad] 📋 job on pad: {title}")
            return run_work_pad({"action": "show"})
        if phase == "ok":
            for n in ("1", "2", "3", "4"):
                run_work_pad({"action": "check", "job": title, "step": n, "state": "done"})
            if note:
                run_work_pad({"action": "save_result", "job": title, "text": note[:900]})
            run_work_pad({"action": "edit_job", "job": title, "status": "done"})
            print(f"[WorkPad] ✅ job done: {title}")
            return run_work_pad({"action": "show"})
        if phase == "fail":
            run_work_pad({
                "action": "check", "job": title, "step": "2",
                "state": "blocked", "note": (note or "failed")[:160],
            })
            run_work_pad({"action": "log_error", "job": title, "text": (note or "failed")[:300]})
            print(f"[WorkPad] ⛔ job blocked: {title}")
            return run_work_pad({"action": "show"})
    except Exception as e:
        print(f"[WorkPad] track_long_task: {e}")
    return None
