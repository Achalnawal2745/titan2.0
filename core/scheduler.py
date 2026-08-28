"""
core/scheduler.py — Async Timer & Schedule Engine.
Ported from DeepSeek Harness (`packages/schedule`).

Allows AI to set:
1. One-shot timers (DurationSeconds)
2. Recurring cron tasks
"""
from __future__ import annotations

import asyncio
from datetime import datetime
from typing import Any, Callable, Dict, List, Optional


class ScheduleTask:
    def __init__(
        self,
        task_id: str,
        prompt: str,
        duration_seconds: float,
        is_recurring: bool = False,
        callback: Optional[Callable[[str], Any]] = None,
    ):
        self.task_id = task_id
        self.prompt = prompt
        self.duration_seconds = duration_seconds
        self.is_recurring = is_recurring
        self.callback = callback
        self.cancelled = False
        self._task_handle: Optional[asyncio.Task] = None

    async def _run(self) -> None:
        try:
            await asyncio.sleep(self.duration_seconds)
            if not self.cancelled and self.callback:
                print(f"[Scheduler] ⏰ Timer fired: {self.prompt}")
                res = self.callback(self.prompt)
                if asyncio.iscoroutine(res):
                    await res
        except asyncio.CancelledError:
            pass


class Scheduler:
    def __init__(self):
        self._tasks: Dict[str, ScheduleTask] = {}
        self._counter = 0

    def add_timer(
        self,
        prompt: str,
        duration_seconds: float,
        callback: Optional[Callable[[str], Any]] = None,
    ) -> str:
        self._counter += 1
        task_id = f"timer_{self._counter}"
        task = ScheduleTask(
            task_id=task_id,
            prompt=prompt,
            duration_seconds=duration_seconds,
            callback=callback,
        )
        self._tasks[task_id] = task
        try:
            loop = asyncio.get_running_loop()
            task._task_handle = loop.create_task(task._run())
        except RuntimeError:
            pass
        return f"⏰ Timer set for {duration_seconds}s: '{prompt}' (ID: {task_id})"

    def cancel(self, task_id: str) -> bool:
        task = self._tasks.get(task_id)
        if task:
            task.cancelled = True
            if task._task_handle:
                task._task_handle.cancel()
            del self._tasks[task_id]
            return True
        return False


# Global singleton
scheduler = Scheduler()


# ── Gemini Tool Declaration ──
SCHEDULE_DECLARATION = {
    "name": "schedule",
    "description": "Set a timer or reminder to run in the background after a specified duration in seconds.",
    "parameters": {
        "type": "OBJECT",
        "properties": {
            "duration_seconds": {"type": "NUMBER", "description": "Number of seconds to wait before triggering"},
            "prompt": {"type": "STRING", "description": "Reminder or task description to execute when timer expires"},
        },
        "required": ["duration_seconds", "prompt"],
    },
}
