"""Checks of the reference method on models with known poles and residues.

Plan B4: with the exact poles of a rational model the reference method recovers the residues up to
rounding. Expected residues come from derivation B2, section 2.4 (pole -1/tau, residue
delta_eps/tau), not from the code under test.
"""
import math

import numpy as np
import pytest

from vfdebye import gabriel
from vfdebye.baseline import fit_residues, log_poles
from vfdebye.metrics import band_h2_error, control_grid, max_relative_error
from vfdebye.quadrature import band_nodes

BAND = (1e7, 1e10)
# Muscle parameters of ADR-0004 with every alpha set to 0: an exactly rational H of order 4.
DEBYE_MUSCLE = [4, 0.2, 50, 7.234, 0, 7000, 353.68, 0, 1.2e6, 318.31, 0, 2.5e7, 2.274, 0]
# Two Debye terms inside the band (relaxations near 160 MHz and 1.6 GHz).
IN_BAND = [4, 0.2, 40, 100, 0, 30, 1, 0, 0, 1, 0, 0, 1, 0]


def debye(row):
    tissue = gabriel.tissue_from_row("Debye", row)
    poles = np.array([-1 / t for d, t in zip(tissue.delta_eps, tissue.tau, strict=True) if d > 0])
    residues = np.array([d / t for d, t in zip(tissue.delta_eps, tissue.tau, strict=True)
                         if d > 0])
    return tissue, poles, residues


def samples(tissue, n=60):
    f, w = band_nodes(*BAND, n)
    return f, gabriel.strictly_proper_part(tissue, gabriel.laplace_variable(f)), w


# --- log_poles -------------------------------------------------------------------------------


def test_log_poles_are_real_negative_log_spaced_in_the_range():
    p = log_poles(1e6, 1e11, 6)
    f = -p / (2 * math.pi)
    assert p.dtype == float and np.all(p < 0)
    assert f[0] == pytest.approx(1e6) and f[-1] == pytest.approx(1e11)
    assert f[1:] / f[:-1] == pytest.approx(np.full(5, 10.0), rel=1e-12)


def test_one_log_pole_sits_at_the_geometric_midpoint():
    assert log_poles(1e7, 1e9, 1) == pytest.approx([-2 * math.pi * 1e8])


@pytest.mark.parametrize(("f_min", "f_max", "r"),
                         [(0, 1e10, 3), (1e10, 1e7, 3), (1e7, 1e10, 0), (1e7, 1e10, 2.0)])
def test_log_poles_rejects_invalid_input(f_min, f_max, r):
    with pytest.raises(ValueError):
        log_poles(f_min, f_max, r)


# --- fit_residues: recovery of known models --------------------------------------------------


def test_exact_poles_recover_the_residues_of_poles_inside_the_band():
    tissue, poles, residues = debye(IN_BAND)
    f, h, w = samples(tissue)
    fit = fit_residues(f, h, poles, w)
    assert fit.model.residues.real == pytest.approx(residues, rel=1e-12)
    assert np.all(fit.model.residues.imag == 0)
    assert fit.rank == 2 and fit.positive_residues
    assert band_h2_error(tissue, fit.model, *BAND) < 1e-13


def test_exact_poles_recover_debye_muscle_including_poles_far_below_the_band():
    # Poles near 70 Hz and 500 Hz are seen only through their tails in the band, so their
    # residues are determined less accurately (condition number about 4e6), but the model on
    # the band is exact to rounding in both measures.
    tissue, poles, residues = debye(DEBYE_MUSCLE)
    f, h, w = samples(tissue)
    fit = fit_residues(f, h, poles, w)
    assert fit.model.residues.real == pytest.approx(residues, rel=1e-8)
    assert fit.condition > 1e5
    assert band_h2_error(tissue, fit.model, *BAND) < 1e-12
    assert max_relative_error(tissue, fit.model, control_grid(*BAND)) < 1e-12


def test_weights_do_not_change_an_exact_fit():
    tissue, poles, residues = debye(IN_BAND)
    f, h, w = samples(tissue)
    unweighted = fit_residues(f, h, poles)
    weighted = fit_residues(f, h, poles, w)
    assert unweighted.model.residues.real == pytest.approx(residues, rel=1e-12)
    assert weighted.model.residues.real == pytest.approx(residues, rel=1e-12)


def test_residues_are_real_for_a_non_rational_tissue():
    muscle = gabriel.tissue_from_row(
        "Muscle", [4, 0.2, 50, 7.234, 0.1, 7000, 353.68, 0.1, 1.2e6, 318.31, 0.1, 2.5e7, 2.274, 0])
    f, h, w = samples(muscle)
    fit = fit_residues(f, h, log_poles(1e6, 1e11, 8), w)
    assert np.all(fit.model.residues.imag == 0)
    assert fit.model.is_real() and fit.model.is_stable()


def test_a_wider_fit_does_not_get_worse_on_its_own_nodes():
    # Least squares: adding a pole can only lower the weighted residual on the fitting nodes.
    muscle = gabriel.tissue_from_row(
        "Muscle", [4, 0.2, 50, 7.234, 0.1, 7000, 353.68, 0.1, 1.2e6, 318.31, 0.1, 2.5e7, 2.274, 0])
    f, h, w = samples(muscle)
    poles = log_poles(1e6, 1e11, 8)
    s = gabriel.laplace_variable(f)
    small = fit_residues(f, h, poles[:-1], w).model
    large = fit_residues(f, h, poles, w).model
    residual = lambda m: np.sum(w * np.abs(m(s) - h) ** 2)  # noqa: E731
    assert residual(large) <= residual(small)


# --- fit_residues: input checks --------------------------------------------------------------


@pytest.mark.parametrize(
    ("f", "h", "poles", "weights"),
    [
        ([1e7, 1e8], [1.0, 2.0], [-1.0, -1.0], None),  # repeated pole
        ([1e7, 1e8], [1.0, 2.0], [-1.0, 1.0], None),  # unstable pole
        ([1e7, 1e8], [1.0, 2.0], [], None),  # no poles
        ([1e7], [1.0], [-1.0, -2.0], None),  # fewer nodes than poles
        ([1e7, 1e8], [1.0], [-1.0], None),  # length mismatch
        ([1e7, 1e8], [1.0, math.nan], [-1.0], None),  # non-finite data
        ([1e7, 1e8], [1.0, 2.0], [-1.0], [1.0, 0.0]),  # zero weight
        ([-1e7, 1e8], [1.0, 2.0], [-1.0], None),  # negative frequency
    ],
)
def test_fit_residues_rejects_invalid_input(f, h, poles, weights):
    with pytest.raises(ValueError):
        fit_residues(f, h, poles, weights)
