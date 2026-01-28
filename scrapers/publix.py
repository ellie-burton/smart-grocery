import time
from datetime import datetime
from bs4 import BeautifulSoup
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC

try:
    from .utils import setup_driver 
except ImportError:
    from utils import setup_driver 

def force_click(driver, element):
    driver.execute_script("arguments[0].click();", element)

def set_store_location(driver, zip_code):
    print(f"Setting Publix (Delivery/Pickup) location to: {zip_code}")
    driver.get("https://delivery.publix.com/store/publix/storefront")
    
    try:
        # 1. Wait for Shopping Modal
        print("Waiting for shopping modal...")
        WebDriverWait(driver, 20).until(
            EC.presence_of_element_located((By.XPATH, "//h2[contains(text(), 'How would you like to shop')]"))
        )
        time.sleep(3)

        # 2. Click 'Edit' Button
        print("Scanning for 'Edit' button...")
        edit_buttons = driver.find_elements(By.XPATH, "//button[contains(., 'Edit')]")
        clicked = False
        
        for btn in edit_buttons:
            try:
                sibling = btn.find_element(By.XPATH, "./preceding-sibling::button")
                if "pickup" in sibling.text.lower():
                    force_click(driver, btn)
                    clicked = True
                    break
            except:
                continue
        
        if not clicked and len(edit_buttons) >= 2:
            force_click(driver, edit_buttons[1])
        
        time.sleep(4) 

        # 3. INTERACT WITH ZIP INPUT
        print("Looking for 'Near...' button to click...")
        try:
            near_btn = WebDriverWait(driver, 10).until(
                EC.element_to_be_clickable((By.XPATH, "//button[.//span[contains(text(), 'Near')]]"))
            )
            near_btn.click()
            time.sleep(1)

            real_input = WebDriverWait(driver, 5).until(
                EC.visibility_of_element_located((By.XPATH, "//input[@type='text' or @type='tel']"))
            )
            
            real_input.clear()
            real_input.send_keys(zip_code)
            real_input.send_keys(Keys.ENTER)

            time.sleep(2) 

            # Keyboard Selection
            real_input.send_keys(Keys.ARROW_DOWN)
            time.sleep(1)
            
            real_input.send_keys(Keys.ENTER)
            print(f"Entered Zip: {zip_code}")
            
        except Exception as e:
            print(f"Zip input interaction failed: {e}")

        time.sleep(3)

        # 3.5 HANDLE "SAVE ADDRESS" BUTTON (The New Fix)
        # Some addresses require a manual save confirmation
        try:
            save_addr_btn = driver.find_elements(By.XPATH, "//button[contains(., 'Save Address')]")
            if save_addr_btn:
                print("Found 'Save Address' button. Clicking it...")
                force_click(driver, save_addr_btn[0])
                time.sleep(3) # Wait for next screen
        except:
            pass

        time.sleep(3) # Wait for Store List to load

        # 4. SELECT FIRST STORE CARD
        print("Selecting first store card...")
        try:
            # Check if store list is present (if not, maybe we are already set)
            store_list = driver.find_elements(By.XPATH, "//ul[@aria-labelledby='locations-list']")
            if store_list:
                first_store_btn = WebDriverWait(driver, 10).until(
                    EC.element_to_be_clickable((By.XPATH, "//ul[@aria-labelledby='locations-list']/li[1]//button"))
                )
                driver.execute_script("arguments[0].scrollIntoView(true);", first_store_btn)
                time.sleep(1)
                force_click(driver, first_store_btn)
                print("Clicked store card.")
            else:
                print("Store list not found. Assuming location set successfully.")
        except Exception as e:
            print(f"Could not click store card: {e}")

        time.sleep(2)

        # 5. STEP 1: CLICK "SHOP THIS STORE"
        print("Step 1: Clicking 'Shop this store'...")
        try:
            shop_btn = WebDriverWait(driver, 5).until(
                EC.element_to_be_clickable((By.XPATH, "//button[contains(., 'Shop this store')]"))
            )
            force_click(driver, shop_btn)
            print("Clicked 'Shop this store'.")
        except:
            print("'Shop this store' button not found (might have skipped).")

        time.sleep(6) 

        # 6. STEP 2: FINAL CONFIRMATION
        print("Step 2: Waiting for Final Confirmation...")
        try:
            confirm_btn = WebDriverWait(driver, 5).until(
                EC.element_to_be_clickable((By.XPATH, "//button[contains(., 'Confirm') or contains(., 'Switch')]"))
            )
            force_click(driver, confirm_btn)
            print("Final Confirmation clicked!")
        except:
            print("No final confirmation popup found (maybe auto-confirmed).")

        time.sleep(5)
        return "Publix Delivery"

    except Exception as e:
        print(f"Error setting location: {e}")
        return "Publix Default"

def scrape_items(driver, items):
    data = []
    print("Preparing to scrape items...")
    
    for item in items:
        print(f"Searching for: {item}...")
        try:
            # 1. FIND THE SEARCH BAR
            try:
                search_box = WebDriverWait(driver, 15).until(
                    EC.element_to_be_clickable((By.ID, "search-bar-input"))
                )
            except:
                print("ID selector failed, trying generic form input...")
                search_box = driver.find_element(By.CSS_SELECTOR, "form[role='search'] input")

            # Click to focus
            try:
                search_box.click()
            except:
                force_click(driver, search_box)

            # 2. TYPE SEARCH TERM
            search_box.send_keys(Keys.CONTROL + "a")
            search_box.send_keys(Keys.BACK_SPACE)
            time.sleep(0.5)
            
            search_box.send_keys(item)
            search_box.send_keys(Keys.RETURN)
            
            time.sleep(6)
            
            # 3. PARSE RESULTS
            cards = driver.find_elements(By.XPATH, "//li[contains(., '$')]")
            count = 0
            
            if not cards:
                print("No cards found with '$'. Trying broader selector...")
                cards = driver.find_elements(By.CSS_SELECTOR, "li")

            for card in cards:
                if count >= 5: break
                text = card.text
                if not text or '$' not in text: continue
                
                lines = text.split('\n')
                price = "N/A"
                title = "Unknown"
                unit = ""
                
                for line in lines:
                    if '$' in line and price == "N/A":
                        price = line
                    elif len(line) > 10 and title == "Unknown" and '$' not in line:
                        title = line
                    elif any(x in line.lower() for x in ['oz', 'ct', 'lb', 'gal', 'pk']):
                        unit = line
                
                full_name = f"Publix {title}"
                
                # --- NEW FLEXIBLE MATCHING ---
                # 1. Split search term into words (e.g., "Stick", "of", "Butter")
                # 2. Ignore small words like "of", "a", "in" (len <= 2)
                query_words = [w.lower() for w in item.split() if len(w) > 2]
                
                # 3. Check if AT LEAST ONE significant word is in the product title
                # If the list is empty (e.g. search was just "oj"), check exact match
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
                    "store": "Publix",
                    "date": datetime.now().strftime("%Y-%m-%d")
                })
                count += 1
                
        except Exception as e:
            print(f"Error scraping {item}: {e}")
            
    return data

def run(zip_code, items):
    driver = setup_driver()
    try:
        set_store_location(driver, zip_code)
        return scrape_items(driver, items) 
    finally:
        driver.quit()

if __name__ == "__main__":
    print(run("2816 Wynthrope Hall Dr", ["eggs", "bread"]))