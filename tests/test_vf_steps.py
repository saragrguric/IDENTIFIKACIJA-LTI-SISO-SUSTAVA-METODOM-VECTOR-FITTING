"""Independent small rational examples for the algebraic pieces of A5."""
import warnings

import numpy as np
import pytest

from vfdebye.vf import (
    barycentric_step,
    fit_fixed_poles,
    matching_distance,
    reflect_unstable_poles,
    relocate_poles,
)

RTOL = 1e-11


def test_order_one_step_recovers_the_known_pole_and_residue():
    s = np.array([1j, 2j])
    h = np.array([1 - 1j, (2 - 4j) / 5])  # H(s) = 2/(s+1).
    step = barycentric_step(s, h, [-3])
    np.testing.assert_allclose(step.numerator_residues, [2], rtol=RTOL)
    np.testing.assert_allclose(step.denominator_residues, [-2], rtol=RTOL)
    assert step.rank == 2
    assert np.isfinite(step.condition)
    assert step.weighted_residual_norm < 1e-14
    poles = relocate_poles([-3], step.denominator_residues)
    np.testing.assert_allclose(poles, [-1], rtol=RTOL)
    fit = fit_fixed_poles(s, h, poles)
    np.testing.assert_allclose(fit.model.residues, [2], rtol=RTOL)
    assert fit.rank == 1


@pytest.mark.parametrize("frequency_scale", [1e-9, 2 * np.pi * 1e9, 1e15])
def test_frequency_rescaling_preserves_the_dimensionless_model(frequency_scale):
    s = frequency_scale * 1j * np.array([0.5, 1, 2, 7])
    h = 2 * frequency_scale / (s + frequency_scale)
    step = barycentric_step(s, h, [-3 * frequency_scale])
    np.testing.assert_allclose(step.numerator_residues / frequency_scale, [2], rtol=RTOL)
    np.testing.assert_allclose(step.denominator_residues / frequency_scale, [-2], rtol=RTOL)
    poles = relocate_poles([-3 * frequency_scale], step.denominator_residues)
    fit = fit_fixed_poles(s, h, poles)
    np.testing.assert_allclose(poles / frequency_scale, [-1], rtol=RTOL)
    np.testing.assert_allclose(fit.model(s), h, rtol=RTOL)


@pytest.mark.parametrize("permutation", [[0, 1, 2], [2, 0, 1], [1, 0, 2]])
def test_mixed_real_and_conjugate_poles_recover_a_known_real_function(permutation):
    # H(s) = (s+5)/(s^2+2s+5) + 3/(s+8), poles -1+-2i and -8.
    s = 1j * np.geomspace(0.2, 30, 24)
    h = (s + 5) / (s**2 + 2 * s + 5) + 3 / (s + 8)
    auxiliary = np.array([-2 - 1j, -7, -2 + 1j])[permutation]
    weights = np.geomspace(0.1, 10, s.size)
    step = barycentric_step(s, h, auxiliary, weights)
    assert step.rank == 6
    poles = relocate_poles(auxiliary, step.denominator_residues)
    distance, _ = matching_distance([-1 + 2j, -8, -1 - 2j], poles)
    assert distance < 2e-11
    fit = fit_fixed_poles(s, h, poles, weights)
    probe = np.array([0, 0.7j, 5j, 2 + 3j, -0.5 + 8j])
    expected = (probe + 5) / (probe**2 + 2 * probe + 5) + 3 / (probe + 8)
    np.testing.assert_allclose(fit.model(probe), expected, rtol=RTOL)
    assert fit.model.is_real() and fit.model.is_stable()
    assert fit.rank == 3
    assert fit.weighted_residual_norm < 1e-12


def test_fixed_pole_weights_multiply_squared_errors_not_rows_directly():
    # Requiring a real residue, min |phi/(1+i)-1|^2 + 4|phi/(1+2i)-2|^2
    # gives phi = (1/2 + 4*2/5)/(1/2 + 4/5) = 21/13.
    fit = fit_fixed_poles([1j, 2j], [1, 2], [-1], [1, 4])
    assert fit.model.residues[0] == pytest.approx(21 / 13, rel=RTOL)
    assert fit.weighted_residual_norm**2 == pytest.approx(1769 / 130, rel=RTOL)
    assert fit.condition == pytest.approx(1)


def test_weighted_barycentric_step_is_stationary_for_the_linearized_objective():
    s = 1j * np.array([0.5, 1, 2, 7])
    h = 1 / (s + 1) + 0.5 / (s + 5)
    weights = np.array([1, 2, 4, 0.5])
    step = barycentric_step(s, h, [-3], weights)
    phi, varphi = step.numerator_residues[0], step.denominator_residues[0]

    def objective(numerator, denominator):
        n = numerator / (s + 3)
        d = 1 + denominator / (s + 3)
        return np.sum(weights * abs(n - h * d) ** 2)

    assert step.weighted_residual_norm**2 == pytest.approx(objective(phi, varphi), rel=RTOL)
    for d_phi, d_varphi in [(1, 0), (0, 1), (1, -2)]:
        # A quadratic LS objective is symmetric about its minimizer in every direction.
        assert objective(phi + d_phi, varphi + d_varphi) == pytest.approx(
            objective(phi - d_phi, varphi - d_varphi), rel=RTOL, abs=1e-13
        )


