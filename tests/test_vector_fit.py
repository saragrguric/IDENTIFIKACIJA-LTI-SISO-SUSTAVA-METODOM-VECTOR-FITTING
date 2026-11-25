"""Full VF loop: known transfer functions and explicit iteration failure states."""
import numpy as np
import pytest

from vfdebye import vf

SETTINGS = dict(
    max_iterations=30, pole_rtol=1e-9, pole_atol=1e-12, denominator_tol=1e-8,
    reflect_unstable=False,
    settle_steps=2, max_period=4, cycle_repeats=2,
)


def fit(s, h, poles, weights=None, **settings):
    return vf.vector_fit(s, h, weights, poles, **(SETTINGS | settings))


@pytest.mark.parametrize("scale", [1e-9, 1.0, 2 * np.pi * 1e9])
@pytest.mark.parametrize("weighted", [False, True])
def test_recovers_known_real_poles_and_residues_at_independent_points(scale, weighted):
    s = scale * 1j * np.geomspace(0.1, 20, 30)
    h = 2 * scale / (s + scale) + 3 * scale / (s + 5 * scale)
    w = np.geomspace(0.2, 5, s.size) if weighted else None
    result = fit(s, h, scale * np.array([-2.0, -8.0]), w, pole_atol=1e-12 * scale)
    assert result.stop_reason == "poles_and_denominator_settled"
    assert result.final_fit_error is None and result.final_fit.rank == 2
    assert result.model.is_stable() and result.model.is_real()
    assert vf.matching_distance(result.model.poles / scale, [-1, -5])[0] < 1e-10
    probe = scale * np.array([0, 0.3j, 2j, 14j, 1 + 3j])
    expected = 2 * scale / (probe + scale) + 3 * scale / (probe + 5 * scale)
    np.testing.assert_allclose(result.model(probe), expected, rtol=1e-10, atol=0)
    assert result.history[-1].denominator_deviation < 1e-10


def test_recovers_conjugate_pair_from_one_sided_samples_without_projection():
    s = 1j * np.geomspace(0.1, 40, 50)
    h = (s + 5) / (s**2 + 2 * s + 5) + 3 / (s + 8)
    result = fit(s, h, [-2 + 1j, -7, -2 - 1j])
    assert result.stop_reason == "poles_and_denominator_settled"
    assert result.model.is_real() and result.model.is_stable()
    expected_poles = [-1 + 2j, -1 - 2j, -8]
    assert vf.matching_distance(result.model.poles, expected_poles)[0] < 1e-10
    probe = np.array([0, 0.3j, 6j, 1 + 2j])
    np.testing.assert_allclose(
        result.model(probe), (probe + 5) / (probe**2 + 2 * probe + 5) + 3 / (probe + 8),
        rtol=1e-11,
    )


def test_real_off_axis_samples_are_allowed_when_reflection_is_disabled():
    s = np.array([1 + 1j, 1 - 1j, 2 + 3j, 2 - 3j])
    result = fit(s, 2 / (s + 1), [-3])
    assert result.stop_reason == "poles_and_denominator_settled"
    np.testing.assert_allclose(result.model(0), 2, rtol=1e-12)


def test_an_unstable_target_is_not_silently_stabilized():
    s = 1j * np.geomspace(0.2, 10, 30)
    result = fit(s, 2 / (s - 1), [-3])
    assert result.stop_reason == "poles_and_denominator_settled"
    assert not result.model.is_stable()
    assert all(item.reflected_count == 0 for item in result.history)
    np.testing.assert_allclose(result.model.poles, [1], rtol=1e-12)


def test_reflection_records_raw_and_used_poles_and_does_not_claim_small_error():
    s = 1j * np.geomspace(0.2, 10, 30)
    h = 2 / (s - 1)
    result = fit(s, h, [-3], reflect_unstable=True)
    assert result.stop_reason == "poles_settled"
    assert result.model.is_stable()
    first = result.history[0]
    np.testing.assert_allclose(first.poles_before, [-3])
    np.testing.assert_allclose(first.raw_poles, [1], rtol=1e-12)
    np.testing.assert_allclose(first.poles_after, [-1], rtol=1e-12)
    assert first.reflected_count == 1
    assert result.history[-1].denominator_deviation > 0.1
    assert result.final_fit.weighted_residual_norm > 0.1


