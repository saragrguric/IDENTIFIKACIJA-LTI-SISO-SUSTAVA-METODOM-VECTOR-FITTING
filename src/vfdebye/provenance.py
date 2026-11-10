"""Provenance record of one experiment run (task A6, docs/plan/PIPELINE.md).

Usage:

    with provenance.run("min_order", settings={...}, inputs=[csv_path]) as rec:
        ...                                   # write artifacts into rec.dir
        rec.update(stop_reason="max_iter", metrics={...})

Each run gets its own directory results/runs/<run_id>/ (outside Git) holding provenance.json
and the run's artifacts. The record is written when the run starts (status "running") and
rewritten when it ends ("completed", or "failed" with the error, which is then re-raised), so
an interrupted run still leaves a trace. A run directory is never overwritten.

Code state: the commit, whether the working tree differs from it, the diff of tracked files
(uncommitted.diff) and copies of untracked, non-ignored files (untracked/). When Git is not
available the record says so with the reason instead of inventing a revision.
"""
from __future__ import annotations

import hashlib
import json
import math
import os
import platform
import shutil
import subprocess
import sys
import time
from collections.abc import Iterable, Iterator, Mapping
from contextlib import contextmanager
from dataclasses import dataclass, field
from datetime import UTC, datetime
from importlib import metadata
from pathlib import Path
from typing import Any

import numpy as np

REPO = Path(__file__).resolve().parents[2]
RUNS_DIR = REPO / "results" / "runs"
RECORD = "provenance.json"
PACKAGES = ("vfdebye", "numpy", "scipy", "matplotlib")
THREAD_VARIABLES = ("OMP_NUM_THREADS", "OPENBLAS_NUM_THREADS", "MKL_NUM_THREADS")
# Untracked files larger than this are listed with their checksum but not copied.
MAX_COPY_BYTES = 1_000_000
GIT_TIMEOUT_SECONDS = 30


def to_jsonable(value: Any) -> Any:
    """Convert settings and metrics to JSON values without losing information.

    Complex numbers become {"re": .., "im": ..}; arrays become nested lists; non-finite floats
    become {"float": "nan"}, {"float": "inf"} or {"float": "-inf"}, so they stay distinct from
    strings. Unknown types raise TypeError.
    """
    if isinstance(value, Mapping):
        return {str(k): to_jsonable(v) for k, v in value.items()}
    if isinstance(value, np.ndarray):
        return [to_jsonable(v) for v in value.tolist()]
    if isinstance(value, (list, tuple)):
        return [to_jsonable(v) for v in value]
    if isinstance(value, np.generic):
        return to_jsonable(value.item())
    if isinstance(value, bool) or value is None or isinstance(value, (int, str)):
        return value
    if isinstance(value, float):
        return value if math.isfinite(value) else {"float": str(value)}
    if isinstance(value, complex):
        return {"re": to_jsonable(value.real), "im": to_jsonable(value.imag)}
    if isinstance(value, Path):
        return str(value)
    raise TypeError(f"cannot record a value of type {type(value).__name__}: {value!r}")


def sha256(path: str | Path) -> str:
    digest = hashlib.sha256()
    with open(path, "rb") as handle:
        for block in iter(lambda: handle.read(1 << 20), b""):
            digest.update(block)
    return digest.hexdigest()


def _git(repo: Path, *args: str) -> subprocess.CompletedProcess[bytes]:
    return subprocess.run(
        ["git", "-C", str(repo), *args], capture_output=True, timeout=GIT_TIMEOUT_SECONDS
    )


def code_state(repo: Path, run_dir: Path) -> dict[str, Any]:
    """Commit and working-tree state; saves the diff and untracked files into run_dir."""
    try:
        head = _git(repo, "rev-parse", "HEAD")
    except (OSError, subprocess.TimeoutExpired) as error:
        return {"available": False, "reason": f"git could not run: {error}"}
    if head.returncode != 0:
        return {"available": False, "reason": head.stderr.decode(errors="replace").strip()}
    branch = _git(repo, "rev-parse", "--abbrev-ref", "HEAD").stdout.decode().strip()
    diff = _git(repo, "diff", "--binary", "HEAD").stdout
    untracked = [
        name for name in
        _git(repo, "ls-files", "--others", "--exclude-standard", "-z").stdout.decode().split("\0")
        if name
    ]
    state: dict[str, Any] = {
        "available": True,
        "commit": head.stdout.decode().strip(),
        "branch": branch,
        "dirty": bool(diff or untracked),
        "uncommitted_diff": None,
        "untracked": [],
    }
    if diff:
        (run_dir / "uncommitted.diff").write_bytes(diff)
        state["uncommitted_diff"] = {
            "file": "uncommitted.diff", "sha256": hashlib.sha256(diff).hexdigest(),
        }
    for name in untracked:
        source = repo / name
        if not source.is_file():
            continue
        entry = {"path": name, "sha256": sha256(source), "bytes": source.stat().st_size}
        if entry["bytes"] <= MAX_COPY_BYTES:
            target = run_dir / "untracked" / name
            target.parent.mkdir(parents=True, exist_ok=True)
            shutil.copyfile(source, target)
            entry["copied"] = True
        else:
            entry["copied"] = False
        state["untracked"].append(entry)
    return state


