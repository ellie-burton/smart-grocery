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


CANONICAL_FIELDNAMES = [
    "search_term",
    "product_name", 
    "unit_size",
    "price",
    "store",
    "date",
    "clean_price",
    "normalized_qty",
    "unit_type",
    "unit_uncertain",
    "price_per_unit",
    "brand_type",
    "category",
    "scraper_error",
    "name_match_uncertain",
]


def append_results(results, path):
    """Append enriched results to CSV; create file with header if needed."""
    path = Path(path)
    path.parent.mkdir(parents=True, exist_ok=True)
    file_exists = path.exists()

    if not results:
        print("No results to save.")
        return

    # Use canonical field order for consistent schema across runs
    # This prevents schema drift when dict key ordering changes
    fieldnames = CANONICAL_FIELDNAMES
    
    # Warn if results have unexpected fields (for debugging)
    result_keys = set(results[0].keys()) if results else set()
    extra_keys = result_keys - set(fieldnames)
    if extra_keys:
        print(f"Warning: Results contain unexpected fields (will be ignored): {extra_keys}")
    
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
