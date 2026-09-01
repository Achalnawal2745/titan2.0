"""Persistent background workers for complex TITAN tasks."""
from __future__ import annotations

import asyncio
import contextvars
import json
import uuid
from dataclasses import dataclass, field
from datetime import datetime
from pathlib import Path
from typing import Awaitable, Callable

from core.nvidia_brain import run_brain_turn

ToolExecutor = Callable[[str, dict], Awaitable[str]]
_worker_id: contextvars.ContextVar[str | None] = contextvars.ContextVar("titan_worker_id", default=None)

# Generator/helper scripts belong in the project, not on the user's Desktop.
# Without an explicit absolute path the worker invented "Desktop/scratch/" and
# littered the Desktop with build scripts and probe files.
SCRATCH_DIR = Path(__file__).resolve().parent.parent / "scratch"


def running_in_worker() -> bool:
    return _worker_id.get() is not None


# Minimum plausible sizes. A real generated deck/doc is tens of KB; anything
# near-empty means the generator ran but produced nothing worth delivering.
_MIN_BYTES = {".pptx": 12_000, ".potx": 12_000, ".docx": 8_000,
              ".xlsx": 4_000, ".pdf": 4_000}


def _inspect_office_file(path: Path) -> list[str]:
    """Cheap structural check on a produced deliverable. Returns problem
    strings (empty == passed). No third-party deps: OOXML files are ZIPs, so
    zipfile alone catches the corruption the pptx skill warns about (an `#` hex
    prefix or 8-digit alpha hex silently writes an unopenable file)."""
    problems: list[str] = []
    ext = path.suffix.lower()
    try:
        size = path.stat().st_size
    except OSError as e:
        return [f"{path.name}: cannot stat the file ({e})"]

    floor = _MIN_BYTES.get(ext)
    if floor and size < floor:
        problems.append(
            f"{path.name} is only {size} bytes - too small to be a real "
            f"deliverable (expected at least ~{floor}). The generator likely "
            "produced an empty or near-empty file."
        )

    if ext in {".pptx", ".potx", ".docx", ".xlsx"}:
        import zipfile
        try:
            with zipfile.ZipFile(path) as zf:
                bad = zf.testzip()
                if bad:
                    problems.append(f"{path.name} is a corrupt archive (bad entry: {bad}).")
                names = zf.namelist()
                if ext in {".pptx", ".potx"}:
                    slides = [n for n in names
                              if n.startswith("ppt/slides/slide") and n.endswith(".xml")]
                    if not slides:
                        problems.append(f"{path.name} contains no slides at all.")
                    elif len(slides) < 3:
                        problems.append(
                            f"{path.name} has only {len(slides)} slide(s) - that is "
                            "not a real presentation."
                        )
                elif ext == ".docx" and "word/document.xml" not in names:
                    problems.append(f"{path.name} is missing word/document.xml.")
        except zipfile.BadZipFile:
            problems.append(
                f"{path.name} is not a valid Office file - it will not open in "
                "PowerPoint/Word. This is usually a bad colour value ('#' prefix "
                "or 8-digit alpha hex) written by the generator script."
            )
        except Exception as e:
            problems.append(f"{path.name} could not be inspected: {e}")

    return problems


@dataclass
class TaskWorker:
    id: str
    task: str
    role: str = "executor"
    status: str = "queued"
    result: str = ""
    error: str = ""
    created_at: str = field(default_factory=lambda: datetime.now().isoformat())
    history: list[dict] = field(default_factory=list)
    inbox: list[str] = field(default_factory=list)
    runner_task: asyncio.Task | None = field(default=None, repr=False)
    plan: list[str] = field(default_factory=list)
    tool_log: list[dict] = field(default_factory=list)
    verified: bool = False
    verified_outputs: list[str] = field(default_factory=list)
    # Worker -> boss -> user question round trip. The worker blocks on
    # `answer_future` while the boss speaks the question aloud; the user's next
    # answer resolves it. Budgeted so a worker cannot interview the user.
    question: str = ""
    answer_future: asyncio.Future | None = field(default=None, repr=False)
    questions_asked: int = 0

    def summary(self) -> dict:
        return {"id": self.id, "task": self.task, "role": self.role, "status": self.status,
                "plan": self.plan, "verified": self.verified, "outputs": self.verified_outputs,
                "question": self.question,
                "result": self.result[:300], "error": self.error[:300]}