def test_small_move_threshold_is_the_larger_scale_not_the_sum(monkeypatch):
    # ADR-0008: Omega / max(atol/rtol, max|lambda|) <= rtol. With atol = 0.3, rtol = 0.01 and
    # |lambda| < 4 the threshold is 0.3; a sum atol + rtol*|lambda| would accept moves of 0.32.
    monkeypatch.setattr(vf, "relocate_poles", lambda poles, *_: poles - 0.32)
    s = 1j * np.array([0.2, 1, 3, 10])
    result = fit(s, 2 / (s + 1), [-3], pole_rtol=0.01, pole_atol=0.3, max_iterations=2,
                 max_period=0)
    assert result.stop_reason == "max_iterations"
    np.testing.assert_allclose([item.pole_distance for item in result.history], 0.32)
    monkeypatch.setattr(vf, "relocate_poles", lambda poles, *_: poles - 0.29)
    result = fit(s, 2 / (s + 1), [-3], pole_rtol=0.01, pole_atol=0.3, max_iterations=2,
                 max_period=0)
    assert result.stop_reason == "poles_settled"  # the forced moves leave d_tilde far from 1


def test_iteration_limit_retains_a_final_residue_fit_but_does_not_report_settling():
    s = 1j * np.geomspace(0.1, 10, 20)
    result = fit(s, 2 / (s + 1), [-3], max_iterations=1)
    assert result.stop_reason == "max_iterations" and len(result.history) == 1
    assert result.model is not None
    np.testing.assert_allclose(result.model(0.7j), 2 / (0.7j + 1), rtol=1e-12)


def test_rank_loss_keeps_the_attempt_and_does_not_relocate_unidentifiable_poles():
    s = np.array([1j, 2j, 3j])
    result = fit(s, np.zeros(3), [-3])
    assert result.stop_reason == "rank_deficient"
    assert "iteration 1" in result.message
    assert result.history[0].step.rank == 1
    assert result.history[0].raw_poles is None
    assert np.isinf(result.history[0].step.condition)
    np.testing.assert_array_equal(result.model(s), 0)


def test_cycle_requires_multiple_returns_and_preserves_the_final_candidate(monkeypatch):
    # Force a two-cycle in the relocation stage; actual LS solves still run at every step.
    updates = iter([[-4], [-3], [-4], [-3]])
    monkeypatch.setattr(vf, "relocate_poles", lambda *args: np.array(next(updates), complex))
    s = 1j * np.array([0.2, 1, 3, 10])
    result = fit(s, 2 / (s + 1), [-3], pole_rtol=0, pole_atol=0)
    assert result.stop_reason == "cycle" and result.cycle_period == 2
    assert len(result.history) == 4
    np.testing.assert_array_equal(result.model.poles, [-3])


def test_disabling_cycle_detection_runs_to_the_budget(monkeypatch):
    monkeypatch.setattr(vf, "relocate_poles", lambda poles, *_: -7 - poles)
    s = 1j * np.array([0.2, 1, 3, 10])
    result = fit(s, 2 / (s + 1), [-3], max_iterations=5, max_period=0)
    assert result.stop_reason == "max_iterations" and len(result.history) == 5
    assert result.cycle_period is None


@pytest.mark.parametrize(
    ("relocated", "poles", "target", "message"),
    [
        ([-2, -2], [-3, -7], lambda s: 2/(s+1) + 3/(s+5), "distinct"),
        ([1j], [-3], lambda s: 2/(s+1), "coincides"),
    ],
)
def test_invalid_new_basis_is_reported_without_deleting_any_poles(
    monkeypatch, relocated, poles, target, message,
):
    monkeypatch.setattr(vf, "relocate_poles", lambda *args: np.array(relocated, complex))
    s = 1j * np.array([1, 2, 5, 10])
    result = fit(s, target(s), poles)
    assert result.stop_reason == "invalid_relocated_poles"
    assert message in result.message
    np.testing.assert_array_equal(result.history[-1].poles_after, relocated)
    np.testing.assert_array_equal(result.model.poles, poles)


