"""
core/scope.py — Scoped Context Isolation.
Ported from DeepSeek Harness (`packages/core/scope`).

Isolates variables, scratch directories, and active tool parameters
between concurrent sub-tasks and subagents so they never collide.
"""
from __future__ import annotations

import os
from pathlib import Path
from typing import Any, Dict, Optional


class TaskScope:
    def __init__(self, scope_id: str, parent_scope: Optional[TaskScope] = None):
        self.scope_id = scope_id
        self.parent_scope = parent_scope
        self._values: Dict[str, Any] = {}
        base = Path(__file__).resolve().parent.parent
        self.scratch_dir = base / "scratch" / "scopes" / scope_id
        self.scratch_dir.mkdir(parents=True, exist_ok=True)

    def set(self, key: str, value: Any) -> None:
        self._values[key] = value

    def get(self, key: str, default: Any = None) -> Any:
        if key in self._values:
            return self._values[key]
        if self.parent_scope:
            return self.parent_scope.get(key, default)
        return default

    def clean(self) -> None:
        self._values.clear()
        try:
            for item in self.scratch_dir.iterdir():
                if item.is_file():
                    item.unlink()
        except Exception:
            pass


root_scope = TaskScope("root")
