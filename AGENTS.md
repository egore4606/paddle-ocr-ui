# Repository guidance for coding agents

## Scope and trust model

This is a localhost-first FastAPI application that invokes PaddleOCR-VL through Docker. It has no authentication. Preserve the default local-only deployment model unless a change explicitly introduces and tests a complete security boundary.

## Required checks

Before proposing a change, run:

```text
ruff check .
pip-audit -r server/requirements.txt
python -m compileall server
node --check web/app.js
pytest --cov=server --cov-report=term-missing
```

## Safety rules

- Never commit `data/`, OCR input/output, logs, `.env`, credentials, cache contents, or model weights.
- Treat filenames, route parameters, uploaded content, generated container output, and OCR text as untrusted.
- Preserve path containment checks and strict job ID validation.
- Do not interpolate untrusted values into shell commands; Docker calls must remain argument arrays without `shell=True`.
- Keep errors returned to HTTP clients generic and record diagnostic details only in server logs.
- Pin dependencies and GitHub Actions to reviewed versions.
- Do not make the mutable upstream Docker image more privileged or mount broader host paths without explicit justification.

## Change discipline

Prefer small, testable changes. Update README, architecture, troubleshooting, changelog, and tests whenever behavior or setup changes. Do not rewrite Git history, fabricate authorship, or bypass repository protections.
