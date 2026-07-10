# Contributing

Thanks for helping improve PaddleOCR-VL Local Web UI. Bug fixes, documentation, tests, accessibility improvements, and focused feature proposals are welcome.

## Before you start

- Search open issues and discussions to avoid duplicate work.
- Use an issue or discussion for changes that affect architecture, security, stored data, or the user experience.
- Never add documents, OCR output, logs, credentials, `.env` files, or model files to Git.

## Local setup

```bash
git clone https://github.com/egore4606/paddle-ocr-ui.git
cd paddle-ocr-ui
python -m venv .venv
source .venv/bin/activate  # Windows: .\.venv\Scripts\Activate.ps1
python -m pip install --upgrade pip
pip install -r requirements-dev.txt
```

## Quality checks

Run the same checks used by CI:

```bash
ruff check .
pip-audit -r server/requirements.txt
python -m compileall server
node --check web/app.js
pytest --cov=server --cov-report=term-missing
```

The unit tests do not require Docker. For changes to OCR execution, also perform one manual CPU or GPU job with a non-sensitive test document.

## Pull requests

Keep each pull request focused and explain what changed, why it changed, and how it was tested. Include screenshots for visible UI changes. Link related issues and call out compatibility, security, storage, or migration effects.

By contributing, you agree that your contribution is licensed under the repository's MIT License and that you will follow the [Code of Conduct](CODE_OF_CONDUCT.md).
