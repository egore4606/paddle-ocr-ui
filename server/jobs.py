import uuid
from pathlib import Path
from typing import Any

from .config import JOBS_DIR
from .utils import ensure_dir, now_iso, output_folder_name, read_json, safe_filename, write_json


def job_dir(job_id: str) -> Path:
    return JOBS_DIR / job_id


def job_log_path(job_id: str) -> Path:
    return job_dir(job_id) / "job.log"


def job_json_path(job_id: str) -> Path:
    return job_dir(job_id) / "job.json"


def create_job(options: dict[str, Any], filenames: list[str]) -> dict[str, Any]:
    job_id = uuid.uuid4().hex
    base = job_dir(job_id)
    input_dir = base / "input"
    output_dir = base / "output"
    ensure_dir(input_dir)
    ensure_dir(output_dir)

    files = []
    for name in filenames:
        safe = safe_filename(name)
        files.append(
            {
                "name": name,
                "saved_name": safe,
                "input_rel": f"input/{safe}",
                "output_rel": f"output/{output_folder_name(safe)}",
                "outputs": [],
            }
        )

    job = {
        "id": job_id,
        "status": "queued",
        "created_at": now_iso(),
        "started_at": None,
        "finished_at": None,
        "options": options,
        "files": files,
        "output_files": [],
        "error": None,
    }
    write_json(job_json_path(job_id), job)
    job_log_path(job_id).write_text("", encoding="utf-8")
    return job


def load_job(job_id: str) -> dict[str, Any]:
    return read_json(job_json_path(job_id))


def save_job(job_id: str, job: dict[str, Any]) -> None:
    write_json(job_json_path(job_id), job)


def append_log(job_id: str, line: str) -> None:
    path = job_log_path(job_id)
    with path.open("a", encoding="utf-8") as f:
        f.write(f"[{now_iso()}] {line}\n")


def set_status(job_id: str, status: str, error: str | None = None) -> None:
    job = load_job(job_id)
    job["status"] = status
    if status == "running":
        job["started_at"] = now_iso()
    if status in ("succeeded", "failed"):
        job["finished_at"] = now_iso()
    job["error"] = error
    save_job(job_id, job)


def update_outputs(job_id: str, files: list[dict[str, Any]], output_files: list[str]) -> None:
    job = load_job(job_id)
    job["files"] = files
    job["output_files"] = output_files
    save_job(job_id, job)


def list_jobs() -> list[dict[str, Any]]:
    items: list[dict[str, Any]] = []
    if not JOBS_DIR.exists():
        return items
    for p in JOBS_DIR.iterdir():
        if not p.is_dir():
            continue
        job_json = p / "job.json"
        if job_json.exists():
            items.append(read_json(job_json))
    items.sort(key=lambda j: j.get("created_at", ""), reverse=True)
    return items
