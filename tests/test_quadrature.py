"""Checks of the quadrature rules against integrals known from the derivation B2.

Expected values come from docs/izvodi/b2-h2-kvadratura.md, not from the code under test:
section 1.4 (norm of 1/(s+a)), sections 4.3-4.5 (rule (3.4) of L1 is exact for L = a),
section 6.2 (integral of 1/(s+a) on a band via arctan) and section 6.3 (convergence).
"""
import itertools
import math

import numpy as np
import pytest
from scipy.integrate import quad

from vfdebye import gabriel
from vfdebye.quadrature import axis_nodes, band_nodes, band_norm

# Muscle parameters from ADR-0004 (tau columns in ps, ns, us, ms as in the Gabriel table).
MUSCLE = [4, 0.2, 50, 7.234, 0.1, 7000, 353.68, 0.1, 1.2e6, 318.31, 0.1, 2.5e7, 2.274, 0]


def one_pole(f, a):
    """G(s) = 1/(s + a) at s = 2j*pi*f, a in rad/s."""
    return 1.0 / (2j * math.pi * np.asarray(f) + a)


def exact_band_norm_squared(a, f_min, f_max):
    """(1/pi) * integral_{omega_1}^{omega_2} d omega / (omega^2 + a^2), derivation section 6.2."""
    w1, w2 = 2 * math.pi * f_min, 2 * math.pi * f_max
    return (math.atan(w2 / a) - math.atan(w1 / a)) / (math.pi * a)


# --- band_nodes ------------------------------------------------------------------------------


def test_band_nodes_lie_inside_the_band_in_increasing_order_with_positive_weights():
    f, w = band_nodes(1e7, 1e10, 40)
    assert f.shape == w.shape == (40,)
    assert np.all((f > 1e7) & (f < 1e10))
    assert np.all(np.diff(f) > 0)
    assert np.all(w > 0)


def test_band_weights_are_gauss_legendre_weights_times_omega():
    # Derivation section 6.3: w_j = (1/pi) * (b - a)/2 * g_j * omega_j, a = ln omega_1,
    # b = ln omega_2. The factor omega_j makes higher nodes count for a wider piece of the
    # axis (section 3.4); g_j itself is largest in the middle of [-1, 1].
    f, w = band_nodes(1e7, 1e10, 41)
    _, g = np.polynomial.legendre.leggauss(41)
    omega = 2 * math.pi * f
    half = 0.5 * (math.log(2 * math.pi * 1e10) - math.log(2 * math.pi * 1e7))
    assert w == pytest.approx(half * g * omega / math.pi, rel=1e-13)
    assert w[-1] > 100 * w[0]


@pytest.mark.parametrize(
    ("a", "f_min", "f_max"),
    [
        (3.0, 0.5 / (2 * math.pi), 40.0 / (2 * math.pi)),  # omega in [0.5, 40]
        (2 * math.pi * 1e8, 1e7, 1e10),  # pole at 100 MHz inside the band of ADR-0004
        (2 * math.pi * 1e5, 1e7, 1e10),  # pole far below the band
    ],
)
def test_band_norm_of_one_pole_matches_the_arctan_formula(a, f_min, f_max):
    f, w = band_nodes(f_min, f_max, 60)
    exact = exact_band_norm_squared(a, f_min, f_max)
    assert band_norm(one_pole(f, a), w) ** 2 == pytest.approx(exact, rel=1e-12)


def test_band_quadrature_converges_with_the_number_of_nodes():
    a, f_min, f_max = 2 * math.pi * 1e8, 1e7, 1e10
    exact = exact_band_norm_squared(a, f_min, f_max)
    errors = []
    for n in (5, 10, 20, 40):
        f, w = band_nodes(f_min, f_max, n)
        errors.append(abs(band_norm(one_pole(f, a), w) ** 2 - exact) / exact)
    assert all(later < earlier for earlier, later in itertools.pairwise(errors))
    assert errors[-1] < 1e-12


def test_band_weights_sum_to_the_band_width_over_pi():
    # Integral of |G|^2 = 1 is (omega_2 - omega_1)/pi; not exact for fixed n (e^u is not a
    # polynomial in u), so this is a convergence check.
    w1, w2 = 2 * math.pi * 1e7, 2 * math.pi * 1e10
    exact = (w2 - w1) / math.pi
    _, w5 = band_nodes(1e7, 1e10, 5)
    _, w20 = band_nodes(1e7, 1e10, 20)
    assert abs(w5.sum() - exact) / exact < 1e-4
    assert w20.sum() == pytest.approx(exact, rel=1e-13)


