"""Checks of the Gabriel tissue model against independent formulas and published values."""
import hashlib
import io
from pathlib import Path

import numpy as np
import pytest

from vfdebye import gabriel

# Rows of AL/OE-TR-1996-0037 as printed on WebNIR (data/README.md), in table units.
BLOOD = ["4", "0.7", "56", "8.377", "0.1", "5200", "132.63", "0.1",
         "0", "159.16", "0.2", "0", "15.915", "0"]
MUSCLE = ["4", "0.2", "50", "7.234", "0.1", "7000", "353.68", "0.1",
          "1.2e+6", "318.31", "0.1", "2.5e+7", "2.274", "0"]
AIR = ["1", "0", "0", "0", "1", "0", "0", "1", "0", "0", "1", "0", "0", "1"]

# Floating-point agreement between two evaluations of the same closed form.
RTOL = 1e-12
DATA_CSV = Path(__file__).resolve().parents[1] / "data/processed/gabriel_parameters.csv"


def row(**changes):
    values = list(MUSCLE)
    names = gabriel.CSV_HEADER[1:]
    for key, value in changes.items():
        values[names.index(key)] = value
    return values


def test_tau_is_converted_from_ps_ns_us_ms_to_seconds():
    tissue = gabriel.tissue_from_row("Muscle", MUSCLE)
    assert tissue.tau == pytest.approx((7.234e-12, 353.68e-9, 318.31e-6, 2.274e-3), rel=RTOL)
    assert gabriel.tau_to_seconds([1, 1, 1, 1]) == (1e-12, 1e-9, 1e-6, 1e-3)


@pytest.mark.parametrize(
    ("name", "values", "eps_real", "sigma"),
    [("Blood", BLOOD, 61.36, 1.538), ("Muscle", MUSCLE, 55.03, 0.943)],
)
def test_control_values_at_900_mhz(name, values, eps_real, sigma):
    # Values recomputed for ADR-0004 (2026-11-07), printed to 4 significant digits.
    tissue = gabriel.tissue_from_row(name, values)
    f = 900e6
    eps = gabriel.permittivity(tissue, gabriel.laplace_variable(f))
    assert eps.real == pytest.approx(eps_real, abs=0.005)
    assert gabriel.conductivity(tissue, f) == pytest.approx(sigma, abs=0.0005)


def test_alpha_zero_gives_the_sum_of_debye_poles():
    # With alpha_n = 0 each term is d/(1 + s tau) = (d/tau)/(s + 1/tau): a real pole -1/tau.
    values = row(alpha_1="0", alpha_2="0", alpha_3="0", alpha_4="0")
    tissue = gabriel.tissue_from_row("synthetic", values)
    s = np.concatenate([gabriel.laplace_variable(np.logspace(0, 11, 50)), [1e3 + 2e8j, 5e9 + 0j]])
    expected = sum((d / t) / (s + 1 / t) for d, t in zip(tissue.delta_eps, tissue.tau, strict=True))
    assert np.allclose(gabriel.strictly_proper_part(tissue, s), expected, rtol=1e-10, atol=0)


def test_real_system_has_conjugate_symmetry():
    tissue = gabriel.tissue_from_row("Muscle", MUSCLE)
    s = np.array([1j * 2e7, 3e6 + 4e9j, 1e10 - 2e9j, 5e8 + 0j])
    h = gabriel.strictly_proper_part(tissue, s)
    assert np.allclose(gabriel.strictly_proper_part(tissue, s.conj()), h.conj(), rtol=RTOL, atol=0)
    assert gabriel.strictly_proper_part(tissue, 5e8).imag == 0


def test_strictly_proper_part_vanishes_at_infinity():
    tissue = gabriel.tissue_from_row("Muscle", MUSCLE)
    total = sum(tissue.delta_eps)
    assert abs(gabriel.strictly_proper_part(tissue, 1j * 1e18)) < 1e-5 * total
    assert gabriel.strictly_proper_part(tissue, 0).real == pytest.approx(total, rel=RTOL)


