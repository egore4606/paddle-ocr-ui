# Troubleshooting

## The page says Docker is not running

Run `docker info` in the same user session that starts Uvicorn. Start Docker Desktop or the Docker daemon if that command fails.

## The image is missing

Use **Pull image** in the header or run:

```bash
docker pull ccr-2vdh3abv-pub.cnc.bj.baidubce.com/paddlepaddle/paddleocr-vl:latest-nvidia-gpu
```

The registry and model downloads may be slow or unavailable from some networks. Retry after verifying DNS, proxy, VPN, and firewall settings.

## GPU mode fails

Verify that the host can expose the GPU to containers:

```bash
nvidia-smi
docker run --rm --gpus all nvidia/cuda:12.0.0-base-ubuntu22.04 nvidia-smi
```

If GPU support is not configured, select **CPU** in the interface. CPU processing is substantially slower but does not require NVIDIA container support.

## A job remains queued after a restart

The current queue is memory-only. Restarted jobs are not automatically resumed. Upload the document again. Old job files can be removed by stopping the server and deleting the corresponding directory under `data/jobs/`.

## The first job is very slow

PaddleOCR downloads models into `~/.paddleocr-vl-cache/` on first use. Later runs reuse that cache. Do not delete it unless you intentionally want a clean model download.

## Port 8000 is already in use

Choose a different local port:

```bash
uvicorn server.app:app --host 127.0.0.1 --port 8080
```

## Reset local application data

Stop Uvicorn, back up anything important, and remove `data/`. This permanently deletes job history, uploads, logs, and OCR output. The model cache is separate and remains intact.

## Still stuck?

Search existing [issues](https://github.com/egore4606/paddle-ocr-ui/issues) and [discussions](https://github.com/egore4606/paddle-ocr-ui/discussions). When reporting a problem, include the operating system, Python version, Docker version, CPU/GPU choice, and sanitized logs. Never attach private source documents or OCR output.
