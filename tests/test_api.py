from pathlib import Path

import pytest
from fastapi.testclient import TestClient

from server import jobs, queue
from server.app import app


@pytest.fixture
def client(tmp_path: Path, monkeypatch: pytest.MonkeyPatch) -> TestClient:
    monkeypatch.setattr(jobs, "JOBS_DIR", tmp_path / "jobs")
    monkeypatch.setattr(queue, "enqueue", lambda _job_id: None)
    return TestClient(app)


def test_health(client: TestClient) -> None:
    response = client.get("/api/health")
    assert response.status_code == 200
    assert response.json() == {"ok": True}


def test_create_job_sanitizes_filename(client: TestClient) -> None:
    response = client.post(
        "/api/jobs",
        files={"files": ("../example.pdf", b"pdf", "application/pdf")},
        data={"device": "cpu"},
    )
    assert response.status_code == 200
    job = jobs.load_job(response.json()["id"])
    assert job["files"][0]["saved_name"] == "example.pdf"


def test_create_job_rejects_unknown_file_type(client: TestClient) -> None:
    response = client.post(
        "/api/jobs",
        files={"files": ("payload.exe", b"bad", "application/octet-stream")},
        data={"device": "cpu"},
    )
    assert response.status_code == 400


def test_create_job_rejects_unknown_device(client: TestClient) -> None:
    response = client.post(
        "/api/jobs",
        files={"files": ("page.png", b"png", "image/png")},
        data={"device": "tpu"},
    )
    assert response.status_code == 422


def test_invalid_job_id_is_not_treated_as_a_path(client: TestClient) -> None:
    response = client.get("/api/jobs/not-a-job")
    assert response.status_code == 404
