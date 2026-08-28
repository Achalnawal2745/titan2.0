"""
core/session_log.py — Immutable Session Event Log.
Ported from DeepSeek Harness (`packages/core/session`).

Appends all events (user input, agent reasoning, tool call, tool result, errors)
as structured JSONL events to disk. Survives crashes and reconnects.
"""
from __future__ import annotations

import json
import uuid
from datetime import datetime
from pathlib import Path
from typing import Any, Dict, List, Optional


class SessionEventLog:
    def __init__(self, session_id: Optional[str] = None):
        self.session_id = session_id or f"sess_{uuid.uuid4().hex[:8]}"
        base = Path(__file__).resolve().parent.parent
        self.log_dir = base / "memory" / "session_events"
        self.log_dir.mkdir(parents=True, exist_ok=True)
        self.log_file = self.log_dir / f"{self.session_id}.jsonl"

    def record_event(self, event_type: str, payload: Dict[str, Any]) -> Dict[str, Any]:
        event = {
            "session_id": self.session_id,
            "timestamp": datetime.now().isoformat(),
            "event_type": event_type,
            "payload": payload,
        }
        try:
            with open(self.log_file, "a", encoding="utf-8") as f:
                f.write(json.dumps(event, default=str) + "\n")
        except Exception as e:
            print(f"[SessionLog] Error recording event: {e}")
        return event

    def list_events(self) -> List[Dict[str, Any]]:
        events = []
        if not self.log_file.exists():
            return events
        try:
            with open(self.log_file, "r", encoding="utf-8") as f:
                for line in f:
                    line = line.strip()
                    if line:
                        events.append(json.loads(line))
        except Exception as e:
            print(f"[SessionLog] Error reading events: {e}")
        return events


# Global active session logger
session_logger = SessionEventLog()
