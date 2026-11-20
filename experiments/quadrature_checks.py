"""Numbers of the derivation B2 recomputed with vfdebye.quadrature (task B3).

Run from the repository root:  uv run python experiments/quadrature_checks.py

Reproduces the tables of docs/izvodi/b2-h2-kvadratura.md:

1. section 4.5: relative error of rule (3.4) of L1 for G = 1/(s + 1) against the exact pi;
2. section 4.6: decades spanned by the positive nodes L cot(j pi / (l + 1));
3. section 6.1: |H| of muscle at a few frequencies and the share of ||H||^2 on the whole axis
   below 1 MHz and on the band; relative error on the whole axis of a model equal to H except
   on the band, where it is zero;
4. section 6.3: share of the top decade of the band in the sum with equal weights on log-spaced
   nodes against the true integral; relative error of Gauss-Legendre and of the trapezoidal rule
   in u = ln(omega).

Muscle uses the parameters quoted in ADR-0004 (Gabriel and Gabriel 1996), so parts 1-4 need no
local table. If the Gabriel table is present (data/fetch_gabriel.py), part 5 repeats parts 2-4 for
every distinct dispersive parameter set and prints the range over all tissues, so that the
arguments for the band and the weights are not based on muscle alone.

Reference integrals use scipy.integrate.quad, independent of the rules tested. The band
is the provisional 10 MHz-10 GHz of the ADR-0004 addendum; Z2 fixes the final one.

Every run is recorded with vfdebye.provenance in results/runs/<run_id>/ (outside Git): the
report is saved there as quadrature_checks.txt next to provenance.json.
"""
from __future__ import annotations

import argparse
import contextlib
import io
import math
import sys
from pathlib import Path

import numpy as np
from scipy.integrate import quad

from vfdebye import gabriel, provenance
from vfdebye.quadrature import axis_nodes, band_nodes, band_norm

ROOT = Path(__file__).resolve().parents[1]
CSV = ROOT / "data" / "processed" / "gabriel_parameters.csv"
BAND_HZ = (1e7, 1e10)
MUSCLE = [4, 0.2, 50, 7.234, 0.1, 7000, 353.68, 0.1, 1.2e6, 318.31, 0.1, 2.5e7, 2.274, 0]
AXIS_L = (0.1, 1.0, 10.0)
AXIS_N = (10, 20, 40)
SPAN_N = (15, 100, 1000, 10_000, 40_000)
SAMPLE_HZ = (1e2, 1e4, 1e6, 1e7, 1e9, 1e10)
EQUAL_WEIGHT_NODES = 40
RULE_N = (10, 20, 40)
ALL_TISSUES_GL_N = 20
WHOLE_AXIS_HZ = (1e-7, 1e15)  # integration range standing in for (0, inf); see check below


def axis_rule_errors() -> dict[str, list[float]]:
    """Section 4.5: |rule - pi| / pi for G = 1/(s + 1), a = 1 rad/s, M_+ = M_- = 1."""
    a = 1.0
    errors = {}
    print("1. rule (3.4) of L1 for G = 1/(s+1): relative error against pi")
    print(f"{'L (rad/s)':>10}" + "".join(f"{'l=' + str(n):>12}" for n in AXIS_N))
    for L in AXIS_L:
        row = []
        for n in AXIS_N:
            rule = axis_nodes(L / (2 * math.pi), n)
            values = np.abs(1 / (2j * math.pi * rule.f + a)) ** 2
            total = np.sum(rule.weights * values) + 2 * rule.edge_weight
            row.append(abs(total - 1 / (2 * a)) * 2 * a)  # normalised: exact is 1/(2a)
        errors[f"L={L}"] = row
        print(f"{L:>10}" + "".join(f"{e:>12.2e}" for e in row))
    return errors


def node_spans() -> dict[int, float]:
    """Section 4.6: log10(largest / smallest positive node) of L cot(j pi / (l + 1))."""
    print("\n2. decades spanned by the positive nodes of (3.4)")
    spans = {}
    for n in SPAN_N:
        f = axis_nodes(1.0, n).f
        positive = f[f > 1e-12]
        spans[n] = float(np.log10(positive.max() / positive.min()))
        print(f"  l = {n:>6}: {spans[n]:.1f} decades")
    return spans


def muscle() -> gabriel.Tissue:
    return gabriel.tissue_from_row("Muscle", MUSCLE)


