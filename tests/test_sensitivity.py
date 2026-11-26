"""Checks of the B7 summaries on small hand-made case records (no fitting)."""
from __future__ import annotations

import math
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "experiments"))
import sensitivity as sv  # noqa: E402

LEVELS = sv.LEVELS


def case(experiment, procedure, r, nodes=240, start=(1e7, 1e10), status="poles_settled",
         debye=True, errors=(0.02, 0.01), passes=("pass", "fail", "fail"), cond=1e6,
         group="Blood"):
    verdicts = {m: dict(zip(LEVELS, passes, strict=True)) for m in sv.MEASURES}
    errs = {m: {"fine": e} for m, e in zip(sv.MEASURES, errors, strict=True)}
    return {"experiment": experiment, "group": group, "procedure": procedure, "r": r,
            "nodes": nodes, "start_hz": list(start), "status": status, "eligible_debye": debye,
            "verdicts": verdicts, "candidate": {"errors": errs, "max_condition": cond}}


def test_node_changes_counts_differences_against_n240():
    cases = [case("dev_base", "vf_log", 8),
             case("dev_nodes", "vf_log", 8, nodes=120, errors=(0.04, 0.01)),
             case("dev_nodes", "vf_log", 8, nodes=480, passes=("pass", "pass", "fail"),
                  status="rank_deficient", debye=False)]
    row = sv.node_changes(cases)["vf_log"]
    assert row["pairs"] == 2
    assert row["status"] == 1 and row["debye"] == 1 and row["verdict"] == 1
    assert math.isclose(row["ratio"], 2.0)
    assert row["verdict_cases"] == [("Blood", 8, 480, [("max_relative_error", "0.01"),
                                                        ("band_error", "0.01")])]


def test_start_statuses_use_primary_base_only_at_sensitivity_orders():
    cases = [case("dev_base", "vf_log", 8), case("dev_base", "vf_log", 9),
             case("dev_start", "vf_log", 8, start=(1e3, 1e11), status="rank_deficient",
                  debye=False)]
    out = sv.start_statuses(cases)
    assert out[("vf_log", "1e+07-1e+10")] == {"poles_settled": 1, "debye": 1}
    assert out[("vf_log", "1e+03-1e+11")] == {"rank_deficient": 1, "debye": 0}


def test_condition_number_reads_the_stored_infinity():
    assert sv.condition_number({"float": "inf"}) == math.inf
    assert sv.condition_number(12.5) == 12.5


def test_conditioning_separates_infinite_and_large_values():
    cases = [case("final_base", "vf_log", 2, cond=10.0),
             case("final_base", "vf_log", 3, cond=30.0),
             case("final_base", "vf_log", 20, cond=2e12),
             case("final_base", "vf_log", 32, cond={"float": "inf"}),
             case("dev_start", "vf_log", 4, cond=1e15)]
    out = sv.conditioning(cases)
    assert out["bands"][("vf_log", (1, 4))] == (20.0, 30.0, 2)
    assert out["above"]["vf_log"] == 1 and out["infinite"]["vf_log"] == 1


def test_conditioning_reports_each_order_and_cases_without_candidate(capsys):
    cases = [case("final_base", "fixed_log_wide", 8, cond=10.0),
             case("final_base", "fixed_log_wide", 8, cond=30.0, group="Fat"),
             case("final_base", "fixed_log_wide", 12, cond=4e11),
             case("final_base", "fixed_log_wide", 13, cond=2e12),
             case("dev_start", "fixed_log_wide", 8, cond=1e15)]
    failed = case("final_base", "vf_log", 4, status="numerical_failure", debye=False)
    failed["candidate"] = None
    cases.append(failed)
    out = sv.conditioning(cases)
    assert out["orders"][("fixed_log_wide", 8)] == (20.0, 30.0, 2)
    assert out["orders"][("fixed_log_wide", 12)] == (4e11, 4e11, 1)
    assert out["missing"] == {"vf_log": 1}
    assert out["infinite"] == {}
    sv.report([], cases, [])
    printed = capsys.readouterr().out
    assert "r  8: 2.0e+01/3.0e+01 (2)" in printed
    assert "vf_log 0/0/1" in printed
