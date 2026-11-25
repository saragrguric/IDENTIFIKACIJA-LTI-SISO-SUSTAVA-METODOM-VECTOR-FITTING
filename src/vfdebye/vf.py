"""Vector fitting (L1, section 2.2) and the objects around it.

The algebraic steps are independently usable; vector_fit composes them into an iteration:

- PoleResidueModel: H_r(s) = d + sum_j phi_j / (s - lambda_j), the model object of the shared
  interface in docs/plan/PODJELA.md, evaluated at arbitrary points;
- matching_distance: the optimal matching distance of two pole sets, L1 (4.3);
- detect_period: lagged pole distances for recognising cycling (L1, Example 4.2, Remark 4.3).
- barycentric_step, relocate_poles, reflect_unstable_poles and fit_fixed_poles: independently
  usable linear algebra from A5, with real-system structure and weighted LS diagnostics.

Stopping tolerances and reflection are explicit caller choices, not experimental defaults.
Comparison with the pilot code B1 and team approval remain separate acceptance steps.
Poles and residues are in the variable s = 2j*pi*f, i.e. in rad/s.
"""
from __future__ import annotations

from collections.abc import Sequence
from dataclasses import dataclass, replace

import numpy as np
from scipy.linalg import norm
from scipy.optimize import linear_sum_assignment
from scipy.sparse import csr_matrix
from scipy.sparse.csgraph import maximum_bipartite_matching

SAMPLE_SYMMETRY_RTOL = 1e-10


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


def _distinct_poles(values: object) -> np.ndarray:
    poles = _complex_vector("poles", values)
    if poles.size == 0:
        raise ValueError("at least one pole is required")
    if np.unique(poles).size != poles.size:
        raise ValueError("poles must be distinct for the barycentric basis")
    return poles


def _real_pole_basis(poles: np.ndarray) -> np.ndarray:
    """Map real parameters to real residues or exact conjugate residue pairs.

    For a conjugate pair, (a, b) maps to (a + ib, a - ib); no poles are projected or averaged.
    """
    transform = np.zeros((poles.size, poles.size), dtype=complex)
    used = set()
    column = 0
    for j, pole in enumerate(poles):
        if j in used:
            continue
        transform[j, column] = 1
        if pole.imag == 0:
            column += 1
        else:
            partners = np.flatnonzero(poles == pole.conjugate())
            if partners.size == 0:
                raise ValueError("complex poles must occur in exact conjugate pairs")
            partner = int(partners[0])
            transform[partner, column] = 1
            transform[j, column + 1] = 1j
            transform[partner, column + 1] = -1j
            used.add(partner)
            column += 2
        used.add(j)
    return transform


def _fit_inputs(s, h, poles, weights):
    s = _complex_vector("s", s)
    h = _complex_vector("h", h)
    poles = _distinct_poles(poles)
    if h.shape != s.shape:
        raise ValueError("s and h must have the same shape")
    if s.size < poles.size:
        raise ValueError("samples must be at least as numerous as poles")
    weights = np.ones(s.size) if weights is None else _complex_vector("weights", weights)
    if np.any(weights.imag != 0):
        raise ValueError("weights must be real")
    weights = weights.real
    if weights.shape != s.shape or np.any(weights <= 0):
        raise ValueError("weights must be positive and have the same shape as s")
    if np.any(s[:, None] == poles):
        raise ValueError("a sample coincides with a pole")
    # Check supplied partners only; one-sided frequency data are fitted by a real model.
    by_point = dict(zip(s, h, strict=True))
    for point, value in zip(s, h, strict=True):
        partner = by_point.get(point.conjugate())
        if partner is not None and not np.isclose(
            value, partner.conjugate(), rtol=SAMPLE_SYMMETRY_RTOL, atol=0
        ):
            raise ValueError("supplied samples violate conjugate symmetry of a real system")
    with np.errstate(over="raise", divide="raise", invalid="raise"):
        cauchy = 1 / (s[:, None] - poles)
    return cauchy, h, poles, weights