def integral_over_log_omega(tissue: gabriel.Tissue, f_lo: float, f_hi: float) -> float:
    """integral_{omega_lo}^{omega_hi} |H(i omega)|^2 d omega by adaptive quadrature in ln omega."""

    def integrand(u: float) -> float:
        omega = math.exp(u)
        return abs(complex(gabriel.strictly_proper_part(tissue, 1j * omega))) ** 2 * omega

    edges = np.linspace(math.log(2 * math.pi * f_lo), math.log(2 * math.pi * f_hi), 200)
    return float(sum(quad(integrand, lo, hi, epsabs=0, epsrel=1e-12)[0]
                     for lo, hi in zip(edges[:-1], edges[1:], strict=True)))


def whole_axis_shares(tissue: gabriel.Tissue) -> dict[str, float]:
    """Section 6.1: where the whole-axis norm of muscle lies."""
    print("\n3. muscle: |H| and the whole-axis norm")
    for f in SAMPLE_HZ:
        value = abs(complex(gabriel.strictly_proper_part(tissue, gabriel.laplace_variable(f))))
        print(f"  |H| at {f:.0e} Hz: {value:.3g}")
    total = integral_over_log_omega(tissue, *WHOLE_AXIS_HZ)
    below = integral_over_log_omega(tissue, WHOLE_AXIS_HZ[0], 1e6)
    band = integral_over_log_omega(tissue, *BAND_HZ)
    # Tails outside WHOLE_AXIS_HZ: H is bounded near 0 and decays like omega^-(1-alpha) at inf.
    edge = integral_over_log_omega(tissue, WHOLE_AXIS_HZ[1] / 10, WHOLE_AXIS_HZ[1])
    shares = {"below_1MHz": below / total, "band": band / total,
              "zero_in_band_relative_error": math.sqrt(band / total),
              "last_decade_share": edge / total}
    print(f"  share of ||H||^2 below 1 MHz: {shares['below_1MHz']:.4f}")
    print(f"  share of ||H||^2 on the band: {shares['band']:.2e}")
    print(f"  relative whole-axis error of a model that is zero on the band: "
          f"{shares['zero_in_band_relative_error']:.3f}")
    print(f"  (check of the cut-off: share of the last decade before "
          f"{WHOLE_AXIS_HZ[1]:.0e} Hz is {shares['last_decade_share']:.1e})")
    return shares


def band_rules(tissue: gabriel.Tissue) -> dict[str, object]:
    """Section 6.3: equal weights against the true integral; Gauss-Legendre against trapezoid."""
    lo, hi = BAND_HZ
    print(f"\n4. muscle on the band {lo:.0e}-{hi:.0e} Hz (provisional)")
    reference = integral_over_log_omega(tissue, lo, hi)
    top = integral_over_log_omega(tissue, hi / 10, hi)

    f_log = np.geomspace(lo, hi, EQUAL_WEIGHT_NODES)
    values = np.abs(gabriel.strictly_proper_part(tissue, gabriel.laplace_variable(f_log))) ** 2
    equal_share = float(values[f_log > hi / 10].sum() / values.sum())
    print(f"  top decade, {EQUAL_WEIGHT_NODES} log nodes with equal weights: {equal_share:.3f} "
          f"of the sum; true integral: {top / reference:.3f}")

    a, b = math.log(2 * math.pi * lo), math.log(2 * math.pi * hi)
    errors: dict[str, dict[int, float]] = {"gauss_legendre": {}, "trapezoid": {}}
    print(f"{'N':>6}{'trapezoid in u':>18}{'Gauss-Legendre':>18}")
    for n in RULE_N:
        f, w = band_nodes(lo, hi, n)
        gl = band_norm(gabriel.strictly_proper_part(tissue, gabriel.laplace_variable(f)), w) ** 2
        u = np.linspace(a, b, n)
        omega = np.exp(u)
        step = (b - a) / (n - 1)
        trap_w = np.full(n, step)
        trap_w[[0, -1]] = step / 2
        h = gabriel.strictly_proper_part(tissue, 1j * omega)
        trap = float(np.sum(trap_w * np.abs(h) ** 2 * omega))
        errors["trapezoid"][n] = abs(trap - reference) / reference
        errors["gauss_legendre"][n] = abs(gl * math.pi - reference) / reference
        print(f"{n:>6}{errors['trapezoid'][n]:>18.1e}{errors['gauss_legendre'][n]:>18.1e}")
    return {"top_decade_equal_weights": equal_share, "top_decade_true": top / reference,
            "relative_errors": errors}


def relaxation_spread(tissue: gabriel.Tissue) -> float:
    """Decades between the lowest and highest relaxation frequency 1/(2 pi tau_n) of the terms."""
    taus = [t for d, t in zip(tissue.delta_eps, tissue.tau, strict=True) if d > 0]
    return float(math.log10(max(taus) / min(taus)))


