"""Download Gabriel's parameter table from WebNIR and write the canonical CSV.

Run from the repository root:  uv run python data/fetch_gabriel.py

Writes data/raw/webnir-gabriel.html and data/processed/gabriel_parameters.csv (both outside
Git, see data/README.md). The CSV keeps the published strings, so its SHA-256 identifies the
table contents; a different checksum is an error, never silently accepted, and leaves the
previously verified files in place.
"""
from __future__ import annotations

import argparse
import hashlib
import sys
import urllib.request
from pathlib import Path

from vfdebye import gabriel

URL = "https://webnir.eu/04-Dosimetry/04-Gabriel.php?lang=gb"
DATA = Path(__file__).resolve().parent
RAW = DATA / "raw" / "webnir-gabriel.html"
CSV = DATA / "processed" / "gabriel_parameters.csv"
# SHA-256 of the canonical CSV, accessed 2026-11-09 (data/README.md).
EXPECTED_CSV_SHA256 = "0644be919b775d19425bd51d2bd732d2cbb6c05cbbaf7b1d76b4e792c3e4d21a"
TIMEOUT_SECONDS = 30


def sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    parser.add_argument(
        "--offline", action="store_true",
        help="rebuild the CSV from the saved HTML instead of downloading it",
    )
    args = parser.parse_args(argv)
    RAW.parent.mkdir(parents=True, exist_ok=True)
    CSV.parent.mkdir(parents=True, exist_ok=True)
    # New files get a .new suffix and replace the verified ones only after the checksum matches,
    # so a changed source never overwrites the CSV the experiments read or the HTML behind it.
    html = RAW
    if not args.offline:
        html = RAW.with_name(RAW.name + ".new")
        with urllib.request.urlopen(URL, timeout=TIMEOUT_SECONDS) as response:
            html.write_bytes(response.read())
    rows = gabriel.parse_webnir_table(html.read_text(encoding="utf-8"))
    for row in rows:
        gabriel.tissue_from_row(row[0], row[1:])
    new_csv = CSV.with_name(CSV.name + ".new")
    gabriel.write_csv(rows, new_csv)
    digest = sha256(new_csv)
    print(f"HTML sha256 {sha256(html)} (informative; the page layout may change)")
    print(f"CSV  sha256 {digest}")
    if digest != EXPECTED_CSV_SHA256:
        print(
            f"CSV checksum differs from the recorded {EXPECTED_CSV_SHA256}. The source table "
            "changed or was parsed differently. The verified files are unchanged; the new ones "
            f"are kept as {new_csv.relative_to(DATA.parent)}"
            + ("" if html == RAW else f" and {html.relative_to(DATA.parent)}")
            + ". Compare the rows before using them and record the new checksum in "
            "data/README.md and this script through a reviewed PR.",
            file=sys.stderr,
        )
        return 1
    new_csv.replace(CSV)
    if html != RAW:
        html.replace(RAW)
    print(f"{len(rows)} rows -> {CSV.relative_to(DATA.parent)}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
