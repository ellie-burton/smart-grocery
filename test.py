"""
Command-line script to run scrapers and save results to data/temp_results.csv.
Use this to verify enrichment and unit standardization without the Streamlit UI.

Usage (from project root):
  python test.py
  python test.py 35401
  python test.py 35401 "milk,eggs,bread"

Defaults: zip 35401, items ["milk", "eggs", "bread"].
Output: data/temp_results.csv
"""
import sys
import csv
from pathlib import Path

import main

# Project root = parent of this file; output under data/
PROJECT_ROOT = Path(__file__).resolve().parent
OUTPUT_DIR = PROJECT_ROOT / "data"
TEMP_CSV = OUTPUT_DIR / "temp_results.csv"
DEFAULT_ZIP = "35401"
DEFAULT_ITEMS = ["milk", "eggs", "bread"]


def parse_args():
    zip_code = DEFAULT_ZIP
    items = DEFAULT_ITEMS
    if len(sys.argv) >= 2:
        zip_code = sys.argv[1].strip()
    if len(sys.argv) >= 3:
        raw = sys.argv[2].strip()
        items = [x.strip() for x in raw.replace(",", "\n").split() if x.strip()]
    return zip_code, items


def save_results(results, path):
    if not results:
        print("No results to save.")
        return
    path = Path(path)
    path.parent.mkdir(parents=True, exist_ok=True)
    fieldnames = list(results[0].keys())
    with open(path, "w", newline="", encoding="utf-8") as f:
        w = csv.DictWriter(f, fieldnames=fieldnames, extrasaction="ignore")
        w.writeheader()
        w.writerows(results)
    print(f"Saved {len(results)} rows to {path}")


def main_cli():
    zip_code, items = parse_args()
    print(f"Running scrapers: zip={zip_code}, items={items}")
    print("(Browsers will open; this may take a minute.)\n")

    results = main.run_scrapers_parallel(zip_code, items)

    print(f"\nTotal results: {len(results)}")
    save_results(results, TEMP_CSV)
    return results


if __name__ == "__main__":
    main_cli()
