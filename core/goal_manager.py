"""
core/goal_manager.py — Event-Sourced Persistent Goal Manager & Round Driver.
Ported from DeepSeek Harness (`packages/goal/goal`, `packages/goal/goal-round-driver`, `packages/goal/command-goal`).

Provides:
1. Event-sourced persistent Goal state (`dsh-goal`).
2. Goal Round Driver (`dsh-goal-round-driver`) with automatic round-boundary prompts.
3. Slash Command `/goal` parser for human direct control (`dsh-command-goal`).
"""
from __future__ import annotations

import json
from datetime import datetime
from pathlib import Path
from typing import Any, Dict, List, Optional


def render_goal_round_prompt(objective: str, round_num: int, max_rounds: int) -> str:
    """Exact prompt format from DeepSeek Harness (`goal-round-driver/src/prompt.ts`)."""
    return (
        "<goal_round>\n"
        f"Objective: {json.dumps(objective)}\n"
        f"Round: {round_num}/{max_rounds}\n\n"
        "Continue working toward the objective in this same session. Treat the current workspace, "
        "tool results, and durable session state as authoritative; inspect them instead of assuming "
        "earlier narration is still current. Make concrete progress and verify the result. Before "
        "claiming completion, gather evidence that the whole objective is achieved, read the current "
        "goal, and mark it complete. If work remains, leave the goal active for the next round. "
        "Follow the configured goal-tool policy before reporting a blocker.\n"
        "</goal_round>"
    )


class Goal:
    def __init__(
        self,
        id: str,
        description: str,
        max_rounds: int = 10,
        status: str = "active",
    ):
        self.id = id
        self.description = description
        self.max_rounds = max_rounds
        self.current_round = 1
        self.status = status  # active, completed, cancelled
        self.created_at = datetime.now().isoformat()
        self.updated_at = datetime.now().isoformat()

    def to_dict(self) -> Dict[str, Any]:
        return {
            "id": self.id,
            "description": self.description,
            "max_rounds": self.max_rounds,
            "current_round": self.current_round,
            "status": self.status,
            "created_at": self.created_at,
            "updated_at": self.updated_at,
        }


class GoalRoundDriver:
    """Manages round progression and auto-continuation for long tasks."""
    def __init__(self, manager: GoalManager):
        self.manager = manager

    def should_continue_round(self) -> bool:
        goal = self.manager.active_goal
        if goal and goal.status == "active":
            return goal.current_round < goal.max_rounds
        return False

    def next_round_prompt(self) -> Optional[str]:
        goal = self.manager.active_goal
        if goal and goal.status == "active":
            goal.current_round += 1
            goal.updated_at = datetime.now().isoformat()
            self.manager.save()
            return render_goal_round_prompt(goal.description, goal.current_round, goal.max_rounds)
        return None


class GoalManager:
    def __init__(self):
        base = Path(__file__).resolve().parent.parent
        self.goal_file = base / "memory" / "goals.json"
        self.active_goal: Optional[Goal] = None
        self.driver = GoalRoundDriver(self)
        self._load()

    def _load(self) -> None:
        if self.goal_file.exists():
            try:
                data = json.loads(self.goal_file.read_text(encoding="utf-8"))
                active_data = data.get("active_goal")
                if active_data:
                    self.active_goal = Goal(
                        id=active_data["id"],
                        description=active_data["description"],
                        max_rounds=active_data.get("max_rounds", 10),
                        status=active_data.get("status", "active"),
                    )
                    self.active_goal.current_round = active_data.get("current_round", 1)
            except Exception:
                self.active_goal = None

    def save(self) -> None:
        self.goal_file.parent.mkdir(parents=True, exist_ok=True)
        data = {
            "active_goal": self.active_goal.to_dict() if self.active_goal else None,
            "saved_at": datetime.now().isoformat(),
        }
        self.goal_file.write_text(json.dumps(data, indent=2), encoding="utf-8")

    def set_goal(self, description: str, max_rounds: int = 10) -> str:
        goal_id = f"goal_{datetime.now().strftime('%Y%m%d_%H%M%S')}"
        self.active_goal = Goal(id=goal_id, description=description, max_rounds=max_rounds)
        self.save()
        return f"🎯 Active Goal Set: '{description}' (Max rounds: {max_rounds})"

    def handle_slash_command(self, text: str) -> Optional[str]:
        """Handles '/goal <objective>' command from human input."""
        raw = text.strip()
        if not raw.startswith("/goal"):
            return None
        parts = raw[5:].strip()
        if not parts:
            if self.active_goal:
                return f"🎯 Current Active Goal: {self.active_goal.description} (Round {self.active_goal.current_round}/{self.active_goal.max_rounds})"
            return "No active goal. Usage: /goal <your objective>"
        return self.set_goal(parts)

    def advance_round(self) -> bool:
        if self.active_goal and self.active_goal.status == "active":
            return self.driver.should_continue_round()
        return False

    def complete_goal(self, outcome: str = "Goal achieved successfully.") -> str:
        if self.active_goal:
            desc = self.active_goal.description
            self.active_goal.status = "completed"
            self.save()
            res = f"🎉 Goal Completed: '{desc}' — {outcome}"
            self.active_goal = None
            self.save()
            return res
        return "No active goal to complete."


# Global singleton
goal_manager = GoalManager()


# ── Gemini Tool Declarations ──
GOAL_TOOLS_DECLARATIONS = [
    {
        "name": "set_goal",
        "description": "Set a persistent long-running goal that spans multiple turns until completed.",
        "parameters": {
            "type": "OBJECT",
            "properties": {
                "description": {"type": "STRING", "description": "Description of the high-level objective"},
                "max_rounds": {"type": "INTEGER", "description": "Maximum number of rounds to iterate (default 10)"},
            },
            "required": ["description"],
        },
    },
    {
        "name": "complete_goal",
        "description": "Mark the active long-running goal as completed.",
        "parameters": {
            "type": "OBJECT",
            "properties": {
                "outcome": {"type": "STRING", "description": "Summary of the final result / deliverable"},
            },
        },
    },
]
