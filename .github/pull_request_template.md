## Summary

<!-- What changed, and why? -->

## Validation

- [ ] `ruff check .`
- [ ] `python -m compileall server`
- [ ] `node --check web/app.js`
- [ ] `pytest --cov=server --cov-report=term-missing`
- [ ] Manual OCR job, if Docker/inference behavior changed

## Review checklist

- [ ] The change is focused and linked to an issue or discussion when appropriate.
- [ ] Tests and documentation cover new behavior.
- [ ] No private documents, OCR output, logs, credentials, or model files are included.
- [ ] UI changes include before/after screenshots.
- [ ] Security, storage, compatibility, and rollback effects are described.
