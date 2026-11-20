"""Error measures and the search for the smallest order (task B4).

Two measures, fixed in the ADR-0004 addendum of 2026-11-09 and METHODOLOGY section 6:

- max_relative_error: max_k |eps_r(i omega_k) - eps(i omega_k)| / |eps(i omega_k)| on a dense
  control grid that is not the set of fitting nodes. eps_inf and sigma_i/(s eps0) are known
  exactly, so the numerator is |H_r - H|;
- band_h2_error: ||H - H_r|| / ||H|| on the band, with the quadrature of vfdebye.quadrature on
  more nodes than any fit uses (derivation B2, sections 6.2 and 6.6).

The measures divide by different quantities, so the same level delta does not mean the same in
both; the smallest order is searched for each measure separately and the results are not added.

Frequencies are f in Hz, s = 2j*pi*f (docs/plan/PODJELA.md). A model is any callable that maps an
array of s to H_r(s), e.g. vfdebye.vf.PoleResidueModel.
"""
from __future__ import annotations

import math
from collections.abc import Callable, Sequence

import numpy as np

from vfdebye import gabriel
from vfdebye.quadrature import band_nodes, band_norm

Model = Callable[[np.ndarray], np.ndarray]


def control_grid(f_min: float, f_max: float, n: int = 2000) -> np.ndarray:
    """n log-spaced frequencies in Hz from f_min to f_max, both included."""
    if not (math.isfinite(f_min) and math.isfinite(f_max) and 0 < f_min < f_max):
        raise ValueError(f"need finite 0 < f_min < f_max, got {f_min} and {f_max}")
    if isinstance(n, bool) or not isinstance(n, (int, np.integer)) or n < 2:
        raise ValueError(f"n must be an integer of at least 2, got {n!r}")
    return np.geomspace(f_min, f_max, int(n))


def max_relative_error(tissue: gabriel.Tissue, model: Model, f: np.ndarray) -> float:
    """max over the grid f (Hz) of |H_r(s) - H(s)| / |eps(s)|, s = 2j*pi*f."""
    s = gabriel.laplace_variable(f)
    if s.ndim != 1 or s.size == 0:
        raise ValueError("f must be a non-empty one-dimensional grid")
    h = gabriel.strictly_proper_part(tissue, s)
    eps = gabriel.permittivity(tissue, s)
    return float(np.max(np.abs(np.asarray(model(s)) - h) / np.abs(eps)))


def band_h2_error(tissue: gabriel.Tissue, model: Model, f_min: float, f_max: float,
                  n: int = 200) -> float:
    """||H - H_r|| / ||H|| on [f_min, f_max] with n Gauss-Legendre nodes in ln(omega)."""
    f, w = band_nodes(f_min, f_max, n)
    s = gabriel.laplace_variable(f)
    h = gabriel.strictly_proper_part(tissue, s)
    return band_norm(np.asarray(model(s)) - h, w) / band_norm(h, w)


def min_order(errors: Sequence[float], delta: float) -> int | None:
    """Smallest r with errors[r - 1] <= delta, where errors[r - 1] is the error of order r.

    The errors need not decrease with r (a fit can stop in a worse local minimum), so every order
    is checked in turn; a failed fit may be reported as nan or inf and never satisfies delta.
    Returns None if no order up to len(errors) reaches delta.
    """
    if not (math.isfinite(delta) and delta > 0):
        raise ValueError(f"delta must be positive and finite, got {delta}")
    for r, error in enumerate(errors, start=1):
        if error <= delta:  # False for nan
            return r
    return None
