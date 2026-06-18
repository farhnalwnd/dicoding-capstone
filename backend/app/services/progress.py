import uuid
from typing import Any, Dict, Optional


class JobProgressManager:
    def __init__(self):
        # Maps job_id -> { "progress": int, "message": str, "status": str, "result": Any }
        self._jobs: Dict[str, Dict[str, Any]] = {}

    def create_job(self) -> str:
        job_id = str(uuid.uuid4())
        self._jobs[job_id] = {
            "progress": 0,
            "message": "Initializing pipeline",
            "status": "processing",
            "result": None,
        }
        return job_id

    def update_progress(
        self, job_id: str, progress: int, message: str, status: str = "processing"
    ):
        if job_id in self._jobs:
            self._jobs[job_id]["progress"] = progress
            self._jobs[job_id]["message"] = message
            self._jobs[job_id]["status"] = status

    def complete_job(self, job_id: str, result: Any):
        if job_id in self._jobs:
            self._jobs[job_id]["progress"] = 100
            self._jobs[job_id]["message"] = "Completed"
            self._jobs[job_id]["status"] = "completed"
            self._jobs[job_id]["result"] = result

    def fail_job(self, job_id: str, error_message: str):
        if job_id in self._jobs:
            self._jobs[job_id]["progress"] = 0
            self._jobs[job_id]["message"] = error_message
            self._jobs[job_id]["status"] = "error"

    def get_job(self, job_id: str) -> Optional[Dict[str, Any]]:
        return self._jobs.get(job_id)


# Global singleton instance
progress_manager = JobProgressManager()
