"""Behaviour of the VF iteration on the Z2 development groups (task A7).

Run from the repository root after data/fetch_gabriel.py:  uv run python experiments/convergence.py

Settings follow the accepted Z2 plan (ADR-0008): band 10 MHz-10 GHz, N = 240 nodes, the two
VF procedures vf_log (log nodes, unit weights) and quadvf_band (band_nodes and their weights),
log-spaced real initial poles, the loop control of section 5 and the development groups only.
The primary start range 1 kHz-100 GHz is run for every r in 1..32; the start-range
sensitivity of section 7 (1 Hz-1 THz and 10 MHz-10 GHz) for r in 4, 8, 16, 32.

Every case is run twice:

- accepted: vector_fit with the section-5 controls, i.e. what B6 will run. Its status, final
  candidate, Debye property and indicative errors are reported.
- trajectory: the same start with stopping disabled for the whole budget, to study the pole
  moves, the bounds of L1 (4.4)-(4.5) and section 4.2 (iii) and what happens after settling.

The paired fixed-pole procedure of section 4 (fixed_log with vf_log, fixed_band with
quadvf_band) is fitted from the same initial poles with baseline.fit_residues, so that the
effect of the start range on both kinds of method is visible.

Errors use a section-6 style grid (band edges and 4096 cell midpoints in ln f and in f) and the
band norm with 1024 nodes, without the refinement check of section 6: they are indicative and
not the conservative pass of B6. No final-evaluation group is touched.

Every run is recorded with vfdebye.provenance in results/runs/<run_id>/ (outside Git):
convergence.txt (report), convergence.json (case summaries) and convergence_iterations.npz
(per-iteration diagnostics and pole sets of the trajectories).
"""
from __future__ import annotations

import argparse
import contextlib
import io
import json
import math
import sys
from pathlib import Path

import numpy as np

from vfdebye import gabriel, metrics, provenance
from vfdebye.baseline import fit_residues, log_poles
from vfdebye.quadrature import band_nodes, band_norm
from vfdebye.vf import detect_period, matching_distance, vector_fit

ROOT = Path(__file__).resolve().parents[1]
CSV = ROOT / "data" / "processed" / "gabriel_parameters.csv"
BAND_HZ = (1e7, 1e10)
NODES = 240
DEV_GROUPS = ("Blood", "Muscle", "Fat", "Bone cortical", "Skin wet")
PRIMARY_START_HZ = (1e3, 1e11)
SENSITIVITY_STARTS_HZ = ((1.0, 1e12), (1e7, 1e10))
SENSITIVITY_ORDERS = (4, 8, 16, 32)
TOLERANCE = 1e-8  # section 5: delta_k and q_k
OMEGA_FLOOR = 2 * math.pi * BAND_HZ[0]  # rad/s, the scale floor of delta_k
CONTROLS = dict(max_iterations=200, pole_rtol=TOLERANCE, pole_atol=TOLERANCE * OMEGA_FLOOR,
                denominator_tol=TOLERANCE, reflect_unstable=True, settle_steps=2,
                max_period=4, cycle_repeats=2)
ILL_CONDITIONED = 1e12  # section 5 label, applied to the final residue LS
POST_HOC_TOLERANCES = (1e-6, 1e-8, 1e-10, 1e-12)
GRID_CELLS = 4096
BAND_NORM_NODES = 1024
TAIL = 20  # last trajectory steps summarised as the noise level of delta_k


def control_grid(f_min: float, f_max: float, cells: int) -> np.ndarray:
    """Band edges plus the midpoints of `cells` equal cells in ln f and in f (Hz)."""
    edges = np.linspace(math.log(f_min), math.log(f_max), cells + 1)
    linear = np.linspace(f_min, f_max, cells + 1)
    points = np.concatenate(([f_min, f_max], np.exp(0.5 * (edges[:-1] + edges[1:])),
                             0.5 * (linear[:-1] + linear[1:])))
    return np.unique(points)


def scaled_moves(history) -> np.ndarray:
    """delta_k = Omega_k / max(2 pi 10 MHz, max|lambda_(k-1)|); nan where no move was made."""
    return np.array([np.nan if item.pole_distance is None else
                     item.pole_distance / max(OMEGA_FLOOR, np.max(np.abs(item.poles_before)))
                     for item in history])


