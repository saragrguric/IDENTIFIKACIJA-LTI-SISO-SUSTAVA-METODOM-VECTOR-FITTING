"""Gabriel's four-term Cole-Cole model of tissue permittivity (ADR-0004).

eps(s) = eps_inf + sum_n d_eps_n / (1 + (s tau_n)^(1 - alpha_n)) + sigma_i / (s eps0),
with s = 2j*pi*f, f in Hz. eps is relative and dimensionless, eps = eps' - j eps''.
The fitted function is the strictly proper part H(s) = eps(s) - eps_inf - sigma_i/(s eps0);
the two exact terms are never approximated.

Parameters come from C. Gabriel and S. Gabriel, AL/OE-TR-1996-0037 (1996), as transcribed
by WebNIR (see data/README.md). The table gives tau_1..tau_4 in ps, ns, us and ms; this
module stores every tau in seconds.

A term with d_eps_n = 0 is absent: it contributes exactly zero, so its tau_n and alpha_n are
not constrained (air and vacuum list alpha_n = 1 there). Every present term needs tau_n > 0
and 0 <= alpha_n < 1.
"""
from __future__ import annotations

import csv
import math
from collections.abc import Iterable, Sequence
from dataclasses import dataclass
from html.parser import HTMLParser
from pathlib import Path

import numpy as np

# Vacuum permittivity in F/m (CODATA 2018). Fixed here so results do not depend on the
# SciPy version's CODATA edition.
EPS0 = 8.8541878128e-12
# Seconds per table unit of tau_1..tau_4: ps, ns, us, ms.
TAU_UNITS = (1e-12, 1e-9, 1e-6, 1e-3)
N_TERMS = 4

# Column names of the canonical CSV, values in the units printed by the source table.
CSV_HEADER = (
    "tissue", "eps_inf", "sigma_i_S_per_m",
    "delta_eps_1", "tau_1_ps", "alpha_1",
    "delta_eps_2", "tau_2_ns", "alpha_2",
    "delta_eps_3", "tau_3_us", "alpha_3",
    "delta_eps_4", "tau_4_ms", "alpha_4",
)
# Header of the parameter table on the WebNIR page, used to recognise it.
WEBNIR_HEADER = (
    "Tissue", "ε∞", "σi (S/m)",
    "Δε1", "τ1 (ps)", "α1", "Δε2", "τ2 (ns)", "α2",
    "Δε3", "τ3 (µs)", "α3", "Δε4", "τ4 (ms)", "α4",
)


@dataclass(frozen=True)
class Tissue:
    """One validated table row; tau in seconds, sigma_i in S/m."""

    name: str
    eps_inf: float
    sigma_i: float
    delta_eps: tuple[float, ...]
    tau: tuple[float, ...]
    alpha: tuple[float, ...]

    @property
    def parameters(self) -> tuple[float, ...]:
        return (self.eps_inf, self.sigma_i, *self.delta_eps, *self.tau, *self.alpha)

    @property
    def is_dispersive(self) -> bool:
        return any(d > 0 for d in self.delta_eps)


def tau_to_seconds(tau_table: Sequence[float]) -> tuple[float, ...]:
    """Convert tau_1..tau_4 from the table units (ps, ns, us, ms) to seconds."""
    if len(tau_table) != N_TERMS:
        raise ValueError(f"expected {N_TERMS} relaxation times, got {len(tau_table)}")
    return tuple(t * unit for t, unit in zip(tau_table, TAU_UNITS, strict=True))


def tissue_from_row(name: str, values: Sequence[float | str]) -> Tissue:
    """Validate one row in table units: eps_inf, sigma_i, then (d_eps, tau, alpha) x 4."""
    name = name.strip()
    if not name:
        raise ValueError("tissue name is empty")
    if len(values) != 2 + 3 * N_TERMS:
        raise ValueError(f"{name}: expected {2 + 3 * N_TERMS} parameters, got {len(values)}")
    try:
        x = [float(v) for v in values]
    except ValueError as error:
        raise ValueError(f"{name}: parameter is not a number ({error})") from None
    if not all(math.isfinite(v) for v in x):
        raise ValueError(f"{name}: parameters must be finite")
    eps_inf, sigma_i = x[0], x[1]
    delta_eps, tau_table, alpha = x[2::3], x[3::3], x[4::3]
    if eps_inf <= 0:
        raise ValueError(f"{name}: eps_inf must be positive, got {eps_inf}")
    if sigma_i < 0:
        raise ValueError(f"{name}: sigma_i must be non-negative, got {sigma_i}")
    for n, (d, t, a) in enumerate(zip(delta_eps, tau_table, alpha, strict=True), start=1):
        if d < 0 or t < 0:
            raise ValueError(f"{name}: delta_eps_{n} and tau_{n} must be non-negative")
        if d > 0 and not (t > 0 and 0 <= a < 1):
            raise ValueError(
                f"{name}: term {n} needs tau_{n} > 0 and 0 <= alpha_{n} < 1, got "
                f"tau={t}, alpha={a}"
            )
    return Tissue(name, eps_inf, sigma_i, tuple(delta_eps), tau_to_seconds(tau_table), tuple(alpha))


