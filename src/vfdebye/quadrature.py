"""Quadrature nodes and weights for H2 norms (L1, section 3.3; derivation B2).

The derivation is in docs/izvodi/b2-h2-kvadratura.md:

- band_nodes: Gauss-Legendre in u = ln(omega) on the band [f_min, f_max] (our deviation from L1,
  derivation section 6.3);
- axis_nodes: the rule (3.4) of L1 on the whole imaginary axis, i.e. the composite trapezoidal
  rule in t after omega = L cot t (derivation sections 4.2-4.4);
- band_norm: sqrt(sum_j w_j |G_j|^2) from values G_j at the nodes.

Frequencies on the interface are f in Hz, s = 2j*pi*f (docs/plan/PODJELA.md). The weights
include the normalisation of the norm, so that sum_j w_j |G(2j*pi*f_j)|^2 approximates the
squared norm itself:

- band: (1/pi) * integral of |G(i omega)|^2 over omega_1 <= omega <= omega_2, which equals
  (1/(2 pi)) times the integral over both signs of the band for a real system;
- axis: (1/(2 pi)) * integral of |G(i omega)|^2 over the whole real line, as in L1 (3.1).

For vector fitting the row weight is rho_j = sqrt(w_j); a common constant factor in all weights
does not change the least-squares solution.
"""
from __future__ import annotations

import math
from dataclasses import dataclass

import numpy as np


# Control functions for correctness of input values.
def _positive_finite(name: str, value: object) -> float:
    try:
        number = float(value)  # type: ignore[arg-type]
    except (TypeError, ValueError):
        raise ValueError(f"{name} must be a real number, got {value!r}") from None
    if not math.isfinite(number) or number <= 0.0:
        raise ValueError(f"{name} must be positive and finite, got {number}")
    return number


def _node_count(n: object) -> int:
    if isinstance(n, bool) or not isinstance(n, (int, np.integer)):
        raise ValueError(f"n must be an integer, got {n!r}")
    if n < 1:
        raise ValueError(f"n must be at least 1, got {n}")
    return int(n)


def band_nodes(f_min: float, f_max: float, n: int) -> tuple[np.ndarray, np.ndarray]:
    """Nodes f_j (Hz) and weights w_j of Gauss-Legendre in ln(omega) on [f_min, f_max].

    sum_j w_j |G(2j*pi*f_j)|^2 approximates (1/pi) * integral_{omega_1}^{omega_2} |G(i omega)|^2
    d omega with omega_k = 2*pi*f_k (derivation B2, sections 6.2-6.3). The nodes are increasing.
    """
    f_min = _positive_finite("f_min", f_min)
    f_max = _positive_finite("f_max", f_max)
    if not f_min < f_max:
        raise ValueError(f"f_min must be smaller than f_max, got {f_min} and {f_max}")
    n = _node_count(n)

    a = math.log(2.0 * math.pi * f_min)
    b = math.log(2.0 * math.pi * f_max)
    x, g = np.polynomial.legendre.leggauss(n)  # nodes and weights on [-1, 1]
    half = 0.5 * (b - a)
    omega = np.exp(half * x + 0.5 * (a + b))  # omega_j = e^{u_j}
    weights = half * g * omega / math.pi  # du = half dx, d omega = omega du, factor 1/pi
    return omega / (2.0 * math.pi), weights


@dataclass(frozen=True, eq=False)
class AxisRule:
    """Rule (3.4) of L1 on the whole axis, with the normalisation 1/(2 pi) of (3.1).

    ||G||^2 is approximated by sum_j weights[j] |G(2j*pi*f[j])|^2
    + edge_weight * (|M_+[G]|^2 + |M_-[G]|^2), M_pm[G] = lim_{omega -> +-inf} i omega G(i omega).
    """

    f: np.ndarray
    weights: np.ndarray
    edge_weight: float


def axis_nodes(L_hz: float, n: int) -> AxisRule:
    """Nodes omega_j = L cot(j pi / (n + 1)), j = 1..n, of L1 (3.4); L = 2*pi*L_hz in rad/s.

    Half of the positive nodes lie below L_hz. Nodes are returned in decreasing order and
    include negative frequencies (derivation B2, sections 4.2-4.5).
    """
    L = 2.0 * math.pi * _positive_finite("L_hz", L_hz)
    n = _node_count(n)

    t = np.arange(1, n + 1) * math.pi / (n + 1)
    omega = L * np.cos(t) / np.sin(t)
    weights = L / (2.0 * (n + 1) * np.sin(t) ** 2)  # (1/(2 pi)) * L pi / ((n + 1) sin^2 t)
    edge_weight = 1.0 / (4.0 * L * (n + 1))  # (1/(2 pi)) * pi / (2 L (n + 1))
    return AxisRule(f=omega / (2.0 * math.pi), weights=weights, edge_weight=edge_weight)


def band_norm(values: object, weights: object) -> float:
    """sqrt(sum_j weights[j] |values[j]|^2): the norm from values at quadrature nodes."""
    v = np.asarray(values, dtype=complex)
    w = np.asarray(weights, dtype=complex)
    if np.any(w.imag != 0):
        raise ValueError("weights must be real")
    w = w.real
    if v.ndim != 1 or w.ndim != 1:
        raise ValueError(f"values and weights must be one-dimensional, got {v.shape}, {w.shape}")
    if v.size == 0 or v.shape != w.shape:
        raise ValueError(f"values and weights must have the same non-zero length, "
                         f"got {v.size} and {w.size}")
    if not np.all(np.isfinite(v)):
        raise ValueError("values must be finite")
    if not np.all(np.isfinite(w)) or np.any(w <= 0.0):
        raise ValueError("weights must be positive and finite")
    return float(math.sqrt(np.sum(w * np.abs(v) ** 2)))
