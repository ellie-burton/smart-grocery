"""
Publix scraper — Selenium-based.

Navigates the Publix delivery (Instacart) storefront, searches for each item,
and parses product cards from the rendered page.

Location selection has been removed — the site uses the browser's default /
previously-saved location, which is sufficient for price comparison purposes.
"""

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
    from .match import product_matches_query, match_score, get_query_tokens
except ImportError:
    from utils import setup_driver
    from match import product_matches_query, match_score, get_query_tokens


def force_click(driver, element):
    driver.execute_script("arguments[0].click();", element)


def _dismiss_landing_popup(driver):
    """
    The Publix/Instacart storefront shows a pickup-or-delivery popup on
    first load.  Click through confirmation buttons until the search bar
    is reachable.  Multiple overlays can appear in sequence, so we loop.
    """
    confirm_xpaths = [
        "//button[contains(., 'Confirm')]",
        "//button[contains(., 'Shop this store')]",
        "//button[contains(., 'Continue')]",
        "//button[contains(., 'Start shopping')]",
    ]
    for attempt in range(5):
        clicked = False
        for xpath in confirm_xpaths:
            btns = driver.find_elements(By.XPATH, xpath)
            if btns:
                try:
                    force_click(driver, btns[0])
                    print(f"Dismissed popup via: {xpath}")
                    clicked = True
                    time.sleep(3)
                    break
                except Exception:
                    continue
        if not clicked:
            break
        time.sleep(1)

    # Wait for any remaining overlay to fade before searching
    try:
        WebDriverWait(driver, 8).until(
            EC.element_to_be_clickable((By.ID, "search-bar-input"))
        )
    except Exception:
        print("Search bar not yet clickable — proceeding anyway.")


def scrape_items(driver, items, debug=False):
    data = []

    print("Navigating to Publix storefront...")
    driver.get("https://delivery.publix.com/store/publix/storefront")
    time.sleep(5)

    _dismiss_landing_popup(driver)

    for item in items:
        print(f"Searching for: {item}...")
        try:
            try:
                search_box = WebDriverWait(driver, 15).until(
                    EC.element_to_be_clickable((By.ID, "search-bar-input"))
                )
            except Exception:
                print("ID selector failed, trying generic form input...")
                search_box = driver.find_element(By.CSS_SELECTOR, "form[role='search'] input")

            try:
                search_box.click()
            except Exception:
                force_click(driver, search_box)

            search_box.send_keys(Keys.CONTROL + "a")
            search_box.send_keys(Keys.BACK_SPACE)
            time.sleep(0.5)

            search_box.send_keys(item)
            search_box.send_keys(Keys.RETURN)

            time.sleep(6)

            count = 0
            index = 0
            max_attempts = 45
            first_fetch = True
            if debug:
                print(f"  [debug] query_tokens for matching: {get_query_tokens(item)}")

            def get_cards():
                cards = driver.find_elements(By.XPATH, "//li[contains(., '$')]")
                if cards:
                    return cards
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
                for line in lines:
                    if "$" in line and price == "N/A":
                        price = line
                    elif price == "N/A" and ("per lb" in line or "per each" in line or "current price" in line.lower()):
                        num = re.search(r"[\d]+\.?[\d]*", line)
                        if num:
                            price = f"${num.group()}" if "$" not in line else line
                    elif any(x in line.lower() for x in ["oz", "ct", "lb", "gal", "pk"]):
                        unit = line
                best_match = None
                best_score = -1.0
                for line in lines:
                    line_clean = line.strip()
                    if not line_clean or "$" in line_clean or len(line_clean) < 2 or len(line_clean) > 200:
                        continue
                    if not product_matches_query(line_clean, item):
                        continue
                    score = match_score(line_clean, item)
                    if score > best_score or (score == best_score and (best_match is None or len(line_clean) > len(best_match))):
                        best_score = score
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
                if not product_matches_query(full_name, item):
                    if debug and count == 0 and index < 5:
                        print(f"  [debug] Skip (no keyword match): {repr(full_name[:70])}...")
                    index += 1
                    continue
                scraper_error = (
                    price == "N/A" or not title or title == "Unknown" or not price.strip()
                )
                data.append({
                    "search_term": item,
                    "product_name": full_name,
                    "unit_size": unit,
                    "price": price,
                    "store": "Publix",
                    "date": datetime.now().strftime("%Y-%m-%d"),
                    "scraper_error": scraper_error,
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
    """
    zip_code is accepted for interface compatibility but no longer used.
    """
    driver = setup_driver()
    try:
        return scrape_items(driver, items, debug=debug)
    finally:
        driver.quit()


if __name__ == "__main__":
    print(run("35401", ["eggs", "bread"]))
