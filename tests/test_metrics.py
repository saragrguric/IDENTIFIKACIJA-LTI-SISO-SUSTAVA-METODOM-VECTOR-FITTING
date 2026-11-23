"""Checks of the error measures against values known without the code under test.

Expected values: the exact model has zero error, the zero model has band error 1 and pointwise
error |H|/|eps|; the band norm of one Debye term follows from derivation B2, sections 2.4 and 6.2.
"""
import math

import numpy as np
import pytest

from vfdebye import gabriel
from vfdebye.metrics import band_h2_error, control_grid, max_relative_error, min_order
from vfdebye.quadrature import band_nodes, band_norm
from vfdebye.vf import PoleResidueModel

BAND = (1e7, 1e10)
MUSCLE = [4, 0.2, 50, 7.234, 0.1, 7000, 353.68, 0.1, 1.2e6, 318.31, 0.1, 2.5e7, 2.274, 0]
# One Debye term (alpha = 0) with relaxation at about 159 MHz, inside the band.
ONE_DEBYE = [4, 0.2, 60, 1000, 0, 0, 1, 0, 0, 1, 0, 0, 1, 0]


def muscle():
    return gabriel.tissue_from_row("Muscle", MUSCLE)


def exact_model(tissue):
    return lambda s: gabriel.strictly_proper_part(tissue, s)


def zero_model(s):
    return np.zeros_like(np.asarray(s, dtype=complex))


# --- control_grid ----------------------------------------------------------------------------


def test_control_grid_is_log_spaced_and_includes_both_ends():
    f = control_grid(*BAND, n=31)
    assert f[0] == pytest.approx(BAND[0]) and f[-1] == pytest.approx(BAND[1])
    ratios = f[1:] / f[:-1]
    assert ratios == pytest.approx(np.full(30, ratios[0]), rel=1e-12)


@pytest.mark.parametrize(("f_min", "f_max", "n"),
                         [(0, 1e10, 10), (1e10, 1e7, 10), (1e7, 1e10, 1), (1e7, 1e10, True)])
def test_control_grid_rejects_invalid_input(f_min, f_max, n):
    with pytest.raises(ValueError):
        control_grid(f_min, f_max, n)


# --- the two measures ------------------------------------------------------------------------


def test_exact_model_has_zero_error_in_both_measures():
    tissue = muscle()
    assert max_relative_error(tissue, exact_model(tissue), control_grid(*BAND)) == 0.0
    assert band_h2_error(tissue, exact_model(tissue), *BAND) == 0.0


def test_zero_model_has_band_error_one():
    assert band_h2_error(muscle(), zero_model, *BAND) == pytest.approx(1.0, rel=1e-14)


def test_zero_model_pointwise_error_is_max_of_h_over_eps():
    # Independent of the measure: eps_r - eps = -H, so the error is max |H| / |eps|.
    tissue = muscle()
    f = control_grid(*BAND, n=500)
    s = 2j * math.pi * f
    expected = np.max(np.abs(gabriel.strictly_proper_part(tissue, s))
                      / np.abs(gabriel.permittivity(tissue, s)))
    assert max_relative_error(tissue, zero_model, f) == pytest.approx(expected, rel=1e-14)


def test_band_error_of_a_scaled_model_is_the_scale_error():
    # H_r = (1 + c) H gives ||H - H_r|| / ||H|| = |c| exactly, for any quadrature.
    tissue = muscle()
    model = lambda s: 1.01 * gabriel.strictly_proper_part(tissue, s)  # noqa: E731
    assert band_h2_error(tissue, model, *BAND) == pytest.approx(0.01, rel=1e-10)


@pytest.mark.parametrize("measure", ["max_relative_error", "band_h2_error"])
@pytest.mark.parametrize("invalid", ["column", "scalar", "nan", "inf"])
def test_measures_reject_wrong_shape_or_nonfinite_model_values(measure, invalid):
    tissue = muscle()

    def model(s):
        values = gabriel.strictly_proper_part(tissue, s)
        if invalid == "column":
            return values[:, None]
        if invalid == "scalar":
            return 0.0
        return np.full_like(values, math.nan if invalid == "nan" else math.inf)

    with pytest.raises(ValueError):
        if measure == "max_relative_error":
            max_relative_error(tissue, model, control_grid(*BAND, n=20))
        else:
            band_h2_error(tissue, model, *BAND, n=20)


@pytest.mark.parametrize("name", ["Air", "Vacuum"])
def test_band_error_explains_undefined_relative_error_for_zero_reference(name):
    tissue = gabriel.tissue_from_row(name, [1, 0] + [0, 1, 1] * 4)
    assert max_relative_error(tissue, zero_model, control_grid(*BAND, n=20)) == 0.0
    with pytest.raises(ValueError, match="reference.*zero"):
        band_h2_error(tissue, zero_model, *BAND, n=20)


def test_band_norm_of_one_debye_term_matches_the_arctan_formula():
    # Derivation 2.4: d/(1 + s tau) = phi/(s + a) with phi = d/tau, a = 1/tau, and 6.2 gives the
    # band integral, so ||H||^2 = phi^2/(pi a) * (atan(w2/a) - atan(w1/a)). The same function
    # written as one pole has zero error.
    tissue = gabriel.tissue_from_row("Debye", ONE_DEBYE)
    d, tau = tissue.delta_eps[0], tissue.tau[0]
    phi, a = d / tau, 1 / tau
    w1, w2 = 2 * math.pi * BAND[0], 2 * math.pi * BAND[1]
    exact = phi**2 / (math.pi * a) * (math.atan(w2 / a) - math.atan(w1 / a))
    pole_model = PoleResidueModel([-a], [phi])  # the same function written as one pole
    assert band_h2_error(tissue, pole_model, *BAND) == pytest.approx(0.0, abs=1e-14)
    f, w = band_nodes(*BAND, 200)
    norm = band_norm(gabriel.strictly_proper_part(tissue, 2j * math.pi * f), w)
    assert norm**2 == pytest.approx(exact, rel=1e-12)


# --- min_order -------------------------------------------------------------------------------


@pytest.mark.parametrize(("delta", "expected"), [(0.05, 3), (0.01, 4), (0.5, 1), (0.001, None)])
def test_min_order_returns_the_first_order_that_reaches_delta(delta, expected):
    assert min_order([0.5, 0.2, 0.04, 0.009], delta) == expected


def test_min_order_does_not_assume_that_errors_decrease():
    # Order 2 reaches 1 % but order 3 does not: the answer is 2, not "first after the last miss".
    assert min_order([0.3, 0.008, 0.02, 0.001], 0.01) == 2


def test_min_order_never_accepts_a_failed_fit():
    assert min_order([math.nan, math.inf, 0.005], 0.01) == 3
    assert min_order([math.nan, math.nan], 0.01) is None


def test_min_order_never_accepts_negative_infinity():
    assert min_order([-math.inf, math.inf, math.nan, 0.005], 0.01) == 4


@pytest.mark.parametrize("error", [-0.1, -1e-300])
def test_min_order_rejects_finite_negative_errors(error):
    with pytest.raises(ValueError, match="non-negative"):
        min_order([error], 0.01)


@pytest.mark.parametrize("delta", [0.0, -0.01, math.nan, math.inf])
def test_min_order_rejects_invalid_delta(delta):
    with pytest.raises(ValueError):
        min_order([0.1], delta)
