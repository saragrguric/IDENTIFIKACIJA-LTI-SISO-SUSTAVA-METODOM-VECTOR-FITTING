"""Main experiment B6: smallest found order per group, procedure, error measure and level.

Run from the repository root after data/fetch_gabriel.py:

    uv run python experiments/min_order.py                      # development experiments
    uv run python experiments/min_order.py --experiments final_base   # after the plan is locked

Everything follows the accepted Z2 plan with its A7 addendum (ADR-0008):

- groups: dispersive tissues with identical parameters form one group, computed once; the five
  development groups are named in DEV_GROUPS, all other dispersive groups are final ones;
  Air and Vacuum (H = 0) have no relative error and are left out with a note;
- procedures: vf_log and quadvf_band (vector_fit with the section-5 controls), fixed_log and
  fixed_band (baseline.fit_residues), all from the same log-spaced poles over the primary
  range; fixed_log_wide and fixed_band_wide use 1 kHz-100 GHz as a stronger fixed-pole
  reference in the general table;
- experiments: dev_base, dev_nodes (N = 120, 480), dev_start (two other start ranges) and
  final_base, with the case counts of the addendum (1280 development and 6912 final cases);
- evaluation (section 6): band edges plus 4096 and 8192 cell midpoints in ln f and in f for the
  largest relative error, 512 and 1024 band_nodes for the band error; E_fine +
  |E_fine - E_coarse| <= level is a pass, E_fine - |E_fine - E_coarse| > level a fail and
  anything else borderline; a difference above 1e-6 is reported as unresolved;
- tables (section 5): a candidate counts only with a settled loop (VF) or fixed poles, full
  rank, every solved LS matrix conditioned at most 1e12, a stable real response, and for the
  Debye table real negative poles with strictly positive residues (PoleResidueModel.is_debye).

Every case is written to cases/<case>.json in results/runs/<run_id>/ (outside Git) as soon as
it is computed; --resume-from <run_dir> reuses finished cases of an earlier run with the same
settings and input, recording the link instead of overwriting anything. min_order.csv and
min_order.txt summarise the run; the hypotheses of section 1 are evaluated on final_base.
"""
from __future__ import annotations

import argparse
import contextlib
import csv
import hashlib
import io
import json
import statistics
import sys
import time
from pathlib import Path

import convergence as z2  # experiments/convergence.py: the ADR-0008 settings and error grid
import numpy as np

from vfdebye import gabriel, provenance
from vfdebye.baseline import fit_residues, log_poles
from vfdebye.quadrature import band_nodes, band_norm
from vfdebye.vf import vector_fit

WIDE_START_HZ = (1e3, 1e11)
ORDERS = tuple(range(1, 33))
LEVELS = (0.05, 0.01, 0.001)
MEASURES = ("max_relative_error", "band_error")
GRID_CELLS = (4096, 8192)  # coarse, fine
BAND_NODES = (512, 1024)  # coarse, fine
RESOLUTION = 1e-6
VF_PROCEDURES = ("vf_log", "quadvf_band")
FIXED_OF = {"vf_log": "fixed_log", "quadvf_band": "fixed_band"}
SETTLED = ("poles_settled", "poles_and_denominator_settled")
EXPERIMENTS = {
    "dev_base": dict(groups="dev", orders=ORDERS, nodes=(240,), starts=(z2.PRIMARY_START_HZ,),
                     wide=True),
    "dev_nodes": dict(groups="dev", orders=z2.SENSITIVITY_ORDERS, nodes=(120, 480),
                      starts=(z2.PRIMARY_START_HZ,), wide=False),
    "dev_start": dict(groups="dev", orders=z2.SENSITIVITY_ORDERS, nodes=(240,),
                      starts=z2.SENSITIVITY_STARTS_HZ, wide=False),
    "final_base": dict(groups="final", orders=ORDERS, nodes=(240,),
                       starts=(z2.PRIMARY_START_HZ,), wide=True),
}
DEV_EXPERIMENTS = ("dev_base", "dev_nodes", "dev_start")


