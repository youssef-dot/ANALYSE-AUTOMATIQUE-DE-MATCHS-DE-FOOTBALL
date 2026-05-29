import threading
import uuid
from dataclasses import dataclass, field
from datetime import datetime, timezone
from enum import Enum
from typing import Dict, Optional


class JobState(str, Enum):
    PENDING = "pending"
    RUNNING = "running"
    COMPLETED = "completed"
    FAILED = "failed"


@dataclass
class Job:
    id: str
    state: JobState = JobState.PENDING
    progress: int = 0
    message: str = "En attente…"
    error: Optional[str] = None
    input_filename: str = ""
    created_at: str = field(default_factory=lambda: datetime.now(timezone.utc).isoformat())
    work_dir: str = ""
    input_path: str = ""
    output_path: str = ""


class JobStore:
    def __init__(self) -> None:
        self._jobs: Dict[str, Job] = {}
        self._lock = threading.Lock()

    def create(
        self,
        *,
        input_filename: str,
        work_dir: str,
        input_path: str,
        output_path: str,
    ) -> Job:
        job = Job(
            id=str(uuid.uuid4()),
            input_filename=input_filename,
            work_dir=work_dir,
            input_path=input_path,
            output_path=output_path,
        )
        with self._lock:
            self._jobs[job.id] = job
        return job

    def get(self, job_id: str) -> Optional[Job]:
        with self._lock:
            return self._jobs.get(job_id)

    def update_progress(self, job_id: str, progress: int, message: str) -> None:
        with self._lock:
            job = self._jobs.get(job_id)
            if job:
                job.progress = progress
                job.message = message

    def set_running(self, job_id: str) -> None:
        with self._lock:
            job = self._jobs.get(job_id)
            if job:
                job.state = JobState.RUNNING
                job.message = "Démarrage de l'analyse…"

    def set_completed(self, job_id: str) -> None:
        with self._lock:
            job = self._jobs.get(job_id)
            if job:
                job.state = JobState.COMPLETED
                job.progress = 100
                job.message = "Analyse terminée"

    def set_failed(self, job_id: str, error: str) -> None:
        with self._lock:
            job = self._jobs.get(job_id)
            if job:
                job.state = JobState.FAILED
                job.error = error
                job.message = "Échec de l'analyse"

    def set_paths(self, job_id: str, work_dir: str, input_path: str, output_path: str) -> None:
        with self._lock:
            job = self._jobs.get(job_id)
            if job:
                job.work_dir = work_dir
                job.input_path = input_path
                job.output_path = output_path


job_store = JobStore()
