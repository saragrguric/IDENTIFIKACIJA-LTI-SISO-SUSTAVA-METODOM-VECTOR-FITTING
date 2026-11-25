"""Walkthrough for the joint pass Z1: from Gabriel's table to a VF model of one tissue.

Run from the repository root after data/fetch_gabriel.py:  uv run python experiments/z1_blood.py

It prints, step by step, what thread A explains (table -> H(s) -> VF poles) and what thread B
explains (errors of the model), for one development group (default Blood, ADR-0008):

1. the table row and the relaxation frequency 1/(2 pi tau_n) of every present term;
2. H(s) = eps(s) - eps_inf - sigma_i/(s eps0) at a few frequencies, and eps', eps'';
3. vf_log from log-spaced initial poles over the band: delta_k, q_k, rank, condition and the
   poles as frequencies -lambda/(2 pi) after every LS step;
4. the final model as Debye terms: tau_j = -1/lambda_j, Delta eps_j = phi_j tau_j;
5. the indicative errors of section 6 (as in experiments/convergence.py) for vf_log,
   quadvf_band and both fixed-pole references, and a short order sweep.

Settings are those of the accepted plan with the A7 addendum (ADR-0008); this is a
development group, so nothing here is a final result. The report is saved as z1_blood.txt
next to provenance.json in results/runs/<run_id>/ (outside Git).
"""
from __future__ import annotations

import argparse
import contextlib
import io
import math
import sys
from pathlib import Path

import convergence as z2  # experiments/convergence.py: the ADR-0008 settings and error grid
import numpy as np

from vfdebye import gabriel, provenance
from vfdebye.baseline import fit_residues, log_poles
from vfdebye.quadrature import band_nodes
from vfdebye.vf import vector_fit

SHOW_HZ = (1e7, 1e8, 1e9, 1e10)
SWEEP_ORDERS = tuple(range(1, 13))
WIDE_START_HZ = (1e3, 1e11)  # fixed_*_wide of the ADR-0008 addendum
STATUS_TAGS = {"poles_and_denominator_settled": "S+q", "poles_settled": "S", "cycle": "C",
               "rank_deficient": "R", "max_iterations": "M", "invalid_relocated_poles": "I",
               "numerical_failure": "N", "fixed poles": ""}


def describe_tissue(tissue: gabriel.Tissue) -> None:
    print(f"1. {tissue.name}: eps_inf = {tissue.eps_inf}, sigma_i = {tissue.sigma_i} S/m")
    for n, (d, tau, a) in enumerate(zip(tissue.delta_eps, tissue.tau, tissue.alpha,
                                        strict=True), start=1):
        if d > 0:
            f = 1 / (2 * math.pi * tau)
            where = "in band" if z2.BAND_HZ[0] <= f <= z2.BAND_HZ[1] else (
                "below band" if f < z2.BAND_HZ[0] else "above band")
            print(f"   term {n}: delta_eps = {d:g}, tau = {tau:.4g} s, alpha = {a}, "
                  f"1/(2 pi tau) = {f:.3e} Hz ({where})")


def describe_h(tissue: gabriel.Tissue) -> None:
    f = np.array(SHOW_HZ)
    s = gabriel.laplace_variable(f)
    eps = gabriel.permittivity(tissue, s)
    h = gabriel.strictly_proper_part(tissue, s)
    print("\n2. H(s) = eps(s) - eps_inf - sigma_i/(s eps0), s = 2j pi f")
    print(f"   {'f Hz':>9}{'eps_prime':>12}{'eps_second':>12}{'Re H':>12}{'Im H':>12}"
          f"{'|H|/|eps|':>11}")
    for fk, ek, hk in zip(f, eps, h, strict=True):
        print(f"   {fk:9.0e}{ek.real:12.4g}{-ek.imag:12.4g}{hk.real:12.4g}{hk.imag:12.4g}"
              f"{abs(hk) / abs(ek):11.3f}")


def describe_iterations(result) -> None:
    print("\n3. vf_log iterations (poles shown as -lambda/(2 pi) in Hz, sorted)")
    delta = z2.scaled_moves(result.history)
    for k, (item, d) in enumerate(zip(result.history, delta, strict=True), start=1):
        poles = item.poles_after if item.poles_after is not None else item.poles_before
        shown = " ".join(f"{p:.3e}" for p in np.sort(-poles.real / (2 * math.pi)))
        q = item.denominator_deviation
        print(f"   k={k:3d} delta={d:9.2e} q={'-' if q is None else format(q, '9.2e')} "
              f"rank={item.step.rank:3d} cond={item.step.condition:8.1e}  {shown}")
    print(f"   stop: {result.stop_reason} after {len(result.history)} LS steps")


def describe_model(model) -> None:
    print(f"\n4. final model as Debye terms (is_debye = {model.is_debye()})")
    for pole, residue in sorted(zip(model.poles, model.residues, strict=True),
                                key=lambda pr: -pr[0].real):
        tau = -1 / pole.real
        print(f"   lambda = {pole.real:.6e} rad/s  tau = {tau:.4e} s  "
              f"1/(2 pi tau) = {1 / (2 * math.pi * tau):.3e} Hz  "
              f"delta_eps = {residue.real * tau:.5g}")


