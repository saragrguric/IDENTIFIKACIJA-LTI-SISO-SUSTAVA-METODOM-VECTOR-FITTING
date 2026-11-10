"""Vector fitting (L1, section 2.2) and the objects around it.

This module so far holds the parts of task A4 that do not depend on the pilot code (B1):

- PoleResidueModel: H_r(s) = d + sum_j phi_j / (s - lambda_j), the model object of the shared
  interface in docs/plan/PODJELA.md, evaluated at arbitrary points;
- matching_distance: the optimal matching distance of two pole sets, L1 (4.3);
- detect_period: lagged pole distances for recognising cycling (L1, Example 4.2, Remark 4.3).

The iteration itself, vector_fit(s, h, weights, poles0, ...), follows after B1 (Z0 agreement).
Poles and residues are in the variable s = 2j*pi*f, i.e. in rad/s.
"""
from __future__ import annotations

from collections.abc import Sequence
from dataclasses import dataclass

import numpy as np
from scipy.optimize import linear_sum_assignment
from scipy.sparse import csr_matrix
from scipy.sparse.csgraph import maximum_bipartite_matching


def _complex_vector(name: str, values: object) -> np.ndarray:
    array = np.array(values, dtype=complex)
    if array.ndim != 1:
        raise ValueError(f"{name} must be one-dimensional, got shape {array.shape}")
    if not np.all(np.isfinite(array)):
        raise ValueError(f"{name} must be finite")
    return array


@dataclass(frozen=True, eq=False)
class PoleResidueModel:
    """H_r(s) = d + sum_j residues[j] / (s - poles[j]); strictly proper when d = 0."""

    poles: np.ndarray
    residues: np.ndarray
    d: complex = 0.0

    def __post_init__(self) -> None:
        poles = _complex_vector("poles", self.poles)
        residues = _complex_vector("residues", self.residues)
        if poles.size == 0:
            raise ValueError("a model needs at least one pole")
        if poles.shape != residues.shape:
            raise ValueError(
                f"poles and residues differ in length: {poles.size} != {residues.size}"
            )
        d = complex(self.d)
        if not np.isfinite(d):
            raise ValueError("d must be finite")
        poles.flags.writeable = False
        residues.flags.writeable = False
        object.__setattr__(self, "poles", poles)
        object.__setattr__(self, "residues", residues)
        object.__setattr__(self, "d", d)

    @property
    def order(self) -> int:
        return self.poles.size

    def __call__(self, s: np.ndarray | complex) -> np.ndarray:
        """Evaluate at any finite points s; a point equal to a pole raises ValueError."""
        s = np.asarray(s, dtype=complex)
        if not np.all(np.isfinite(s)):
            raise ValueError("s must be finite")
        diff = s[..., None] - self.poles
        if np.any(diff == 0):
            raise ValueError("an evaluation point coincides with a pole")
        return self.d + np.sum(self.residues / diff, axis=-1)

    def is_stable(self) -> bool:
        """All poles in the open left half-plane (L1, section 1)."""
        return bool(np.all(self.poles.real < 0))

    def is_real(self, rtol: float = 1e-10) -> bool:
        """Real system: H_r(conj s) = conj H_r(s).

        Holds when the poles are closed under conjugation and conjugate poles carry conjugate
        residues (real poles with real residues), and d is real. rtol is relative to the largest
        pole and residue magnitudes; for Im d the threshold is rtol * max(|d|, 1), so it is
        absolute when |d| < 1.
        """
        pole_scale = np.max(np.abs(self.poles))
        residue_scale = max(np.max(np.abs(self.residues)), np.finfo(float).tiny)
        distance, sigma = matching_distance(self.poles, self.poles.conj())
        if distance > rtol * pole_scale:
            return False
        residue_gap = np.max(np.abs(self.residues[sigma] - self.residues.conj()))
        d_gap = abs(self.d.imag)
        return bool(residue_gap <= rtol * residue_scale and d_gap <= rtol * max(abs(self.d), 1.0))


def matching_distance(
    a: Sequence[complex] | np.ndarray,
    b: Sequence[complex] | np.ndarray,
    *,
    relative: bool = False,
) -> tuple[float, np.ndarray]:
    """Optimal matching distance of two pole sets, L1 (4.3).

    Omega = min over permutations sigma of max_j |a_j - b_sigma(j)|, or with relative=True of
    max_j |a_j - b_sigma(j)| / |a_j|. Returns (Omega, sigma) with b[sigma] paired to a; among
    the optimal sigma the one with the smallest sum of distances is returned.

    The absolute distance (4.3) is symmetric; the relative one is not, since it is scaled by a:
    for a = {-1, -100} and b = {-2, -100} it is 1 for (a, b) and 0.5 for (b, a).
    """
    a = _complex_vector("a", a)
    b = _complex_vector("b", b)
    if a.shape != b.shape:
        raise ValueError(f"pole sets differ in size: {a.size} != {b.size}")
    if a.size == 0:
        return 0.0, np.zeros(0, dtype=int)
    cost = np.abs(a[:, None] - b[None, :])
    if relative:
        if np.any(a == 0):
            raise ValueError("relative distance needs nonzero poles in a")
        cost = cost / np.abs(a)[:, None]
    # Bottleneck assignment: the smallest threshold whose graph has a perfect matching.
    levels = np.unique(cost)
    lo, hi = 0, levels.size - 1
    while lo < hi:
        mid = (lo + hi) // 2
        graph = csr_matrix(cost <= levels[mid])
        if np.all(maximum_bipartite_matching(graph, perm_type="column") >= 0):
            hi = mid
        else:
            lo = mid + 1
    omega = float(levels[lo])
    penalty = np.where(cost <= omega, cost, cost.max() * a.size + 1.0)
    rows, sigma = linear_sum_assignment(penalty)
    return omega, sigma[np.argsort(rows)]


def detect_period(
    pole_history: Sequence[np.ndarray],
    *,
    rtol: float,
    max_period: int,
) -> int | None:
    """Smallest lag tau in 1..max_period with relative matching distance between the pole set
    tau steps before the last one and the last one at most rtol; None when there is none.

    The distance is scaled by the earlier set, as ||(lambda^(k) - lambda^(k+tau)) ./
    lambda^(k)||_inf in L1, Fig. 2; the relative distance is not symmetric (matching_distance).
    tau = 1 means the poles have settled; tau = 2 is the cycling of L1, Example 4.2. A
    detected period says only that the iteration repeats, not that the model is good. One
    repetition suffices: for the history [x, y, x] the result is 2, which may be chance. A
    stopping rule built on this may require the period to repeat; that choice is open (Z2).
    """
    if max_period < 1:
        raise ValueError("max_period must be at least 1")
    last = pole_history[-1]
    for tau in range(1, min(max_period, len(pole_history) - 1) + 1):
        omega, _ = matching_distance(pole_history[-1 - tau], last, relative=True)
        if omega <= rtol:
            return tau
    return None