def settle_iteration(delta: np.ndarray, tolerance: float, consecutive: int = 2) -> int | None:
    """Number of LS steps after which `consecutive` successive delta_k <= tolerance; else None.

    Same count as len(history) of vector_fit with settle_steps=consecutive, pole_rtol=tolerance
    and pole_atol=tolerance*OMEGA_FLOOR, when no cycle or failure stops it earlier.
    """
    run = 0
    for k, value in enumerate(delta, start=1):
        run = run + 1 if value <= tolerance else 0
        if run >= consecutive:
            return k
    return None


def step_diagnostics(s: np.ndarray, history) -> dict[str, np.ndarray]:
    """Per-step quantities of A5 section 7 for one trajectory (nan where not reached).

    omega_raw: Omega between the old poles and the unreflected roots, bounded in L1 (4.4) by
    bound_44 = sqrt(r)(2r-1)||varphi||_2 in exact arithmetic. The computed roots carry rounding
    of order rounding = eps*max|lambda|, which dominates once ||varphi|| is that small, so the
    bound is checked as (omega_raw - bound_44) / rounding. eta = r max|varphi| / mu bounds
    q = max|d_tilde - 1| (section 4.2 (iii)), and omega_raw/mu bounds the relative change of
    the LS matrix (4.5). relative is the Fig. 2 measure of L1, scaled by the older set.
    """
    rows = []
    for item in history:
        varphi = item.step.denominator_residues
        r = varphi.size
        mu = float(np.min(np.abs(s[:, None] - item.poles_before)))
        raw = (np.nan if item.raw_poles is None
               else matching_distance(item.poles_before, item.raw_poles)[0])
        relative = (np.nan if item.poles_after is None
                    else matching_distance(item.poles_before, item.poles_after, relative=True)[0])
        rows.append((
            raw, math.sqrt(r) * (2 * r - 1) * float(np.linalg.norm(varphi)),
            r * float(np.max(np.abs(varphi))) / mu, raw / mu, relative,
            np.nan if item.denominator_deviation is None else item.denominator_deviation,
            item.step.condition, item.step.rank, item.step.weighted_residual_norm,
            item.reflected_count,
            np.nan if item.poles_after is None else int(np.count_nonzero(item.poles_after.imag)),
            np.finfo(float).eps * float(np.max(np.abs(item.poles_before))),
        ))
    names = ("omega_raw", "bound_44", "eta", "omega_raw_over_mu", "relative", "q",
             "condition", "rank", "linearized_residual", "reflected", "complex_poles",
             "rounding")
    table = np.array(rows, dtype=float).reshape(len(rows), len(names))
    return {name: table[:, j] for j, name in enumerate(names)}


class Reference:
    """H of one group on the control grid and on band-norm nodes computed once (section 6)."""

    def __init__(self, tissue: gabriel.Tissue, grid: np.ndarray, band: tuple) -> None:
        self.tissue, self.grid = tissue, grid
        f_band, self.band_weights = band
        self.band_s = gabriel.laplace_variable(f_band)
        self.band_h = gabriel.strictly_proper_part(tissue, self.band_s)
        self.band_h_norm = band_norm(self.band_h, self.band_weights)

    def errors(self, model) -> dict:
        """max relative error (metrics.max_relative_error) and ||H - H_r|| / ||H|| on the band.

        The band error is metrics.band_h2_error with precomputed nodes; a zero reference norm
        or non-finite model values raise ValueError, as there.
        """
        if self.band_h_norm == 0.0:
            raise ValueError("relative band error is undefined: reference norm is zero")
        values = np.asarray(model(self.band_s), dtype=complex)
        if not np.all(np.isfinite(values)):
            raise ValueError("model values must be finite")
        return {"max_relative_error": metrics.max_relative_error(self.tissue, model, self.grid),
                "band_error": band_norm(values - self.band_h, self.band_weights)
                / self.band_h_norm}


def candidate(reference: Reference, result) -> dict:
    """Properties and indicative errors of the final residue fit of one vector_fit call."""
    if result.final_fit is None:
        return {"available": False, "final_fit_error": result.final_fit_error}
    return fit_summary(reference, result.final_fit)


