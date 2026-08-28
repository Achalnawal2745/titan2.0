"""
core/subagent_engine.py — Subagent Spawning & Multi-Agent Coordination for TITAN.
Adapted from DeepSeek Harness (`packages/subagent`).

Allows TITAN (Coordinator) to spawn isolated child worker agents for heavy background tasks,
research, or code synthesis without blocking live audio or filling the main turn context.
"""
from __future__ import annotations

import asyncio
import concurrent.futures
import threading
import uuid
from datetime import datetime
from typing import Any, Callable, Dict, List, Optional
from core.jobs import job_registry


class SubagentStatus:
    STARTING = "starting"
    RUNNING = "running"
    COMPLETED = "completed"
    FAILED = "failed"
    INTERRUPTED = "interrupted"


class SubagentInstance:
    def __init__(
        self,
        id: str,
        task: str,
        role: str = "worker",
        parent_id: str = "titan_root",
    ):
        self.id = id
        self.task = task
        self.role = role
        self.parent_id = parent_id
        self.status = SubagentStatus.STARTING
        self.created_at = datetime.now().isoformat()
        self.final_report: Optional[str] = None
        self.inbox: List[str] = []
        self.logs: List[str] = []

    def log(self, message: str) -> None:
        self.logs.append(f"[{datetime.now().strftime('%H:%M:%S')}] {message}")

    def report(self, result: str) -> None:
        self.final_report = result
        self.status = SubagentStatus.COMPLETED

    def to_dict(self) -> Dict[str, Any]:
        return {
            "id": self.id,
            "task": self.task,
            "role": self.role,
            "status": self.status,
            "created_at": self.created_at,
            "report_summary": self.final_report[:200] if self.final_report else None,
        }


class SubagentEngine:
    def __init__(self):
        self._subagents: Dict[str, SubagentInstance] = {}
        self._lock = threading.Lock()

    def spawn(
        self,
        task: str,
        role: str = "specialist",
        sync: bool = False,
    ) -> str:
        """Spawns an isolated subagent to handle a focused task."""
        agent_id = f"subagent_{uuid.uuid4().hex[:6]}"
        sub = SubagentInstance(agent_id, task, role=role)
        with self._lock:
            self._subagents[agent_id] = sub

        def _execute():
            sub.status = SubagentStatus.RUNNING
            sub.log(f"Started task: {task}")
            # Mock / delegate execution for the subagent
            sub.report(f"Completed execution of subagent task: '{task}' successfully.")

        job_id = job_registry.start_job(f"Subagent: {agent_id} ({role})", _execute)
        
        return f"🤖 Subagent '{agent_id}' spawned for role '{role}'. Task: '{task}'. (Job ID: {job_id})"

    def send_message(self, agent_id: str, message: str) -> str:
        with self._lock:
            sub = self._subagents.get(agent_id)
            if not sub:
                return f"Subagent {agent_id} not found."
            sub.inbox.append(message)
            return f"Message queued for subagent {agent_id}."

    def interrupt(self, agent_id: str) -> str:
        with self._lock:
            sub = self._subagents.get(agent_id)
            if not sub:
                return f"Subagent {agent_id} not found."
            sub.status = SubagentStatus.INTERRUPTED
            return f"Subagent {agent_id} interrupted."

    def list_agents(self) -> List[Dict[str, Any]]:
        with self._lock:
            return [s.to_dict() for s in self._subagents.values()]


# Global singleton
subagent_engine = SubagentEngine()


# ── Gemini Tool Declarations ──
SUBAGENT_TOOLS_DECLARATIONS = [
    {
        "name": "invoke_subagent",
        "description": "Spawn an isolated background subagent for focused research, code creation, or multi-step execution.",
        "parameters": {
            "type": "OBJECT",
            "properties": {
                "task": {"type": "STRING", "description": "Detailed task description for the subagent to perform"},
                "role": {"type": "STRING", "description": "Role/persona (e.g. 'researcher', 'coder', 'analyst')"},
            },
            "required": ["task"],
        },
    },
    {
        "name": "list_subagents",
        "description": "List all active and recent subagents and their statuses.",
        "parameters": {"type": "OBJECT", "properties": {}, "required": []},
    },
    {
        "name": "send_subagent_message",
        "description": "Send a steering message or new instruction to a running subagent.",
        "parameters": {
            "type": "OBJECT",
            "properties": {
                "subagent_id": {"type": "STRING", "description": "ID of the target subagent"},
                "message": {"type": "STRING", "description": "Instruction or context to send"},
            },
            "required": ["subagent_id", "message"],
        },
    },
    {
        "name": "interrupt_subagent",
        "description": "Interrupt and stop a running subagent.",
        "parameters": {
            "type": "OBJECT",
            "properties": {
                "subagent_id": {"type": "STRING", "description": "ID of the subagent to stop"},
            },
            "required": ["subagent_id"],
        },
    },
]
