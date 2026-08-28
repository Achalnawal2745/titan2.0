"""
core/todo_engine.py — Dynamic Task Checklist Engine.
Ported from DeepSeek Harness (`packages/todo`).

Manages real-time task checklist with states:
- PENDING (🟡 pending)
- IN_PROGRESS (🔵 in_progress)
- COMPLETED (🟢 completed)
- BLOCKED (🔴 blocked)

Writes directly to memory/workpad.md and emits live updates.
"""
from __future__ import annotations

import json
from datetime import datetime
from enum import Enum
from pathlib import Path
from typing import Any, Dict, List, Optional


class TodoStatus(str, Enum):
    PENDING = "pending"
    IN_PROGRESS = "in_progress"
    COMPLETED = "completed"
    BLOCKED = "blocked"


class TodoItem:
    def __init__(
        self,
        id: int,
        title: str,
        status: TodoStatus = TodoStatus.PENDING,
        details: str = "",
    ):
        self.id = id
        self.title = title
        self.status = status if isinstance(status, TodoStatus) else TodoStatus(status)
        self.details = details
        self.updated_at = datetime.now().isoformat()

    def to_dict(self) -> Dict[str, Any]:
        return {
            "id": self.id,
            "title": self.title,
            "status": self.status.value,
            "details": self.details,
            "updated_at": self.updated_at,
        }


class TodoEngine:
    def __init__(self):
        base = Path(__file__).resolve().parent.parent
        self.state_file = base / "memory" / "todo_state.json"
        self.workpad_file = base / "memory" / "workpad.md"
        self.title = "Active Task Plan"
        self.items: List[TodoItem] = []
        self._load()

    def _load(self) -> None:
        if self.state_file.exists():
            try:
                data = json.loads(self.state_file.read_text(encoding="utf-8"))
                self.title = data.get("title", "Active Task Plan")
                self.items = [
                    TodoItem(
                        id=it["id"],
                        title=it["title"],
                        status=TodoStatus(it.get("status", "pending")),
                        details=it.get("details", ""),
                    )
                    for it in data.get("items", [])
                ]
            except Exception:
                self.items = []

    def save(self) -> None:
        # Save JSON state
        data = {
            "title": self.title,
            "updated_at": datetime.now().isoformat(),
            "items": [it.to_dict() for it in self.items],
        }
        self.state_file.parent.mkdir(parents=True, exist_ok=True)
        self.state_file.write_text(json.dumps(data, indent=2), encoding="utf-8")

        # Save human-readable Workpad Markdown
        md_lines = [f"# 📋 {self.title}", "", f"> Last updated: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}", ""]
        for it in self.items:
            if it.status == TodoStatus.COMPLETED:
                icon = "🟢 [x]"
                tag = "COMPLETED"
            elif it.status == TodoStatus.IN_PROGRESS:
                icon = "🔵 [/]"
                tag = "IN_PROGRESS"
            elif it.status == TodoStatus.BLOCKED:
                icon = "🔴 [!]"
                tag = "BLOCKED"
            else:
                icon = "🟡 [ ]"
                tag = "PENDING"
            
            line = f"- {icon} **Step {it.id}**: {it.title} `({tag})`"
            if it.details:
                line += f"\n  - *Notes:* {it.details}"
            md_lines.append(line)

        self.workpad_file.write_text("\n".join(md_lines) + "\n", encoding="utf-8")

    def set_plan(self, title: str, steps: List[str]) -> str:
        """Initializes a new task plan."""
        self.title = title.strip() or "Active Task Plan"
        self.items = [
            TodoItem(id=idx + 1, title=step.strip(), status=TodoStatus.PENDING)
            for idx, step in enumerate(steps)
            if step.strip()
        ]
        self.save()
        return self.get_summary()

    def update_step(self, step_id: int, status: str, details: str = "") -> str:
        """Updates status of a specific step."""
        for it in self.items:
            if it.id == step_id:
                try:
                    it.status = TodoStatus(status.lower())
                except ValueError:
                    it.status = TodoStatus.IN_PROGRESS
                if details:
                    it.details = details
                it.updated_at = datetime.now().isoformat()
                self.save()
                return f"Step {step_id} updated to {it.status.value.upper()}."
        return f"Step {step_id} not found."

    def get_summary(self) -> str:
        if not self.items:
            return "No active task plan."
        lines = [f"📋 {self.title}:"]
        for it in self.items:
            st = it.status.value.upper()
            lines.append(f"  • Step {it.id}: [{st}] {it.title}")
        return "\n".join(lines)

    def has_pending_steps(self) -> bool:
        return any(it.status in (TodoStatus.PENDING, TodoStatus.IN_PROGRESS) for it in self.items)


# Global singleton
todo_engine = TodoEngine()


# ── Gemini Tool Declarations ──
TODO_WRITE_DECLARATION = {
    "name": "todo_write",
    "description": (
        "Create or update the step-by-step task checklist on the Workpad. "
        "Use this tool whenever starting a multi-step task or updating progress. "
        "Action can be: 'set_plan' (title, steps list) or 'update_step' (step_id, status: 'pending'|'in_progress'|'completed'|'blocked', details)."
    ),
    "parameters": {
        "type": "OBJECT",
        "properties": {
            "action": {"type": "STRING", "description": "'set_plan' to create steps, or 'update_step' to update a step's status"},
            "title": {"type": "STRING", "description": "Title of the plan (used with 'set_plan')"},
            "steps": {"type": "ARRAY", "items": {"type": "STRING"}, "description": "List of step titles (used with 'set_plan')"},
            "step_id": {"type": "INTEGER", "description": "Step number to update (used with 'update_step')"},
            "status": {"type": "STRING", "description": "'pending', 'in_progress', 'completed', or 'blocked'"},
            "details": {"type": "STRING", "description": "Optional notes or outcome for this step"},
        },
        "required": ["action"],
    },
}

TODO_READ_DECLARATION = {
    "name": "todo_read",
    "description": "Read the current active task checklist and step statuses from the Workpad.",
    "parameters": {
        "type": "OBJECT",
        "properties": {},
    },
}
