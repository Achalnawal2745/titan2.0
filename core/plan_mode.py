"""
core/plan_mode.py — Architectural Plan Mode Engine for TITAN.
Adapted from DeepSeek Harness (`packages/plan/plan-mode`).

Allows TITAN to enter structured planning mode before executing large-scale or multi-file changes.
"""
from __future__ import annotations

from pathlib import Path
from typing import Any, Dict, List, Optional


class PlanMode:
    def __init__(self):
        base = Path(__file__).resolve().parent.parent
        self.plan_file = base / "memory" / "active_plan.md"
        self.is_active = False
        self.active_goal = ""
        self.plan_text = ""

    def enter_plan_mode(self, goal: str) -> str:
        """Enters planning mode for architectural/multi-step tasks."""
        self.is_active = True
        self.active_goal = goal.strip()
        return (
            f"🗺️ Plan Mode Activated for: '{self.active_goal}'.\n"
            "Now formulate your architectural plan, outline key components and steps, "
            "and call 'exit_plan_mode' once ready to begin execution."
        )

    def save_plan(self, plan_markdown: str) -> str:
        """Saves architectural plan to memory/active_plan.md."""
        self.plan_text = plan_markdown
        self.plan_file.parent.mkdir(parents=True, exist_ok=True)
        self.plan_file.write_text(plan_markdown, encoding="utf-8")
        return "Plan saved to memory/active_plan.md."

    def exit_plan_mode(self, summary: str = "") -> str:
        """Exits planning mode and transitions to execution."""
        self.is_active = False
        res = f"🚀 Plan Approved. Exiting Plan Mode. Transitioning to execution."
        if summary:
            res += f" Summary: {summary}"
        return res


# Global singleton
plan_mode = PlanMode()


# ── Gemini Tool Declarations ──
PLAN_MODE_DECLARATIONS = [
    {
        "name": "enter_plan_mode",
        "description": "Enter Plan Mode when a request requires architectural decisions, multi-file design, or user alignment before execution.",
        "parameters": {
            "type": "OBJECT",
            "properties": {
                "goal": {"type": "STRING", "description": "High-level description of what is being planned"},
            },
            "required": ["goal"],
        },
    },
    {
        "name": "exit_plan_mode",
        "description": "Exit Plan Mode and begin executing the approved plan.",
        "parameters": {
            "type": "OBJECT",
            "properties": {
                "summary": {"type": "STRING", "description": "Brief summary of the finalized plan"},
            },
        },
    },
]