def test_band_norm_of_muscle_matches_an_independent_integral():
    # Reference: adaptive quadrature in u = ln(omega), independent of Gauss-Legendre.
    muscle = gabriel.tissue_from_row("Muscle", MUSCLE)
    w1, w2 = 2 * math.pi * 1e7, 2 * math.pi * 1e10

    def integrand(u):
        omega = math.exp(u)
        return abs(complex(gabriel.strictly_proper_part(muscle, 1j * omega))) ** 2 * omega

    reference, _ = quad(integrand, math.log(w1), math.log(w2), epsabs=0, epsrel=1e-13, limit=200)
    reference /= math.pi
    f, w = band_nodes(1e7, 1e10, 40)
    values = gabriel.strictly_proper_part(muscle, gabriel.laplace_variable(f))
    assert band_norm(values, w) ** 2 == pytest.approx(reference, rel=1e-12)


# --- axis_nodes ------------------------------------------------------------------------------


@pytest.mark.parametrize("n", [1, 2, 5, 20])
@pytest.mark.parametrize("a", [0.5, 2.0, 2 * math.pi * 1e9])
def test_axis_rule_is_exact_for_one_pole_when_L_equals_a(a, n):
    # Derivation 4.5: with L = a the integrand in t is the constant 1/a; M_+ = M_- = 1.
    rule = axis_nodes(a / (2 * math.pi), n)
    values = np.append(one_pole(rule.f, a), [1.0, 1.0])
    weights = np.append(rule.weights, [rule.edge_weight, rule.edge_weight])
    assert band_norm(values, weights) ** 2 == pytest.approx(1 / (2 * a), rel=1e-13)


def test_axis_rule_converges_when_L_misses_the_pole():
    a = 1.0
    errors = []
    for n in (10, 20, 40):
        rule = axis_nodes(0.1 * a / (2 * math.pi), n)
        total = np.sum(rule.weights * np.abs(one_pole(rule.f, a)) ** 2) + 2 * rule.edge_weight
        errors.append(abs(total - 1 / (2 * a)) * 2 * a)
    assert all(later < earlier for earlier, later in itertools.pairwise(errors))
    assert errors[-1] < 1e-3  # derivation table 4.5: 5.3e-4


@pytest.mark.parametrize("n", [6, 7, 20])
def test_axis_nodes_are_symmetric_and_half_lie_below_L(n):
    # Derivation 4.5: t = pi/4 gives omega = L and the t_j are equispaced, so about half of the
    # positive nodes lie below L: the counts differ by at most one (a node exactly at L,
    # when (n + 1) is divisible by 4, is not counted).
    rule = axis_nodes(2.0, n)
    assert rule.f == pytest.approx(-rule.f[::-1], abs=1e-12)
    assert rule.weights == pytest.approx(rule.weights[::-1], rel=1e-12)
    positive = rule.f[rule.f > 1e-12]
    off_L = positive[np.abs(positive - 2.0) > 1e-9]
    assert abs(int(np.sum(off_L < 2.0)) - int(np.sum(off_L > 2.0))) <= 1


# --- input checks ----------------------------------------------------------------------------


@pytest.mark.parametrize(
    ("f_min", "f_max", "n"),
    [
        (0.0, 1e10, 10),
        (-1e7, 1e10, 10),
        (1e10, 1e7, 10),
        (1e7, 1e7, 10),
        (float("nan"), 1e10, 10),
        (1e7, float("inf"), 10),
        ("abc", 1e10, 10),
        (1e7, 1e10, 0),
        (1e7, 1e10, 2.5),
        (1e7, 1e10, True),
    ],
)
def test_band_nodes_rejects_invalid_input(f_min, f_max, n):
    with pytest.raises(ValueError):
        band_nodes(f_min, f_max, n)


@pytest.mark.parametrize(("L_hz", "n"), [(0.0, 5), (-1.0, 5), (float("nan"), 5), (1.0, 0)])
def test_axis_nodes_rejects_invalid_input(L_hz, n):
    with pytest.raises(ValueError):
        axis_nodes(L_hz, n)


@pytest.mark.parametrize(
    ("values", "weights"),
    [
        ([1.0, 2.0], [1.0]),
        ([], []),
        ([1.0, float("nan")], [1.0, 1.0]),
        ([1.0, 2.0], [1.0, 0.0]),
        ([1.0, 2.0], [1.0, -1.0]),
        ([[1.0, 2.0]], [[1.0, 1.0]]),
    ],
)
def test_band_norm_rejects_invalid_input(values, weights):
    with pytest.raises(ValueError):
        band_norm(values, weights)

