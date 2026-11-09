"""Checks of the pole-residue model, the matching distance (4.3) and cycle detection."""
import itertools

import numpy as np
import pytest

from vfdebye import gabriel
from vfdebye.vf import PoleResidueModel, detect_period, matching_distance

RTOL = 1e-12


def brute_force_distance(a, b, relative=False):
    """Definition (4.3) evaluated over every permutation; only for small sets."""
    scale = np.abs(a) if relative else np.ones(len(a))
    return min(
        max(abs(a[j] - b[p[j]]) / scale[j] for j in range(len(a)))
        for p in itertools.permutations(range(len(a)))
    )


def test_model_evaluates_the_pole_residue_sum():
    model = PoleResidueModel([-1.0, -2 + 3j, -2 - 3j], [2.0, 1 - 1j, 1 + 1j], d=0.5)
    s = 1j
    expected = 0.5 + 2 / (1j + 1) + (1 - 1j) / (1j + 2 - 3j) + (1 + 1j) / (1j + 2 + 3j)
    assert model(s) == pytest.approx(expected, rel=RTOL)
    assert model.order == 3
    assert model(np.array([[1j, 2j]])).shape == (1, 2)


def test_debye_sum_is_a_model_with_real_poles_minus_one_over_tau():
    # Muscle row with every alpha_n = 0: d/(1 + s tau) = (d/tau)/(s + 1/tau).
    values = ["4", "0.2", "50", "7.234", "0", "7000", "353.68", "0",
              "1.2e+6", "318.31", "0", "2.5e+7", "2.274", "0"]
    tissue = gabriel.tissue_from_row("synthetic", values)
    tau = np.array(tissue.tau)
    model = PoleResidueModel(-1 / tau, np.array(tissue.delta_eps) / tau)
    s = gabriel.laplace_variable(np.logspace(5, 11, 40))
    assert np.allclose(model(s), gabriel.strictly_proper_part(tissue, s), rtol=1e-10, atol=0)
    assert model.is_stable() and model.is_real()


def test_real_model_has_conjugate_symmetry():
    model = PoleResidueModel([-1.0, -2 + 3j, -2 - 3j], [2.0, 1 - 1j, 1 + 1j])
    s = np.array([0.3 + 2j, 5j, -1 + 0.5j])
    assert np.allclose(model(s.conj()), model(s).conj(), rtol=RTOL, atol=0)


@pytest.mark.parametrize(
    ("poles", "residues", "d", "real"),
    [
        ([-1.0, -5.0], [2.0, 3.0], 0, True),
        ([-1 + 2j, -1 - 2j], [3 + 1j, 3 - 1j], 0, True),
        ([-1 - 2j, -3.0, -1 + 2j], [3 - 1j, 1.0, 3 + 1j], 0, True),
        ([-1 + 2j, -1 - 2j], [3 + 1j, 3 + 1j], 0, False),   # residues not conjugate
        ([-1 + 2j, -1 - 1j], [1.0, 1.0], 0, False),          # poles not conjugate
        ([-1.0], [2 + 1e-3j], 0, False),                    # complex residue at real pole
        ([-1.0], [2.0], 1j, False),                         # complex direct term
    ],
)
def test_realness_check(poles, residues, d, real):
    assert PoleResidueModel(poles, residues, d).is_real() is real


def test_stability_is_the_open_left_half_plane():
    assert PoleResidueModel([-1e-9, -3.0], [1, 1]).is_stable()
    assert not PoleResidueModel([0.0, -3.0], [1, 1]).is_stable()
    assert not PoleResidueModel([2.0, -3.0], [1, 1]).is_stable()


@pytest.mark.parametrize(
    ("poles", "residues", "message"),
    [
        ([-1.0, -2.0], [1.0], "differ in length"),
        ([], [], "at least one pole"),
        ([[-1.0]], [[1.0]], "one-dimensional"),
        ([-1.0, np.nan], [1.0, 1.0], "finite"),
        ([-1.0], [np.inf], "finite"),
    ],
)
def test_invalid_models_raise(poles, residues, message):
    with pytest.raises(ValueError, match=message):
        PoleResidueModel(poles, residues)


def test_evaluation_at_a_pole_raises_and_arrays_are_read_only():
    model = PoleResidueModel([-1.0], [1.0])
    with pytest.raises(ValueError, match="coincides with a pole"):
        model(np.array([0.0, -1.0]))
    with pytest.raises(ValueError):
        model.poles[0] = 5


def test_matching_distance_agrees_with_the_definition_on_random_sets():
    rng = np.random.default_rng(20261109)
    for r in range(1, 7):
        for _ in range(20):
            a = rng.normal(size=r) + 1j * rng.normal(size=r)
            b = rng.normal(size=r) + 1j * rng.normal(size=r)
            for relative in (False, True):
                omega, sigma = matching_distance(a, b, relative=relative)
                assert omega == pytest.approx(brute_force_distance(a, b, relative), rel=RTOL)
                scale = np.abs(a) if relative else 1.0
                assert np.max(np.abs(a - b[sigma]) / scale) == pytest.approx(omega, rel=RTOL)
                assert sorted(sigma) == list(range(r))


def test_matching_distance_ignores_the_order_of_poles():
    a = np.array([-1.0, -2 + 3j, -2 - 3j, -10.0])
    perturbation = np.array([1e-6, -2e-6j, 3e-6, 0])
    b = (a + perturbation)[[3, 0, 2, 1]]
    omega, sigma = matching_distance(a, b)
    assert omega == pytest.approx(3e-6, rel=1e-6)
    assert list(sigma) == [1, 3, 2, 0]


def test_bound_4_4_for_zeros_of_the_denominator():
    # L1 (4.4): poles move by at most r(2r-1) max|phi| when lambda+ are the zeros of
    # d(s) = 1 + sum phi_j/(s - lambda_j). Those zeros are eig(diag(lambda) - phi e^T).
    rng = np.random.default_rng(4)
    for r in (2, 5, 10):
        lam = -rng.uniform(1, 10, r) + 1j * rng.normal(size=r)
        phi = 1e-3 * (rng.normal(size=r) + 1j * rng.normal(size=r))
        zeros = np.linalg.eigvals(np.diag(lam) - np.outer(phi, np.ones(r)))
        denominator = 1 + np.sum(phi / (zeros[:, None] - lam), axis=1)
        assert np.max(np.abs(denominator)) < 1e-8
        omega, _ = matching_distance(lam, zeros)
        assert omega <= r * (2 * r - 1) * np.max(np.abs(phi))


def test_detect_period_recognises_settling_cycling_and_neither():
    a = np.array([-1.0, -2.0, -3.0])
    b = np.array([-1.5, -2.5, -4.0])
    settled = [b, a * (1 + 1e-3), a * (1 + 1e-12), a]
    assert detect_period(settled, rtol=1e-9, max_period=3) == 1
    cycling = [a, b, a, b, a * (1 + 1e-13)]
    assert detect_period(cycling, rtol=1e-9, max_period=3) == 2
    drifting = [a * (1 + k / 10) for k in range(6)]
    assert detect_period(drifting, rtol=1e-9, max_period=3) is None
    with pytest.raises(ValueError):
        detect_period(settled, rtol=1e-9, max_period=0)
