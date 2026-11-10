#!/usr/bin/env python3
"""Run the numerical project checks in the locked uv environment (ADR-0006).

tools/check_before_stop.py calls this runner once pyproject.toml exists. A missing uv or a
uv.lock that no longer matches pyproject.toml is a failure, never a skipped check.
"""
from __future__ import annotations

import shutil
import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
# pytest's -ra summary keeps "SKIPPED ... NOT RUN: reason" lines visible to check_before_stop.
CHECKS = (
    ("pytest", ["pytest"]),
    ("ruff", ["ruff", "check", "."]),
)


def main() -> int:
    uv = shutil.which("uv")
    if uv is None:
        print(
            "uv is not on PATH, so the numerical checks cannot run. Install uv as described in "
            "docs/plan/PIPELINE.md.",
            file=sys.stderr,
        )
        return 2
    status = 0
    for name, command in CHECKS:
        print(f"== {name}", flush=True)
        result = subprocess.run([uv, "run", "--locked", *command], cwd=ROOT)
        if result.returncode != 0:
            print(f"{name} failed (exit {result.returncode})", file=sys.stderr)
            status = 1
    return status


if __name__ == "__main__":
    sys.exit(main())