def fixed_candidate(reference: Reference, f, h, poles0, weights) -> dict:
    """The fixed-pole reference method (B4) from the same initial poles and nodes."""
    try:
        fit = fit_residues(f, h, poles0, weights)
    except (FloatingPointError, np.linalg.LinAlgError) as error:
        return {"available": False, "final_fit_error": str(error)}
    return fit_summary(reference, fit)


def fit_summary(reference: Reference, fit) -> dict:
    """Rank, conditioning, Debye property and indicative errors of a residue fit."""
    model = fit.model
    summary = {
        "available": True, "rank": fit.rank, "full_rank": fit.rank == model.order,
        "condition": fit.condition, "ill_conditioned": not fit.condition <= ILL_CONDITIONED,
        "stable": model.is_stable(), "real": model.is_real(), "debye": model.is_debye(),
        "complex_poles": int(np.count_nonzero(model.poles.imag)),
        "min_residue_real": float(np.min(model.residues.real)),
        "poles": model.poles, "residues": model.residues,
    }
    try:
        summary |= reference.errors(model)
    except ValueError as error:  # e.g. non-finite model values: reported, not hidden
        summary["error_evaluation_failed"] = str(error)
    return summary


def run_case(reference, f, s, h, weights, poles0, max_iterations):
    controls = CONTROLS | {"max_iterations": max_iterations}
    accepted = vector_fit(s, h, weights, poles0, **controls)
    trajectory = vector_fit(s, h, weights, poles0, **(controls | {
        "settle_steps": max_iterations + 1, "max_period": 0}))
    delta = scaled_moves(trajectory.history)
    diagnostics = step_diagnostics(s, trajectory.history)
    diagnostics["delta"] = delta
    settled = {f"{tol:.0e}": settle_iteration(delta, tol) for tol in POST_HOC_TOLERANCES}
    primary = settled[f"{TOLERANCE:.0e}"]
    moved = delta[~np.isnan(delta)]
    poles = [np.asarray(poles0, dtype=complex)] + [
        item.poles_after for item in trajectory.history if item.poles_after is not None]
    with np.errstate(invalid="ignore"):
        bound_excess = np.nanmax((diagnostics["omega_raw"] - diagnostics["bound_44"])
                                 / diagnostics["rounding"], initial=-np.inf)
        q_over_eta = np.nanmax(diagnostics["q"] / diagnostics["eta"], initial=0.0)
    summary = {
        "accepted": {
            "stop_reason": accepted.stop_reason, "iterations": len(accepted.history),
            "message": accepted.message, "cycle_period": accepted.cycle_period,
            "q_at_stop": (accepted.history[-1].denominator_deviation
                          if accepted.history else None),
            "candidate": candidate(reference, accepted),
        },
        "trajectory": {
            "stop_reason": trajectory.stop_reason, "iterations": len(trajectory.history),
            "message": trajectory.message,
            "settle_iteration": settled,
            # Post hoc rule = vector_fit rule when no cycle stopped the accepted run first.
            "consistent_with_accepted": (accepted.stop_reason.endswith("settled")
                                         == (primary is not None)
                                         and (primary is None
                                              or primary == len(accepted.history))),
            "max_delta_after_settling": (None if primary is None or primary >= delta.size
                                         else float(np.nanmax(delta[primary:], initial=0.0))),
            "tail_median_delta": float(np.median(moved[-TAIL:])) if moved.size else None,
            "final_q": float(diagnostics["q"][-1]) if moved.size else None,
            "max_bound_44_excess_in_rounding_units": float(bound_excess),
            "max_q_over_eta": float(q_over_eta),
            "period_at_end": (detect_period(poles, rtol=TOLERANCE, max_period=4)
                              if len(poles) > 1 else None),
            "candidate": candidate(reference, trajectory),
        },
        "fixed": fixed_candidate(reference, f, h, poles0, weights),
    }
    return summary, diagnostics, poles


def methods():
    f_log = np.geomspace(*BAND_HZ, NODES)
    f_band, w_band = band_nodes(*BAND_HZ, NODES)
    return {"vf_log": (f_log, np.ones(NODES)), "quadvf_band": (f_band, w_band)}