def fits(tissue: gabriel.Tissue, nodes: dict, r: int, max_iterations: int) -> dict[str, tuple]:
    """Final residue fits of the four section-4 procedures and the two wide fixed-pole ones."""
    out = {}
    for method, (f, w) in nodes.items():
        s = gabriel.laplace_variable(f)
        h = gabriel.strictly_proper_part(tissue, s)
        result = vector_fit(s, h, w, log_poles(*z2.PRIMARY_START_HZ, r),
                            **(z2.CONTROLS | {"max_iterations": max_iterations}))
        out[method] = (result, result.final_fit, result.stop_reason)
        fixed = "fixed_log" if method == "vf_log" else "fixed_band"
        for name, start in ((fixed, z2.PRIMARY_START_HZ), (f"{fixed}_wide", WIDE_START_HZ)):
            fit = fit_residues(f, h, log_poles(*start, r), w)
            out[name] = (None, fit, "fixed poles")
    return out


def error_row(reference, fit) -> str:
    summary = z2.fit_summary(reference, fit)
    if "max_relative_error" not in summary:
        return f"{'-':>10}{'-':>10}"
    flags = []
    if not summary["full_rank"]:
        flags.append("rank")
    if summary["ill_conditioned"]:
        flags.append("ill")
    if not summary["debye"]:
        flags.append("non-Debye")
    return (f"{summary['max_relative_error']:10.2e}{summary['band_error']:10.2e}  "
            + (",".join(flags) or "ok"))


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    parser.add_argument("--csv", type=Path, default=z2.CSV)
    parser.add_argument("--runs-dir", type=Path, default=provenance.RUNS_DIR)
    parser.add_argument("--tissue", default="Blood")
    parser.add_argument("--order", type=int, default=7)
    parser.add_argument("--sweep", type=int, nargs="*", default=list(SWEEP_ORDERS))
    parser.add_argument("--max-iterations", type=int, default=z2.CONTROLS["max_iterations"])
    args = parser.parse_args(argv)
    if not args.csv.is_file():
        print(f"{args.csv} is missing; run uv run python data/fetch_gabriel.py", file=sys.stderr)
        return 1
    tissues = {t.name: t for t in gabriel.read_csv(args.csv)}
    if args.tissue not in tissues or not tissues[args.tissue].is_dispersive:
        parser.error(f"unknown or non-dispersive tissue: {args.tissue!r}")
    if args.order < 1 or args.max_iterations < 1 or min(args.sweep, default=1) < 1:
        parser.error("orders and --max-iterations must be positive")
    tissue = tissues[args.tissue]
    settings = {
        "purpose": "Z1 walkthrough on a development group (ADR-0008 with the A7 addendum)",
        "tissue": tissue.name, "order": args.order, "sweep_orders": args.sweep,
        "band_hz": z2.BAND_HZ, "nodes": z2.NODES, "start_hz": z2.PRIMARY_START_HZ,
        "wide_fixed_start_hz": WIDE_START_HZ,
        "controls": z2.CONTROLS | {"max_iterations": args.max_iterations},
        "control_grid_cells": z2.GRID_CELLS, "band_norm_nodes": z2.BAND_NORM_NODES,
        "solver": "numpy.linalg.lstsq", "rcond": None, "seed": None,
    }
    with provenance.run("z1_blood", settings=settings, inputs=[args.csv],
                        runs_dir=args.runs_dir) as record:
        reference = z2.Reference(tissue, z2.control_grid(*z2.BAND_HZ, z2.GRID_CELLS),
                                 band_nodes(*z2.BAND_HZ, z2.BAND_NORM_NODES))
        nodes = z2.methods()
        text = io.StringIO()
        with contextlib.redirect_stdout(text):
            describe_tissue(tissue)
            describe_h(tissue)
            main_fits = fits(tissue, nodes, args.order, args.max_iterations)
            vf_result = main_fits["vf_log"][0]
            describe_iterations(vf_result)
            if vf_result.model is not None:
                describe_model(vf_result.model)
            print(f"\n5. indicative errors at r = {args.order} "
                  "(max relative, band; flags: rank, ill, non-Debye)")
            for name, (_, fit, status) in main_fits.items():
                print(f"   {name:17}{status:31}" + (error_row(reference, fit) if fit else "-"))
            print("\n   order sweep, max relative error (status or flags after the value)")
            print(f"   {'r':>3}" + "".join(f"{name:>22}" for name in main_fits))
            for r in args.sweep:
                cells = []
                for _name, (_, fit, status) in fits(tissue, nodes, r, args.max_iterations).items():
                    summary = z2.fit_summary(reference, fit) if fit else {}
                    value = summary.get("max_relative_error")
                    tag = STATUS_TAGS[status] + ("" if summary.get("debye") else "*")
                    cells.append(f"{'-' if value is None else format(value, '.2e')} {tag:>8}")
                print(f"   {r:3d}" + "".join(f"{c:>22}" for c in cells))
            print("   VF status: S+q poles and denominator settled, S poles settled, C cycle, "
                  "R rank deficient, M iteration limit, I invalid poles, N numerical failure;\n"
                  "   * not a Debye model (or no candidate)")
        (record.dir / "z1_blood.txt").write_text(text.getvalue(), encoding="utf-8")
        record.update(stop_reason=vf_result.stop_reason, iterations=len(vf_result.history),
                      artifacts=["z1_blood.txt"])
    print(text.getvalue(), end="")
    print(f"run {record.run_id} -> {record.dir}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
