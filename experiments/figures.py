"""Seminar figures from recorded runs of B6 (min_order) and A7 (convergence).

Run from the repository root, naming the recorded runs the figures are drawn from:

    uv run python experiments/figures.py \
        --min-order-run results/runs/<id>-min_order --convergence-run results/runs/<id>-convergence

Figures (PDF for the seminar, PNG for a quick look), with Croatian labels:

1. fig_udio_skupina: share of final groups with an acceptable model of order at most r, per
   procedure, measure and accuracy level (general table; for VF it equals the Debye table);
2. fig_pogreska_red: both error measures against r for one final group (default Liver);
3. fig_putanja: delta_k and q_k along the A7 trajectory of vf_log for Blood at three orders;
4. fig_raspon: number of development groups whose VF loop settles, per start range and r.

Colours: categorical slots 1-4 of the dataviz reference palette and its blue ordinal steps
250/450/650, validated for a white surface. Aqua and yellow are below 3:1 contrast, so every
series is named in a legend and all plotted values are written to figures.txt as tables.
Everything is recorded with vfdebye.provenance in results/runs/<run_id>/ (outside Git).
"""
from __future__ import annotations

import argparse
import csv
import io
import json
import sys
from pathlib import Path

import matplotlib

matplotlib.use("Agg")
import matplotlib.pyplot as plt  # noqa: E402
import numpy as np  # noqa: E402

from vfdebye import provenance  # noqa: E402

SERIES = {  # procedure -> (Croatian label, categorical slot colour)
    "vf_log": ("VF, log. čvorovi", "#2a78d6"),
    "quadvf_band": ("QuadVF, pojas", "#eb6834"),
    "fixed_log_wide": ("fiksni polovi, 1 kHz–100 GHz", "#1baf7a"),
    "fixed_log": ("fiksni polovi, 10 MHz–10 GHz", "#eda100"),
}
ORDINAL = ("#104281", "#2a78d6", "#86b6ef")  # blue 650 / 450 / 250: dark = first item
TEXT, TEXT_2, GRID = "#0b0b0b", "#52514e", "#e4e3df"
LEVELS = (("0.05", "5 %"), ("0.01", "1 %"), ("0.001", "0,1 %"))
MEASURES = (("max_relative_error", "najveća relativna pogreška"),
            ("band_error", "relativna pogreška na pojasu"))
STARTS = (("1e+07-1e+10", "10 MHz–10 GHz"), ("1e+03-1e+11", "1 kHz–100 GHz"),
          ("1e+00-1e+12", "1 Hz–1 THz"))
ORDERS = np.arange(1, 33)


def style() -> None:
    plt.rcParams.update({
        "font.size": 8, "axes.titlesize": 8, "axes.labelsize": 8, "legend.fontsize": 7.5,
        "xtick.labelsize": 7, "ytick.labelsize": 7, "axes.edgecolor": GRID,
        "axes.labelcolor": TEXT_2, "xtick.color": TEXT_2, "ytick.color": TEXT_2,
        "axes.titlecolor": TEXT, "text.color": TEXT, "axes.grid": True, "grid.color": GRID,
        "grid.linewidth": 0.5, "axes.linewidth": 0.5, "axes.spines.top": False,
        "axes.spines.right": False, "lines.linewidth": 1.5, "lines.solid_capstyle": "round",
        "lines.solid_joinstyle": "round", "figure.facecolor": "white",
        "axes.facecolor": "white", "savefig.facecolor": "white", "pdf.fonttype": 42,
    })


def save(fig, directory: Path, name: str) -> list[str]:
    fig.savefig(directory / f"{name}.pdf", bbox_inches="tight")
    fig.savefig(directory / f"{name}.png", dpi=200, bbox_inches="tight")
    plt.close(fig)
    return [f"{name}.pdf", f"{name}.png"]


def share_of_groups(rows: list[dict]) -> dict:
    """{(measure, level, procedure): percent of final groups with min_r <= r, for r = 1..32}."""
    out = {}
    for measure, _ in MEASURES:
        for level, _ in LEVELS:
            for procedure in SERIES:
                found = [row["min_r"] for row in rows if row["experiment"] == "final_base"
                         and row["table"] == "general" and row["measure"] == measure
                         and row["level"] == level and row["procedure"] == procedure]
                if not found:
                    raise ValueError(f"no final_base rows for {measure} {level} {procedure}")
                r = np.array([int(x) if x else 10**6 for x in found])
                out[measure, level, procedure] = 100 * np.array([(r <= k).mean() for k in ORDERS])
    return out