def parameter_groups(tissues: list[gabriel.Tissue]) -> tuple[dict, dict, list[str]]:
    """Development and final groups {label: [names]} by identical parameters, and H = 0 names.

    A group is labelled by its DEV_GROUPS name when it has one, else by its first table name.
    """
    by_parameters: dict[tuple, list[str]] = {}
    skipped = []
    for tissue in tissues:
        if tissue.is_dispersive:
            by_parameters.setdefault(tissue.parameters, []).append(tissue.name)
        else:
            skipped.append(tissue.name)
    dev, final = {}, {}
    for names in by_parameters.values():
        label = next((n for n in z2.DEV_GROUPS if n in names), None)
        (dev if label else final)[label or names[0]] = names
    return dev, final, skipped


def nodes(n: int) -> dict[str, tuple[np.ndarray, np.ndarray]]:
    """Fitting nodes (Hz) and weights of the two node families for N = n (section 4)."""
    f_band, w_band = band_nodes(*z2.BAND_HZ, n)
    return {"log": (np.geomspace(*z2.BAND_HZ, n), np.ones(n)), "band": (f_band, w_band)}


def case_plan(experiments: list[str], dev: dict, final: dict, orders: tuple | None) -> list[dict]:
    """Every case of the chosen experiments, in a fixed order."""
    cases = []
    for name in experiments:
        spec = EXPERIMENTS[name]
        groups = dev if spec["groups"] == "dev" else final
        for group in groups:
            for n in spec["nodes"]:
                for start in spec["starts"]:
                    for r in spec["orders"]:
                        if orders is not None and r not in orders:
                            continue
                        for procedure in (*VF_PROCEDURES, *FIXED_OF.values()):
                            cases.append(dict(experiment=name, group=group, procedure=procedure,
                                              nodes=n, start_hz=start, r=r))
                        if spec["wide"]:
                            for fixed in FIXED_OF.values():
                                cases.append(dict(experiment=name, group=group,
                                                  procedure=f"{fixed}_wide", nodes=n,
                                                  start_hz=WIDE_START_HZ, r=r))
    return cases


def case_id(case: dict) -> str:
    start = f"{case['start_hz'][0]:.0e}-{case['start_hz'][1]:.0e}"
    group = "".join(c if c.isalnum() else "_" for c in case["group"])
    return (f"{case['experiment']}__{group}__{case['procedure']}__N{case['nodes']}__{start}"
            f"__r{case['r']:02d}")


class Evaluator:
    """H of one group on the coarse and fine control grids and band-norm nodes (section 6)."""

    def __init__(self, tissue: gabriel.Tissue, grids: tuple, bands: tuple) -> None:
        self.grid_s = [gabriel.laplace_variable(f) for f in grids]
        self.grid_h = [gabriel.strictly_proper_part(tissue, s) for s in self.grid_s]
        self.grid_eps = [np.abs(gabriel.permittivity(tissue, s)) for s in self.grid_s]
        self.band_s = [gabriel.laplace_variable(f) for f, _ in bands]
        self.band_w = [w for _, w in bands]
        self.band_h = [gabriel.strictly_proper_part(tissue, s) for s in self.band_s]
        self.band_h_norm = [band_norm(h, w) for h, w in zip(self.band_h, self.band_w, strict=True)]

    def errors(self, model) -> dict:
        """Coarse and fine values of both measures; ValueError for non-finite model values."""
        out = {}
        for measure, pairs in (
            ("max_relative_error", zip(self.grid_s, self.grid_h, self.grid_eps, strict=True)),
            ("band_error", zip(self.band_s, self.band_h, self.band_w, self.band_h_norm,
                               strict=True)),
        ):
            values = []
            for s, h, *scale in pairs:
                response = np.asarray(model(s), dtype=complex)
                if not np.all(np.isfinite(response)):
                    raise ValueError("model values must be finite")
                if measure == "max_relative_error":
                    values.append(float(np.max(np.abs(response - h) / scale[0])))
                else:
                    weights, norm = scale
                    if norm == 0.0:
                        raise ValueError("relative band error is undefined: reference norm is zero")
                    values.append(band_norm(response - h, weights) / norm)
            coarse, fine = values
            out[measure] = {"coarse": coarse, "fine": fine, "difference": abs(fine - coarse),
                            "resolved": abs(fine - coarse) <= RESOLUTION}
        return out


