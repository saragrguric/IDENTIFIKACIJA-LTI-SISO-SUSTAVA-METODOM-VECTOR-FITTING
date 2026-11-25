"""A7 runner: the post hoc stopping rule, the bounds of A5 section 7 and complete records."""
import json
import math
from importlib.util import module_from_spec, spec_from_file_location
from pathlib import Path

import numpy as np
import pytest

from vfdebye import gabriel, metrics
from vfdebye.baseline import fit_residues, log_poles
from vfdebye.quadrature import band_nodes
from vfdebye.vf import vector_fit

ROOT = Path(__file__).resolve().parents[1]
spec = spec_from_file_location("convergence", ROOT / "experiments" / "convergence.py")
convergence = module_from_spec(spec)
spec.loader.exec_module(convergence)

# Two exact Debye terms (alpha = 0) with relaxations at about 32 MHz and 1.6 GHz, in table units.
DEBYE_ROW = ["Synthetic Debye", "4", "0.1", "50", "100", "0", "200", "5", "0",
             "0", "0", "0", "0", "0", "0"]
# The same with Cole-Cole terms (alpha = 0.1): no finite order is exact.
COLE_ROW = ["Synthetic Cole", "4", "0.1", "50", "100", "0.1", "200", "5", "0.1",
            "0", "0", "0", "0", "0", "0"]


def band_case(row, r, n=80):
    tissue = gabriel.tissue_from_row(row[0], row[1:])
    f, w = band_nodes(*convergence.BAND_HZ, n)
    s = gabriel.laplace_variable(f)
    return tissue, s, gabriel.strictly_proper_part(tissue, s), w, log_poles(1e7, 1e10, r)


def test_post_hoc_settling_is_the_accepted_stopping_rule():
    _, s, h, w, poles0 = band_case(DEBYE_ROW, 2)
    accepted = vector_fit(s, h, w, poles0, **convergence.CONTROLS)
    assert accepted.stop_reason == "poles_and_denominator_settled"
    trajectory = vector_fit(s, h, w, poles0, **(convergence.CONTROLS | {
        "settle_steps": 201, "max_period": 0}))
    delta = convergence.scaled_moves(trajectory.history)
    assert convergence.settle_iteration(delta, 1e-8) == len(accepted.history)
    # delta_k is Omega_k over max(2 pi 10 MHz, max|lambda|): here the poles exceed the floor.
    first = trajectory.history[0]
    assert np.max(np.abs(first.poles_before)) > convergence.OMEGA_FLOOR
    assert delta[0] == pytest.approx(first.pole_distance / np.max(np.abs(first.poles_before)))


@pytest.mark.parametrize(("values", "expected"), [
    ([1e-3, 1e-9, 1e-3, 1e-9, 1e-9], 5),
    ([1e-9, 1e-9], 2),
    ([1e-9, np.nan, 1e-9], None),
    ([1e-3] * 5, None),
])
def test_settle_iteration_needs_two_consecutive_small_moves(values, expected):
    assert convergence.settle_iteration(np.array(values), 1e-8) == expected


@pytest.mark.parametrize(("row", "r"), [(DEBYE_ROW, 1), (DEBYE_ROW, 2), (COLE_ROW, 2),
                                        (COLE_ROW, 4)])
def test_trajectory_respects_bounds_4_4_and_q_below_eta(row, r):
    # L1 (4.4): Omega_raw <= sqrt(r)(2r-1)||varphi||; A5 7.3: max|d_tilde - 1| <= eta. Both hold
    # in exact arithmetic; the computed roots lambda - ... carry rounding eps*max|lambda|.
    _, s, h, w, poles0 = band_case(row, r)
    trajectory = vector_fit(s, h, w, poles0, **(convergence.CONTROLS | {
        "max_iterations": 25, "settle_steps": 26, "max_period": 0}))
    d = convergence.step_diagnostics(s, trajectory.history)
    moved = ~np.isnan(d["omega_raw"])
    assert len(d["q"]) == len(trajectory.history) and np.count_nonzero(moved) >= 10
    assert np.all(d["omega_raw"][moved] <= d["bound_44"][moved] + 16 * r * d["rounding"][moved])
    assert np.all(d["q"][moved] <= d["eta"][moved] * (1 + 1e-12))


def test_rank_loss_leaves_the_step_without_relocation_diagnostics():
    # Order 5 for an exact order-2 function: the first LS matrix is rank deficient.
    _, s, h, w, poles0 = band_case(DEBYE_ROW, 5)
    trajectory = vector_fit(s, h, w, poles0, **convergence.CONTROLS)
    assert trajectory.stop_reason == "rank_deficient" and len(trajectory.history) == 1
    d = convergence.step_diagnostics(s, trajectory.history)
    assert np.isnan(d["omega_raw"][0]) and np.isnan(d["q"][0]) and d["rank"][0] < 10
    assert np.isnan(convergence.scaled_moves(trajectory.history)[0])


