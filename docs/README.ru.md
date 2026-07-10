<div align="center">
  <img src="../assets/logo.svg" alt="PaddleOCR-VL Local Web UI" width="720">

  # PaddleOCR-VL Local Web UI

  **Локальное распознавание PDF и изображений через удобный веб-интерфейс.**

  [English](../README.md) · Русский · [Deutsch](README.de.md)
</div>

---

PaddleOCR-VL Local Web UI — небольшое приложение на FastAPI, которое ставит задания OCR в очередь и запускает PaddleOCR-VL внутри Docker. Документы не отправляются в облако: загруженные файлы, журналы и результаты остаются в локальной папке `data/`.

> [!IMPORTANT]
> В приложении нет авторизации. Оно предназначено для доверенного компьютера и адреса `127.0.0.1`. Не публикуйте его напрямую в интернете.

## Возможности

- загрузка PDF и изображений перетаскиванием;
- обработка на CPU или NVIDIA GPU;
- фоновая очередь и журнал выполнения в реальном времени;
- просмотр Markdown, текста, JSON и изображений;
- скачивание всех результатов задания одним ZIP-архивом;
- локальный кеш моделей между запусками.

## Требования

- Python 3.10 или новее;
- Docker Desktop или Docker Engine;
- примерно 10 ГБ свободного места для образа и моделей;
- для GPU: NVIDIA GPU, актуальный драйвер и поддержка NVIDIA Container Toolkit.

## Быстрый запуск в Windows PowerShell

```powershell
git clone https://github.com/egore4606/paddle-ocr-ui.git
cd paddle-ocr-ui
python -m venv .venv
.\.venv\Scripts\Activate.ps1
python -m pip install --upgrade pip
pip install -r server\requirements.txt
docker pull ccr-2vdh3abv-pub.cnc.bj.baidubce.com/paddlepaddle/paddleocr-vl:latest-nvidia-gpu
uvicorn server.app:app --host 127.0.0.1 --port 8000
```

Откройте [http://127.0.0.1:8000](http://127.0.0.1:8000), выберите CPU или GPU, добавьте файлы и запустите задание. Первый запуск может быть долгим: Docker и PaddleOCR загружают несколько гигабайт данных.

Поддерживаются `.pdf`, `.png`, `.jpg`, `.jpeg`, `.bmp`, `.tif`, `.tiff` и `.webp`. Результаты сохраняются в `data/jobs/<идентификатор>/output/`.

## Документация

- [Архитектура](ARCHITECTURE.md)
- [Решение проблем](TROUBLESHOOTING.md)
- [Как внести вклад](../CONTRIBUTING.md)
- [Политика безопасности](../SECURITY.md)

Вопросы и идеи можно публиковать в [Discussions](https://github.com/egore4606/paddle-ocr-ui/discussions). Уязвимости следует отправлять только через [приватный отчёт](https://github.com/egore4606/paddle-ocr-ui/security/advisories/new).

Проект распространяется по [лицензии MIT](../LICENSE). PaddleOCR и используемый Docker-образ являются отдельными проектами со своими лицензиями.
