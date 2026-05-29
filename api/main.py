import os
import threading
from pathlib import Path
from typing import Optional

from fastapi import FastAPI, File, HTTPException, UploadFile
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import FileResponse
from fastapi.staticfiles import StaticFiles
from pydantic import BaseModel

from api.jobs import JobState, job_store
from pipeline.analysis import run_analysis

PROJECT_ROOT = Path(__file__).resolve().parent.parent
JOBS_DIR = PROJECT_ROOT / "web_jobs"
MODEL_PATH = PROJECT_ROOT / "models" / "best.pt"
FRONTEND_DIST = PROJECT_ROOT / "frontend" / "dist"

MAX_UPLOAD_BYTES = 500 * 1024 * 1024  # 500 MB
ALLOWED_EXTENSIONS = {".mp4", ".avi", ".mov", ".mkv", ".webm"}

app = FastAPI(
    title="Football CV Analysis API",
    description="Upload a match video and get an annotated analysis.",
    version="1.0.0",
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "http://localhost:5173",
        "http://127.0.0.1:5173",
        "http://localhost:8000",
        "http://127.0.0.1:8000",
    ],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


class JobStatusResponse(BaseModel):
    job_id: str
    state: JobState
    progress: int
    message: str
    error: Optional[str] = None
    input_filename: str
    has_result: bool


def _job_to_response(job) -> JobStatusResponse:
    return JobStatusResponse(
        job_id=job.id,
        state=job.state,
        progress=job.progress,
        message=job.message,
        error=job.error,
        input_filename=job.input_filename,
        has_result=job.state == JobState.COMPLETED and os.path.exists(job.output_path),
    )


def _run_job(job_id: str) -> None:
    job = job_store.get(job_id)
    if not job:
        return

    job_store.set_running(job_id)

    def on_progress(percent: int, message: str) -> None:
        job_store.update_progress(job_id, percent, message)

    try:
        run_analysis(
            job.input_path,
            job.output_path,
            model_path=str(MODEL_PATH),
            work_dir=job.work_dir,
            use_stubs=True,
            progress_cb=on_progress,
        )
        job_store.set_completed(job_id)
    except Exception as exc:
        job_store.set_failed(job_id, str(exc))


@app.get("/api/health")
def health():
    return {
        "status": "ok",
        "model_exists": MODEL_PATH.exists(),
    }


@app.post("/api/jobs", response_model=JobStatusResponse)
async def create_job(file: UploadFile = File(...)):
    if not MODEL_PATH.exists():
        raise HTTPException(
            status_code=503,
            detail=f"Modèle YOLO introuvable : {MODEL_PATH}. Placez best.pt dans models/.",
        )

    suffix = Path(file.filename or "").suffix.lower()
    if suffix not in ALLOWED_EXTENSIONS:
        raise HTTPException(
            status_code=400,
            detail=f"Format non supporté. Utilisez : {', '.join(sorted(ALLOWED_EXTENSIONS))}",
        )

    content = await file.read()
    if len(content) > MAX_UPLOAD_BYTES:
        raise HTTPException(status_code=413, detail="Fichier trop volumineux (max 500 Mo).")
    if not content:
        raise HTTPException(status_code=400, detail="Fichier vide.")

    JOBS_DIR.mkdir(parents=True, exist_ok=True)

    safe_name = Path(file.filename or "video.mp4").name
    job = job_store.create(
        input_filename=safe_name,
        work_dir="",
        input_path="",
        output_path="",
    )

    job_dir = JOBS_DIR / job.id
    stubs_dir = job_dir / "stubs"
    job_dir.mkdir(parents=True, exist_ok=True)
    stubs_dir.mkdir(parents=True, exist_ok=True)

    input_path = job_dir / safe_name
    output_path = job_dir / "output_annotated.mp4"
    input_path.write_bytes(content)

    job_store.set_paths(
        job.id,
        work_dir=str(stubs_dir),
        input_path=str(input_path),
        output_path=str(output_path),
    )

    thread = threading.Thread(target=_run_job, args=(job.id,), daemon=True)
    thread.start()

    job = job_store.get(job.id)
    return _job_to_response(job)


@app.get("/api/jobs/{job_id}", response_model=JobStatusResponse)
def get_job_status(job_id: str):
    job = job_store.get(job_id)
    if not job:
        raise HTTPException(status_code=404, detail="Job introuvable.")
    return _job_to_response(job)


@app.get("/api/jobs/{job_id}/result")
def download_result(job_id: str):
    job = job_store.get(job_id)
    if not job:
        raise HTTPException(status_code=404, detail="Job introuvable.")
    if job.state != JobState.COMPLETED:
        raise HTTPException(status_code=409, detail="Analyse pas encore terminée.")
    if not os.path.exists(job.output_path):
        raise HTTPException(status_code=404, detail="Fichier résultat introuvable.")

    return FileResponse(
        job.output_path,
        media_type="video/mp4",
        filename=f"analyse_{job_id[:8]}.mp4",
    )


if FRONTEND_DIST.exists():
    app.mount("/", StaticFiles(directory=str(FRONTEND_DIST), html=True), name="frontend")