def test_imaginary_axis_poles_are_not_jittered_by_stabilization(monkeypatch):
    monkeypatch.setattr(vf, "relocate_poles", lambda *args: np.array([0j]))
    s = 1j * np.array([1, 2, 5])
    result = fit(s, 2 / (s + 1), [-3], reflect_unstable=True)
    assert result.stop_reason == "invalid_relocated_poles"
    assert "imaginary axis" in result.message
    np.testing.assert_array_equal(result.history[-1].poles_after, [0])
    np.testing.assert_array_equal(result.model.poles, [-3])


def test_numerical_failure_in_the_first_step_is_explicit(monkeypatch):
    def fail(*args):
        raise np.linalg.LinAlgError("synthetic SVD failure")

    monkeypatch.setattr(vf, "barycentric_step", fail)
    s = np.array([1j, 2j])
    result = fit(s, 2 / (s + 1), [-3])
    assert result.stop_reason == "numerical_failure"
    assert "iteration 1: synthetic SVD failure" == result.message
    assert result.history == () and result.model is not None


def test_final_residue_failure_does_not_erase_the_iteration_status(monkeypatch):
    def fail(*args):
        raise FloatingPointError("synthetic final fit failure")

    monkeypatch.setattr(vf, "fit_fixed_poles", fail)
    s = np.array([1j, 2j])
    result = fit(s, 2 / (s + 1), [-3], max_iterations=1)
    assert result.stop_reason == "max_iterations"
    assert result.final_fit_error == "synthetic final fit failure"
    assert result.model is None and result.final_fit is None


def test_caller_arrays_and_iteration_snapshots_are_preserved():
    s = 1j * np.geomspace(0.1, 10, 12)
    h, poles, weights = 2 / (s + 1), np.array([-3.0]), np.ones(s.size)
    originals = [array.copy() for array in (s, h, poles, weights)]
    result = fit(s, h, poles, weights)
    for original, after in zip(originals, (s, h, poles, weights), strict=True):
        np.testing.assert_array_equal(original, after)
    for item in result.history:
        for values in (item.poles_before, item.raw_poles, item.poles_after,
                       item.step.numerator_residues, item.step.denominator_residues):
            with pytest.raises(ValueError):
                values[0] = 7


@pytest.mark.parametrize(
    ("name", "value"),
    [("max_iterations", 0), ("max_iterations", True), ("settle_steps", 1.5),
     ("settle_steps", 0), ("max_period", -1), ("cycle_repeats", 0),
     ("cycle_repeats", np.bool_(True)), ("pole_rtol", -1), ("pole_rtol", np.inf),
     ("pole_rtol", np.nan), ("pole_rtol", 1j), ("pole_atol", -1),
     ("pole_atol", [0.1]), ("pole_atol", True), ("denominator_tol", -1),
     ("denominator_tol", np.nan), ("reflect_unstable", "yes")],
)
def test_invalid_controls_raise_before_solving(name, value):
    with pytest.raises(ValueError, match=name):
        fit([1j, 2j], [1-1j, (2-4j)/5], [-3], **{name: value})


def test_bad_samples_and_unpaired_poles_raise_instead_of_becoming_numerical_failures():
    with pytest.raises(ValueError, match="same shape"):
        fit([1j, 2j], [1], [-3])
    with pytest.raises(ValueError, match="conjugate"):
        fit([1j, 2j], [1, 2], [-3 + 1j])
    with pytest.raises(ValueError, match="symmetry"):
        fit([1j, -1j], [1j, 1j], [-3])
    with pytest.raises(ValueError, match="imaginary axis"):
        fit([1+1j, 2+1j], [1, 2], [-3], reflect_unstable=True)