def _real_lstsq(matrix, h, weights):
    with np.errstate(over="raise", invalid="raise"):
        row_weights = np.sqrt(weights)
        weighted_matrix = row_weights[:, None] * matrix
        weighted_h = row_weights * h
    a = np.vstack((weighted_matrix.real, weighted_matrix.imag))
    b = np.concatenate((weighted_h.real, weighted_h.imag))
    if not np.all(np.isfinite(a)) or not np.all(np.isfinite(b)):
        raise FloatingPointError("weighted LS matrix or right-hand side is not finite")
    coefficients, _, rank, singular = np.linalg.lstsq(a, b, rcond=None)
    if not np.all(np.isfinite(coefficients)) or not np.all(np.isfinite(singular)):
        raise FloatingPointError("least-squares solution or singular values are not finite")
    condition = float(singular[0] / singular[-1]) if rank == a.shape[1] else float("inf")
    with np.errstate(over="raise", invalid="raise"):
        residual = a @ coefficients - b
    residual_norm = float(norm(residual))
    if not np.isfinite(residual_norm):
        raise FloatingPointError("weighted residual norm is not finite")
    return coefficients, int(rank), condition, residual_norm


@dataclass(frozen=True, eq=False)
class BarycentricStep:
    """One linearized LS solve; rank and condition refer to the weighted real matrix.

    numerator_residues and denominator_residues are phi and varphi in L1 (2.5).
    weighted_residual_norm is ||sqrt(w) (n_tilde - h*d_tilde)||_2, not a rational error.
    Full column rank is 2r; rank loss is reported and is not a convergence decision.
    """

    numerator_residues: np.ndarray
    denominator_residues: np.ndarray
    rank: int
    condition: float
    weighted_residual_norm: float


def barycentric_step(s, h, poles, weights=None) -> BarycentricStep:
    """Solve one real-system step with A = [C, -diag(h) C], L1 (2.7), (2.12).

    s: finite sample points in rad/s; h: H(s); poles: distinct auxiliary points in rad/s,
    real or exactly conjugate-paired. weights are the positive coefficients w of |error|^2,
    not row weights: rows are multiplied by sqrt(w). At least r samples are required.

    This is the step with d_tilde(infinity) = 1 after SK weight absorption. For a fixed-basis
    SK step the caller would supply w / |d_previous(s)|^2. No weight is chosen internally;
    None means all ones. No pole reflection or stopping criterion is applied here.
    """
    cauchy, h, poles, weights = _fit_inputs(s, h, poles, weights)
    transform = _real_pole_basis(poles)
    with np.errstate(over="raise", invalid="raise"):
        basis = cauchy @ transform
        matrix = np.column_stack((basis, -h[:, None] * basis))
    x, rank, condition, residual = _real_lstsq(matrix, h, weights)
    r = poles.size
    return BarycentricStep(transform @ x[:r], transform @ x[r:], rank, condition, residual)


def relocate_poles(poles, denominator_residues) -> np.ndarray:
    """Zeros of q(s) = prod(s-lambda) * (1 + sum varphi/(s-lambda)), L1 (2.9).

    Computes eig(diag(lambda) - varphi*e^T). A real equivalent matrix preserves exact
    conjugate pairing in the result. Input poles and varphi must describe a real system.
    When a varphi is zero the polynomial q may retain an auxiliary point even though the
    rational d_tilde has a removable singularity there. No roots are dropped or reflected.
    """
    poles = _distinct_poles(poles)
    varphi = _complex_vector("denominator_residues", denominator_residues)
    if varphi.shape != poles.shape:
        raise ValueError("poles and denominator_residues must have the same shape")
    transform = _real_pole_basis(poles)
    with np.errstate(over="raise", invalid="raise"):
        matrix = np.diag(poles) - varphi[:, None]
        real_matrix = np.linalg.solve(transform, matrix @ transform)
    if np.any(real_matrix.imag != 0):
        raise ValueError("denominator residues must be real or exactly conjugate-paired")
    if not np.all(np.isfinite(real_matrix)):
        raise FloatingPointError("pole relocation matrix is not finite")
    relocated = np.asarray(np.linalg.eigvals(real_matrix.real), dtype=complex)
    if not np.all(np.isfinite(relocated)):
        raise FloatingPointError("relocated poles are not finite")
    return relocated