def tissue_figures(tissue: gabriel.Tissue) -> dict[str, float]:
    """Parts 2-4 for one tissue: spread, whole-axis shares, equal weights, Gauss-Legendre."""
    lo, hi = BAND_HZ
    total = integral_over_log_omega(tissue, *WHOLE_AXIS_HZ)
    below = integral_over_log_omega(tissue, WHOLE_AXIS_HZ[0], 1e6)
    band = integral_over_log_omega(tissue, lo, hi)
    top = integral_over_log_omega(tissue, hi / 10, hi)
    f_log = np.geomspace(lo, hi, EQUAL_WEIGHT_NODES)
    values = np.abs(gabriel.strictly_proper_part(tissue, gabriel.laplace_variable(f_log))) ** 2
    f, w = band_nodes(lo, hi, ALL_TISSUES_GL_N)
    gl = band_norm(gabriel.strictly_proper_part(tissue, gabriel.laplace_variable(f)), w) ** 2
    return {
        "relaxation_spread_decades": relaxation_spread(tissue),
        "below_1MHz": below / total,
        "band": band / total,
        "zero_in_band_relative_error": math.sqrt(band / total),
        "top_decade_equal_weights": float(values[f_log > hi / 10].sum() / values.sum()),
        "top_decade_true": top / band,
        "gauss_legendre_error": abs(gl * math.pi - band) / band,
    }


def all_tissues(tissues: list[gabriel.Tissue]) -> dict[str, object]:
    """Part 5: parts 2-4 for every distinct dispersive parameter set of the Gabriel table."""
    duplicates = {name for group in gabriel.duplicate_groups(tissues) for name in group[1:]}
    distinct = [t for t in tissues if t.is_dispersive and t.name not in duplicates]
    print(f"\n5. all {len(distinct)} distinct dispersive parameter sets of the Gabriel table "
          f"(duplicates skipped)")
    print(f"{'tissue':<24}{'spread':>8}{'<1MHz':>8}{'band':>10}{'zero-in-band':>14}"
          f"{'top eq.':>9}{'top true':>10}{'GL N=' + str(ALL_TISSUES_GL_N):>11}")
    rows = {}
    for tissue in distinct:
        r = tissue_figures(tissue)
        rows[tissue.name] = r
        print(f"{tissue.name:<24}{r['relaxation_spread_decades']:>8.1f}{r['below_1MHz']:>8.4f}"
              f"{r['band']:>10.1e}{r['zero_in_band_relative_error']:>14.3f}"
              f"{r['top_decade_equal_weights']:>9.3f}{r['top_decade_true']:>10.3f}"
              f"{r['gauss_legendre_error']:>11.1e}")
    keys = next(iter(rows.values())).keys()
    ranges = {k: (min(r[k] for r in rows.values()), max(r[k] for r in rows.values()))
              for k in keys}
    print("range over all tissues (min, max):")
    for k, (a, b) in ranges.items():
        print(f"  {k}: {a:.3g} .. {b:.3g}")
    return {"tissues": rows, "ranges": ranges, "count": len(distinct)}


def report(tissues: list[gabriel.Tissue] | None) -> dict[str, object]:
    tissue = muscle()
    summary = {
        "axis_rule_errors": axis_rule_errors(),
        "node_span_decades": node_spans(),
        "whole_axis": whole_axis_shares(tissue),
        "band": band_rules(tissue),
    }
    if tissues is None:
        print("\n5. skipped: no local Gabriel table (run uv run python data/fetch_gabriel.py)")
    else:
        summary["all_tissues"] = all_tissues(tissues)
    return summary


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    parser.add_argument("--csv", type=Path, default=CSV)
    parser.add_argument("--runs-dir", type=Path, default=provenance.RUNS_DIR)
    args = parser.parse_args(argv)
    has_table = args.csv.is_file()
    settings = {"band_hz": BAND_HZ, "band_status": "provisional", "muscle": MUSCLE,
                "axis_L_rad_s": AXIS_L, "axis_n": AXIS_N, "span_n": SPAN_N,
                "equal_weight_nodes": EQUAL_WEIGHT_NODES, "rule_n": RULE_N,
                "whole_axis_hz": WHOLE_AXIS_HZ, "all_tissues_gl_n": ALL_TISSUES_GL_N,
                "reference": "scipy.integrate.quad in ln omega"}
    with provenance.run("quadrature_checks", settings=settings,
                        inputs=[args.csv] if has_table else [],
                        runs_dir=args.runs_dir) as record:
        text = io.StringIO()
        with contextlib.redirect_stdout(text):
            summary = report(gabriel.read_csv(args.csv) if has_table else None)
        (record.dir / "quadrature_checks.txt").write_text(text.getvalue(), encoding="utf-8")
        record.update(summary=summary, artifacts=["quadrature_checks.txt"])
    print(text.getvalue(), end="")
    print(f"run {record.run_id} -> {record.dir}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