def verdict(error: dict, level: float) -> str:
    """pass, fail or borderline for one measure at one accuracy level (section 6)."""
    if error["fine"] + error["difference"] <= level:
        return "pass"
    if error["fine"] - error["difference"] > level:
        return "fail"
    return "borderline"


def run_case(case: dict, tissue: gabriel.Tissue, evaluator: Evaluator, node_sets: dict) -> dict:
    """Fit one case and record everything needed for the tables; never raises for numerics."""
    procedure = case["procedure"]
    family = "log" if procedure.startswith(("vf_log", "fixed_log")) else "band"
    f, w = node_sets[case["nodes"]][family]
    s = gabriel.laplace_variable(f)
    h = gabriel.strictly_proper_part(tissue, s)
    poles0 = log_poles(*case["start_hz"], case["r"])
    started = time.perf_counter()
    record = dict(case, id=case_id(case))
    if procedure in VF_PROCEDURES:
        result = vector_fit(s, h, w, poles0, **z2.CONTROLS)
        fit = result.final_fit
        conditions = [item.step.condition for item in result.history]
        record |= {"status": result.stop_reason, "iterations": len(result.history),
                   "message": result.message, "cycle_period": result.cycle_period,
                   "final_fit_error": result.final_fit_error,
                   "q_at_stop": (result.history[-1].denominator_deviation
                                 if result.history else None)}
        loop_ok = result.stop_reason in SETTLED
    else:
        try:
            fit = fit_residues(f, h, poles0, w)
            record["status"] = "fixed_poles"
        except (FloatingPointError, np.linalg.LinAlgError) as error:
            fit = None
            record |= {"status": "numerical_failure", "message": str(error)}
        conditions = []
        loop_ok = fit is not None
    record["seconds"] = time.perf_counter() - started
    if fit is None:
        record |= {"candidate": None, "eligible_general": False, "eligible_debye": False}
        return record
    model = fit.model
    conditions.append(fit.condition)
    candidate = {
        "rank": fit.rank, "full_rank": fit.rank == model.order, "final_condition": fit.condition,
        "max_condition": max(conditions), "stable": model.is_stable(), "real": model.is_real(),
        "debye": model.is_debye(), "zero_residue": bool(np.any(model.residues == 0)),
        "complex_poles": int(np.count_nonzero(model.poles.imag)),
        "poles": model.poles, "residues": model.residues,
    }
    candidate["ill_conditioned"] = not candidate["max_condition"] <= z2.ILL_CONDITIONED
    try:
        candidate["errors"] = evaluator.errors(model)
    except ValueError as error:
        candidate["errors"] = None
        candidate["error_evaluation_failed"] = str(error)
    general = bool(loop_ok and candidate["full_rank"] and not candidate["ill_conditioned"]
                   and candidate["stable"] and candidate["real"]
                   and candidate["errors"] is not None)
    record |= {"candidate": candidate, "eligible_general": general,
               "eligible_debye": general and candidate["debye"]}
    if candidate["errors"] is not None:
        record["verdicts"] = {m: {str(level): verdict(candidate["errors"][m], level)
                                  for level in LEVELS} for m in MEASURES}
    return record


def smallest_orders(records: list[dict]) -> list[dict]:
    """Smallest passing r per (experiment, group, procedure, N, start, table, measure, level)."""
    keyed: dict[tuple, list[dict]] = {}
    for rec in records:
        key = (rec["experiment"], rec["group"], rec["procedure"], rec["nodes"],
               tuple(rec["start_hz"]))
        keyed.setdefault(key, []).append(rec)
    rows = []
    for key, recs in keyed.items():
        recs = sorted(recs, key=lambda rec: rec["r"])
        for table in ("debye", "general"):
            for measure in MEASURES:
                for level in LEVELS:
                    passing, borderline = None, []
                    for rec in recs:
                        if not rec[f"eligible_{table}"]:
                            continue
                        v = rec["verdicts"][measure][str(level)]
                        if v == "pass":
                            passing = rec["r"]
                            break
                        if v == "borderline":
                            borderline.append(rec["r"])
                    rows.append(dict(
                        experiment=key[0], group=key[1], procedure=key[2], nodes=key[3],
                        start_hz=f"{key[4][0]:.0e}-{key[4][1]:.0e}", table=table,
                        measure=measure, level=level, min_r=passing,
                        borderline_below=" ".join(map(str, borderline)),
                        orders_tested=f"{recs[0]['r']}-{recs[-1]['r']} ({len(recs)})"))
    return rows


