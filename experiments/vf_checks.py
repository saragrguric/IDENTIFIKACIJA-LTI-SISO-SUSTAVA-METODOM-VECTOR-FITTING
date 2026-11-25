"""Reproducible synthetic checks of the complete VF loop, not tissue experiments.

Run: uv run python experiments/vf_checks.py
Three cases: two known real poles with unit weights, a conjugate pair plus a real pole,
and the real-pole case with finite-band quadrature weights. All settings and full iteration
histories are saved through provenance; no Gabriel table, B1 numbers or Z2 decision is used.
"""
from __future__ import annotations

import argparse
import json
from dataclasses import asdict
from pathlib import Path

import numpy as np

from vfdebye import provenance
from vfdebye.quadrature import band_nodes
from vfdebye.vf import vector_fit

CHECK_RTOL = 1e-9


def real_response(s):
    return 2 / (s + 1) + 3 / (s + 5)


def paired_response(s):
    return (s + 5) / (s**2 + 2 * s + 5) + 3 / (s + 8)


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    parser.add_argument("--runs-dir", type=Path, default=provenance.RUNS_DIR)
    parser.add_argument("--max-iterations", type=int, default=30)
    args = parser.parse_args(argv)
    if args.max_iterations < 1:
        parser.error("--max-iterations must be at least 1")

    # These values are for known synthetic systems only, not an approved tissue setup.
    controls = dict(max_iterations=args.max_iterations, pole_rtol=1e-9, pole_atol=1e-12,
                    reflect_unstable=True, settle_steps=2, max_period=4, cycle_repeats=2)
    s = 1j * np.geomspace(0.1, 40, 60)
    f_quad, w_quad = band_nodes(0.1 / (2 * np.pi), 40 / (2 * np.pi), 60)
    cases = [
        ("real_poles", s, np.ones(s.size), [-2, -8], real_response),
        ("conjugate_pair", s, np.ones(s.size), [-2+1j, -7, -2-1j], paired_response),
        ("band_weights", 2j * np.pi * f_quad, w_quad, [-2, -8], real_response),
    ]
    probe = np.array([0, 0.3j, 2j, 14j, 1+3j])
    settings = dict(purpose="synthetic implementation checks; not final tissue experiments",
                    controls=controls, check_rtol=CHECK_RTOL, probe_s_rad_per_s=probe,
                    solver="numpy.linalg.lstsq", rcond=None)
    settings["cases"] = [dict(name=name, s_rad_per_s=points, weights=weights, poles0=poles,
                             reference="2/(s+1)+3/(s+5)" if response is real_response else
                             "(s+5)/(s**2+2*s+5)+3/(s+8)")
                         for name, points, weights, poles, response in cases]
    outcomes = []
    with provenance.run("vf_checks", settings=settings, runs_dir=args.runs_dir) as record:
        for name, points, weights, poles, response in cases:
            result = vector_fit(points, response(points), weights, poles, **controls)
            error = None
            if result.model is not None:
                reference = response(probe)
                error = float(np.max(np.abs(result.model(probe) - reference))
                              / np.max(np.abs(reference)))
            passed = bool(result.stop_reason == "poles_settled" and error is not None
                          and error < CHECK_RTOL and result.model.is_stable()
                          and result.model.is_real() and result.final_fit.rank == len(poles)
                          and result.final_fit_error is None)
            outcomes.append(dict(name=name, passed=passed, response_relative_max=error,
                                 result=asdict(result)))
            print(f"{name}: {result.stop_reason}, iterations={len(result.history)}, "
                  f"response_relative_max={error}, {'PASS' if passed else 'FAIL'}")
        output = record.dir / "vf_checks.json"
        output.write_text(json.dumps(provenance.to_jsonable(outcomes), indent=2, allow_nan=False)
                          + "\n", encoding="utf-8")
        passed = all(item["passed"] for item in outcomes)
        record.update(checks_passed=passed, passed_cases=sum(item["passed"] for item in outcomes),
                      total_cases=len(outcomes), artifacts=[output.name])
        print(f"run_id={record.run_id}")
    return 0 if passed else 1


if __name__ == "__main__":
    raise SystemExit(main())