def read_csv(path: str | Path) -> list[Tissue]:
    """Load the canonical CSV written by data/fetch_gabriel.py; row order is kept."""
    with open(path, newline="", encoding="utf-8") as handle:
        rows = list(csv.reader(handle))
    if not rows or tuple(rows[0]) != CSV_HEADER:
        raise ValueError(f"{path}: header does not match vfdebye.gabriel.CSV_HEADER")
    tissues = [tissue_from_row(row[0], row[1:]) for row in rows[1:]]
    names = [t.name for t in tissues]
    repeated = sorted({n for n in names if names.count(n) > 1})
    if repeated:
        raise ValueError(f"{path}: repeated tissue names {repeated}")
    return tissues


def write_csv(rows: Iterable[Sequence[str]], path: str | Path) -> None:
    """Write table rows verbatim (published strings) with LF line ends on every system."""
    with open(path, "w", newline="", encoding="utf-8") as handle:
        writer = csv.writer(handle, lineterminator="\n")
        writer.writerow(CSV_HEADER)
        writer.writerows(rows)


class _TableCells(HTMLParser):
    def __init__(self) -> None:
        super().__init__()
        self.tables: list[list[list[str]]] = []
        self._cell: list[str] | None = None

    def handle_starttag(self, tag: str, attrs: object) -> None:
        if tag == "table":
            self.tables.append([])
        elif tag == "tr" and self.tables:
            self.tables[-1].append([])
        elif tag in ("td", "th") and self.tables and self.tables[-1]:
            self._cell = []

    def handle_endtag(self, tag: str) -> None:
        if tag in ("td", "th") and self._cell is not None:
            self.tables[-1][-1].append(" ".join("".join(self._cell).split()))
            self._cell = None

    def handle_data(self, data: str) -> None:
        if self._cell is not None:
            self._cell.append(data)


def parse_webnir_table(page: str) -> list[list[str]]:
    """Return the parameter rows of the WebNIR page as published strings, header excluded.

    The table is recognised by its exact header (names and units). A changed header raises
    ValueError instead of guessing the columns.
    """
    parser = _TableCells()
    parser.feed(page)
    for table in parser.tables:
        if table and table[0] and table[0][0] == WEBNIR_HEADER[0] and len(table[0]) > 1 \
                and table[0][1] == WEBNIR_HEADER[1]:
            if tuple(table[0]) != WEBNIR_HEADER:
                raise ValueError(f"parameter table header changed: {table[0]}")
            rows = [row for row in table[1:] if row]
            bad = [row for row in rows if len(row) != len(WEBNIR_HEADER)]
            if bad:
                raise ValueError(f"parameter rows with a wrong number of cells: {bad}")
            return rows
    raise ValueError("no table with the Gabriel parameter header was found")


def duplicate_groups(tissues: Iterable[Tissue]) -> list[list[str]]:
    """Groups (of two or more names) whose parameters are identical, in table order."""
    groups: dict[tuple[float, ...], list[str]] = {}
    for tissue in tissues:
        groups.setdefault(tissue.parameters, []).append(tissue.name)
    return [names for names in groups.values() if len(names) > 1]


def laplace_variable(f: np.ndarray | float) -> np.ndarray:
    """s = 2j*pi*f for frequencies f in Hz; f must be finite and positive."""
    f = np.asarray(f, dtype=float)
    if not np.all(np.isfinite(f)) or np.any(f <= 0):
        raise ValueError("frequencies must be finite and positive (Hz)")
    return 2j * np.pi * f


def _as_s(s: np.ndarray | complex) -> np.ndarray:
    s = np.asarray(s, dtype=complex)
    if not np.all(np.isfinite(s)):
        raise ValueError("s must be finite")
    return s


def strictly_proper_part(tissue: Tissue, s: np.ndarray | complex) -> np.ndarray:
    """H(s): the sum of the Cole-Cole terms, using the principal branch of the power.

    H(conj(s)) = conj(H(s)) away from the branch cut on the negative real axis.
    """
    s = _as_s(s)
    h = np.zeros_like(s)
    for d, t, a in zip(tissue.delta_eps, tissue.tau, tissue.alpha, strict=True):
        if d > 0:
            h += d / (1 + (s * t) ** (1 - a))
    return h


def exact_part(tissue: Tissue, s: np.ndarray | complex) -> np.ndarray:
    """eps_inf + sigma_i / (s eps0): the terms known exactly; s must be nonzero."""
    s = _as_s(s)
    if np.any(s == 0):
        raise ValueError("s = 0 is a pole of the conduction term")
    return tissue.eps_inf + tissue.sigma_i / (s * EPS0)


def permittivity(tissue: Tissue, s: np.ndarray | complex) -> np.ndarray:
    """Relative complex permittivity eps(s) = exact_part + strictly_proper_part."""
    return exact_part(tissue, s) + strictly_proper_part(tissue, s)


def conductivity(tissue: Tissue, f: np.ndarray | float) -> np.ndarray:
    """Total conductivity sigma = omega eps0 eps'' in S/m at frequencies f in Hz."""
    s = laplace_variable(f)
    return -(2 * np.pi * np.asarray(f, dtype=float)) * EPS0 * permittivity(tissue, s).imag
