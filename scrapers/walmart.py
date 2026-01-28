import time
from datetime import datetime
from bs4 import BeautifulSoup
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import StaleElementReferenceException
import undetected_chromedriver as uc 

def setup_stealth_driver():
    options = uc.ChromeOptions()
    driver = uc.Chrome(options=options)
    driver.maximize_window()
    return driver

def force_click(driver, element):
    driver.execute_script("arguments[0].click();", element)

# --- STORE LOCATION LOGIC ---
def set_store_location(driver, zip_code):
    print(f"Setting Walmart location to: {zip_code}")
    driver.get("https://www.walmart.com/store-finder")
    
    # Anti-Bot Buffer
    time.sleep(3)
    if "Press and hold" in driver.page_source:
        print("Bot check detected! Please solve it manually on the screen.")
        input("Press Enter here once the page loads...")

    try:
        # 1. TYPE ZIP CODE
        print("Waiting for Zip Input...")
        for attempt in range(3):
            try:
                search_input = WebDriverWait(driver, 15).until(
                    EC.presence_of_element_located((By.CSS_SELECTOR, "input[data-automation-id='store-zip-code']"))
                )
                force_click(driver, search_input)
                time.sleep(0.5)
                search_input.clear()
                search_input.send_keys(zip_code)
                time.sleep(1)
                search_input.send_keys(Keys.RETURN)
                break
            except Exception as e:
                print(f"Retry {attempt}: {e}")
                time.sleep(2)
        
        time.sleep(5) # Wait for results list to populate
        
        # 2. SELECT FIRST STORE RESULT
        print("Selecting first store...")
        try:
            first_store_card = WebDriverWait(driver, 10).until(
                EC.element_to_be_clickable((By.XPATH, "(//button[@role='checkbox'])[1]"))
            )
            force_click(driver, first_store_card)
        except Exception as e:
            print(f"Could not click store card (maybe already selected?): {e}")
        
        time.sleep(3) # Wait for details to expand
        
        # 3. CLICK "MAKE THIS MY STORE" (The Fix)
        print("Clicking 'Make this my store'...")
        try:
            # Updated Selector: Target aria-label OR text text
            make_store_btn = WebDriverWait(driver, 10).until(
                EC.presence_of_element_located((By.XPATH, "//button[contains(@aria-label, 'Make this my store') or contains(., 'Make this my store')]"))
            )
            
            # Scroll to it (Critical for Walmart lazy loading)
            driver.execute_script("arguments[0].scrollIntoView({block: 'center'});", make_store_btn)
            time.sleep(1)
            
            force_click(driver, make_store_btn)
            print("Store set successfully!")
        except Exception as e:
            print(f"Make store button issue (Store might already be set): {e}")

        time.sleep(3)
        return "Walmart Store"

    except Exception as e:
        print(f"Error setting Walmart location: {e}")
        return "Walmart Default"

# --- PRODUCT SCRAPING LOGIC ---
def scrape_items(driver, items):
    data = []
    
    for item in items:
        print(f"Searching for: {item}...")
        try:
            search_url = f"https://www.walmart.com/search?q={item}"
            driver.get(search_url)
            
            time.sleep(5) 
            
            if "Press and hold" in driver.page_source:
                print("Bot check! Solve manually.")
                input("Press Enter to continue...")

            soup = BeautifulSoup(driver.page_source, 'html.parser')
            cards = soup.find_all('div', attrs={'data-test-id': 'gpt-product-tile-grid-container'})
            
            count = 0
            for card in cards:
                if count >= 5: break
                try:
                    title_tag = card.find('h3', attrs={'data-automation-id': 'product-title'})
                    title = title_tag.get_text(strip=True) if title_tag else "Unknown"
                    
                    price = "N/A"
                    price_container = card.find('div', attrs={'data-automation-id': 'product-price'})
                    
                    if price_container:
                        sr_text = price_container.find('span', class_='w_iUH7')
                        if sr_text:
                            raw_price = sr_text.get_text(strip=True)
                            if "$" in raw_price:
                                price = "$" + raw_price.split("$")[-1]
                        
                        if price == "N/A":
                            price_flex = price_container.find('div', attrs={'data-test-id': 'gpt-price-flex-container'})
                            if price_flex:
                                price = price_flex.get_text(strip=True)

                    unit = "" 
                    if "," in title:
                        parts = title.split(',')
                        if len(parts) > 1:
                            unit = parts[-1].strip()

                    full_name = f"Walmart {title}"
                    
                    # --- NEW FLEXIBLE MATCHING ---
                    query_words = [w.lower() for w in item.split() if len(w) > 2]
                    
                    if query_words:
                        if not any(w in full_name.lower() for w in query_words):
                            continue
                    else:
                        if item.lower() not in full_name.lower():
                            continue
                    # -----------------------------

                    data.append({
                        "search_term": item,
                        "product_name": full_name,
                        "unit_size": unit,
                        "price": price,
                        "store": "Walmart",
                        "date": datetime.now().strftime("%Y-%m-%d")
                    })
                    count += 1
                    
                except AttributeError:
                    continue
                    
        except Exception as e:
            print(f"Error scraping {item}: {e}")
            
    return data

def run(zip_code, items):
    driver = setup_stealth_driver()
    try:
        set_store_location(driver, zip_code)
        return scrape_items(driver, items) 
    finally:
        try:
            driver.quit()
        except OSError:
            pass 

if __name__ == "__main__":
    print(run("37129", ["eggs"]))