# old – Archived / debug files

This folder holds scripts and outputs that are no longer part of the main workflow. Kept for reference only.

| Item | Description |
|------|-------------|
| **parallel.py** | Deprecated. Use `main.py` and `main.run_scrapers_parallel()` instead (includes enrichment). |
| **run_publix_debug.py** | One-off debug script to run only Publix with `debug=True` (e.g. for "Large Eggs", "Bananas"). |
| **run_walmart_only.py** | One-off script to run only the Walmart scraper for quick checks. |
| **test.py** | Legacy copy of the CLI test script; canonical version is at project root `test.py` (writes to `data/temp_results.csv`). |
| **grocery_prices.csv** | Temp scraper output (if present). |
| **temp_results.csv** | Temp scraper output (if present). |

Nothing in this folder is required to run the app, daily basket, or tests.
