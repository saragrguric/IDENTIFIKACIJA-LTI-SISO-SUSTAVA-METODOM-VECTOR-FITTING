"""The project runner must fail loudly instead of reporting checks that did not run."""
from __future__ import annotations

import contextlib
import io
import subprocess
import unittest
from unittest.mock import patch

import check_project as project


class CheckProjectTests(unittest.TestCase):
    def run_main(self, *, uv: str | None, codes: list[int]) -> tuple[int, list[list[str]], str]:
        calls: list[list[str]] = []

        def fake_run(command: list[str], cwd: object) -> subprocess.CompletedProcess[str]:
            calls.append(command)
            return subprocess.CompletedProcess(command, codes[len(calls) - 1])

        errors = io.StringIO()
        with (
            patch.object(project.shutil, "which", return_value=uv),
            patch.object(project.subprocess, "run", side_effect=fake_run),
            contextlib.redirect_stdout(io.StringIO()), contextlib.redirect_stderr(errors),
        ):
            status = project.main()
        return status, calls, errors.getvalue()

    def test_missing_uv_is_a_failure_and_runs_nothing(self) -> None:
        status, calls, errors = self.run_main(uv=None, codes=[])
        self.assertEqual((status, calls), (2, []))
        self.assertIn("uv is not on PATH", errors)

    def test_every_check_runs_in_the_locked_environment(self) -> None:
        status, calls, errors = self.run_main(uv="uv", codes=[0, 0])
        self.assertEqual((status, errors), (0, ""))
        self.assertEqual([call[:3] for call in calls], [["uv", "run", "--locked"]] * 2)
        self.assertEqual([call[3] for call in calls], ["pytest", "ruff"])

    def test_a_failing_check_fails_the_runner_but_the_rest_still_run(self) -> None:
        status, calls, errors = self.run_main(uv="uv", codes=[1, 0])
        self.assertEqual((status, len(calls)), (1, 2))
        self.assertIn("pytest failed (exit 1)", errors)


if __name__ == "__main__":
    unittest.main()
