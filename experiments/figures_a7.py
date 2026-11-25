"""Seminar figures of thread A from a recorded A7 run (experiments/convergence.py).

Run from the repository root, naming the recorded convergence run:

    uv run python experiments/figures_a7.py --convergence-run results/runs/<id>-convergence

Figures (PDF for the seminar, PNG for a quick look), with Croatian labels:

1. fig_putanja: delta_k and q_k along the trajectory of vf_log for Blood at r = 4, 7 and 10,
   initial poles on the band 10 MHz-10 GHz;
2. fig_raspon: number of development groups whose VF loop settles, per start range and r.

The run must contain all three start ranges for every order, as the A7 run
20261125T090048328276Z-convergence does. Colours are the blue ordinal steps 250/450/650 of the
dataviz reference palette, validated for a white surface; all plotted values are also written
to figures_a7.txt. Everything is recorded with vfdebye.provenance in results/runs/<run_id>/.
"""
from __future__ import annotations

import argparse
import io
import json
import sys
from pathlib import Path

import matplotlib

matplotlib.use("Agg")
import matplotlib.pyplot as plt  # noqa: E402
import numpy as np  # noqa: E402

from vfdebye import provenance  # noqa: E402

ORDINAL = ("#104281", "#2a78d6", "#86b6ef")  # blue 650 / 450 / 250: dark = first item
TEXT, TEXT_2, GRID = "#0b0b0b", "#52514e", "#e4e3df"
METHODS = (("vf_log", "VF, log. čvorovi"), ("quadvf_band", "QuadVF, pojas"))
STARTS = (("1e+07-1e+10", "10 MHz–10 GHz"), ("1e+03-1e+11", "1 kHz–100 GHz"),
          ("1e+00-1e+12", "1 Hz–1 THz"))
ORDERS = np.arange(1, 33)
TRAJECTORY_ORDERS = (4, 7, 10)
STEPS = 100


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


def figure_trajectory(npz: Path, directory: Path, table: io.StringIO) -> list[str]:
    fig, axes = plt.subplots(1, 2, figsize=(6.4, 2.5), sharex=True)
    for ax in axes:  # fixed before plotting, so an all-zero synthetic series cannot collapse it
        ax.set_yscale("log")
        ax.set_ylim(1e-16, 1e2)
        ax.set_yticks([1e-16, 1e-12, 1e-8, 1e-4, 1.0])
    table.write("fig_putanja: Blood, vf_log, početni polovi 10 MHz–10 GHz\n")
    with np.load(npz) as data:
        for r, colour in zip(TRAJECTORY_ORDERS, ORDINAL[::-1], strict=True):
            key = f"Blood|vf_log|1e+07-1e+10|{r}"
            for ax, name in zip(axes, ("delta", "q"), strict=True):
                values = data[f"{key}|{name}"][:STEPS]
                k = np.arange(1, values.size + 1)
                ax.plot(k, np.where(values > 0, values, np.nan), color=colour,
                        label=f"r = {r}")
                table.write(f"r={r} {name}: " + " ".join(f"{v:.2e}" for v in values) + "\n")
    titles = (r"$\delta_k$ (relativni pomak polova)", r"$q_k=\max_i\,|\tilde d(\xi_i)-1|$")
    for ax, label in zip(axes, titles, strict=True):
        ax.axhline(1e-8, color=TEXT_2, linewidth=0.5)
        ax.text(STEPS, 1e-8, " prag 10⁻⁸", va="bottom", ha="right", fontsize=7, color=TEXT_2)
        ax.set_title(label, loc="left")
        ax.set_xlabel("korak k")
        ax.set_xlim(0, STEPS)
    axes[0].legend(frameon=False, loc="upper right")
    fig.tight_layout()
    return save(fig, directory, "fig_putanja")


def start_key(row: dict) -> str:
    return f"{row['start_hz'][0]:.0e}-{row['start_hz'][1]:.0e}"


def figure_start(rows: list[dict], directory: Path, table: io.StringIO) -> list[str]:
    fig, axes = plt.subplots(1, 2, figsize=(6.4, 2.4), sharey=True)
    groups = len({row["group"] for row in rows})
    table.write(f"\nfig_raspon: broj razvojnih skupina s ustaljenom petljom (od {groups})\n")
    for ax, (method, method_label) in zip(axes, METHODS, strict=True):
        for (start, label), colour in zip(STARTS, ORDINAL, strict=True):
            counts = [sum(1 for row in rows if row["method"] == method and row["r"] == r
                          and start_key(row) == start
                          and row["accepted"]["stop_reason"].endswith("settled"))
                      for r in ORDERS]
            ax.plot(ORDERS, counts, color=colour, marker="o", markersize=3,
                    markeredgecolor="white", markeredgewidth=0.6, label=label)
            table.write(f"{method} {start}: " + " ".join(map(str, counts)) + "\n")
        ax.set_title(method_label, loc="left")
        ax.set_xlabel("red r")
        ax.set_xlim(0.5, 32.5)
        ax.set_xticks([1, 8, 16, 24, 32])
        ax.set_yticks(range(groups + 1))
    axes[0].set_ylabel(f"ustaljenih skupina (od {groups})")
    handles, labels = axes[0].get_legend_handles_labels()
    fig.legend(handles, labels, loc="upper center", ncol=3, frameon=False,
               bbox_to_anchor=(0.5, 1.0))
    fig.text(0.01, 0.97, "početni polovi:", fontsize=7.5, color=TEXT_2, va="top")
    fig.tight_layout(rect=(0, 0, 1, 0.88))
    return save(fig, directory, "fig_raspon")


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    parser.add_argument("--convergence-run", type=Path, required=True)
    parser.add_argument("--runs-dir", type=Path, default=provenance.RUNS_DIR)
    args = parser.parse_args(argv)
    cv = args.convergence_run
    inputs = [cv / "provenance.json", cv / "convergence.json", cv / "convergence_iterations.npz"]
    missing = [str(p) for p in inputs if not p.is_file()]
    if missing:
        parser.error(f"missing recorded results: {missing}")
    source = json.loads(inputs[0].read_text(encoding="utf-8"))["run_id"]
    settings = {"convergence_run": source, "ordinal": ORDINAL,
                "trajectory_orders": TRAJECTORY_ORDERS, "trajectory_steps": STEPS}
    style()
    with provenance.run("figures_a7", settings=settings, inputs=inputs,
                        runs_dir=args.runs_dir) as record:
        rows = json.loads(inputs[1].read_text(encoding="utf-8"))
        table = io.StringIO()
        table.write(f"izvor: {source}\n")
        artifacts = figure_trajectory(inputs[2], record.dir, table)
        artifacts += figure_start(rows, record.dir, table)
        (record.dir / "figures_a7.txt").write_text(table.getvalue(), encoding="utf-8")
        record.update(artifacts=artifacts + ["figures_a7.txt"])
    print(f"run {record.run_id} -> {record.dir}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
