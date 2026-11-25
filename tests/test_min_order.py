"""B6 runner: groups, the section-6 verdicts, smallest orders, case counts and resumable runs."""
import json
import sys
from importlib.util import module_from_spec, spec_from_file_location
from pathlib import Path

import pytest

from vfdebye import gabriel

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "experiments"))  # min_order imports experiments/convergence.py
spec = spec_from_file_location("min_order", ROOT / "experiments" / "min_order.py")
mo = module_from_spec(spec)
spec.loader.exec_module(mo)


def row(name, *terms, eps_inf="4", sigma="0.1"):
    cells = [name, eps_inf, sigma]
    for n in range(4):
        cells += list(terms[n]) if n < len(terms) else ["0", "0", "0"]
    return cells


# Exact Debye terms (alpha = 0) at about 32 MHz and 1.6 GHz; tau in ps and ns as in the table.
DEBYE = (("50", "100", "0"), ("200", "5", "0"))
COLE = (("50", "100", "0.1"), ("200", "5", "0.1"))
AIR = ["Air", "1", "0", "0", "0", "1", "0", "0", "1", "0", "0", "1", "0", "0", "1"]


def test_groups_follow_parameters_and_development_names():
    tissues = [gabriel.tissue_from_row(r[0], r[1:]) for r in (
        AIR, row("Blood", *DEBYE), row("Mucous membrane", *COLE), row("Skin wet", *COLE),
        row("Liver", ("30", "50", "0.1")), row("Spleen", ("30", "50", "0.1")))]
    dev, final, skipped = mo.parameter_groups(tissues)
    assert dev == {"Blood": ["Blood"], "Skin wet": ["Mucous membrane", "Skin wet"]}
    assert final == {"Liver": ["Liver", "Spleen"]}
    assert skipped == ["Air"]


@pytest.mark.parametrize(("fine", "difference", "expected"), [
    (0.0090, 0.0005, "pass"), (0.0098, 0.0005, "borderline"), (0.0106, 0.0005, "fail"),
    (0.0100, 0.0, "pass"),
])
def test_verdict_is_conservative_in_the_grid_difference(fine, difference, expected):
    assert mo.verdict({"fine": fine, "difference": difference}, 0.01) == expected


def fake(r, verdict, eligible=True, procedure="vf_log", group="G"):
    verdicts = {m: {str(level): verdict for level in mo.LEVELS} for m in mo.MEASURES}
    return dict(experiment="final_base", group=group, procedure=procedure, nodes=240,
                start_hz=[1e7, 1e10], r=r, eligible_general=eligible, eligible_debye=eligible,
                verdicts=verdicts)


def pick(rows, procedure="vf_log", group="G"):
    [found] = [x for x in rows if x["procedure"] == procedure and x["group"] == group
               and x["table"] == "debye" and x["measure"] == "band_error" and x["level"] == 0.01]
    return found


def test_smallest_order_does_not_assume_monotone_errors():
    rows = mo.smallest_orders([fake(1, "fail"), fake(2, "borderline"), fake(3, "pass", False),
                               fake(4, "pass"), fake(5, "fail")])
    found = pick(rows)
    assert found["min_r"] == 4 and found["borderline_below"] == "2"
    assert found["orders_tested"] == "1-5 (5)"
    assert pick(mo.smallest_orders([fake(1, "fail"), fake(2, "borderline")]))["min_r"] is None


def test_pairwise_comparison_separates_one_sided_passes():
    records = []
    for group, (vf, fixed) in {"A": (3, 5), "B": (4, 4), "C": (None, 6), "D": (2, None),
                               "E": (None, None)}.items():
        for procedure, r in (("vf_log", vf), ("fixed_log", fixed)):
            records += [fake(k, "pass" if k == r else "fail", procedure=procedure, group=group)
                        for k in range(1, 7)]
    out = mo.compare(mo.smallest_orders(records), "final_base", "debye", "band_error", 0.01,
                     "vf_log", "fixed_log")
    assert out["groups"] == 5 and out["median_difference"] == -1
    assert out["counts"] == {"first_smaller": 1, "tie": 1, "second_smaller": 0,
                             "first_only": 1, "second_only": 1, "neither": 1}


def test_case_counts_match_the_adr_0008_addendum():
    dev = {f"d{i}": [f"d{i}"] for i in range(5)}
    final = {f"f{i}": [f"f{i}"] for i in range(36)}
    counts = {name: len(mo.case_plan([name], dev, final, None)) for name in mo.EXPERIMENTS}
    assert counts == {"dev_base": 960, "dev_nodes": 160, "dev_start": 160, "final_base": 6912}
    vf = sum(c["procedure"] in mo.VF_PROCEDURES
             for c in mo.case_plan(list(mo.EXPERIMENTS), dev, final, None))
    assert vf == 2784  # unchanged VF cases: 200 * 2784 = 556800 LS steps at most
    ids = [mo.case_id(c) for c in mo.case_plan(list(mo.EXPERIMENTS), dev, final, None)]
    assert len(set(ids)) == len(ids)


def test_run_recovers_exact_debye_tissue_and_resumes_without_recomputing(tmp_path, monkeypatch):
    monkeypatch.setattr(mo, "GRID_CELLS", (16, 32))
    monkeypatch.setattr(mo, "BAND_NODES", (16, 32))
    csv = tmp_path / "table.csv"
    gabriel.write_csv([AIR, row("Blood", *DEBYE), row("Synthetic Cole", *COLE)], csv)
    runs = tmp_path / "runs"
    common = ["--csv", str(csv), "--runs-dir", str(runs), "--experiments", "dev_base",
              "--orders", "1", "2", "3"]
    assert mo.main(common) == 0
    [first] = list(runs.iterdir())
    record = json.loads((first / "provenance.json").read_text(encoding="utf-8"))
    assert record["status"] == "completed"
    assert len(list((first / "cases").glob("*.json"))) == 3 * 6  # one dev group, no final
    assert record["outcome"]["summary"]["cases"] == 18
    rows = list(__import__("csv").DictReader(open(first / "min_order.csv", encoding="utf-8")))
    for procedure in ("vf_log", "quadvf_band"):
        [cell] = [x for x in rows if x["procedure"] == procedure and x["table"] == "debye"
                  and x["measure"] == "max_relative_error" and x["level"] == "0.001"]
        assert cell["min_r"] == "2" and cell["group"] == "Blood"
    assert not any(x["experiment"] == "final_base" for x in rows)

    assert mo.main(common + ["--resume-from", str(first)]) == 0
    second = next(p for p in runs.iterdir() if p != first)
    again = json.loads((second / "provenance.json").read_text(encoding="utf-8"))
    assert again["outcome"]["reused_cases"] == 18
    case = json.loads(next((second / "cases").glob("*vf_log*r02.json")).read_text())
    assert case["reused_from"] == record["run_id"]
    assert (second / "min_order.csv").read_text() == (first / "min_order.csv").read_text()

    with pytest.raises(SystemExit):  # other orders mean other settings: no silent reuse
        mo.main(["--csv", str(csv), "--runs-dir", str(runs), "--experiments", "dev_base",
                 "--orders", "1", "2", "--resume-from", str(first)])
