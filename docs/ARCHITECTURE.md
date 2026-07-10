# Architecture

PaddleOCR-VL Local Web UI intentionally separates orchestration from inference. The host-side application remains small, while the compute-heavy OCR runtime stays in the upstream Docker image.

## Components

| Component | Responsibility |
| --- | --- |
| `web/` | Static single-page interface for uploads, job history, previews, downloads, and logs |
| `server/app.py` | FastAPI routes, upload handling, static content, Docker status, and downloads |
| `server/queue.py` | One in-process FIFO worker thread |
| `server/jobs.py` | Job metadata, paths, state changes, and logs |
| `server/ocr.py` | Docker command construction, inference execution, and output post-processing |
| `server/config.py` | Local data paths, cache paths, image name, accepted extensions, and defaults |

## Job lifecycle

1. The browser sends multipart uploads and a device choice to `POST /api/jobs`.
2. The server creates a random 32-character job ID and writes inputs under `data/jobs/<id>/input/`.
3. The ID is added to the in-memory queue.
4. The worker starts one temporary PaddleOCR-VL container for every file in the job.
5. Container output is mounted at `data/jobs/<id>/output/` and model caches are mounted from `~/.paddleocr-vl-cache/`.
6. JSON results are post-processed into convenient text and Markdown files.
7. The browser polls job metadata and logs, then previews or downloads output.

## Trust boundaries

- The HTTP interface has no authentication and must remain bound to localhost.
- Uploaded documents and OCR output are untrusted and potentially sensitive.
- The configured container image executes with access to the current job directories and model caches.
- Docker access is privileged in practice; anyone able to use this web interface can ask the host to pull the configured image and start OCR containers.

## Persistence and concurrency

Job metadata is stored as JSON, so history survives application restarts. The queue itself is memory-only; a job left in `queued` or `running` state during a crash is not automatically resumed. A single worker processes jobs sequentially to avoid accidental GPU overcommit.

This design is appropriate for personal workstation use. Multi-user deployments would need authentication, request limits, durable queueing, explicit tenant isolation, and operational monitoring.