def test_control_grid_has_edges_and_midpoints_in_ln_f_and_f():
    grid = convergence.control_grid(1e7, 1e10, 8)
    assert grid[0] == 1e7 and grid[-1] == 1e10 and np.all(np.diff(grid) > 0)
    log_mid = np.sqrt(np.geomspace(1e7, 1e10, 9)[:-1] * np.geomspace(1e7, 1e10, 9)[1:])
    lin_mid = np.linspace(1e7, 1e10, 9)[:-1] + (1e10 - 1e7) / 16
    for point in np.concatenate((log_mid, lin_mid)):
        assert np.min(np.abs(grid - point)) <= 1e-12 * point
    assert grid.size == 2 + 16


def test_reference_errors_match_the_metrics_module():
    tissue = gabriel.tissue_from_row(COLE_ROW[0], COLE_ROW[1:])
    f, _ = band_nodes(*convergence.BAND_HZ, 40)
    s = gabriel.laplace_variable(f)
    model = fit_residues(f, gabriel.strictly_proper_part(tissue, s), log_poles(1e7, 1e10, 3)).model
    grid = convergence.control_grid(*convergence.BAND_HZ, 32)
    reference = convergence.Reference(tissue, grid, band_nodes(*convergence.BAND_HZ, 64))
    errors = reference.errors(model)
    assert errors["max_relative_error"] == metrics.max_relative_error(tissue, model, grid)
    assert errors["band_error"] == pytest.approx(
        metrics.band_h2_error(tissue, model, *convergence.BAND_HZ, 64), rel=1e-12)


def test_cli_records_every_case_and_recovers_an_exact_debye_tissue(tmp_path, monkeypatch):
    monkeypatch.setattr(convergence, "GRID_CELLS", 64)
    monkeypatch.setattr(convergence, "BAND_NORM_NODES", 64)
    csv = tmp_path / "table.csv"
    gabriel.write_csv([DEBYE_ROW, COLE_ROW], csv)
    runs = tmp_path / "runs"
    code = convergence.main(["--csv", str(csv), "--runs-dir", str(runs),
                             "--groups", "Synthetic Debye", "--orders", "1", "2",
                             "--sensitivity-orders", "2", "--max-iterations", "40"])
    assert code == 0
    [run_dir] = list(runs.iterdir())
    record = json.loads((run_dir / "provenance.json").read_text(encoding="utf-8"))
    rows = json.loads((run_dir / "convergence.json").read_text(encoding="utf-8"))
    assert record["status"] == "completed"
    assert record["settings"]["groups"] == {"Synthetic Debye": ["Synthetic Debye"]}
    # 2 methods x (2 primary orders + 2 sensitivity ranges x 1 order).
    assert record["outcome"]["summary"]["cases"] == len(rows) == 8
    assert record["outcome"]["summary"]["post_hoc_consistent"] is True
    assert record["outcome"]["summary"]["max_q_over_eta"] <= 1 + 1e-12
    assert record["outcome"]["summary"]["max_bound_44_excess_in_rounding_units"] <= 16
    exact = [row for row in rows if row["r"] == 2]
    assert len(exact) == 6
    for row in exact:
        acc = row["accepted"]
        assert acc["stop_reason"] == "poles_and_denominator_settled", row["start_hz"]
        assert acc["candidate"]["debye"] is True
        assert acc["candidate"]["max_relative_error"] < 1e-9
        poles = sorted(-p["re"] for p in acc["candidate"]["poles"])
        np.testing.assert_allclose(poles, [1 / 5e-9, 1 / 100e-12], rtol=1e-8)
    for row in rows:  # the paired fixed-pole fit from the same initial poles
        assert row["fixed"]["available"] and row["fixed"]["rank"] == row["r"]
        assert len(row["fixed"]["poles"]) == row["r"]
    with np.load(run_dir / "convergence_iterations.npz") as arrays:
        key = f"Synthetic Debye|quadvf_band|{1e3:.0e}-{1e11:.0e}|2"
        assert arrays[f"{key}|delta"].size == arrays[f"{key}|q"].size >= 1
        assert arrays[f"{key}|poles"].shape[1] == 2
    assert math.isfinite(rows[0]["trajectory"]["max_q_over_eta"])


def test_cli_rejects_unknown_or_non_dispersive_groups(tmp_path):
    csv = tmp_path / "table.csv"
    gabriel.write_csv([DEBYE_ROW, ["Air", "1", "0", "0", "0", "1", "0", "0", "1",
                                   "0", "0", "1", "0", "0", "1"]], csv)
    for group in ("Missing", "Air"):
        with pytest.raises(SystemExit):
            convergence.main(["--csv", str(csv), "--runs-dir", str(tmp_path / "runs"),
                              "--groups", group])
    assert not (tmp_path / "runs").exists()
