"""Overview of Gabriel's parameters against the provisional band (task A2).

Run from the repository root after data/fetch_gabriel.py:  uv run python experiments/data_checks.py

For every tissue it prints the relaxation frequency 1/(2 pi tau_n) and alpha_n of each present
term, and the largest share max_f |term_n(s)| / |H(s)| of each term on the band. The band is
the provisional 10 MHz-10 GHz from the ADR-0004 addendum of 2026-11-09; Z2 fixes the final one.
Output goes to stdout only; recorded runs need vfdebye.provenance (task A6).
"""
from __future__ import annotations

import argparse
import sys
from pathlib import Path

import numpy as np

from vfdebye import gabriel

ROOT = Path(__file__).resolve().parents[1]
CSV = ROOT / "data" / "processed" / "gabriel_parameters.csv"
BAND_HZ = (1e7, 1e10)
GRID_POINTS = 401


def term_shares(tissue: gabriel.Tissue, s: np.ndarray) -> list[float]:
    """max over s of |term_n(s)| / |H(s)| for each term n (0 for absent terms)."""
    h = np.abs(gabriel.strictly_proper_part(tissue, s))
    shares = []
    for d, t, a in zip(tissue.delta_eps, tissue.tau, tissue.alpha, strict=True):
        term = d / (1 + (s * t) ** (1 - a)) if d > 0 else np.zeros_like(s)
        shares.append(float(np.max(np.abs(term) / h)))
    return shares


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    parser.add_argument("--csv", type=Path, default=CSV)
    args = parser.parse_args(argv)
    if not args.csv.is_file():
        print(f"{args.csv} is missing; run uv run python data/fetch_gabriel.py", file=sys.stderr)
        return 1
    tissues = gabriel.read_csv(args.csv)
    duplicates = {name: group[0] for group in gabriel.duplicate_groups(tissues)
                  for name in group[1:]}
    s = gabriel.laplace_variable(np.geomspace(*BAND_HZ, GRID_POINTS))
    lo, hi = BAND_HZ

    print(f"band {lo:.0e}-{hi:.0e} Hz (provisional), {GRID_POINTS} log-spaced points")
    print(f"{'tissue':<22}{'same as':<16}" + "".join(
        f"{'f' + str(n) + ' Hz':>10}{'a' + str(n):>6}{'share':>7}" for n in range(1, 5)))
    dispersive = [t for t in tissues if t.is_dispersive]
    for tissue in tissues:
        if not tissue.is_dispersive:
            print(f"{tissue.name:<22}{duplicates.get(tissue.name, ''):<16}no dispersion")
            continue
        shares = term_shares(tissue, s)
        cells = []
        for d, t, a, share in zip(tissue.delta_eps, tissue.tau, tissue.alpha, shares, strict=True):
            if d > 0:
                cells.append(f"{1 / (2 * np.pi * t):>10.2e}{a:>6.2f}{share:>7.3f}")
            else:
                cells.append(f"{'-':>10}{'':>6}{'':>7}")
        print(f"{tissue.name:<22}{duplicates.get(tissue.name, ''):<16}" + "".join(cells))

    present = [(t, n) for t in dispersive for n in range(4) if t.delta_eps[n] > 0]
    alphas = [t.alpha[n] for t, n in present]
    taus = [t.tau[n] for t, n in present]
    in_band = [t.name for t in dispersive
               if any(lo <= 1 / (2 * np.pi * t.tau[n]) <= hi
                      for n in range(4) if t.delta_eps[n] > 0)]
    print()
    print(f"rows {len(tissues)}, dispersive {len(dispersive)}, "
          f"distinct dispersive parameter sets {len({t.parameters for t in dispersive})}")
    print(f"present terms {len(present)}: alpha in [{min(alphas)}, {max(alphas)}], "
          f"tau in [{min(taus):.3e}, {max(taus):.3e}] s")
    print(f"tissues with a relaxation frequency inside the band: {len(in_band)}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
