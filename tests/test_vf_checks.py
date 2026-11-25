"""The synthetic CLI preserves complete records for successes and iteration limits."""
import json
import subprocess
import sys
from pathlib import Path

import pytest

ROOT = Path(__file__).resolve().parents[1]


@pytest.mark.parametrize(("iterations", "exit_code", "passed_cases"), [(30, 0, 3), (1, 1, 0)])
def test_cli_records_every_case_and_reports_unsuccessful_termination(
    tmp_path, iterations, exit_code, passed_cases,
):
    completed = subprocess.run(
        [sys.executable, str(ROOT / "experiments" / "vf_checks.py"),
         "--runs-dir", str(tmp_path), "--max-iterations", str(iterations)],
        cwd=ROOT, capture_output=True, text=True, timeout=30,
    )
    assert completed.returncode == exit_code, completed.stdout + completed.stderr
    [run_dir] = list(tmp_path.iterdir())
    record = json.loads((run_dir / "provenance.json").read_text())
    outcomes = json.loads((run_dir / "vf_checks.json").read_text())
    assert record["status"] == "completed"  # Recording completed, not a convergence claim.
    assert record["outcome"]["passed_cases"] == passed_cases
    assert record["outcome"]["total_cases"] == 3
    assert record["outcome"]["checks_passed"] is (passed_cases == 3)
    assert record["settings"]["controls"]["max_iterations"] == iterations
    assert {item["name"] for item in outcomes} == {
        "real_poles", "conjugate_pair", "band_weights",
    }
    for item in outcomes:
        assert item["result"]["final_fit"] is not None
        first = item["result"]["history"][0]
        assert first["poles_before"] and first["raw_poles"] and first["poles_after"]
        assert first["step"]["rank"] > 0
        assert first["step"]["condition"] > 0
        if exit_code:
            assert item["result"]["stop_reason"] == "max_iterations"
