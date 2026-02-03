import concurrent.futures
import time
from scrapers import aldi, publix, walmart
from lib.enrich import enrich_results


def run_scrapers_parallel(zip_code, items, category_map=None):
    """
    Runs Aldi, Publix, and Walmart scrapers in parallel.
    Enriches results with clean_price, normalized_qty, unit_type, brand_type,
    category, and price_per_unit. Returns a combined list of product dicts.
    """
    print(f"🚀 Starting parallel scrape for: {items} in {zip_code}")
    results = []

    with concurrent.futures.ThreadPoolExecutor(max_workers=3) as executor:
        future_aldi = executor.submit(aldi.run, zip_code, items)
        time.sleep(1)
        future_publix = executor.submit(publix.run, zip_code, items)
        time.sleep(1)
        future_walmart = executor.submit(walmart.run, zip_code, items)

        name_to_future = {
            "Aldi": future_aldi,
            "Publix": future_publix,
            "Walmart": future_walmart,
        }
        for future in concurrent.futures.as_completed(name_to_future.values()):
            name = next(n for n, f in name_to_future.items() if f is future)
            try:
                data = future.result()
                if data:
                    results.extend(data)
            except Exception as e:
                print(f"❌ {name} scraper crashed: {e}")

    enrich_results(results, category_map=category_map)
    return results

if __name__ == "__main__":
    # --- TEST CONFIGURATION ---
    # This block only runs when you execute 'python main.py' directly.
    # It does NOT run when 'app.py' imports this file.
    
    MY_ZIP = "35401" 
    MY_LIST = ["eggs", "bread", "milk"]

    start_time = time.time()
    
    # Run!
    all_products = run_scrapers_parallel(MY_ZIP, MY_LIST)
    
    end_time = time.time()
    
    # REPORT
    print("\n" + "="*40)
    print(f"🏁 SCRAPING COMPLETE in {end_time - start_time:.2f} seconds")
    print("="*40)
    
    # Sort by enriched clean_price
    all_products.sort(key=lambda p: p.get("clean_price") or 999.0)

    # Print clean list to console
    for p in all_products:
        ppu = p.get("price_per_unit")
        ppu_str = f" (${ppu:.4f}/{p.get('unit_type', '')})" if ppu is not None else ""
        print(f"[{p['store']}] {p['product_name']} | {p['price']}{ppu_str}")