def case_list(orders, sensitivity_orders):
    cases = [(PRIMARY_START_HZ, r) for r in orders]
    cases += [(start, r) for start in SENSITIVITY_STARTS_HZ for r in sensitivity_orders]
    return cases


def fmt(value, spec=".2e"):
    return "-" if value is None else format(value, spec)


def report(rows: list[dict], max_iterations: int) -> dict:
    """Print the case table and the aggregate checks; return the run outcome."""
    print(f"band {BAND_HZ[0]:.0e}-{BAND_HZ[1]:.0e} Hz, N = {NODES}, accepted controls "
          f"(ADR-0008, section 5) with max_iterations = {max_iterations}")
    print("indicative errors: section-6 grid without refinement, band norm with "
          f"{BAND_NORM_NODES} nodes; development groups only\n")
    header = (f"{'group':<14}{'method':<12}{'start Hz':<14}{'r':>3}  {'status':<30}{'it':>4}"
              f"{'cond':>9}{'debye':>6}{'cpx':>4}{'max rel':>10}{'band':>10}"
              f"{'q stop':>9}{'k(1e-8)':>8}{'tail d':>9}{'q end':>9}{'fixed':>10}{'f cond':>9}")
    print(header)
    statuses: dict[str, int] = {}
    for row in rows:
        acc, traj = row["accepted"], row["trajectory"]
        cand = acc["candidate"]
        statuses[acc["stop_reason"]] = statuses.get(acc["stop_reason"], 0) + 1
        start = f"{row['start_hz'][0]:.0e}-{row['start_hz'][1]:.0e}"
        print(f"{row['group']:<14}{row['method']:<12}{start:<14}{row['r']:>3}  "
              f"{acc['stop_reason']:<30}{acc['iterations']:>4}"
              f"{fmt(cand.get('condition'), '.1e'):>9}"
              f"{('yes' if cand.get('debye') else 'no'):>6}{cand.get('complex_poles', '-'):>4}"
              f"{fmt(cand.get('max_relative_error')):>10}{fmt(cand.get('band_error')):>10}"
              f"{fmt(acc['q_at_stop'], '.1e'):>9}"
              f"{fmt(traj['settle_iteration']['1e-08'], 'd'):>8}"
              f"{fmt(traj['tail_median_delta'], '.1e'):>9}{fmt(traj['final_q'], '.1e'):>9}"
              f"{fmt(row['fixed'].get('max_relative_error')):>10}"
              f"{fmt(row['fixed'].get('condition'), '.1e'):>9}")
    first_step_rank = sorted({(r["method"], f"{r['start_hz'][0]:.0e}-{r['start_hz'][1]:.0e}",
                               r["r"]) for r in rows
                              if r["accepted"]["stop_reason"] == "rank_deficient"
                              and r["accepted"]["iterations"] == 1})
    bound = max(r["trajectory"]["max_bound_44_excess_in_rounding_units"] for r in rows)
    q_eta = max(r["trajectory"]["max_q_over_eta"] for r in rows)
    consistent = all(r["trajectory"]["consistent_with_accepted"] for r in rows
                     if r["accepted"]["stop_reason"] != "cycle")
    print("\naccepted-run statuses: " + ", ".join(f"{k} {v}" for k, v in sorted(statuses.items())))
    print(f"rank loss already in the first LS step (method, start, r): {len(first_step_rank)}")
    for method, start, r in first_step_rank:
        print(f"  {method} {start} r={r}")
    print(f"largest (Omega_raw - bound (4.4)) / (eps max|lambda|) over all steps: {bound:.3g}"
          " (<= 0: holds; a few units: rounding of the computed roots)")
    print(f"largest q / eta over all steps: {q_eta:.17g} (holds up to rounding if <= 1)")
    print(f"post hoc settling equals the accepted run: {consistent}")
    return {"cases": len(rows), "statuses": statuses,
            "first_step_rank_deficient": len(first_step_rank),
            "max_bound_44_excess_in_rounding_units": bound, "max_q_over_eta": q_eta,
            "post_hoc_consistent": consistent}


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    parser.add_argument("--csv", type=Path, default=CSV)
    parser.add_argument("--runs-dir", type=Path, default=provenance.RUNS_DIR)
    parser.add_argument("--groups", nargs="+", default=list(DEV_GROUPS),
                        help="representative tissue names; duplicates are added automatically")
    parser.add_argument("--orders", type=int, nargs="+", default=list(range(1, 33)))
    parser.add_argument("--sensitivity-orders", type=int, nargs="*",
                        default=list(SENSITIVITY_ORDERS))
    parser.add_argument("--max-iterations", type=int, default=CONTROLS["max_iterations"])
    args = parser.parse_args(argv)
    if not args.csv.is_file():
        print(f"{args.csv} is missing; run uv run python data/fetch_gabriel.py", file=sys.stderr)
        return 1
    if args.max_iterations < 1 or min(args.orders + args.sensitivity_orders, default=1) < 1:
        parser.error("orders and --max-iterations must be positive")
    tissues = {t.name: t for t in gabriel.read_csv(args.csv)}
    unknown = [g for g in args.groups if g not in tissues or not tissues[g].is_dispersive]
    if unknown:
        parser.error(f"unknown or non-dispersive groups: {unknown}")
    members = {g: [n for n, t in tissues.items() if t.parameters == tissues[g].parameters]
               for g in args.groups}

    nodes = methods()
    grid = control_grid(*BAND_HZ, GRID_CELLS)
    band = band_nodes(*BAND_HZ, BAND_NORM_NODES)
    cases = case_list(args.orders, args.sensitivity_orders)
    settings = {
        "purpose": "A7 development run on Z2 development groups (ADR-0008)",
        "band_hz": BAND_HZ, "nodes": NODES, "groups": members,
        "methods": {"vf_log": "geomspace nodes incl. band edges, unit weights",
                    "quadvf_band": "quadrature.band_nodes and weights"},
        "initial_poles": "baseline.log_poles(start_hz, r)", "cases": cases,
        "controls": CONTROLS | {"max_iterations": args.max_iterations},
        "omega_floor_rad_per_s": OMEGA_FLOOR, "ill_conditioned_above": ILL_CONDITIONED,
        "trajectory": "same controls with settle_steps = max_iterations + 1 and max_period = 0",
        "post_hoc_tolerances": POST_HOC_TOLERANCES, "control_grid_cells": GRID_CELLS,
        "band_norm_nodes": BAND_NORM_NODES, "tail_steps": TAIL,
        "solver": "numpy.linalg.lstsq", "rcond": None, "seed": None,
    }
    with provenance.run("convergence", settings=settings, inputs=[args.csv],
                        runs_dir=args.runs_dir) as record:
        rows, arrays = [], {}
        for group in args.groups:
            tissue = tissues[group]
            reference = Reference(tissue, grid, band)
            for method, (f, weights) in nodes.items():
                s = gabriel.laplace_variable(f)
                h = gabriel.strictly_proper_part(tissue, s)
                for start, r in cases:
                    summary, diagnostics, poles = run_case(
                        reference, f, s, h, weights, log_poles(*start, r), args.max_iterations)
                    key = f"{group}|{method}|{start[0]:.0e}-{start[1]:.0e}|{r}"
                    rows.append({"group": group, "names": members[group], "method": method,
                                 "start_hz": start, "r": r, **summary})
                    for name, values in diagnostics.items():
                        arrays[f"{key}|{name}"] = values
                    arrays[f"{key}|poles"] = np.array(poles)
        text = io.StringIO()
        with contextlib.redirect_stdout(text):
            outcome = report(rows, args.max_iterations)
        (record.dir / "convergence.txt").write_text(text.getvalue(), encoding="utf-8")
        (record.dir / "convergence.json").write_text(
            json.dumps(provenance.to_jsonable(rows), indent=1, allow_nan=False) + "\n",
            encoding="utf-8")
        np.savez_compressed(record.dir / "convergence_iterations.npz", **arrays)
        record.update(summary=outcome, artifacts=[
            "convergence.txt", "convergence.json", "convergence_iterations.npz"])
    print(text.getvalue(), end="")
    print(f"run {record.run_id} -> {record.dir}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
