import concurrent.futures
import time
from scrapers import publix, walmart, aldi

def run_scrapers_parallel(zip_code, items):
    print(f"🚀 Starting parallel scrape for: {items}")
    results = []

    # ThreadPoolExecutor allows us to run I/O bound tasks (like waiting for a website) in parallel
    with concurrent.futures.ThreadPoolExecutor(max_workers=3) as executor:
        # 1. Submit both functions to the pool
        # syntax: executor.submit(function_name, arg1, arg2)
        future_aldi = executor.submit(aldi .run, zip_code, items)

        future_publix = executor.submit(publix.run, zip_code, items)
        
        # Add a tiny delay for Walmart to prevent resource contention on startup
        time.sleep(1) 
        future_walmart = executor.submit(walmart.run, zip_code, items)

        # 2. Wait for them to finish and gather results
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
    # CONFIGURATION
    MY_ZIP = "35401" # Or "2816 Wynthrope Hall Dr"
    MY_LIST = ["eggs", "bread", "milk"]

    start_time = time.time()
    
    # Run!
    all_products = run_scrapers_parallel(MY_ZIP, MY_LIST)
    
    end_time = time.time()
    
    # REPORT
    print("\n" + "="*40)
    print(f"🏁 SCRAPING COMPLETE in {end_time - start_time:.2f} seconds")
    print("="*40)
    
    # Sort by price (cheapest first) for fun
    def get_price(p):
        try:
            return float(p['price'].replace('$', ''))
        except:
            return 999.0
            
    all_products.sort(key=get_price)

    for p in all_products:
        print(f"[{p['store']}] {p['product_name']} | {p['price']}")