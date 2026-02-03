import re
import time
from datetime import datetime
from bs4 import BeautifulSoup
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import StaleElementReferenceException

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

def scrape_items(driver, items, debug=False):
    data = []
    print("Preparing to scrape items...")

    # Build query words once per item; strip parentheses for more flexible matching
    def get_query_words(search_term):
        words = []
        for w in search_term.replace("(", " ").replace(")", " ").split():
            w_clean = w.lower().strip()
            if len(w_clean) > 2 and w_clean not in ("the", "and", "for"):
                words.append(w_clean)
        return words if words else [search_term.lower()]

    def word_matches(text_lower, query_word):
        """True if query_word or its singular/plural form appears in text (e.g. bananas vs banana)."""
        if query_word in text_lower:
            return True
        if query_word.endswith("s") and len(query_word) > 1:
            if query_word[:-1] in text_lower:
                return True
        elif query_word + "s" in text_lower:
            return True
        return False

    for item in items:
        print(f"Searching for: {item}...")
        try:
            # 1. FIND THE SEARCH BAR
            try:
                search_box = WebDriverWait(driver, 15).until(
                    EC.element_to_be_clickable((By.ID, "search-bar-input"))
                )
            except Exception:
                print("ID selector failed, trying generic form input...")
                search_box = driver.find_element(By.CSS_SELECTOR, "form[role='search'] input")

            # Click to focus
            try:
                search_box.click()
            except Exception:
                force_click(driver, search_box)

            # 2. TYPE SEARCH TERM
            search_box.send_keys(Keys.CONTROL + "a")
            search_box.send_keys(Keys.BACK_SPACE)
            time.sleep(0.5)

            search_box.send_keys(item)
            search_box.send_keys(Keys.RETURN)

            time.sleep(6)

            # 3. PARSE RESULTS (re-find cards each index to avoid stale element)
            count = 0
            index = 0
            max_attempts = 45
            first_fetch = True
            query_words = get_query_words(item)
            if debug:
                print(f"  [debug] query_words for matching: {query_words}")

            def get_cards():
                # Primary: li with price symbol (most product cards)
                cards = driver.find_elements(By.XPATH, "//li[contains(., '$')]")
                if cards:
                    return cards
                # Produce/weight items often show "per lb" or "Current price" without $ in same li
                cards = driver.find_elements(
                    By.XPATH,
                    "//li[contains(., 'Current price') or contains(., 'per lb') or contains(., 'per each') or contains(., 'Price')]",
                )
                if cards:
                    return cards
                return driver.find_elements(By.CSS_SELECTOR, "li")

            while count < 5 and index < max_attempts:
                cards = get_cards()
                if not cards and first_fetch:
                    print("No cards found with '$'. Waiting 4s for produce/weight items...")
                    time.sleep(4)
                    cards = get_cards()
                if not cards and first_fetch:
                    print("Trying broader selector...")
                    first_fetch = False
                if first_fetch and cards and debug:
                    print(f"  [debug] Found {len(cards)} cards (li elements)")
                if first_fetch and cards:
                    first_fetch = False
                if not cards or index >= len(cards):
                    break
                text = None
                for _ in range(2):
                    try:
                        card = cards[index]
                        text = card.text
                        break
                    except StaleElementReferenceException:
                        time.sleep(0.5)
                        cards = get_cards()
                        if not cards or index >= len(cards):
                            break
                if text is None:
                    index += 1
                    continue
                # Skip if no price hint at all ($ or produce-style "per lb" / "Current price")
                has_price_hint = "$" in text or "per lb" in text or "per each" in text or "Current price" in text.lower()
                if not text or not has_price_hint:
                    if debug and index < 3:
                        print(f"  [debug] Skip card (no price): {repr(text[:80])}...")
                    index += 1
                    continue
                lines = text.split("\n")
                price = "N/A"
                title = "Unknown"
                unit = ""
                # First pass: collect price and unit; pick title (prefer line that matches search)
                for line in lines:
                    if "$" in line and price == "N/A":
                        price = line
                    elif price == "N/A" and ("per lb" in line or "per each" in line or "current price" in line.lower()):
                        num = re.search(r"[\d]+\.?[\d]*", line)
                        if num:
                            price = f"${num.group()}" if "$" not in line else line
                    elif any(x in line.lower() for x in ["oz", "ct", "lb", "gal", "pk"]):
                        unit = line
                # Title: prefer a line that matches our search (e.g. "Banana", "Organic Bananas")
                # so we don't use the badge text ("Best seller", "Gluten free") as the product name.
                # When several lines match, prefer the longest (more descriptive product name).
                if query_words:
                    best_match = None
                    for line in lines:
                        line_clean = line.strip()
                        if not line_clean or "$" in line_clean or len(line_clean) < 2 or len(line_clean) > 200:
                            continue
                        if not any(word_matches(line_clean.lower(), w) for w in query_words):
                            continue
                        if best_match is None or len(line_clean) > len(best_match):
                            best_match = line_clean
                    if best_match:
                        title = best_match
                if title == "Unknown":
                    for line in lines:
                        line_clean = line.strip()
                        if len(line_clean) > 10 and "$" not in line_clean and "per lb" not in line_clean:
                            title = line_clean
                            break
                full_name = f"Publix {title}"
                name_lower = full_name.lower()
                if query_words:
                    if not any(word_matches(name_lower, w) for w in query_words):
                        if debug and count == 0 and index < 5:
                            print(f"  [debug] Skip (no keyword match): {repr(full_name[:70])}...")
                        index += 1
                        continue
                else:
                    if item.lower() not in full_name.lower():
                        index += 1
                        continue
                data.append({
                    "search_term": item,
                    "product_name": full_name,
                    "unit_size": unit,
                    "price": price,
                    "store": "Publix",
                    "date": datetime.now().strftime("%Y-%m-%d"),
                })
                if debug:
                    print(f"  [debug] Kept: {full_name[:60]}... | {price}")
                count += 1
                index += 1

            if debug:
                print(f"  [debug] Total kept for '{item}': {count}")

        except Exception as e:
            print(f"Error scraping {item}: {e}")
            if debug:
                import traceback
                traceback.print_exc()

    return data

def run(zip_code, items, debug=False):
    driver = setup_driver()
    try:
        set_store_location(driver, zip_code)
        return scrape_items(driver, items, debug=debug)
    finally:
        driver.quit()

if __name__ == "__main__":
    print(run("2816 Wynthrope Hall Dr", ["eggs", "bread"]))