def linear_algebra() -> dict[str, Any]:
    """BLAS and LAPACK numpy was built with; LS and eig results can differ between them."""
    build = np.show_config(mode="dicts")["Build Dependencies"]
    keys = ("name", "version", "openblas configuration")
    return {lib: {k: build[lib][k] for k in keys if k in build.get(lib, {})}
            for lib in ("blas", "lapack")}


def recorded_path(path: Path, repo: Path) -> str:
    """Path relative to the repository when inside it, so no personal absolute path is kept."""
    try:
        return path.resolve().relative_to(repo.resolve()).as_posix()
    except ValueError:
        return str(path.resolve())


def environment(repo: Path) -> dict[str, Any]:
    packages = {}
    for name in PACKAGES:
        try:
            packages[name] = metadata.version(name)
        except metadata.PackageNotFoundError:
            packages[name] = None
    lock = repo / "uv.lock"
    return {
        "python": sys.version,
        "executable": sys.executable,
        "platform": platform.platform(),
        "machine": platform.machine(),
        "packages": packages,
        "uv_lock_sha256": sha256(lock) if lock.is_file() else None,
        "threads": {name: os.environ.get(name) for name in THREAD_VARIABLES},
        "linear_algebra": linear_algebra(),
    }


@dataclass
class RunRecord:
    """Mutable record of a running experiment; written to <dir>/provenance.json."""

    dir: Path
    data: dict[str, Any] = field(default_factory=dict)

    @property
    def run_id(self) -> str:
        return self.data["run_id"]

    def update(self, **fields: Any) -> None:
        """Add outcome fields, e.g. stop_reason, iterations, metrics, warnings, artifacts."""
        for key, value in fields.items():
            if key in _RESERVED:
                raise ValueError(f"{key!r} is set by vfdebye.provenance itself")
            self.data.setdefault("outcome", {})[key] = to_jsonable(value)
        self.write()

    def write(self) -> None:
        text = json.dumps(self.data, indent=2, ensure_ascii=False, allow_nan=False)
        (self.dir / RECORD).write_text(text + "\n", encoding="utf-8")


_RESERVED = {"run_id", "status", "error"}


def new_run_id(experiment: str, now: datetime) -> str:
    if not experiment or not all(c.isalnum() or c in "_-" for c in experiment):
        raise ValueError(f"experiment name must be [A-Za-z0-9_-]+, got {experiment!r}")
    return f"{now:%Y%m%dT%H%M%S%fZ}-{experiment}"


@contextmanager
def run(
    experiment: str,
    *,
    settings: Mapping[str, Any],
    inputs: Iterable[str | Path] = (),
    runs_dir: str | Path | None = None,
    repo: str | Path | None = None,
    command: list[str] | None = None,
) -> Iterator[RunRecord]:
    """Create results/runs/<run_id>/ and keep its provenance.json up to date.

    settings: everything that determines the result (band, nodes and weights, order,
    initial poles, solver, tolerances, iteration limits, seed if any). inputs: data files whose
    SHA-256 identifies the input; paths inside the repository are recorded relative to it.
    """
    repo = Path(repo) if repo is not None else REPO
    runs_dir = Path(runs_dir) if runs_dir is not None else RUNS_DIR
    started = datetime.now(UTC)
    run_id = new_run_id(experiment, started)
    run_dir = runs_dir / run_id
    run_dir.mkdir(parents=True, exist_ok=False)
    input_paths = [Path(p) for p in inputs]
    missing = [str(p) for p in input_paths if not p.is_file()]
    if missing:
        shutil.rmtree(run_dir)
        raise ValueError(f"input files do not exist: {missing}")
    record = RunRecord(run_dir, {
        "run_id": run_id,
        "experiment": experiment,
        "status": "running",
        "started": started.isoformat(),
        "finished": None,
        "duration_seconds": None,
        "command": command if command is not None else [sys.executable, *sys.argv],
        "settings": to_jsonable(settings),
        "inputs": [{"path": recorded_path(p, repo), "sha256": sha256(p)} for p in input_paths],
        "code": code_state(repo, run_dir),
        "environment": environment(repo),
        "outcome": {},
        "error": None,
    })
    record.write()
    clock = time.perf_counter()
    try:
        yield record
    except BaseException as error:
        record.data["status"] = "failed"
        record.data["error"] = f"{type(error).__name__}: {error}"
        raise
    else:
        record.data["status"] = "completed"
    finally:
        record.data["finished"] = datetime.now(UTC).isoformat()
        record.data["duration_seconds"] = time.perf_counter() - clock
        record.write()
