import json
import re
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Iterable


INVALID_CHARS = re.compile(r'[<>:"/\\\\|?*]')


def now_iso() -> str:
    return datetime.now(timezone.utc).astimezone().isoformat(timespec="seconds")


def ensure_dir(path: Path) -> None:
    path.mkdir(parents=True, exist_ok=True)


def safe_filename(name: str) -> str:
    base = Path(name).name
    base = INVALID_CHARS.sub("_", base)
    base = base.strip().strip(".")
    return base or "file"


def output_folder_name(filename: str) -> str:
    return safe_filename(filename).replace(".", "_")


def write_json(path: Path, data: Any) -> None:
    ensure_dir(path.parent)
    path.write_text(json.dumps(data, ensure_ascii=False, indent=2), encoding="utf-8")


def read_json(path: Path) -> Any:
    return json.loads(path.read_text(encoding="utf-8"))


def list_files(root: Path) -> list[str]:
    files: list[str] = []
    if not root.exists():
        return files
    for p in root.rglob("*"):
        if p.is_file():
            files.append(p.relative_to(root).as_posix())
    return files


def is_safe_subpath(base: Path, target: Path) -> bool:
    try:
        target.resolve().relative_to(base.resolve())
        return True
    except Exception:
        return False


def join_text(lines: Iterable[str]) -> str:
    return "\r\n\r\n".join([line for line in lines if line.strip()])