class TaskWorkerManager:
    def __init__(self) -> None:
        self.workers: dict[str, TaskWorker] = {}
        self.events: asyncio.Queue[dict] = asyncio.Queue()

    def start(self, task: str, executor: ToolExecutor, declarations: list[dict], skill_catalog: str, role: str = "executor") -> TaskWorker:
        worker = TaskWorker(f"task_{uuid.uuid4().hex[:8]}", task.strip(), role=role)
        self.workers[worker.id] = worker
        worker.runner_task = asyncio.create_task(self._run(worker, executor, declarations, skill_catalog))
        return worker

    async def _run(self, worker: TaskWorker, executor: ToolExecutor, declarations: list[dict], catalog: str) -> None:
        worker.status = "running"
        await self.events.put({"kind": "state", "message": "planning", "worker": worker.summary()})
        prompt = (
            "You are a persistent task worker, not a chat assistant. Own this one task until it ends. "
            "Your history is durable: loaded SKILL.md instructions remain active for every later step. "
            "Choose and load relevant skills, plan only multi-step work, execute real tools, inspect every result, "
            "and never claim success after a failed command or failed validation. First call task_set_plan. "
            "Before giving a final answer, call verify_task_result with real output file paths and a factual summary. "
            "Never claim success unless that verification returns passed. You have every power the voice "
            "assistant has except speaking. If a genuinely blocking decision is missing - one that would "
            "change the deliverable and has no reasonable default - call ask_user_question; the voice "
            "assistant will speak it and route the answer back to you. You get at most two such questions, "
            "so never use one on something you could sensibly default. For everything else, pick a "
            "professional default and continue. Return a short factual final report "
            "with output paths and remaining limitations.\n\n"
            "DO NOT GUESS AN UNDOCUMENTED API. If a loaded skill gives you example code in a specific "
            "language/library, use that exact language and library, copying its patterns closely — do not "
            "switch to a different library and improvise its API from memory or by trial and error. If a "
            "generated script fails, read the actual error message and fix that specific line — do not start "
            "writing throwaway probe scripts (test.js, test2.js, debug.py, etc.) to interactively explore an "
            "API's shape. One quick sanity check is fine; more than one means you're guessing, not debugging — "
            "stop, re-read the skill's example code or the package's real usage pattern, and use that instead. "
            "You have a limited number of tool calls for this task: spend them building and fixing the real "
            "deliverable, not probing an unfamiliar library's internals.\n\n"
            "CREATING FILES (decks, documents, spreadsheets, PDFs, apps):\n"
            f"- Working directory for scripts is {SCRATCH_DIR}. Put every generator, helper and "
            "throwaway script there using its ABSOLUTE path. Never create a 'scratch' folder on "
            "the Desktop - the Desktop is for finished deliverables only.\n"
            "- Call load_skill FIRST for the format (pptx, docx, xlsx, pdf). You receive the skill's FULL "
            "instructions AND a <skill_resources> list of any ready-made helper scripts it ships "
            "(e.g. scripts/add_slide.py). CHECK THAT LIST BEFORE WRITING ANYTHING: if a helper script "
            "already does what you need, run it with run_command — do not write a brand-new generator "
            "from scratch that duplicates it. Only write your own generator when no matching script exists.\n"
            f"- Write the complete generator script with write_file ({SCRATCH_DIR}\\generate_<name>.py or .js) "
            "using python-pptx / docx / openpyxl / pptxgenjs, then run it with run_command. Default to "
            "python-pptx for .pptx unless the skill's own scripts or resources are JS-based — most skill "
            "folders ship Python helpers, and pptxgenjs has almost no in-context documentation here, so "
            "choosing it means improvising its API blind. Never write a mock script that only prints "
            "strings, and never run dummy print commands to narrate progress.\n"
            "- If a library throws an environment/native-module error unrelated to your own code (a require() "
            "crash inside the package's own dist files, a missing native binary, etc.), that is a signal to "
            "switch approach — not to reverse-engineer the package's internals with console.log/Object.keys "
            "probes. Switch to the skill's documented language/library instead of debugging a black box.\n"
            "- The design rules are the POINT of loading the skill. A script that exits 0 but ignores the "
            "skill's colours, layout and quality guidance and emits bare default-template output (default "
            "theme, plain bullet lists, no visual hierarchy) has NOT satisfied the request. 'It ran' and "
            "'it looks good' are two different bars - clear BOTH.\n"
            "- Run the skill's own validation script when it provides one (e.g. scripts/office/validate.py) "
            "before you verify. verify_task_result also checks the file structurally and WILL reject a "
            "corrupt file, a near-empty file, a deck with under three slides, or a skill-backed format you "
            "built without ever calling load_skill.\n"
            "- Save deliverables where the user asked; default to the Desktop.\n"
            "- When a command fails, read the real error and fix that line. Missing module -> install it with "
            "pip/npm via run_command, then retry. Do not narrate debugging.\n\n" + catalog
        )
        token = _worker_id.set(worker.id)
        try:
            async def worker_executor(name: str, args: dict) -> str:
                # Keep the terminal trace unambiguous: after handoff these are
                # worker actions, not extra actions from the voice coordinator.
                # ASCII only: this print used to contain a U+2192 arrow, which
                # raised UnicodeEncodeError on a cp1252 console. That exception
                # happened BEFORE the real tool ran and was swallowed by
                # run_brain_turn's except-block into "Tool 'x' raised an
                # exception", so every worker tool call silently failed and the
                # worker always ended unverified. Never put non-ASCII here.
                print(f"[WORKER {worker.id}] -> {name}")
                await self.events.put({
                    "kind": "progress", "worker": worker.summary(), "tool": name,
                })
                if worker.inbox:
                    messages = "\n".join(worker.inbox)
                    worker.inbox.clear()
                    worker.history.append({
                        "role": "user",
                        "content": f"[VOICE COORDINATOR UPDATE]\n{messages}",
                    })
                result = await executor(name, args)
                worker.tool_log.append({"name": name, "args": args, "result": str(result)[:4000]})
                await self.events.put({"kind": "tool_result", "worker": worker.summary(), "tool": name, "result": str(result)[:300]})
                return result

            worker.result = await run_brain_turn(
                worker.task, worker.history, worker_executor,
                [d for d in declarations if d.get("name") not in {
                    "start_task_worker",
                    "send_task_worker_message", "interrupt_task_worker",
                    "answer_worker_question",
                }],
                prompt,
                max_tool_hops=30,
            )
            if worker.verified:
                worker.status = "completed"
                await self.events.put({"kind": "completed", "worker": worker.summary()})
            else:
                worker.status = "failed"
                worker.error = "Worker ended without verification evidence."
                await self.events.put({"kind": "failed", "worker": worker.summary()})
        except asyncio.CancelledError:
            worker.status = "interrupted"
            await self.events.put({"kind": "interrupted", "worker": worker.summary()})
            raise
        except Exception as exc:
            worker.error = str(exc)
            worker.status = "failed"
            await self.events.put({"kind": "failed", "worker": worker.summary()})
        finally:
            _worker_id.reset(token)

    async def pop_events(self) -> list[dict]:
        result = []
        while True:
            try: result.append(self.events.get_nowait())
            except asyncio.QueueEmpty: return result

    def list(self) -> list[dict]:
        return [w.summary() for w in self.workers.values()]

    async def set_plan(self, steps: list[str]) -> str:
        worker = self.workers.get(_worker_id.get())
        if not worker:
            return "Plan rejected: no active worker."
        worker.plan = [str(step).strip() for step in steps if str(step).strip()][:12]
        await self.events.put({"kind": "state", "message": "plan recorded", "worker": worker.summary()})
        return f"Plan recorded: {len(worker.plan)} steps."

    async def verify_current(self, outputs: list[str], summary: str) -> str:
        worker = self.workers.get(_worker_id.get())
        if not worker:
            return "Verification rejected: no active worker."
        await self.events.put({"kind": "state", "message": "verifying", "worker": worker.summary()})
        if isinstance(outputs, str):
            try:
                outputs = json.loads(outputs)
            except json.JSONDecodeError:
                outputs = [outputs]
        if not isinstance(outputs, list):
            outputs = []
        executed = any(item["name"] in {"write_file", "str_replace_editor", "run_command", "python_eval"} for item in worker.tool_log)
        desktop = Path.home() / "Desktop"
        existing = []
        for path in outputs:
            raw = str(path).strip()
            if not raw:
                continue
            candidate = desktop / raw.split("/", 1)[1] if raw.lower().startswith("desktop/") else Path(raw)
            if candidate.exists():
                existing.append(str(candidate.resolve()))
        if not executed:
            return "Verification rejected: no real edit/create/command tool was executed."
        if not existing:
            return "Verification rejected: none of the declared output files exist."

        # Quality gate. "The file exists" and "the file is any good" are two
        # different bars; only the first used to be checked, so a corrupt or
        # bare default-template deck passed and was reported as success.
        problems: list[str] = []
        skill_backed = {".pptx", ".potx", ".docx", ".xlsx", ".pdf"}
        touched_skill_format = False
        for path_str in existing:
            p = Path(path_str)
            ext = p.suffix.lower()
            if ext not in skill_backed:
                continue
            touched_skill_format = True
            problems.extend(_inspect_office_file(p))

        if touched_skill_format:
            loaded = [i for i in worker.tool_log if i["name"] == "load_skill"]
            if not loaded:
                problems.append(
                    "you never called load_skill, so the format's real rules and "
                    "validation steps were never read"
                )

        if problems:
            return (
                "Verification REJECTED - the file exists but did not pass quality checks:\n"
                + "\n".join(f"- {p}" for p in problems)
                + "\nFix these for real and call verify_task_result again. Do not report success."
            )

        worker.verified = True
        worker.verified_outputs = existing
        worker.result = summary.strip()
        return "Verification passed. You may now report completion."

    # ── Worker -> boss -> user question round trip ───────────────────────────
    # The worker has every power the boss has except speaking, so when it needs
    # a decision it cannot ask directly - it asks the boss, the boss speaks the
    # question, and the user's answer is routed back here.
    MAX_QUESTIONS_PER_WORKER = 2
    ANSWER_TIMEOUT_S = 240

    async def ask_boss(self, question: str, options: list[str] | None = None) -> str:
        """Worker-only. Blocks this worker until the user answers, the timeout
        expires, or its question budget is spent. Never blocks the boss - the
        voice loop keeps running and can still steer or interrupt."""
        worker = self.workers.get(_worker_id.get())
        if not worker:
            return "Question rejected: no active worker."
        question = (question or "").strip()
        if not question:
            return "Question rejected: empty question."

        if worker.questions_asked >= self.MAX_QUESTIONS_PER_WORKER:
            return (
                "Question budget spent - you have already asked "
                f"{worker.questions_asked}. Do NOT ask again. Choose the most "
                "sensible professional default, continue, and state the "
                "assumption you made in your final report."
            )

        worker.questions_asked += 1
        worker.question = question
        loop = asyncio.get_running_loop()
        worker.answer_future = loop.create_future()
        await self.events.put({
            "kind": "question", "worker": worker.summary(),
            "question": question, "options": options or [],
        })

        try:
            answer = await asyncio.wait_for(
                worker.answer_future, timeout=self.ANSWER_TIMEOUT_S
            )
            return f"The user answered: {answer}"
        except asyncio.TimeoutError:
            # Never strand the deliverable waiting on a human. Proceed.
            return (
                "No answer arrived in time. Do not ask again. Proceed now using "
                "the most sensible professional default and note the assumption "
                "in your final report."
            )
        finally:
            worker.question = ""
            worker.answer_future = None

    def answer_question(self, worker_id: str, answer: str) -> str:
        """Boss-side: deliver the user's spoken answer back to a blocked worker."""
        worker = self.workers.get(worker_id)
        if not worker:
            # Convenience: with a single blocked worker, don't require the id.
            blocked = [w for w in self.workers.values() if w.answer_future
                       and not w.answer_future.done()]
            if len(blocked) == 1:
                worker = blocked[0]
            else:
                return f"Worker {worker_id} not found."
        fut = worker.answer_future
        if not fut or fut.done():
            return f"Worker {worker.id} is not waiting for an answer."
        fut.set_result((answer or "").strip())
        return f"Answer delivered to worker {worker.id}."

    def pending_question(self) -> dict | None:
        for w in self.workers.values():
            if w.answer_future and not w.answer_future.done():
                return {"worker_id": w.id, "question": w.question}
        return None

    def send_message(self, worker_id: str, message: str) -> str:
        worker = self.workers.get(worker_id)
        if not worker:
            return f"Worker {worker_id} not found."
        if worker.status not in {"queued", "running"}:
            return f"Worker {worker_id} is already {worker.status}."
        worker.inbox.append(message.strip())
        return f"Update queued for worker {worker_id}."

    def interrupt(self, worker_id: str) -> str:
        worker = self.workers.get(worker_id)
        if not worker:
            return f"Worker {worker_id} not found."
        if worker.runner_task and not worker.runner_task.done():
            worker.runner_task.cancel()
            return f"Worker {worker_id} interruption requested."
        return f"Worker {worker_id} is already {worker.status}."


