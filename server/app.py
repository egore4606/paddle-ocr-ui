import logging
import shutil
import subprocess
import zipfile
from contextlib import asynccontextmanager
from pathlib import Path
from typing import Literal

from fastapi import FastAPI, File, Form, HTTPException, UploadFile
from fastapi.responses import FileResponse, HTMLResponse, JSONResponse, PlainTextResponse
from fastapi.staticfiles import StaticFiles

from . import jobs, queue
from .config import ALLOWED_EXTS, DEFAULT_DEVICE, DEFAULT_PIPELINE_VERSION, IMAGE, WEB_DIR, ensure_dirs
from .utils import is_safe_subpath, list_files, safe_filename

logger = logging.getLogger(__name__)


@asynccontextmanager
async def lifespan(_app: FastAPI):
    ensure_dirs()
    queue.start_worker()
    yield

app = FastAPI(
    title="PaddleOCR-VL Local Web UI",
    description="A localhost-first job interface for PaddleOCR-VL.",
    version="1.1.0",
    lifespan=lifespan,
)

app.mount("/static", StaticFiles(directory=WEB_DIR), name="static")


@app.get("/")
def index() -> HTMLResponse:
    html = (WEB_DIR / "index.html").read_text(encoding="utf-8")
    return HTMLResponse(content=html)


@app.get("/api/health")
def health() -> dict:
    return {"ok": True}


@app.get("/api/docker/status")
def docker_status() -> dict:
    status = {"docker_ok": False, "image_present": False, "error": None}
    try:
        info = subprocess.run(  # noqa: S603
            ["docker", "info"],
            capture_output=True,
            text=True,
            encoding="utf-8",
        )
        if info.returncode != 0:
            status["error"] = info.stderr.strip() or info.stdout.strip()
            return status
        status["docker_ok"] = True
    except Exception:  # noqa: BLE001
        logger.exception("Unable to inspect Docker status")
        status["error"] = "Docker is not available"
        return status

    inspect = subprocess.run(  # noqa: S603
        ["docker", "image", "inspect", IMAGE],
        capture_output=True,
        text=True,
        encoding="utf-8",
    )
    status["image_present"] = inspect.returncode == 0
    return status


@app.post("/api/docker/pull")
def docker_pull() -> JSONResponse:
    try:
        pull = subprocess.run(  # noqa: S603
            ["docker", "pull", IMAGE],
            capture_output=True,
            text=True,
            encoding="utf-8",
        )
        if pull.returncode == 0:
            return JSONResponse({"ok": True, "output": pull.stdout or "Image downloaded"})
        logger.error("Docker image pull failed: %s", (pull.stderr or pull.stdout or "unknown error").strip())
        return JSONResponse({"ok": False, "output": "Unable to pull the OCR image. Check the server logs."})
    except Exception:  # noqa: BLE001
        logger.exception("Unable to pull the Docker image")
        return JSONResponse({"ok": False, "output": "Docker is not available"})


@app.post("/api/jobs")
def create_job(
    files: list[UploadFile] = File(...),
    device: Literal["cpu", "gpu"] = Form(DEFAULT_DEVICE),
) -> dict:
    if not files:
        raise HTTPException(status_code=400, detail="No files uploaded")

    safe_files = []
    used = set()
    for f in files:
        base = safe_filename(f.filename or "file")
        name = base
        counter = 1
        while name in used:
            stem = Path(base).stem
            suffix = Path(base).suffix
            name = f"{stem}_{counter}{suffix}"
            counter += 1
        used.add(name)
        ext = Path(name).suffix.lower()
        if ext not in ALLOWED_EXTS:
            raise HTTPException(status_code=400, detail=f"Unsupported file type: {name}")
        safe_files.append(name)

    pipeline_version = DEFAULT_PIPELINE_VERSION
    job = jobs.create_job(options={"pipeline_version": pipeline_version, "device": device}, filenames=safe_files)
    job_id = job["id"]

    base = jobs.job_dir(job_id)
    input_dir = base / "input"
    for upload, safe_name in zip(files, safe_files, strict=False):
        dst = input_dir / safe_name
        with dst.open("wb") as f:
            shutil.copyfileobj(upload.file, f)
    jobs.append_log(job_id, f"Uploaded {len(safe_files)} file(s)")
    queue.enqueue(job_id)
    return {"id": job_id}


@app.get("/api/jobs")
def list_jobs() -> list[dict]:
    return jobs.list_jobs()


@app.get("/api/jobs/{job_id}")
def get_job(job_id: str) -> dict:
    try:
        return jobs.load_job(job_id)
    except (FileNotFoundError, ValueError):
        raise HTTPException(status_code=404, detail="Job not found") from None


@app.get("/api/jobs/{job_id}/logs")
def get_logs(job_id: str, offset: int = 0) -> dict:
    try:
        path = jobs.job_log_path(job_id)
    except ValueError:
        raise HTTPException(status_code=404, detail="Job not found") from None
    if not path.exists():
        raise HTTPException(status_code=404, detail="Log not found")
    with path.open("r", encoding="utf-8", errors="replace") as f:
        f.seek(max(offset, 0))
        data = f.read()
        next_offset = f.tell()
    return {"text": data, "next_offset": next_offset}


@app.get("/api/jobs/{job_id}/files")
def list_job_files(job_id: str) -> dict:
    try:
        base = jobs.job_dir(job_id)
    except ValueError:
        raise HTTPException(status_code=404, detail="Job not found") from None
    output_dir = base / "output"
    if not output_dir.exists():
        raise HTTPException(status_code=404, detail="Output not found")
    return {"files": list_files(output_dir)}


@app.get("/api/jobs/{job_id}/file/{path:path}")
def get_job_file(job_id: str, path: str):
    try:
        base = jobs.job_dir(job_id)
    except ValueError:
        raise HTTPException(status_code=404, detail="Job not found") from None
    output_dir = base / "output"
    target = (output_dir / path).resolve()
    if not is_safe_subpath(output_dir, target) or not target.exists():
        raise HTTPException(status_code=404, detail="File not found")
    if target.suffix.lower() in {".txt", ".md", ".json"}:
        return PlainTextResponse(target.read_text(encoding="utf-8", errors="replace"))
    return FileResponse(target)


@app.get("/api/jobs/{job_id}/download")
def download_job(job_id: str):
    try:
        base = jobs.job_dir(job_id)
    except ValueError:
        raise HTTPException(status_code=404, detail="Job not found") from None
    output_dir = base / "output"
    if not output_dir.exists():
        raise HTTPException(status_code=404, detail="Output not found")

    zip_path = base / "output.zip"
    with zipfile.ZipFile(zip_path, "w", zipfile.ZIP_DEFLATED) as zf:
        for p in output_dir.rglob("*"):
            if p.is_file() and is_safe_subpath(output_dir, p.resolve()):
                zf.write(p, p.relative_to(output_dir))
    return FileResponse(zip_path, filename=f"{job_id}.zip")
