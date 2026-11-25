"""Seminar figures are drawn from recorded runs and keep their sources and data tables."""
import json
import sys
from importlib.util import module_from_spec, spec_from_file_location
from pathlib import Path

from vfdebye import gabriel

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "experiments"))


def load(name):
    spec = spec_from_file_location(name, ROOT / "experiments" / f"{name}.py")
    module = module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def row(name, alpha):
    return [name, "4", "0.1", "50", "100", alpha, "200", "5", alpha, "0", "0", "0", "0", "0", "0"]


def test_figures_from_small_recorded_runs(tmp_path, monkeypatch):
    mo, cv, figures = load("min_order"), load("convergence"), load("figures")
    monkeypatch.setattr(mo, "GRID_CELLS", (16, 32))
    monkeypatch.setattr(mo, "BAND_NODES", (16, 32))
    monkeypatch.setattr(cv, "GRID_CELLS", 16)
    monkeypatch.setattr(cv, "BAND_NORM_NODES", 16)
    csv = tmp_path / "table.csv"
    gabriel.write_csv([row("Blood", "0"), row("Liver", "0.1")], csv)
    runs = tmp_path / "runs"
    assert mo.main(["--csv", str(csv), "--runs-dir", str(runs / "mo"), "--experiments",
                    "final_base", "--orders", "1", "2", "3"]) == 0
    assert cv.main(["--csv", str(csv), "--runs-dir", str(runs / "cv"), "--groups", "Blood",
                    "--orders", "4", "7", "10", "--sensitivity-orders", "4",
                    "--max-iterations", "30"]) == 0
    [mo_run], [cv_run] = list((runs / "mo").iterdir()), list((runs / "cv").iterdir())
    assert figures.main(["--min-order-run", str(mo_run), "--convergence-run", str(cv_run),
                         "--runs-dir", str(runs / "fig")]) == 0
    [fig_run] = list((runs / "fig").iterdir())
    record = json.loads((fig_run / "provenance.json").read_text(encoding="utf-8"))
    assert record["status"] == "completed"
    assert record["settings"]["min_order_run"] == mo_run.name
    assert record["settings"]["convergence_run"] == cv_run.name
    for name in ("fig_udio_skupina", "fig_pogreska_red", "fig_putanja", "fig_raspon"):
        for suffix in (".pdf", ".png"):
            assert (fig_run / f"{name}{suffix}").stat().st_size > 1000
    table = (fig_run / "figures.txt").read_text(encoding="utf-8")
    assert "fig_udio_skupina" in table and "Liver" in table and "r=7 delta" in table
    inputs = record["inputs"]
    assert any(item["path"].endswith("min_order.csv") for item in inputs)