def test_common_weight_factor_preserves_the_fit_and_scales_the_residual_norm():
    s, h, weights = [1j, 2j], [1, 2], np.array([1, 4])
    first = fit_fixed_poles(s, h, [-1], weights)
    second = fit_fixed_poles(s, h, [-1], 9 * weights)
    np.testing.assert_allclose(first.model.residues, second.model.residues, rtol=RTOL)
    assert second.weighted_residual_norm == pytest.approx(3 * first.weighted_residual_norm)


@pytest.mark.parametrize("solve", [barycentric_step, fit_fixed_poles])
def test_complex_dtype_with_zero_imaginary_weights_is_accepted_without_cast_warnings(solve):
    with warnings.catch_warnings():
        warnings.simplefilter("error")
        result = solve([1j, 2j], [1 - 1j, (2 - 4j) / 5], [-3], [1 + 0j, 4 + 0j])
    assert np.isfinite(result.weighted_residual_norm)


def test_relocation_agrees_with_an_independently_factored_quadratic():
    # q(s) = (s+1)(s+3) = (s+2)(s+5) - (s+5)/3 - 8(s+2)/3.
    expected = [-1, -3]
    for poles, varphi in [([-2, -5], [-1 / 3, -8 / 3]), ([-5, -2], [-8 / 3, -1 / 3])]:
        relocated = relocate_poles(poles, varphi)
        assert matching_distance(expected, relocated)[0] < 1e-13


def test_zero_denominator_residues_retain_all_auxiliary_points():
    poles = np.array([-1, -2 + 3j, -2 - 3j])
    result = relocate_poles(poles, [0, 0, 0])
    assert result.size == 3
    assert matching_distance(poles, result)[0] < 1e-14


def test_relocation_retains_root_multiplicity():
    # q(s) = (s+2)^2 = (s+1)(s+3) + (s+3)/2 - (s+1)/2.
    result = relocate_poles([-1, -3], [0.5, -0.5])
    assert result.size == 2
    np.testing.assert_allclose(result, [-2, -2], rtol=0, atol=1e-7)


def test_relocation_preserves_real_structure_without_sorting_assumptions():
    rng = np.random.default_rng(20261123)
    for _ in range(20):
        upper = -rng.uniform(0.1, 10, 4) + 1j * rng.uniform(0.1, 10, 4)
        residues = rng.normal(size=4) + 1j * rng.normal(size=4)
        poles = np.r_[upper, -3, upper.conj()]
        varphi = np.r_[residues, 0.2, residues.conj()]
        order = rng.permutation(poles.size)
        new = relocate_poles(poles[order], varphi[order])
        assert matching_distance(new, new.conj())[0] == 0
        # Direct substitution into d_tilde independently checks the sign of the update.
        denominator = 1 + np.sum(varphi / (new[:, None] - poles), axis=1)
        np.testing.assert_allclose(denominator, 0, rtol=0, atol=1e-10)


def test_relocation_does_not_silently_reflect_unstable_roots():
    np.testing.assert_allclose(relocate_poles([-1], [-3]), [2])


def test_reflection_is_across_the_imaginary_axis_and_does_not_modify_input():
    poles = np.array([2 + 3j, 2 - 3j, -5, 0, 1j])
    original = poles.copy()
    np.testing.assert_array_equal(reflect_unstable_poles(poles), [-2 + 3j, -2 - 3j, -5, 0, 1j])
    np.testing.assert_array_equal(poles, original)


def test_reflection_has_unit_modulus_scaling_on_the_imaginary_axis():
    unstable = np.array([2 + 3j, 2 - 3j, 5])
    reflected = reflect_unstable_poles(unstable)
    s = 1j * np.linspace(-20, 20, 81)
    scaling = np.prod((s[:, None] - unstable) / (s[:, None] - reflected), axis=1)
    np.testing.assert_allclose(abs(scaling), 1, rtol=RTOL)
    off_axis = np.prod((1 + 2j - unstable) / (1 + 2j - reflected))
    assert not np.isclose(abs(off_axis), 1)


def test_reflection_does_not_merge_collisions_or_shift_imaginary_axis_poles():
    np.testing.assert_array_equal(reflect_unstable_poles([1, -1, 0, 2j]), [-1, -1, 0, 2j])
    with pytest.raises(ValueError, match="distinct"):
        fit_fixed_poles([1j, 2j], [1, 2], reflect_unstable_poles([1, -1]))


