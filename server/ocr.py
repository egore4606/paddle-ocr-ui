import json
import subprocess
from pathlib import Path
from typing import Any

from . import jobs
from .config import IMAGE, PADDLEOCR_CACHE, PADDLEX_CACHE
from .utils import ensure_dir, join_text, list_files, output_folder_name


def process_job(job_id: str) -> None:
    job = jobs.load_job(job_id)
    jobs.set_status(job_id, "running")
    jobs.append_log(job_id, "Job started")

    base = jobs.job_dir(job_id)
    input_dir = base / "input"
    output_dir = base / "output"

    updated_files = []
    for item in job["files"]:
        original_name = item["name"]
        saved_name = item["saved_name"]
        file_output_dir = output_dir / output_folder_name(saved_name)
        ensure_dir(file_output_dir)

        jobs.append_log(job_id, f"Processing: {original_name}")
        run_doc_parser(
            input_dir=input_dir,
            output_dir=file_output_dir,
            filename=saved_name,
            pipeline_version=job["options"]["pipeline_version"],
            device=job["options"]["device"],
            log=lambda line: jobs.append_log(job_id, line),
        )

        postprocess_outputs(file_output_dir, log=lambda line: jobs.append_log(job_id, line))
        item["output_rel"] = file_output_dir.relative_to(base).as_posix()
        item["outputs"] = list_files(file_output_dir)
        updated_files.append(item)

    all_outputs = list_files(output_dir)
    jobs.update_outputs(job_id, updated_files, all_outputs)
    jobs.set_status(job_id, "succeeded")
    jobs.append_log(job_id, "Job finished")


def run_doc_parser(
    input_dir: Path,
    output_dir: Path,
    filename: str,
    pipeline_version: str,
    device: str,
    log,
) -> None:
    args: list[str] = ["docker", "run", "--rm"]
    if device == "gpu":
        args += ["--gpus", "all"]

    args += [
        "-e",
        "PADDLE_PDX_DISABLE_MODEL_SOURCE_CHECK=True",
        "-v",
        f"{input_dir}:/work/input",
        "-v",
        f"{output_dir}:/work/out",
        "-v",
        f"{PADDLEX_CACHE}:/home/paddleocr/.paddlex",
        "-v",
        f"{PADDLEOCR_CACHE}:/home/paddleocr/.paddleocr",
        IMAGE,
        "paddleocr",
        "doc_parser",
        "-i",
        f"/work/input/{filename}",
        "--save_path",
        "/work/out",
        "--pipeline_version",
        pipeline_version,
    ]

    if device == "gpu":
        args += ["--device", "gpu:0"]
    else:
        args += ["--device", "cpu"]

    log("Running docker: " + " ".join(args))

    process = subprocess.Popen(  # noqa: S603
        args,
        stdout=subprocess.PIPE,
        stderr=subprocess.STDOUT,
        text=True,
        encoding="utf-8",
        errors="replace",
    )

    assert process.stdout is not None
    for line in process.stdout:
        log(line.rstrip())

    code = process.wait()
    if code != 0:
        raise RuntimeError(f"Docker exited with code {code}")


def postprocess_outputs(output_dir: Path, log) -> None:
    json_files = sorted(output_dir.glob("*_res.json"))
    if not json_files:
        return

    for json_path in json_files:
        try:
            data: dict[str, Any] = json.loads(json_path.read_text(encoding="utf-8"))
        except Exception as exc:  # noqa: BLE001
            log(f"Failed to read JSON {json_path.name}: {exc}")
            continue

        blocks = []
        for item in data.get("parsing_res_list", []):
            content = str(item.get("block_content", "")).strip()
            if content:
                blocks.append(content)
        text = join_text(blocks)

        txt_path = json_path.with_name(json_path.stem.replace("_res", "_text") + ".txt")
        txt_path.write_text(text, encoding="utf-8")
        log(f"Generated text: {txt_path.name}")

        md_name = json_path.stem.replace("_res", "") + ".md"
        md_path = json_path.with_name(md_name)
        if not md_path.exists():
            md_path.write_text(text, encoding="utf-8")
            log(f"Generated markdown: {md_path.name}")