def test_permittivity_splits_into_exact_terms_and_h():
    tissue = gabriel.tissue_from_row("Blood", BLOOD)
    s = gabriel.laplace_variable(np.array([1e7, 1e9, 1e10]))
    exact = tissue.eps_inf + tissue.sigma_i / (s * gabriel.EPS0)
    assert np.allclose(gabriel.exact_part(tissue, s), exact, rtol=RTOL, atol=0)
    assert np.allclose(
        gabriel.permittivity(tissue, s), exact + gabriel.strictly_proper_part(tissue, s),
        rtol=RTOL, atol=0,
    )


def test_conduction_only_material_has_constant_conductivity():
    # sigma = omega eps0 eps'' with eps = eps' - j eps'': sign and units of the conduction term.
    values = ["2", "0.5"] + ["0", "0", "1"] * 4
    tissue = gabriel.tissue_from_row("conductor", values)
    f = np.logspace(3, 10, 8)
    assert np.allclose(gabriel.conductivity(tissue, f), 0.5, rtol=RTOL, atol=0)


def test_air_has_no_dispersion_and_unit_permittivity():
    air = gabriel.tissue_from_row("Air", AIR)
    s = gabriel.laplace_variable([1e6, 1e9])
    assert not air.is_dispersive
    assert np.all(gabriel.strictly_proper_part(air, s) == 0)
    assert np.all(gabriel.permittivity(air, s) == 1)


@pytest.mark.parametrize(
    ("values", "message"),
    [
        (row(delta_eps_2="nan"), "finite"),
        (row(sigma_i_S_per_m="-0.1"), "sigma_i"),
        (row(eps_inf="0"), "eps_inf"),
        (row(delta_eps_1="-1"), "non-negative"),
        (row(alpha_3="1"), "alpha_3"),
        (row(alpha_1="-0.1"), "alpha_1"),
        (row(tau_4_ms="0"), "tau_4"),
        (row(tau_2_ns="abc"), "not a number"),
        (MUSCLE[:-1], "expected 14"),
    ],
)
def test_invalid_rows_raise(values, message):
    with pytest.raises(ValueError, match=message):
        gabriel.tissue_from_row("bad", values)


def test_empty_name_raises():
    with pytest.raises(ValueError, match="empty"):
        gabriel.tissue_from_row("  ", MUSCLE)


@pytest.mark.parametrize("f", [0.0, -1e6, float("nan"), float("inf")])
def test_invalid_frequency_raises(f):
    with pytest.raises(ValueError, match="frequencies"):
        gabriel.laplace_variable([1e6, f])


def test_conduction_term_rejects_s_zero_and_nonfinite_s():
    tissue = gabriel.tissue_from_row("Blood", BLOOD)
    with pytest.raises(ValueError, match="s = 0"):
        gabriel.permittivity(tissue, [0j, 1j])
    with pytest.raises(ValueError, match="finite"):
        gabriel.strictly_proper_part(tissue, [complex("nan")])


def test_duplicate_groups_keep_every_name_in_order():
    tissues = [
        gabriel.tissue_from_row("Aorta", MUSCLE),
        gabriel.tissue_from_row("Blood", BLOOD),
        gabriel.tissue_from_row("Blood vessel", MUSCLE),
    ]
    assert gabriel.duplicate_groups(tissues) == [["Aorta", "Blood vessel"]]


def page(header, rows):
    cells = "".join(f"<th>{h}</th>" for h in header)
    body = "".join("<tr>" + "".join(f"<td> {v} </td>" for v in r) + "</tr>" for r in rows)
    return f"<p>x</p><table><tr><th>Other</th></tr></table><table><tr>{cells}</tr>{body}</table>"


def test_parse_webnir_table_returns_published_strings():
    rows = gabriel.parse_webnir_table(page(gabriel.WEBNIR_HEADER, [["Blood", *BLOOD]]))
    assert rows == [["Blood", *BLOOD]]


