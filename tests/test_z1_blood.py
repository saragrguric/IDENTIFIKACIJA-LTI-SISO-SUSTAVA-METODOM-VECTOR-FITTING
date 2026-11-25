"""Z1 walkthrough: Debye parameters from poles and residues, and a complete recorded run."""
import contextlib
import io
import json
import re
import sys
from importlib.util import module_from_spec, spec_from_file_location
from pathlib import Path

import numpy as np
import pytest

from vfdebye import gabriel
from vfdebye.vf import PoleResidueModel

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "experiments"))  # z1_blood imports experiments/convergence.py
spec = spec_from_file_location("z1_blood", ROOT / "experiments" / "z1_blood.py")
z1 = module_from_spec(spec)
spec.loader.exec_module(z1)

DEBYE_ROW = ["Synthetic Debye", "4", "0.1", "50", "100", "0", "200", "5", "0",
             "0", "0", "0", "0", "0", "0"]


def test_debye_terms_are_read_back_from_poles_and_residues():
    # Delta_eps / (1 + s tau) = (Delta_eps / tau) / (s + 1 / tau).
    tau, delta = np.array([5e-9, 1e-10]), np.array([200.0, 50.0])
    text = io.StringIO()
    with contextlib.redirect_stdout(text):
        z1.describe_model(PoleResidueModel(-1 / tau, delta / tau))
    found = [(float(t), float(d)) for t, d in
             re.findall(r"tau = (\S+) s .* delta_eps = (\S+)", text.getvalue())]
    assert "is_debye = True" in text.getvalue()
    np.testing.assert_allclose(found, [(5e-9, 200.0), (1e-10, 50.0)], rtol=1e-4)


def test_walkthrough_records_every_step_for_an_exact_debye_tissue(tmp_path, monkeypatch):
    monkeypatch.setattr(z1.z2, "GRID_CELLS", 64)
    monkeypatch.setattr(z1.z2, "BAND_NORM_NODES", 64)
    csv = tmp_path / "table.csv"
    gabriel.write_csv([DEBYE_ROW], csv)
    runs = tmp_path / "runs"
    code = z1.main(["--csv", str(csv), "--runs-dir", str(runs), "--tissue", "Synthetic Debye",
                    "--order", "2", "--sweep", "1", "2", "--max-iterations", "40"])
    assert code == 0
    [run_dir] = list(runs.iterdir())
    record = json.loads((run_dir / "provenance.json").read_text(encoding="utf-8"))
    report = (run_dir / "z1_blood.txt").read_text(encoding="utf-8")
    assert record["status"] == "completed"
    assert record["outcome"]["stop_reason"] == "poles_and_denominator_settled"
    assert record["settings"]["start_hz"] == [1e7, 1e10]
    for step in ("1. Synthetic Debye", "\n2. H(s)", "\n3. vf_log", "\n4. final model",
                 "\n5. indicative errors", "order sweep"):
        assert step in report
    assert "is_debye = True" in report
    for name in ("vf_log", "fixed_log", "fixed_log_wide", "quadvf_band", "fixed_band_wide"):
        assert f"   {name} " in report


def test_unknown_tissue_is_rejected(tmp_path):
    csv = tmp_path / "table.csv"
    gabriel.write_csv([DEBYE_ROW], csv)
    with pytest.raises(SystemExit):
        z1.main(["--csv", str(csv), "--runs-dir", str(tmp_path / "runs"), "--tissue", "Liver"])
    assert not (tmp_path / "runs").exists()
