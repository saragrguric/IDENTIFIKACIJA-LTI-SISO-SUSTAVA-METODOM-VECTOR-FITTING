"""Smoke checks for the agreed environment (ADR-0006), independent of the VF code."""
import math
import sys

import numpy as np
import pytest
from scipy import integrate

import vfdebye

# quad on a smooth integrand over the whole real line; far looser than its error estimate.
QUAD_RTOL = 1e-8


def test_package_and_python_version():
    assert vfdebye.__doc__
    assert sys.version_info >= (3, 12)


@pytest.mark.parametrize("a", [1.0, 2.5e3, 6.0e9])
def test_quadrature_reproduces_known_h2_norm(a):
    # H(s) = 1/(s + a), a > 0: the integral of |H(iw)|^2 over the real line is pi/a
    # (docs/plan/METHODOLOGY.md, section 7). Substituting w = a*x keeps the integrand O(1).
    def integrand(x):
        return abs(1.0 / (1j * a * x + a)) ** 2 * a

    value, _ = integrate.quad(integrand, -np.inf, np.inf)
    assert math.isclose(value, math.pi / a, rel_tol=QUAD_RTOL)
