# Security Policy

## Supported versions

Security fixes are applied to the latest release and the default branch.

| Version | Supported |
| --- | --- |
| Latest release | Yes |
| `main` | Yes |
| Older releases | No |

## Reporting a vulnerability

Please **do not open a public issue** and do not publish proof-of-concept details before a fix is available.

Use GitHub's [private vulnerability reporting form](https://github.com/egore4606/paddle-ocr-ui/security/advisories/new). Include:

- the affected version or commit;
- impact and realistic attack scenario;
- reproduction steps or a minimal proof of concept;
- suggested mitigation, if known.

Reports will be acknowledged as capacity permits. This is a community-maintained personal project, so no response-time or remediation SLA is guaranteed.

## Deployment assumptions

The application is localhost-first and has no authentication or authorization. Binding it to a public or shared network interface creates risks that are outside the supported deployment model. Uploaded files, logs, and OCR results may contain confidential data and must be protected accordingly.

## Scope

Vulnerabilities in this repository's Python or browser code are in scope. Issues that exist only in PaddleOCR, PaddlePaddle, Docker, NVIDIA software, or the upstream container image should also be reported to the relevant upstream project.