task_workers = TaskWorkerManager()

TASK_WORKER_DECLARATIONS = [
    {"name": "start_task_worker", "description": "Start a persistent background worker for complex multi-step work involving skills, research, files, retries, or validation. Use direct tools for simple one-step requests.", "parameters": {"type": "OBJECT", "properties": {"task": {"type": "STRING", "description": "Complete goal, constraints, and deliverable."}, "role": {"type": "STRING", "description": "Focused role such as executor, researcher, or validator."}}, "required": ["task"]}},
    {"name": "task_worker_status", "description": "List persistent task workers and their actual status/results.", "parameters": {"type": "OBJECT", "properties": {}}},
    {"name": "send_task_worker_message", "description": "Send a new instruction or additional context to a worker that is still running (e.g. the user added detail after the worker already started).", "parameters": {"type": "OBJECT", "properties": {"worker_id": {"type": "STRING", "description": "The worker's id, from task_worker_status."}, "message": {"type": "STRING", "description": "The update/instruction to inject."}}, "required": ["worker_id", "message"]}},
    {"name": "interrupt_task_worker", "description": "Stop a running worker (e.g. the user explicitly says to cancel/stop the task).", "parameters": {"type": "OBJECT", "properties": {"worker_id": {"type": "STRING", "description": "The worker's id, from task_worker_status."}}, "required": ["worker_id"]}},
    {"name": "task_set_plan", "description": "Worker-only: record the concrete task plan before execution.", "parameters": {"type": "OBJECT", "properties": {"steps": {"type": "ARRAY", "items": {"type": "STRING"}}}, "required": ["steps"]}},
    {"name": "verify_task_result", "description": "Worker-only: verify completion before claiming success, using real existing output paths.", "parameters": {"type": "OBJECT", "properties": {"outputs": {"type": "ARRAY", "items": {"type": "STRING"}}, "summary": {"type": "STRING"}}, "required": ["outputs", "summary"]}},
    {"name": "answer_worker_question", "description": "Boss-only: deliver the user's spoken answer back to a worker that is blocked waiting on a question. Call this as soon as the user answers a question you relayed from a worker.", "parameters": {"type": "OBJECT", "properties": {"worker_id": {"type": "STRING", "description": "The worker that asked. Optional when only one worker is waiting."}, "answer": {"type": "STRING", "description": "What the user actually said, in their own terms."}}, "required": ["answer"]}},
]