"""Thread-A figures are drawn from a recorded A7 run and keep their source and data tables."""
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


def test_figures_from_a_small_recorded_convergence_run(tmp_path, monkeypatch):
    cv, figures = load("convergence"), load("figures_a7")
    monkeypatch.setattr(cv, "GRID_CELLS", 16)
    monkeypatch.setattr(cv, "BAND_NORM_NODES", 16)
    table = tmp_path / "table.csv"
    gabriel.write_csv([["Blood", "4", "0.1", "50", "100", "0.1", "200", "5", "0.1",
                        "0", "0", "0", "0", "0", "0"]], table)
    runs = tmp_path / "runs"
    assert cv.main(["--csv", str(table), "--runs-dir", str(runs / "cv"), "--groups", "Blood",
                    "--orders", "4", "7", "10", "--sensitivity-orders", "4",
                    "--max-iterations", "30"]) == 0
    [cv_run] = list((runs / "cv").iterdir())
    assert figures.main(["--convergence-run", str(cv_run), "--runs-dir", str(runs / "fig")]) == 0
    [fig_run] = list((runs / "fig").iterdir())
    record = json.loads((fig_run / "provenance.json").read_text(encoding="utf-8"))
    assert record["status"] == "completed"
    assert record["settings"]["convergence_run"] == cv_run.name
    for name in ("fig_putanja", "fig_raspon"):
        for suffix in (".pdf", ".png"):
            assert (fig_run / f"{name}{suffix}").stat().st_size > 1000
    text = (fig_run / "figures_a7.txt").read_text(encoding="utf-8")
    assert "r=7 delta" in text and "vf_log 1e+07-1e+10" in text
    assert any(item["path"].endswith("convergence_iterations.npz") for item in record["inputs"])
