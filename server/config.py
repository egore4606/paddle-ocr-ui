from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parents[1]
SERVER_DIR = Path(__file__).resolve().parent
WEB_DIR = PROJECT_ROOT / "web"
DATA_DIR = PROJECT_ROOT / "data"
JOBS_DIR = DATA_DIR / "jobs"

IMAGE = "ccr-2vdh3abv-pub.cnc.bj.baidubce.com/paddlepaddle/paddleocr-vl:latest-nvidia-gpu"

CACHE_ROOT = Path.home() / ".paddleocr-vl-cache"
PADDLEX_CACHE = CACHE_ROOT / "paddlex"
PADDLEOCR_CACHE = CACHE_ROOT / "paddleocr"

DEFAULT_PIPELINE_VERSION = "v1"
DEFAULT_DEVICE = "gpu"

ALLOWED_EXTS = {".png", ".jpg", ".jpeg", ".bmp", ".tif", ".tiff", ".webp", ".pdf"}


def ensure_dirs() -> None:
    DATA_DIR.mkdir(parents=True, exist_ok=True)
    JOBS_DIR.mkdir(parents=True, exist_ok=True)
    CACHE_ROOT.mkdir(parents=True, exist_ok=True)
    PADDLEX_CACHE.mkdir(parents=True, exist_ok=True)
    PADDLEOCR_CACHE.mkdir(parents=True, exist_ok=True)