def compare(rows: list[dict], experiment: str, table: str, measure: str, level: float,
            first: str, second: str) -> dict:
    """Pairwise outcome over groups: first smaller, tie, second smaller, one-sided, neither."""
    pick = {(row["group"], row["procedure"]): row["min_r"] for row in rows
            if row["experiment"] == experiment and row["table"] == table
            and row["measure"] == measure and row["level"] == level and row["nodes"] == 240}
    groups = sorted({g for g, _ in pick})
    counts = dict.fromkeys(("first_smaller", "tie", "second_smaller", "first_only",
                            "second_only", "neither"), 0)
    differences = []
    for group in groups:
        a, b = pick.get((group, first)), pick.get((group, second))
        if a is not None and b is not None:
            counts["first_smaller" if a < b else "second_smaller" if b < a else "tie"] += 1
            differences.append(a - b)
        else:
            counts["first_only" if a is not None else "second_only" if b is not None
                   else "neither"] += 1
    return dict(groups=len(groups), counts=counts,
                median_difference=statistics.median(differences) if differences else None)


def report(records: list[dict], rows: list[dict], groups: dict, skipped: list[str]) -> dict:
    """Print the summary and hypotheses; return the outcome recorded in provenance."""
    print("B6 min_order: settings of ADR-0008 with the A7 addendum")
    print(f"groups: {len(groups['dev'])} development ({sum(map(len, groups['dev'].values()))}"
          f" names), {len(groups['final'])} final ({sum(map(len, groups['final'].values()))}"
          f" names); without relative error (H = 0): {', '.join(skipped) or '-'}")
    status: dict[str, int] = {}
    for rec in records:
        status[f"{rec['procedure']}: {rec['status']}"] = status.get(
            f"{rec['procedure']}: {rec['status']}", 0) + 1
    print("\ncase statuses: " + "; ".join(f"{k} {v}" for k, v in sorted(status.items())))
    unresolved = sum(1 for rec in records if rec.get("candidate") and rec["candidate"]["errors"]
                     and not all(e["resolved"] for e in rec["candidate"]["errors"].values()))
    borderline = sum(1 for row in rows if row["borderline_below"])
    seconds = sum(rec["seconds"] for rec in records if "reused_from" not in rec)
    print(f"cases {len(records)}; error estimates with |fine - coarse| > {RESOLUTION:g}: "
          f"{unresolved}; table cells with a borderline smaller order: {borderline}; "
          f"fit time of computed cases {seconds:.0f} s")
    for experiment in sorted({row["experiment"] for row in rows}):
        print(f"\n== {experiment}: smallest passing r (Debye table / general table), "
              "max relative error and band error")
        procedures = [p for p in (*VF_PROCEDURES, *FIXED_OF.values(), "fixed_log_wide",
                                  "fixed_band_wide")
                      if any(row["procedure"] == p and row["experiment"] == experiment
                             for row in rows)]
        wide = f"{WIDE_START_HZ[0]:.0e}-{WIDE_START_HZ[1]:.0e}"
        settings = sorted({(row["nodes"], row["start_hz"]) for row in rows
                           if row["experiment"] == experiment
                           and not row["procedure"].endswith("_wide")})
        for n, start in settings:
            note = f" (*_wide: {wide} Hz)" if any(p.endswith("_wide") for p in procedures) else ""
            print(f"-- N = {n}, start {start} Hz{note}; cell: d/g for 5 %, 1 %, 0.1 % "
                  "(- none among the orders tested)")
            for measure in MEASURES:
                print(f"   {measure}")
                print(f"   {'group':<16}" + "".join(f"{p:>26}" for p in procedures))
                for group in sorted({row["group"] for row in rows
                                     if row["experiment"] == experiment}):
                    cells = []
                    for p in procedures:
                        parts = []
                        for level in LEVELS:
                            got = {row["table"]: row["min_r"] for row in rows
                                   if row["experiment"] == experiment and row["group"] == group
                                   and row["procedure"] == p and row["measure"] == measure
                                   and row["level"] == level and row["nodes"] == n
                                   and row["start_hz"] == (wide if p.endswith("_wide")
                                                           else start)}
                            if not got:
                                continue
                            parts.append("/".join("-" if got[t] is None else str(got[t])
                                                  for t in ("debye", "general")))
                        cells.append(" ".join(parts) if parts else "")
                    print(f"   {group:<16}" + "".join(f"{c:>26}" for c in cells))
    hypotheses = {}
    for experiment in ("final_base", "dev_base"):
        if not any(row["experiment"] == experiment for row in rows):
            continue
        print(f"\n== hypotheses on {experiment} (counts over groups; one-sided passes listed "
              "separately)")
        for table in ("debye", "general"):
            for measure in MEASURES:
                for level in LEVELS:
                    for vf, fixed in (("vf_log", "fixed_log"), ("quadvf_band", "fixed_band"),
                                      ("vf_log", "fixed_log_wide"),
                                      ("quadvf_band", "fixed_band_wide")):
                        out = compare(rows, experiment, table, measure, level, vf, fixed)
                        c = out["counts"]
                        supported = c["first_smaller"] + c["first_only"] > out["groups"] / 2
                        hypotheses[f"{experiment}|H1|{table}|{measure}|{level}|{vf}|{fixed}"] = (
                            out | {"vf_smaller_in_more_than_half": supported})
                        print(f"   H1 {table:7} {measure:18} {level:<6} {vf:>11} vs "
                              f"{fixed:<16} VF smaller {c['first_smaller']}, tie {c['tie']}, "
                              f"fixed smaller {c['second_smaller']}, VF only {c['first_only']}, "
                              f"fixed only {c['second_only']}, neither {c['neither']} "
                              f"-> {'more than half' if supported else 'not more than half'}")
        for measure in MEASURES:
            for level in LEVELS:
                out = compare(rows, experiment, "debye", measure, level, "quadvf_band",
                              "vf_log")
                hypotheses[f"{experiment}|H2|debye|{measure}|{level}"] = out
                c = out["counts"]
                paired = c["first_smaller"] + c["tie"] + c["second_smaller"]
                print(f"   H2 debye {measure:18} {level:<6} median r(quadvf_band) - r(vf_log) "
                      f"= {out['median_difference']} over {paired} paired groups; quadvf only "
                      f"{c['first_only']}, vf_log only {c['second_only']}, "
                      f"neither {c['neither']}")
    return {"cases": len(records), "statuses": status, "unresolved_error_estimates": unresolved,
            "borderline_cells": borderline, "fit_seconds": seconds, "hypotheses": hypotheses}