def test_parse_webnir_table_rejects_changed_header_and_missing_table():
    header = list(gabriel.WEBNIR_HEADER)
    header[4] = "τ1 (ns)"
    with pytest.raises(ValueError, match="header changed"):
        gabriel.parse_webnir_table(page(header, [["Blood", *BLOOD]]))
    with pytest.raises(ValueError, match="no table"):
        gabriel.parse_webnir_table("<table><tr><td>1</td></tr></table>")


def test_csv_round_trip_and_repeated_names(tmp_path):
    path = tmp_path / "t.csv"
    gabriel.write_csv([["Blood", *BLOOD], ["Muscle", *MUSCLE]], path)
    assert b"\r" not in path.read_bytes()
    assert [t.name for t in gabriel.read_csv(path)] == ["Blood", "Muscle"]
    gabriel.write_csv([["Blood", *BLOOD], ["Blood", *MUSCLE]], path)
    with pytest.raises(ValueError, match="repeated"):
        gabriel.read_csv(path)
    path.write_text("a,b\n", encoding="utf-8")
    with pytest.raises(ValueError, match="header"):
        gabriel.read_csv(path)


def load_fetch_script():
    from importlib.util import module_from_spec, spec_from_file_location

    spec = spec_from_file_location("fetch_gabriel", DATA_CSV.parents[1] / "fetch_gabriel.py")
    fetch = module_from_spec(spec)
    spec.loader.exec_module(fetch)
    return fetch


def test_fetch_replaces_verified_files_only_when_the_checksum_matches(tmp_path, monkeypatch):
    fetch = load_fetch_script()
    raw, csv = tmp_path / "raw" / "page.html", tmp_path / "processed" / "table.csv"
    raw.parent.mkdir()
    csv.parent.mkdir()
    raw.write_text("verified page", encoding="utf-8")
    csv.write_text("verified table", encoding="utf-8")
    html = page(gabriel.WEBNIR_HEADER, [["Blood", *BLOOD]])
    monkeypatch.setattr(fetch, "DATA", tmp_path)
    monkeypatch.setattr(fetch, "RAW", raw)
    monkeypatch.setattr(fetch, "CSV", csv)
    monkeypatch.setattr(fetch.urllib.request, "urlopen",
                        lambda url, timeout: io.BytesIO(html.encode("utf-8")))

    monkeypatch.setattr(fetch, "EXPECTED_CSV_SHA256", "0" * 64)
    assert fetch.main([]) == 1
    assert raw.read_text(encoding="utf-8") == "verified page"
    assert csv.read_text(encoding="utf-8") == "verified table"
    assert (tmp_path / "raw" / "page.html.new").is_file()
    assert (tmp_path / "processed" / "table.csv.new").is_file()

    expected = tmp_path / "expected.csv"
    gabriel.write_csv([["Blood", *BLOOD]], expected)
    monkeypatch.setattr(fetch, "EXPECTED_CSV_SHA256",
                        hashlib.sha256(expected.read_bytes()).hexdigest())
    assert fetch.main([]) == 0
    assert raw.read_text(encoding="utf-8") == html
    assert csv.read_bytes() == expected.read_bytes()
    assert sorted(p.name for p in tmp_path.rglob("*.new")) == []


def test_downloaded_table_matches_the_recorded_checksum():
    if not DATA_CSV.is_file():
        pytest.skip("NOT RUN: data/processed/gabriel_parameters.csv missing; "
                    "run uv run python data/fetch_gabriel.py")
    fetch = load_fetch_script()
    assert hashlib.sha256(DATA_CSV.read_bytes()).hexdigest() == fetch.EXPECTED_CSV_SHA256
    tissues = gabriel.read_csv(DATA_CSV)
    assert len(tissues) == 57
    assert sum(t.is_dispersive for t in tissues) == 55
    assert len(gabriel.duplicate_groups(tissues)) == 10
