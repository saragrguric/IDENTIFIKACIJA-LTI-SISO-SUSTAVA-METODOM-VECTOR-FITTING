"""Sensitivity to N and to the start poles, and LS conditioning (task B7, ADR-0008 section 7).

Run from the repository root, after experiments/min_order.py:

    uv run python experiments/sensitivity.py --dev-run results/runs/<dev run> \
        --final-run results/runs/<final run>

The script fits nothing. It reads the case records written by min_order.py: the development
run (experiments dev_base, dev_nodes and dev_start) and the final run (final_base). It prints

1. nodes: for the orders 4, 8, 16 and 32 of the plan, how the status, the Debye property and the
   verdicts at 5 %, 1 % and 0.1 % change when N = 240 is replaced by 120 or 480, and the largest
   ratio of the fine errors;
2. start: the statuses of each procedure for the three start ranges (primary 10 MHz-10 GHz and
   the two wider ranges of the A7 addendum);
3. conditioning: the largest condition number of the LS matrices of each case (max_condition,
   as recorded by min_order.py) in dev_base and final_base, by procedure and order; the number
   of cases above the ill_conditioned threshold 1e12 or with lost rank; and the condition
   number of the selected models of the Debye table.

Scaling and reordering of the LS rows (L1, section 4.3) are not examined; see the B7 record
docs/izvodi/b7-osjetljivost.md.

Every run is recorded with vfdebye.provenance in results/runs/<run_id>/ (outside Git): the
report is saved there as sensitivity.txt next to provenance.json.
"""
from __future__ import annotations

import argparse
import contextlib
import csv
import io
import json
import math
import statistics
import sys
from collections import Counter, defaultdict
from pathlib import Path

from vfdebye import provenance

PRIMARY = (1e7, 1e10)
LEVELS = ("0.05", "0.01", "0.001")
MEASURES = ("max_relative_error", "band_error")
PROCEDURES = ("fixed_log", "vf_log", "fixed_band", "quadvf_band", "fixed_log_wide",
              "fixed_band_wide")
ORDER_BANDS = ((1, 4), (5, 8), (9, 16), (17, 32))
ILL_CONDITIONED = 1e12


def load_cases(run_dir: Path) -> list[dict]:
    """All case records of one min_order run."""
    return [json.loads(p.read_text(encoding="utf-8"))
            for p in sorted((run_dir / "cases").glob("*.json"))]


def is_primary(case: dict) -> bool:
    return tuple(case["start_hz"]) == PRIMARY


def summary(case: dict) -> dict:
    """Status, Debye property, verdicts and fine errors of one case."""
    cand = case.get("candidate") or {}
    errors = cand.get("errors") or {}
    return {
        "status": case["status"],
        "debye": bool(case.get("eligible_debye")),
        "verdicts": {(m, lv): case["verdicts"][m][lv] if case.get("verdicts") else "fail"
                     for m in MEASURES for lv in LEVELS},
        "fine": {m: errors[m]["fine"] if m in errors else None for m in MEASURES},
    }


def node_changes(cases: list[dict]) -> dict:
    """Compare N = 120 and 480 with N = 240 at the same group, procedure, order and start.

    Returns, per procedure, the number of compared pairs, the pairs whose status, Debye property
    or any verdict differs, and the largest ratio max(e/e240, e240/e) of the fine errors.
    """
    base = {(c["group"], c["procedure"], c["r"]): summary(c) for c in cases
            if c["experiment"] == "dev_base" and c["nodes"] == 240 and is_primary(c)}
    out: dict[str, dict] = defaultdict(lambda: {"pairs": 0, "status": 0, "debye": 0,
                                                "verdict": 0, "ratio": 1.0, "verdict_cases": []})
    for c in cases:
        if c["experiment"] != "dev_nodes":
            continue
        ref = base[(c["group"], c["procedure"], c["r"])]
        now = summary(c)
        row = out[c["procedure"]]
        row["pairs"] += 1
        row["status"] += now["status"] != ref["status"]
        row["debye"] += now["debye"] != ref["debye"]
        changed = [k for k in ref["verdicts"] if now["verdicts"][k] != ref["verdicts"][k]]
        if changed:
            row["verdict"] += 1
            row["verdict_cases"].append((c["group"], c["r"], c["nodes"], changed))
        for m in MEASURES:
            a, b = now["fine"][m], ref["fine"][m]
            if a and b:
                row["ratio"] = max(row["ratio"], a / b, b / a)
    return dict(out)


def start_statuses(cases: list[dict]) -> dict:
    """Status counts per (procedure, start range) on the sensitivity orders, N = 240."""
    orders = {c["r"] for c in cases if c["experiment"] == "dev_start"}
    out: dict[tuple, Counter] = defaultdict(Counter)
    for c in cases:
        primary = c["experiment"] == "dev_base" and is_primary(c) and c["r"] in orders
        if c["experiment"] == "dev_start" or primary:
            key = (c["procedure"], f"{c['start_hz'][0]:.0e}-{c['start_hz'][1]:.0e}")
            out[key][c["status"]] += 1
            out[key]["debye"] += bool(c.get("eligible_debye"))
    return dict(out)


def condition_number(value) -> float:
    """min_order.py stores an infinite condition number (lost rank) as {"float": "inf"}."""
    if isinstance(value, dict):
        return float(value["float"])
    return float(value)


