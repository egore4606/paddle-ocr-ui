from pathlib import Path

import pytest

from server import jobs
from server.utils import is_safe_subpath, safe_filename


@pytest.mark.parametrize(
    ("value", "expected"),
    [
        ("scan.pdf", "scan.pdf"),
        ("../../report.pdf", "report.pdf"),
        ("bad:name?.png", "bad_name_.png"),
        ("...", "file"),
    ],
)
def test_safe_filename(value: str, expected: str) -> None:
    assert safe_filename(value) == expected


def test_job_ids_are_strictly_validated(tmp_path: Path, monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.setattr(jobs, "JOBS_DIR", tmp_path)
    assert jobs.job_dir("a" * 32) == tmp_path / ("a" * 32)

    with pytest.raises(ValueError, match="Invalid job ID"):
        jobs.job_dir("../outside")


def test_safe_subpath_rejects_parent_escape(tmp_path: Path) -> None:
    base = tmp_path / "jobs"
    assert is_safe_subpath(base, base / "one" / "result.txt")
    assert not is_safe_subpath(base, tmp_path / "secret.txt")
