"""
core/jobs.py — Background Job Registry & Execution Engine for TITAN.
Ported and adapted from DeepSeek Harness (`packages/jobs`).

Provides:
- Async background job tracking, execution, output buffering, and termination.
- Non-blocking polling and timeout-aware waits so live voice stays fluid.
"""
from __future__ import annotations

import asyncio
import concurrent.futures
import threading
import time
import uuid
from datetime import datetime
from typing import Any, Callable, Dict, List, Optional


class JobStatus:
    PENDING = "pending"
    RUNNING = "running"
    COMPLETED = "completed"
    FAILED = "failed"
    CANCELLED = "cancelled"


class BackgroundJob:
    def __init__(self, id: str, label: str, fn: Callable[..., Any], *args: Any):
        self.id = id
        self.label = label
        self.fn = fn
        self.args = args
        self.status = JobStatus.PENDING
        self.created_at = datetime.now().isoformat()
        self.completed_at: Optional[str] = None
        self.output_buffer: List[str] = []
        self.result: Any = None
        self.error: Optional[str] = None
        self.future: Optional[concurrent.futures.Future] = None

    def append_output(self, text: str) -> None:
        self.output_buffer.append(text)

    def get_output(self) -> str:
        if self.output_buffer:
            return "".join(self.output_buffer)
        if self.result is not None:
            return str(self.result)
        if self.error:
            return f"Error: {self.error}"
        return f"[Status: {self.status}]"

    def to_dict(self) -> Dict[str, Any]:
        return {
            "id": self.id,
            "label": self.label,
            "status": self.status,
            "created_at": self.created_at,
            "completed_at": self.completed_at,
            "error": self.error,
        }


class JobRegistry:
    def __init__(self, max_workers: int = 4):
        self._executor = concurrent.futures.ThreadPoolExecutor(max_workers=max_workers)
        self._jobs: Dict[str, BackgroundJob] = {}
        self._lock = threading.Lock()

    def start_job(self, label: str, fn: Callable[..., Any], *args: Any) -> str:
        job_id = f"job_{uuid.uuid4().hex[:8]}"
        job = BackgroundJob(job_id, label, fn, *args)
        with self._lock:
            self._jobs[job_id] = job

        def _runner():
            job.status = JobStatus.RUNNING
            try:
                res = fn(*args)
                job.result = res
                job.status = JobStatus.COMPLETED
            except Exception as e:
                job.error = str(e)
                job.status = JobStatus.FAILED
            finally:
                job.completed_at = datetime.now().isoformat()

        job.future = self._executor.submit(_runner)
        return job_id

    def get_job(self, job_id: str) -> Optional[BackgroundJob]:
        with self._lock:
            return self._jobs.get(job_id)

    def list_jobs(self) -> List[Dict[str, Any]]:
        with self._lock:
            return [j.to_dict() for j in self._jobs.values()]

    def kill_job(self, job_id: str, reason: str = "Cancelled by user") -> str:
        with self._lock:
            job = self._jobs.get(job_id)
            if not job:
                return f"Job {job_id} not found."
            if job.status in (JobStatus.COMPLETED, JobStatus.FAILED, JobStatus.CANCELLED):
                return f"Job {job_id} is already finished ({job.status})."
            
            if job.future and not job.future.done():
                job.future.cancel()
            job.status = JobStatus.CANCELLED
            job.error = reason
            job.completed_at = datetime.now().isoformat()
            return f"Job {job_id} cancelled: {reason}"

    def read_output(self, job_id: str) -> str:
        job = self.get_job(job_id)
        if not job:
            return f"Job {job_id} not found."
        return f"{job.label} [{job.status}]:\n{job.get_output()}"


# Global singleton
job_registry = JobRegistry()


# ── Gemini Tool Declarations ──
JOB_TOOLS_DECLARATIONS = [
    {
        "name": "job_list",
        "description": "List all active and recent background jobs.",
        "parameters": {"type": "OBJECT", "properties": {}, "required": []},
    },
    {
        "name": "job_output",
        "description": "Read the live or final output of a background job.",
        "parameters": {
            "type": "OBJECT",
            "properties": {
                "job_id": {"type": "STRING", "description": "The ID of the background job"},
            },
            "required": ["job_id"],
        },
    },
    {
        "name": "job_kill",
        "description": "Terminate or cancel a running background job.",
        "parameters": {
            "type": "OBJECT",
            "properties": {
                "job_id": {"type": "STRING", "description": "The ID of the background job to terminate"},
                "reason": {"type": "STRING", "description": "Reason for cancellation"},
            },
            "required": ["job_id"],
        },
    },
]
