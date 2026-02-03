"""
Quick test: run only the Walmart scraper (no Aldi/Publix).
Usage: python run_walmart_only.py [zip]
Default zip: 35401. Example: python run_walmart_only.py 35401
"""
import sys
from scrapers import walmart

ZIP = sys.argv[1].strip() if len(sys.argv) >= 2 else "35401"
ITEMS = ["eggs", "bread"]  # minimal list for a quick check

if __name__ == "__main__":
    print(f"Running Walmart only for zip={ZIP}, items={ITEMS}...")
    print("(A Chrome window will open.)\n")
    try:
        results = walmart.run(ZIP, ITEMS)
        print(f"\nDone. Got {len(results)} results.")
        for r in results:
            print(f"  [{r['product_name'][:50]}] {r['price']}")
    except Exception as e:
        print(f"Walmart scraper failed: {e}")
        raise
    # If you see "Exception ignored in: <function Chrome.__del__>" with OSError [WinError 6],
    # that's a known undetected_chromedriver quirk on Windows at exit and can be ignored.
