"""Reference method: fixed log-spaced real poles and least-squares residues (task B4).

METHODOLOGY section 6: the poles -1/tau_j are fixed and spaced logarithmically, and only the
residues are computed, by a linear least-squares problem (L1 (1.1) with the poles held fixed).
This isolates the effect of moving the poles in VF and QuadVF.

The pole range [f_min, f_max] is a parameter and need not be the band: tissues have relaxations
far below the band whose tails act inside it, and the range changes the order needed a lot.
The range is a decision for the experiment plan (Z2), taken on a development subset before the
final runs, not on the tissues used for evaluation (AGENTS.md, rule 7).

The poles are real, so the residues are required to be real as well, which keeps the model real:
the real and imaginary parts of C phi ~ h are stacked, which is the same as fitting the
conjugate samples at negative frequencies too. Weights multiply the rows as rho_k = sqrt(w_k),
the same convention as for QuadVF (vfdebye.quadrature).

Frequencies are f in Hz, s = 2j*pi*f; poles are in rad/s (docs/plan/PODJELA.md).
"""
from __future__ import annotations

import math
from dataclasses import dataclass

import numpy as np

from vfdebye import gabriel
from vfdebye.vf import PoleResidueModel


def log_poles(f_min: float, f_max: float, r: int) -> np.ndarray:
    """r real poles -2*pi*f_j in rad/s, f_j log-spaced over [f_min, f_max] Hz; r = 1: midpoint."""
    if not (math.isfinite(f_min) and math.isfinite(f_max) and 0 < f_min < f_max):
        raise ValueError(f"need finite 0 < f_min < f_max, got {f_min} and {f_max}")
    if isinstance(r, bool) or not isinstance(r, (int, np.integer)) or r < 1:
        raise ValueError(f"r must be a positive integer, got {r!r}")
    if r == 1:
        f = np.array([math.sqrt(f_min * f_max)])
    else:
        f = np.geomspace(f_min, f_max, int(r))
    return -2.0 * math.pi * f


@dataclass(frozen=True, eq=False)
class BaselineFit:
    """Result of fit_residues, with what must be reported alongside it (AGENTS.md, rule 4)."""

    model: PoleResidueModel
    rank: int  # numerical rank of the stacked least-squares matrix
    condition: float  # 2-norm condition number of that matrix

    @property
    def positive_residues(self) -> bool:
        """All residues > 0, i.e. every term is a physical Debye term with delta_eps > 0."""
        return bool(np.all(self.model.residues.real > 0))


def fit_residues(f: object, h: object, poles: object, weights: object = None) -> BaselineFit:
    """Real residues phi minimising sum_k w_k |sum_j phi_j / (s_k - poles_j) - h_k|^2.

    f: nodes in Hz; h: values H(2j*pi*f); poles: distinct real negative poles in rad/s;
    weights: positive w_k (default all 1). Needs at least as many nodes as poles.
    """
    s = gabriel.laplace_variable(f)
    h = np.asarray(h, dtype=complex)
    p = np.asarray(poles, dtype=complex)
    if np.any(p.imag != 0):
        raise ValueError("poles must be real")
    p = p.real
    if s.ndim != 1 or h.shape != s.shape:
        raise ValueError(f"f and h must be one-dimensional of equal length, got {s.shape}, "
                         f"{h.shape}")
    if not np.all(np.isfinite(h)):
        raise ValueError("h must be finite")
    if p.ndim != 1 or p.size == 0 or not np.all(np.isfinite(p)) or np.any(p >= 0):
        raise ValueError("poles must be a non-empty list of finite negative real numbers")
    if np.unique(p).size != p.size:
        raise ValueError("poles must be distinct")
    if s.size < p.size:
        raise ValueError(f"{s.size} nodes are fewer than {p.size} poles")
    if weights is None:
        w = np.ones(s.size)
    else:
        w = np.asarray(weights, dtype=complex)
        if np.any(w.imag != 0):
            raise ValueError("weights must be real")
        w = w.real
        if w.shape != s.shape or not np.all(np.isfinite(w)) or np.any(w <= 0):
            raise ValueError("weights must be positive, finite and one per node")

    rho = np.sqrt(w)[:, None]
    c = 1.0 / (s[:, None] - p[None, :])  # Cauchy matrix C_kj = 1/(s_k - lambda_j)
    a = np.vstack([rho * c.real, rho * c.imag])
    b = np.concatenate([rho[:, 0] * h.real, rho[:, 0] * h.imag])
    phi, _, rank, singular = np.linalg.lstsq(a, b, rcond=None)
    condition = float(singular[0] / singular[-1]) if singular[-1] > 0 else math.inf
    return BaselineFit(model=PoleResidueModel(p, phi), rank=int(rank), condition=condition)
