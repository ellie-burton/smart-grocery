import concurrent.futures
import time
from scrapers import aldi, publix, walmart

def run_scrapers_parallel(zip_code, items):
    """
    Runs Publix and Walmart scrapers simultaneously.
    Returns a combined list of product dictionaries.
    """
    print(f"🚀 Starting parallel scrape for: {items} in {zip_code}")
    results = []

    # ThreadPoolExecutor allows us to run I/O bound tasks (browsers) in parallel
    with concurrent.futures.ThreadPoolExecutor(max_workers=2) as executor:
        # 1. Submit both functions to the pool
        # syntax: executor.submit(function_name, arg1, arg2)
        future_aldi = executor.submit(aldi.run, zip_code, items)
        time.sleep(1)

        future_publix = executor.submit(publix.run, zip_code, items)
        
        # Add a tiny delay for Walmart to prevent conflicting browser startup
        time.sleep(1) 
        future_walmart = executor.submit(walmart.run, zip_code, items)

        # 2. Wait for them to finish and gather results as they complete
        futures = [future_aldi, future_publix, future_walmart]
        
        for future in concurrent.futures.as_completed(futures):
            try:
                data = future.result()
                if data:
                    results.extend(data)
            except Exception as e:
                print(f"❌ A scraper crashed: {e}")

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
    
    # Helper to sort by price (removing '$' sign)
    def get_price(p):
        try:
            # Cleanup "$3.99" -> 3.99
            clean_price = p['price'].replace('$', '').replace('current price', '').strip()
            return float(clean_price)
        except:
            return 999.0 # Put "N/A" prices at the bottom
            
    all_products.sort(key=get_price)

    # Print clean list to console
    for p in all_products:
        print(f"[{p['store']}] {p['product_name']} | {p['price']}")