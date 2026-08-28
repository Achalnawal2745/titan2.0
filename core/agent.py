"""
core/agent.py — Agent Lifecycle & Status Manager.
Ported from DeepSeek Harness (`packages/core/agent`).

Tracks:
- Agent instance identity, session UUID, creation time.
- Status enum: IDLE, PLANNING, EXECUTING, WAITING_USER, DONE, FAILED.
- Parent-child ownership for subagents and background worker tasks.
"""
from __future__ import annotations

import uuid
from datetime import datetime
from enum import Enum
from typing import Any, Dict, List, Optional


class AgentStatus(str, Enum):
    IDLE = "idle"
    PLANNING = "planning"
    EXECUTING = "executing"
    WAITING_USER = "waiting_user"
    DONE = "done"
    FAILED = "failed"


class Agent:
    def __init__(
        self,
        name: str = "TITAN-Core",
        owner_id: Optional[str] = None,
        metadata: Optional[Dict[str, Any]] = None,
    ):
        self.id = f"agent_{uuid.uuid4().hex[:8]}"
        self.name = name
        self.owner_id = owner_id
        self.status = AgentStatus.IDLE
        self.created_at = datetime.now().isoformat()
        self.metadata = metadata or {}
        self.current_job_id: Optional[str] = None
        self.subagents: List[str] = []

    def set_status(self, status: AgentStatus) -> None:
        self.status = status

    def spawn_child(self, name: str, metadata: Optional[Dict[str, Any]] = None) -> Agent:
        child = Agent(name=name, owner_id=self.id, metadata=metadata)
        self.subagents.append(child.id)
        return child

    def to_dict(self) -> Dict[str, Any]:
        return {
            "id": self.id,
            "name": self.name,
            "owner_id": self.owner_id,
            "status": self.status.value,
            "created_at": self.created_at,
            "current_job_id": self.current_job_id,
            "subagents": list(self.subagents),
            "metadata": self.metadata,
        }


class AgentRegistry:
    """Registry maintaining active agent sessions."""
    def __init__(self):
        self._agents: Dict[str, Agent] = {}
        self.root_agent = Agent(name="TITAN-Root")
        self.register(self.root_agent)

    def register(self, agent: Agent) -> None:
        self._agents[agent.id] = agent

    def get(self, agent_id: str) -> Optional[Agent]:
        return self._agents.get(agent_id)

    def list_all(self) -> List[Agent]:
        return list(self._agents.values())


# Global singleton registry
agent_registry = AgentRegistry()
