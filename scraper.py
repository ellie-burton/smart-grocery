import time
import pandas as pd
from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from webdriver_manager.chrome import ChromeDriverManager
from bs4 import BeautifulSoup
from datetime import datetime

# 1. Setup Phase
def setup_driver():
    options = webdriver.ChromeOptions()
    # options.add_argument("--headless") # Keep commented out so you can see it working
    options.add_argument("user-agent=Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36")
    driver = webdriver.Chrome(service=Service(ChromeDriverManager().install()), options=options)
    driver.maximize_window() # Maximizing helps ensure elements aren't hidden
    return driver

# 2. Scraping Phase
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

                    # --- RELEVANCE FILTER ---
                    # Checks if "egg" is actually in the title to avoid "Lego sets"
                    keyword = item.rstrip('s').lower()
                    
                    if keyword not in full_product_name.lower():
                        # Optional: Print what we skipped to verify it's working
                        # print(f"Skipping irrelevant result: {full_product_name}") 
                        continue 

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

# 3. Execution Phase
if __name__ == "__main__":
    # You can expand this list later
    grocery_list = ["eggs", "bread", "milk"] 
    
    driver = setup_driver()
    try:
        scraped_data = scrape_prices(driver, grocery_list)
    finally:
        driver.quit()

    if scraped_data:
        df = pd.DataFrame(scraped_data)
        print("\n--- FINAL SUCCESSFUL DATA ---")
        print(df)
        df.to_csv("grocery_prices_mvp.csv", index=False)
        print("Data saved to grocery_prices_mvp.csv")
    else:
        print("No data found. Check the console for errors.")