def conditioning(cases: list[dict]) -> dict:
    """Median and largest finite max_condition per (procedure, order band), N = 240.

    Only the base experiments enter (primary start; the *_wide procedures use their own range).

    Also counts, per procedure, the finite values above 1e12 and the infinite ones (lost rank).
    """
    groups: dict[tuple, list[float]] = defaultdict(list)
    above: Counter = Counter()
    infinite: Counter = Counter()
    for c in cases:
        if not c["experiment"].endswith("_base"):
            continue
        cond = condition_number(c["candidate"]["max_condition"])
        if not math.isfinite(cond):
            infinite[c["procedure"]] += 1
            continue
        band = next(b for b in ORDER_BANDS if b[0] <= c["r"] <= b[1])
        groups[(c["procedure"], band)].append(cond)
        above[c["procedure"]] += cond > ILL_CONDITIONED
    return {"bands": {k: (statistics.median(v), max(v), len(v)) for k, v in groups.items()},
            "above": dict(above), "infinite": dict(infinite)}


def selected_conditioning(cases: list[dict], rows: list[dict]) -> dict:
    """Largest condition number of the models chosen in the Debye table (final_base)."""
    by_key = {(c["group"], c["procedure"], c["r"]): c for c in cases
              if c["experiment"] == "final_base" and c["nodes"] == 240 and is_primary(c)}
    out: dict[tuple, list[float]] = defaultdict(list)
    for row in rows:
        if (row["experiment"] != "final_base" or row["table"] != "debye" or not row["min_r"]
                or row["start_hz"] != "1e+07-1e+10"):
            continue
        case = by_key[(row["group"], row["procedure"], int(row["min_r"]))]
        out[(row["procedure"], row["measure"], row["level"])].append(
            condition_number(case["candidate"]["max_condition"]))
    return {k: (statistics.median(v), max(v), len(v)) for k, v in out.items()}


def report(dev: list[dict], final: list[dict], final_rows: list[dict]) -> None:
    print("1. Nodes: N = 120 and 480 against N = 240 (dev groups, orders 4, 8, 16, 32)")
    for proc, row in sorted(node_changes(dev).items()):
        print(f"  {proc:12s} pairs {row['pairs']:3d}  status changed {row['status']:2d}  "
              f"debye changed {row['debye']:2d}  any verdict changed {row['verdict']:2d}  "
              f"largest error ratio {row['ratio']:.3f}")
        for group, r, n, changed in row["verdict_cases"]:
            print(f"    {group}, r = {r}, N = {n}: {', '.join(f'{m} {lv}' for m, lv in changed)}")
    print("\n2. Start poles (dev groups, orders 4, 8, 16, 32, N = 240)")
    for (proc, start), counts in sorted(start_statuses(dev).items()):
        text = ", ".join(f"{k} {v}" for k, v in sorted(counts.items()) if k != "debye")
        print(f"  {proc:12s} {start:13s} {text}; Debye {counts['debye']}")
    print("\n3. Conditioning of the LS matrices (largest per case; median/largest finite)")
    for name, cases in (("dev", dev), ("final", final)):
        result = conditioning(cases)
        print(f"  {name}: finite above {ILL_CONDITIONED:.0e} / infinite (lost rank): "
              + ", ".join(f"{p} {result['above'].get(p, 0)}/{result['infinite'].get(p, 0)}"
                          for p in PROCEDURES))
        for proc in PROCEDURES:
            cells = []
            for band in ORDER_BANDS:
                med, top, _ = result["bands"].get((proc, band), (math.nan, math.nan, 0))
                cells.append(f"r {band[0]}-{band[1]}: {med:.1e}/{top:.1e}")
            print(f"    {proc:15s} " + "  ".join(cells))
    print("\n  Selected Debye models (final_base), median/largest condition number:")
    for (proc, measure, level), (med, top, n) in sorted(
            selected_conditioning(final, final_rows).items()):
        print(f"    {proc:12s} {measure:19s} {float(level):.1%}: {med:.1e}/{top:.1e} ({n})")


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    parser.add_argument("--dev-run", type=Path, required=True)
    parser.add_argument("--final-run", type=Path, required=True)
    parser.add_argument("--runs-dir", type=Path, default=provenance.RUNS_DIR)
    args = parser.parse_args(argv)
    for run_dir in (args.dev_run, args.final_run):
        if not (run_dir / "cases").is_dir():
            print(f"{run_dir} has no cases/; run experiments/min_order.py first", file=sys.stderr)
            return 1
    dev, final = load_cases(args.dev_run), load_cases(args.final_run)
    with open(args.final_run / "min_order.csv", newline="", encoding="utf-8") as handle:
        final_rows = list(csv.DictReader(handle))
    run_ids = {name: json.loads((d / "provenance.json").read_text(encoding="utf-8"))["run_id"]
               for name, d in (("dev", args.dev_run), ("final", args.final_run))}
    settings = {"purpose": "B7 sensitivity and conditioning (ADR-0008 section 7)",
                "source_runs": run_ids, "ill_conditioned_above": ILL_CONDITIONED,
                "order_bands": ORDER_BANDS}
    inputs = [args.dev_run / "min_order.csv", args.final_run / "min_order.csv"]
    with provenance.run("sensitivity", settings=settings, inputs=inputs,
                        runs_dir=args.runs_dir) as record:
        text = io.StringIO()
        with contextlib.redirect_stdout(text):
            report(dev, final, final_rows)
        (record.dir / "sensitivity.txt").write_text(text.getvalue(), encoding="utf-8")
        print(text.getvalue(), end="")
        print(f"\nrun recorded in {record.dir}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