def figure_share(shares: dict, directory: Path, table: io.StringIO) -> list[str]:
    fig, axes = plt.subplots(2, 3, figsize=(6.4, 3.9), sharex=True, sharey=True)
    for i, (measure, measure_label) in enumerate(MEASURES):
        for j, (level, level_label) in enumerate(LEVELS):
            ax = axes[i, j]
            for procedure, (label, colour) in SERIES.items():
                ax.step(ORDERS, shares[measure, level, procedure], where="post", color=colour,
                        label=label)
            ax.set_title(f"{measure_label}, {level_label}", loc="left")
            ax.set_xlim(0.5, 32.5)
            ax.set_ylim(-3, 103)
            ax.set_xticks([1, 8, 16, 24, 32])
            ax.set_yticks([0, 50, 100])
            if i == 1:
                ax.set_xlabel("red r")
            if j == 0:
                ax.set_ylabel("skupina s modelom (%)")
    handles, labels = axes[0, 0].get_legend_handles_labels()
    fig.legend(handles, labels, loc="upper center", ncol=4, frameon=False,
               bbox_to_anchor=(0.5, 1.0))
    fig.tight_layout(rect=(0, 0, 1, 0.93))
    table.write("fig_udio_skupina: postotak završnih skupina s prihvatljivim modelom reda <= r "
                "(opća tablica)\n")
    for (measure, level, procedure), values in shares.items():
        table.write(f"{measure} {level} {procedure}: " + " ".join(f"{v:.0f}" for v in values)
                    + "\n")
    return save(fig, directory, "fig_udio_skupina")


def group_errors(cases: Path, group: str) -> dict:
    """{procedure: (orders, fine max relative error, fine band error)} of eligible candidates."""
    out = {}
    safe = "".join(c if c.isalnum() else "_" for c in group)
    for procedure in SERIES:
        start = "1e+03-1e+11" if procedure.endswith("_wide") else "1e+07-1e+10"
        pts = []
        for path in sorted(cases.glob(f"final_base__{safe}__{procedure}__N240__{start}__r*.json")):
            rec = json.loads(path.read_text(encoding="utf-8"))
            r = rec["r"]
            if rec["eligible_general"]:
                errors = rec["candidate"]["errors"]
                pts.append((r, errors["max_relative_error"]["fine"],
                            errors["band_error"]["fine"]))
        out[procedure] = tuple(np.array(column) for column in zip(*pts, strict=True)) if pts \
            else (np.array([]), np.array([]), np.array([]))
    return out


def figure_errors(errors: dict, group: str, directory: Path, table: io.StringIO) -> list[str]:
    fig, axes = plt.subplots(1, 2, figsize=(6.4, 2.6), sharey=True)
    for ax, (k, (_, measure_label)) in zip(axes, enumerate(MEASURES, start=1), strict=True):
        for level, level_label in LEVELS:
            ax.axhline(float(level), color=TEXT_2, linewidth=0.5)
            ax.text(32.6, float(level), level_label, va="center", ha="left", fontsize=7,
                    color=TEXT_2)
        for procedure, (label, colour) in SERIES.items():
            orders, *values = errors[procedure]
            ax.plot(orders, values[k - 1], color=colour, marker="o", markersize=3,
                    markeredgecolor="white", markeredgewidth=0.6, label=label)
        ax.set_yscale("log")
        ax.set_xlim(0.5, 32.5)
        ax.set_xticks([1, 8, 16, 24, 32])
        ax.set_xlabel("red r")
        ax.set_title(measure_label, loc="left")
    axes[0].set_ylabel(f"relativna pogreška ({group})")
    handles, labels = axes[0].get_legend_handles_labels()
    fig.legend(handles, labels, loc="upper center", ncol=4, frameon=False,
               bbox_to_anchor=(0.5, 1.0))
    fig.tight_layout(rect=(0, 0.06, 1, 0.9))
    fig.text(0.01, 0.0, "Prikazani su samo prihvatljivi kandidati; linija prestaje gdje petlja "
             "gubi rang ili je uvjetovanost veća od 10¹².", fontsize=6.5, color=TEXT_2)
    table.write(f"\nfig_pogreska_red: {group}, prihvatljivi kandidati (r, najveća relativna, "
                "pojasna; fina procjena)\n")
    for procedure, (orders, rel, band) in errors.items():
        table.write(f"{procedure}: " + "; ".join(
            f"{r} {a:.3e} {b:.3e}" for r, a, b in zip(orders, rel, band, strict=True)) + "\n")
    return save(fig, directory, "fig_pogreska_red")


def figure_trajectory(npz: Path, directory: Path, table: io.StringIO,
                      orders=(4, 7, 10), steps: int = 100) -> list[str]:
    fig, axes = plt.subplots(1, 2, figsize=(6.4, 2.5), sharex=True)
    for ax in axes:  # fixed before plotting, so an all-zero synthetic series cannot collapse it
        ax.set_yscale("log")
        ax.set_ylim(1e-16, 1e2)
        ax.set_yticks([1e-16, 1e-12, 1e-8, 1e-4, 1.0])
    table.write("\nfig_putanja: Blood, vf_log, početni polovi 10 MHz–10 GHz\n")
    with np.load(npz) as data:
        for r, colour in zip(orders, ORDINAL[::-1], strict=True):
            key = f"Blood|vf_log|1e+07-1e+10|{r}"
            for ax, name in zip(axes, ("delta", "q"), strict=True):
                values = data[f"{key}|{name}"][:steps]
                k = np.arange(1, values.size + 1)
                ax.plot(k, np.where(values > 0, values, np.nan), color=colour,
                            label=f"r = {r}")
                table.write(f"r={r} {name}: " + " ".join(f"{v:.2e}" for v in values) + "\n")
    titles = (r"$\delta_k$ (relativni pomak polova)", r"$q_k=\max_i\,|\tilde d(\xi_i)-1|$")
    for ax, label in zip(axes, titles, strict=True):
        ax.axhline(1e-8, color=TEXT_2, linewidth=0.5)
        ax.text(steps, 1e-8, " prag 10⁻⁸", va="bottom", ha="right", fontsize=7, color=TEXT_2)
        ax.set_title(label, loc="left")
        ax.set_xlabel("korak k")
        ax.set_xlim(0, steps)
    axes[0].legend(frameon=False, loc="upper right")
    fig.tight_layout()
    return save(fig, directory, "fig_putanja")


