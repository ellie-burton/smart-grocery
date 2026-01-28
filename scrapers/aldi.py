import time
from datetime import datetime
from bs4 import BeautifulSoup
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC

# Import the shared setup function
# Note: This relative import works when running from main.py
# To run this file directly, use: python -m scrapers.aldi
try:
    # This works when running from main.py
    from .utils import setup_driver 
except ImportError:
    # This works when running this file directly for testing
    from utils import setup_driver
    
def scrape_prices(driver, items):
    data = []
    
    print("Navigating to Aldi homepage...")
    driver.get("https://new.aldi.us/")
    
    # Wait for the page to load the body tag effectively
    WebDriverWait(driver, 10).until(EC.presence_of_element_located((By.TAG_NAME, "body")))

    for item in items:
        print(f"Searching for: {item}...")
        
        try:
            # --- THE FIX ---
            # We use the ID you found in the HTML: "search-bar-input"
            search_box = WebDriverWait(driver, 10).until(
                EC.element_to_be_clickable((By.ID, "search-bar-input"))
            )
            
            # Interaction: Click -> Clear -> Type -> Enter
            search_box.click() 
            search_box.clear()
            search_box.send_keys(item)
            search_box.send_keys(Keys.RETURN)
            
            # Wait for results (give it 5 seconds for the grid to update)
            time.sleep(5) 
            
            # --- PARSING ---
            soup = BeautifulSoup(driver.page_source, 'html.parser')
            product_cards = soup.find_all('div', class_='product-teaser-item')

            found_count = 0
            
            for card in product_cards: 
                if found_count >= 5: break 

                try:
                    # Extract Data using the selectors we confirmed earlier
                    brand_div = card.find('div', class_='product-tile__brandname')
                    brand = brand_div.text.strip() if brand_div else "Unknown Brand"

                    title_div = card.find('div', class_='product-tile__name')
                    title = title_div.text.strip() if title_div else "No Title"

                    unit_div = card.find('div', class_='product-tile__unit-of-measurement')
                    unit = unit_div.text.strip() if unit_div else ""

                    price_span = card.find('span', class_='product-tile__price')
                    price = price_span.text.strip() if price_span else "N/A"

                    full_product_name = f"{brand} {title}".strip()

                    # --- NEW FLEXIBLE MATCHING ---
                    query_words = [w.lower() for w in item.split() if len(w) > 2]
                    
                    if query_words:
                        if not any(w in full_product_name.lower() for w in query_words):
                            continue
                    else:
                        if item.lower() not in full_product_name.lower():
                            continue
                    # -----------------------------


                    data.append({
                        "search_term": item,
                        "product_name": full_product_name,
                        "unit_size": unit,
                        "price": price,
                        "store": "Aldi",
                        "date": datetime.now().strftime("%Y-%m-%d")
                    })
                    found_count += 1
                    
                except AttributeError:
                    continue 

        except Exception as e:
            print(f"Error processing {item}: {e}")
            driver.refresh()
            time.sleep(5)

    return data

# --- MAIN INTERFACE FUNCTION ---
# This is what main.py will call
def run(zip_code, items):
    # zip_code is accepted here to match the interface of publix.py, 
    # even if Aldi doesn't use it yet.
    driver = setup_driver()
    try:
        # If we later decide to add specific store selection for Aldi,
        # we would call a set_location(driver, zip_code) function here.
        return scrape_prices(driver, items)
    finally:
        driver.quit()

# 3. Execution Phase (For Testing)
if __name__ == "__main__":
    # To run this test: python -m scrapers.aldi
    grocery_list = ["eggs", "bread", "milk"]
    test_zip = "35401"
    
    print("Testing Aldi Scraper Module...")
    data = run(test_zip, grocery_list)
    print(data)