def alpha_table(rows: list[dict], tissues: dict, groups: dict) -> None:
    """Exploratory H3: largest active alpha against the smallest Debye vf_log order at 1 %."""
    print("\n== H3 (exploratory): largest active alpha and smallest Debye r at 1 % "
          "(max relative error)")
    for experiment, kind in (("final_base", "final"), ("dev_base", "dev")):
        for group, names in groups[kind].items():
            got = [row["min_r"] for row in rows if row["experiment"] == experiment
                   and row["group"] == group and row["procedure"] == "vf_log"
                   and row["table"] == "debye" and row["measure"] == "max_relative_error"
                   and row["level"] == 0.01]
            if not got:
                continue
            tissue = tissues[names[0]]
            alpha = max(a for d, a in zip(tissue.delta_eps, tissue.alpha, strict=True) if d > 0)
            print(f"   {experiment:<11}{group:<28} alpha_max {alpha:<5} vf_log r "
                  f"{'-' if got[0] is None else got[0]}")


def settings_identity(settings: dict, csv_sha: str) -> str:
    """Hash of everything that determines a case result; resumed cases must share it."""
    fixed = {k: v for k, v in settings.items() if k not in ("experiments", "resume_from")}
    text = json.dumps(provenance.to_jsonable(fixed | {"input_sha256": csv_sha}), sort_keys=True)
    return hashlib.sha256(text.encode()).hexdigest()


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    parser.add_argument("--csv", type=Path, default=z2.CSV)
    parser.add_argument("--runs-dir", type=Path, default=provenance.RUNS_DIR)
    parser.add_argument("--experiments", nargs="+", default=list(DEV_EXPERIMENTS),
                        choices=list(EXPERIMENTS))
    parser.add_argument("--orders", type=int, nargs="+",
                        help="restrict the orders (tests only; recorded in the settings)")
    parser.add_argument("--resume-from", type=Path,
                        help="earlier run directory whose finished cases are reused")
    args = parser.parse_args(argv)
    if not args.csv.is_file():
        print(f"{args.csv} is missing; run uv run python data/fetch_gabriel.py", file=sys.stderr)
        return 1
    table = gabriel.read_csv(args.csv)
    tissues = {t.name: t for t in table}
    dev, final, skipped = parameter_groups(table)
    groups = {"dev": dev, "final": final}
    orders = tuple(sorted(set(args.orders))) if args.orders else None
    cases = case_plan(args.experiments, dev, final, orders)
    settings = {
        "purpose": "B6 smallest found order (ADR-0008 with the A7 addendum)",
        "experiments": args.experiments, "orders_restricted_to": orders,
        "groups": groups, "without_relative_error": skipped, "band_hz": z2.BAND_HZ,
        "experiment_specs": EXPERIMENTS, "wide_fixed_start_hz": WIDE_START_HZ,
        "controls": z2.CONTROLS, "ill_conditioned_above": z2.ILL_CONDITIONED,
        "levels": LEVELS, "grid_cells": GRID_CELLS, "band_norm_nodes": BAND_NODES,
        "resolution": RESOLUTION, "solver": "numpy.linalg.lstsq", "rcond": None, "seed": None,
        "resume_from": str(args.resume_from) if args.resume_from else None,
    }
    identity = settings_identity(settings, provenance.sha256(args.csv))
    reusable = {}
    if args.resume_from:
        for path in sorted((args.resume_from / "cases").glob("*.json")):
            old = json.loads(path.read_text(encoding="utf-8"))
            if old["settings_identity"] != identity:
                parser.error(f"{path} was computed with other settings or input")
            reusable[old["id"]] = old
        previous_run = json.loads((args.resume_from / "provenance.json").read_text(
            encoding="utf-8"))["run_id"]
    with provenance.run("min_order", settings=settings | {"settings_identity": identity},
                        inputs=[args.csv], runs_dir=args.runs_dir) as record:
        (record.dir / "cases").mkdir()
        grids = tuple(z2.control_grid(*z2.BAND_HZ, cells) for cells in GRID_CELLS)
        bands = tuple(band_nodes(*z2.BAND_HZ, n) for n in BAND_NODES)
        node_sets = {n: nodes(n) for n in sorted({c["nodes"] for c in cases})}
        evaluators: dict[str, Evaluator] = {}
        records = []
        for case in cases:
            kind = "dev" if case["experiment"].startswith("dev") else "final"
            names = groups[kind][case["group"]]
            identifier = case_id(case)
            if identifier in reusable:
                rec = reusable[identifier] | {"reused_from": previous_run}
            else:
                if case["group"] not in evaluators:
                    evaluators[case["group"]] = Evaluator(tissues[names[0]], grids, bands)
                rec = run_case(case, tissues[names[0]], evaluators[case["group"]], node_sets)
                rec["settings_identity"] = identity
            rec["names"] = names
            (record.dir / "cases" / f"{identifier}.json").write_text(
                json.dumps(provenance.to_jsonable(rec), indent=1, allow_nan=False) + "\n",
                encoding="utf-8")
            records.append(json.loads(json.dumps(provenance.to_jsonable(rec))))
        rows = smallest_orders(records)
        with open(record.dir / "min_order.csv", "w", newline="", encoding="utf-8") as handle:
            writer = csv.DictWriter(handle, fieldnames=list(rows[0]) if rows else ["empty"],
                                    lineterminator="\n")
            writer.writeheader()
            writer.writerows(rows)
        text = io.StringIO()
        with contextlib.redirect_stdout(text):
            outcome = report(records, rows, groups, skipped)
            alpha_table(rows, tissues, groups)
        (record.dir / "min_order.txt").write_text(text.getvalue(), encoding="utf-8")
        record.update(summary=outcome, artifacts=["cases/", "min_order.csv", "min_order.txt"],
                      reused_cases=sum("reused_from" in rec for rec in records))
    print(text.getvalue(), end="")
    print(f"run {record.run_id} -> {record.dir}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