def figure_start(rows: list[dict], directory: Path, table: io.StringIO) -> list[str]:
    fig, axes = plt.subplots(1, 2, figsize=(6.4, 2.4), sharey=True)
    table.write("\nfig_raspon: broj razvojnih skupina s ustaljenom petljom (od 5)\n")
    for ax, procedure in zip(axes, ("vf_log", "quadvf_band"), strict=True):
        for (start, label), colour in zip(STARTS, ORDINAL, strict=True):
            counts = []
            for r in ORDERS:
                settled = [row for row in rows if row["method"] == procedure
                           and row["r"] == r and start_key(row) == start
                           and row["accepted"]["stop_reason"].endswith("settled")]
                counts.append(len(settled))
            ax.plot(ORDERS, counts, color=colour, marker="o", markersize=3,
                    markeredgecolor="white", markeredgewidth=0.6, label=label)
            table.write(f"{procedure} {start}: " + " ".join(map(str, counts)) + "\n")
        ax.set_title(SERIES[procedure][0], loc="left")
        ax.set_xlabel("red r")
        ax.set_xlim(0.5, 32.5)
        ax.set_xticks([1, 8, 16, 24, 32])
        ax.set_yticks(range(6))
    axes[0].set_ylabel("ustaljenih skupina (od 5)")
    handles, labels = axes[0].get_legend_handles_labels()
    fig.legend(handles, labels, title=None, loc="upper center", ncol=3, frameon=False,
               bbox_to_anchor=(0.5, 1.0))
    fig.text(0.01, 0.97, "početni polovi:", fontsize=7.5, color=TEXT_2, va="top")
    fig.tight_layout(rect=(0, 0, 1, 0.88))
    return save(fig, directory, "fig_raspon")


def start_key(row: dict) -> str:
    return f"{row['start_hz'][0]:.0e}-{row['start_hz'][1]:.0e}"


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    parser.add_argument("--min-order-run", type=Path, required=True)
    parser.add_argument("--convergence-run", type=Path, required=True)
    parser.add_argument("--group", default="Liver")
    parser.add_argument("--runs-dir", type=Path, default=provenance.RUNS_DIR)
    args = parser.parse_args(argv)
    mo, cv = args.min_order_run, args.convergence_run
    inputs = [mo / "provenance.json", mo / "min_order.csv", cv / "provenance.json",
              cv / "convergence.json", cv / "convergence_iterations.npz"]
    safe = "".join(c if c.isalnum() else "_" for c in args.group)
    inputs += sorted((mo / "cases").glob(f"final_base__{safe}__*.json"))
    missing = [str(p) for p in inputs[:5] if not p.is_file()]
    if missing or len(inputs) == 5:
        parser.error(f"missing recorded results: {missing or 'cases of ' + args.group}")
    source = {"min_order_run": json.loads(inputs[0].read_text(encoding="utf-8"))["run_id"],
              "convergence_run": json.loads(inputs[2].read_text(encoding="utf-8"))["run_id"]}
    settings = source | {"group": args.group, "palette": {k: v[1] for k, v in SERIES.items()},
                         "ordinal": ORDINAL, "trajectory_orders": (4, 7, 10)}
    style()
    with provenance.run("figures", settings=settings, inputs=inputs,
                        runs_dir=args.runs_dir) as record:
        with open(mo / "min_order.csv", encoding="utf-8") as handle:
            rows = list(csv.DictReader(handle))
        convergence_rows = json.loads((cv / "convergence.json").read_text(encoding="utf-8"))
        table = io.StringIO()
        table.write(f"izvor: {source['min_order_run']} i {source['convergence_run']}\n")
        artifacts = figure_share(share_of_groups(rows), record.dir, table)
        artifacts += figure_errors(group_errors(mo / "cases", args.group), args.group,
                                   record.dir, table)
        artifacts += figure_trajectory(cv / "convergence_iterations.npz", record.dir, table)
        artifacts += figure_start(convergence_rows, record.dir, table)
        (record.dir / "figures.txt").write_text(table.getvalue(), encoding="utf-8")
        record.update(artifacts=artifacts + ["figures.txt"])
    print(f"run {record.run_id} -> {record.dir}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
