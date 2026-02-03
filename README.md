# PaddleOCR‑VL Local Web UI (Docker)

> **Disclaimer**  
> I’m not a programmer, and this entire project was built with the help of AI.  
> I’d be very happy if others improve it and make it more useful for people.

This repository provides a **local** web interface for PaddleOCR‑VL.  
It runs on **localhost**, uses **Docker** for inference, and stores results under `data/`.

## Requirements

- Docker Desktop installed and running
- Image:
  ```
  ccr-2vdh3abv-pub.cnc.bj.baidubce.com/paddlepaddle/paddleocr-vl:latest-nvidia-gpu
  ```
- Python 3.10+

## Setup

```powershell
cd C:\Users\egor0\Downloads\WebforAI\publish
python -m venv .venv
.\.venv\Scripts\Activate.ps1
pip install -r server\requirements.txt
```

## Run

```powershell
uvicorn server.app:app --host 127.0.0.1 --port 8000
```

Open in browser: `http://127.0.0.1:8000`

## Outputs

All results are stored in:

```
data\jobs\<job_id>\output
```

You can also download ZIP files from the UI.

## Notes

- The UI is in English.
- The server always uses **PaddleOCR‑VL v1** (no model selection).

## Contributing

If you want to improve the UI/UX, performance, or add features (DOCX/PDF export, better previews, queue management), feel free to open issues or PRs.
