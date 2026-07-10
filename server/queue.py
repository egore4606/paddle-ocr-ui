import queue
import threading

from . import jobs, ocr

_job_queue: queue.Queue[str] = queue.Queue()
_worker_thread: threading.Thread | None = None


def start_worker() -> None:
    global _worker_thread
    if _worker_thread and _worker_thread.is_alive():
        return
    _worker_thread = threading.Thread(target=_worker_loop, daemon=True)
    _worker_thread.start()


def enqueue(job_id: str) -> None:
    _job_queue.put(job_id)


def _worker_loop() -> None:
    while True:
        job_id = _job_queue.get()
        try:
            ocr.process_job(job_id)
        except Exception as exc:  # noqa: BLE001
            jobs.append_log(job_id, f"ERROR: {exc}")
            jobs.set_status(job_id, "failed", error=str(exc))
        finally:
            _job_queue.task_done()

