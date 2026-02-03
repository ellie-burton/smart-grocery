r"""
Run only the Publix scraper with debug output to see why some search terms
return no results. Focuses on the two terms that were missing from daily_basket:
  "Large Eggs (12 count)" and "Bananas".
Also runs "Whole Milk" as a control (should return results).

Usage (in Command Prompt from project root):
  conda deactivate
  .venv\Scripts\activate
  python run_publix_debug.py [zip]

Default zip: 35401
"""
import sys
from scrapers import publix

ZIP = sys.argv[1].strip() if len(sys.argv) >= 2 else "35401"
# Missing in daily_basket + one that works
ITEMS = [
    "Large Eggs (12 count)",
    "Bananas",
    "Whole Milk",
]

if __name__ == "__main__":
    print(f"Publix debug run for zip={ZIP}")
    print(f"Items: {ITEMS}\n")
    results = publix.run(ZIP, ITEMS, debug=True)
    print(f"\n=== Total results: {len(results)} ===")
    for r in results:
        print(f"  [{r['search_term']}] {r['product_name'][:50]} | {r['price']}")