@pytest.mark.parametrize("solve", [barycentric_step, fit_fixed_poles])
@pytest.mark.parametrize(
    ("s", "h", "poles", "weights", "message"),
    [
        ([[1j, 2j]], [1, 2], [-1], None, "one-dimensional"),
        ([1j, 2j], [[1, 2]], [-1], None, "one-dimensional"),
        ([1j, 2j], [1], [-1], None, "same shape"),
        ([1j, np.nan], [1, 2], [-1], None, "finite"),
        ([1j, 2j], [1, np.inf], [-1], None, "finite"),
        ([1j, 2j], [1, 2], [], None, "at least one pole"),
        ([1j, 2j], [1, 2], [-1, -1], None, "distinct"),
        ([1j, 2j], [1, 2], [-1 + 2j], None, "conjugate pairs"),
        ([1j, 2j], [1, 2], [-1 + 2j, -1 - 2.0000000001j], None, "conjugate pairs"),
        ([1j, 2j], [1, 2], [-1, np.inf], None, "finite"),
        ([1j], [1], [-1, -2], None, "at least as numerous"),
        ([1j, 2j], [1, 2], [1j, -1j], None, "coincides"),
        ([1j, 2j], [1, 2], [-1], [1, 0], "positive"),
        ([1j, 2j], [1, 2], [-1], [1, -2], "positive"),
        ([1j, 2j], [1, 2], [-1], [1, np.nan], "finite"),
        ([1j, 2j], [1, 2], [-1], [1, np.inf], "finite"),
        ([1j, 2j], [1, 2], [-1], [1], "same shape"),
        ([1j, 2j], [1, 2], [-1], np.array([1, 2 + 1j]), "real"),
        ([1j, -1j], [1 - 1j, 1 - 2j], [-1], None, "conjugate symmetry"),
        ([0, 1j], [1 + 1j, 2], [-1], None, "conjugate symmetry"),
    ],
)
def test_invalid_fit_inputs_are_rejected(solve, s, h, poles, weights, message):
    with pytest.raises(ValueError, match=message):
        solve(s, h, poles, weights)


@pytest.mark.parametrize("solve", [barycentric_step, fit_fixed_poles])
def test_consistent_two_sided_data_give_the_same_real_model(solve):
    positive_s = 1j * np.array([1, 2, 3])
    positive_h = 2 / (positive_s + 1)
    s = np.r_[positive_s, positive_s.conj()]
    h = np.r_[positive_h, positive_h.conj()]
    one = solve(positive_s, positive_h, [-3])
    two = solve(s, h, [-3])
    if solve is barycentric_step:
        np.testing.assert_allclose(one.numerator_residues, two.numerator_residues, rtol=RTOL)
        np.testing.assert_allclose(one.denominator_residues, two.denominator_residues, rtol=RTOL)
    else:
        np.testing.assert_allclose(one.model.residues, two.model.residues, rtol=RTOL)


def test_rank_loss_is_reported_for_repeated_samples_and_nearly_coincident_poles():
    s = np.full(3, 1j)
    h = np.full(3, 1 - 1j)
    step = barycentric_step(s, h, [-1, -2])
    assert step.rank < 4 and np.isinf(step.condition)
    fit = fit_fixed_poles(s, h, [-1, -2, -3])
    assert fit.rank < 3 and np.isinf(fit.condition)
    close = [-1, np.nextafter(-1.0, -np.inf)]
    s = 1j * np.arange(1, 6)
    fit = fit_fixed_poles(s, 2 / (s + 1), close)
    assert fit.model.order == 2
    assert fit.rank == 1 and np.isinf(fit.condition)


def test_zero_data_do_not_make_the_poles_identifiable_despite_a_zero_residual():
    s = 1j * np.arange(1, 5)
    step = barycentric_step(s, np.zeros(s.size), [-1])
    assert step.weighted_residual_norm == 0
    assert step.rank == 1 and np.isinf(step.condition)
    np.testing.assert_array_equal(step.denominator_residues, [0])
    fit = fit_fixed_poles(s, np.zeros(s.size), [-1])
    np.testing.assert_array_equal(fit.model(s), np.zeros(s.size))


def test_fixed_pole_solve_reports_an_unstable_model_without_changing_the_poles():
    s = 1j * np.arange(1, 5)
    fit = fit_fixed_poles(s, 3 / (s - 1), [1])
    assert not fit.model.is_stable()
    assert fit.model.is_real()
    np.testing.assert_allclose(fit.model.residues, [3], rtol=RTOL)


@pytest.mark.parametrize(
    ("poles", "varphi", "message"),
    [
        ([-1], [0, 1], "same shape"),
        ([-1], [np.nan], "finite"),
        ([-1], [1j], "denominator residues"),
        ([-1 + 2j, -1 - 2j], [1 + 2j, 1 + 2j], "denominator residues"),
        ([-1, -1], [0, 0], "distinct"),
    ],
)
def test_invalid_relocation_inputs_are_rejected(poles, varphi, message):
    with pytest.raises(ValueError, match=message):
        relocate_poles(poles, varphi)


@pytest.mark.parametrize("solve", [barycentric_step, fit_fixed_poles])
def test_overflow_near_a_sample_is_an_explicit_numerical_failure(solve):
    with pytest.raises(FloatingPointError):
        solve([0], [1], [-1e-320])
