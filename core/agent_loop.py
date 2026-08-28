"""
core/agent_loop.py — Finite State Machine & Turn/Step Controller.
Ported from DeepSeek Harness (`packages/core/agent-loop`).

Coordinates:
- Turn Start: Initiates planning, sets active job state.
- Step Cycle: Executes step -> validates via ToolPipeline -> checks WorkPad steps.
- Continuation: Guarantees multi-step chaining without premature termination.
"""
from __future__ import annotations

import asyncio
from datetime import datetime
from enum import Enum
from typing import Any, Callable, Dict, List, Optional

from core.agent import Agent, AgentStatus, agent_registry
from core.error_guard import ErrorGuard
from core.tool_pipeline import ToolPipeline


class LoopState(str, Enum):
    IDLE = "idle"
    PLANNING = "planning"
    STEP_RUNNING = "step_running"
    EVALUATING = "evaluating"
    TURN_STOPPING = "turn_stopping"
    TURN_CLOSED = "turn_closed"


class AgentLoop:
    def __init__(self, agent: Optional[Agent] = None):
        self.agent = agent or agent_registry.root_agent
        self.guard = ErrorGuard()
        self.pipeline = ToolPipeline(self.guard)
        self.state = LoopState.IDLE
        self.active_turn_steps: List[Dict[str, Any]] = []
        self.turn_number = 0

    def start_turn(self, goal: str) -> None:
        """Starts a new agent turn."""
        self.turn_number += 1
        self.state = LoopState.PLANNING
        self.agent.set_status(AgentStatus.PLANNING)
        self.active_turn_steps = []

    def pre_step(self, tool_name: str, args: dict) -> dict:
        """Called before a tool executes in the current step."""
        self.state = LoopState.STEP_RUNNING
        self.agent.set_status(AgentStatus.EXECUTING)
        return self.pipeline.pre_execute(tool_name, args)

    def post_step(self, tool_name: str, args: dict, raw_result: Any) -> Dict[str, Any]:
        """Called after a tool executes to sanitize output, check errors, and advance step."""
        self.state = LoopState.EVALUATING
        step_result = self.pipeline.post_execute(tool_name, args, raw_result)
        
        self.active_turn_steps.append({
            "tool": tool_name,
            "args": args,
            "ok": step_result["ok"],
            "timestamp": datetime.now().isoformat(),
        })

        return step_result

    def check_turn_completion(self, has_pending_workpad_steps: bool) -> bool:
        """Determines if the current turn has completed all required work.

        Returns:
            True if all steps are satisfied and agent can speak;
            False if more steps remain owed.
        """
        if has_pending_workpad_steps:
            # More steps owed
            self.state = LoopState.STEP_RUNNING
            return False
        
        self.state = LoopState.TURN_CLOSED
        self.agent.set_status(AgentStatus.DONE)
        return True

    def reset(self) -> None:
        self.state = LoopState.IDLE
        self.agent.set_status(AgentStatus.IDLE)
        self.active_turn_steps = []


# Singleton global loop
main_agent_loop = AgentLoop()