def reflect_unstable_poles(poles) -> np.ndarray:
    """Reflect Re(lambda)>0 across the imaginary axis: lambda -> -conj(lambda), L1 4.1.

    Returns a copy, without changing imaginary-axis poles. Reflection can create duplicate
    poles; no merging, jitter or pole shift is performed. Inspect stability and distinctness
    before a subsequent LS solve. This helper does not choose a stabilization policy.
    """
    reflected = _complex_vector("poles", poles)
    unstable = reflected.real > 0
    reflected[unstable] = -reflected[unstable].conj()
    return reflected


@dataclass(frozen=True, eq=False)
class ResidueFit:
    """Fixed-pole real model and weighted LS diagnostics; full column rank is r."""

    model: PoleResidueModel
    rank: int
    condition: float
    weighted_residual_norm: float


def fit_fixed_poles(s, h, poles, weights=None) -> ResidueFit:
    """Fit final residues for given real or conjugate-paired poles (L1 4.2, after (iii)).

    Minimizes sum w_i |sum phi_j/(s_i-lambda_j) - h_i|^2 over real-system residues.
    Inputs have the same units and validation as barycentric_step. Returns a strictly proper
    model; stability and residue positivity are reported by inspecting it, never imposed.
    No direct term is fitted. Rank loss and conditioning are retained in the result.
    """
    cauchy, h, poles, weights = _fit_inputs(s, h, poles, weights)
    transform = _real_pole_basis(poles)
    with np.errstate(over="raise", invalid="raise"):
        basis = cauchy @ transform
    x, rank, condition, residual = _real_lstsq(basis, h, weights)
    return ResidueFit(PoleResidueModel(poles, transform @ x), rank, condition, residual)


def _pole_snapshot(poles: np.ndarray) -> np.ndarray:
    snapshot = poles.copy()
    snapshot.flags.writeable = False
    return snapshot


@dataclass(frozen=True, eq=False)
class VFIteration:
    """One attempted LS step, including raw relocation and any explicit reflection.

    poles_before/after and raw_poles are in rad/s. pole_distance is the absolute bottleneck
    distance between before/after, not a coefficient-wise distance or an accuracy estimate.
    None means an operation was not reached, e.g. relocation after a rank-deficient LS.
    """

    poles_before: np.ndarray
    step: BarycentricStep
    raw_poles: np.ndarray | None = None
    poles_after: np.ndarray | None = None
    reflected_count: int = 0
    pole_distance: float | None = None
    denominator_deviation: float | None = None


@dataclass(frozen=True, eq=False)
class VectorFitResult:
    """Iteration outcome and final LS at the last valid pole set.

    poles_settled is a stopping observation, never proof of accuracy or optimality.
    A candidate can accompany rank loss, cycling or exhaustion; inspect stop_reason, the
    history and final_fit diagnostics before accepting it. final_fit_error records a failed
    final residue solve separately, without erasing the iteration's stop reason.
    """

    history: tuple[VFIteration, ...]
    stop_reason: str
    final_fit: ResidueFit | None
    message: str | None = None
    cycle_period: int | None = None
    final_fit_error: str | None = None

    @property
    def model(self) -> PoleResidueModel | None:
        return self.final_fit.model if self.final_fit is not None else None


def _poles_close(a, b, rtol, atol):
    with np.errstate(over="raise", invalid="raise"):
        distance, _ = matching_distance(a, b)
        threshold = atol + rtol * np.max(np.abs(a))
    return distance, bool(distance <= threshold)


