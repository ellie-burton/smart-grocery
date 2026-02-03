"""
Daily basket script: runs the fixed 12-item list and appends results to data/daily_basket.csv.
Schedule with Windows Task Scheduler (see DAILY_RUN.md) to build longitudinal price data.

Usage (from project root):
  python run_daily_basket.py
  python run_daily_basket.py 35401

Optional: set SMART_GROCERY_ZIP in the environment to override default zip.
"""
import os
import csv
from pathlib import Path

import main
import config

# Output file for longitudinal data
DATA_DIR = Path(__file__).resolve().parent / "data"
DAILY_BASKET_CSV = DATA_DIR / "daily_basket.csv"
DEFAULT_ZIP = "35401"


def get_zip_code():
    """Zip from first CLI arg, or env SMART_GROCERY_ZIP, or default."""
    import sys
    if len(sys.argv) >= 2:
        return sys.argv[1].strip()
    return os.environ.get("SMART_GROCERY_ZIP", DEFAULT_ZIP)


def append_results(results, path):
    """Append enriched results to CSV; create file with header if needed."""
    path = Path(path)
    path.parent.mkdir(parents=True, exist_ok=True)
    file_exists = path.exists()

    if not results:
        print("No results to save.")
        return

    fieldnames = list(results[0].keys())
    with open(path, "a", newline="", encoding="utf-8") as f:
        w = csv.DictWriter(f, fieldnames=fieldnames, extrasaction="ignore")
        if not file_exists:
            w.writeheader()
        w.writerows(results)
    print(f"Appended {len(results)} rows to {path}")


def run():
    zip_code = get_zip_code()
    print(f"Running daily basket for zip={zip_code} ({len(config.DAILY_BASKET)} items).")
    print("This will open browsers and may take several minutes.\n")

    results = main.run_scrapers_parallel(
        zip_code,
        config.DAILY_BASKET,
        category_map=config.DAILY_BASKET_CATEGORY_MAP,
    )

    print(f"\nTotal results: {len(results)}")
    append_results(results, DAILY_BASKET_CSV)


if __name__ == "__main__":
    run()