def vector_fit(
    s, h, weights, poles0, *, max_iterations: int, pole_rtol: float, pole_atol: float,
    reflect_unstable: bool, settle_steps: int, max_period: int, cycle_repeats: int,
) -> VectorFitResult:
    """Real-system VF with external squared-error weights (L1 2.2, 4.1, 4.2).

    s is in rad/s; weights are positive w in sum w*|error|^2 (None means ones). All control
    settings are required: they are software choices for the caller, not a selected Z2 plan.
    Stop after settle_steps consecutive moves with Omega <= pole_atol + pole_rtol*max|old|;
    pole_atol is in rad/s. max_period=0 disables cycle detection, otherwise a period >=2
    requires cycle_repeats successive returns under that same distance criterion.

    Reflection is applied after relocation, only for imaginary-axis samples, where the
    unit-modulus argument holds. Initial auxiliary poles are recorded unchanged. Neither
    real negative poles nor positive final residues are imposed. The final model is strictly
    proper. No samples or poles are dropped, merged, projected or jittered.

    Malformed inputs raise ValueError. Numerical failures inside the iteration are returned
    explicitly with a last-valid candidate when its final residue solve succeeds. Rank loss
    stops the iteration; a large condition number is recorded without an automatic cutoff.
    """
    for name, value, minimum in (
        ("max_iterations", max_iterations, 1), ("settle_steps", settle_steps, 1),
        ("max_period", max_period, 0), ("cycle_repeats", cycle_repeats, 1),
    ):
        if (isinstance(value, (bool, np.bool_))
                or not isinstance(value, (int, np.integer)) or value < minimum):
            raise ValueError(f"{name} must be an integer >= {minimum}")
    for name, value in (("pole_rtol", pole_rtol), ("pole_atol", pole_atol)):
        if (isinstance(value, (bool, np.bool_))
                or not isinstance(value, (int, float, np.integer, np.floating))
                or not np.isfinite(value) or value < 0):
            raise ValueError(f"{name} must be a finite nonnegative real number")
    if not isinstance(reflect_unstable, (bool, np.bool_)):
        raise ValueError("reflect_unstable must be a boolean")
    # Validate once before failure reporting: malformed caller inputs are programming errors.
    _, h, poles, weights = _fit_inputs(s, h, poles0, weights)
    s = _complex_vector("s", s)
    _real_pole_basis(poles)
    if reflect_unstable and np.any(s.real != 0):
        raise ValueError("pole reflection requires samples on the imaginary axis")

    history = []
    pole_history = [_pole_snapshot(poles)]
    small_moves = 0
    reason, message, period = "max_iterations", None, None
    numerical_errors = (FloatingPointError, np.linalg.LinAlgError)
    for iteration in range(1, max_iterations + 1):
        try:
            step = barycentric_step(s, h, poles, weights)
            step.numerator_residues.flags.writeable = False
            step.denominator_residues.flags.writeable = False
            history.append(VFIteration(_pole_snapshot(poles), step))
            if step.rank < 2 * poles.size:
                reason, message = "rank_deficient", f"iteration {iteration}: rank < 2r"
                break
            with np.errstate(over="raise", divide="raise", invalid="raise"):
                deviation = np.max(np.abs(np.sum(
                    step.denominator_residues / (s[:, None] - poles), axis=1
                )))
            if not np.isfinite(deviation):
                raise FloatingPointError("denominator deviation is not finite")
            history[-1] = replace(history[-1], denominator_deviation=float(deviation))
            raw = relocate_poles(poles, step.denominator_residues)
            updated = reflect_unstable_poles(raw) if reflect_unstable else raw.copy()
            history[-1] = replace(
                history[-1], raw_poles=_pole_snapshot(raw), poles_after=_pole_snapshot(updated),
                reflected_count=int(np.count_nonzero(raw.real > 0)) if reflect_unstable else 0,
            )
            try:
                _fit_inputs(s, h, updated, weights)
                _real_pole_basis(updated)
                if reflect_unstable and np.any(updated.real >= 0):
                    raise ValueError("reflection leaves poles on the imaginary axis")
            except ValueError as error:
                reason, message = "invalid_relocated_poles", f"iteration {iteration}: {error}"
                break
            distance, small = _poles_close(poles, updated, pole_rtol, pole_atol)
            history[-1] = replace(history[-1], pole_distance=distance)
            poles = updated
            pole_history.append(_pole_snapshot(poles))
            small_moves = small_moves + 1 if small else 0
            if small_moves >= settle_steps:
                reason = "poles_settled"
                break
            for lag in range(2, min(max_period, (len(pole_history) - 1) // cycle_repeats) + 1):
                if all(_poles_close(
                    pole_history[-1 - (j + 1) * lag], pole_history[-1 - j * lag],
                    pole_rtol, pole_atol,
                )[1] for j in range(cycle_repeats)):
                    period, reason = lag, "cycle"
                    break
            if period is not None:
                break
        except numerical_errors as error:
            reason, message = "numerical_failure", f"iteration {iteration}: {error}"
            break

    final_fit, final_error = None, None
    try:
        final_fit = fit_fixed_poles(s, h, poles, weights)
    except numerical_errors as error:
        final_error = str(error)
    return VectorFitResult(tuple(history), reason, final_fit, message, period, final_error)
