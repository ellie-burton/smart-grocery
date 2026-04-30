"""
Walmart scraper — HTTP-only.

Fetches search results via plain HTTP requests and parses the server-rendered
HTML.  No Selenium or browser automation required, which avoids Walmart's
aggressive PerimeterX/HUMAN bot detection entirely.

Location-specific pricing is not set; Walmart.com returns prices for the
nearest store based on the requester's IP geolocation, which is close enough
for comparison purposes.
"""

import re
from datetime import datetime
from urllib.parse import quote_plus
from urllib.request import Request, urlopen
from bs4 import BeautifulSoup

try:
    from .utils import _get_chrome_version
    from .match import product_matches_query
except ImportError:
    from utils import _get_chrome_version
    from match import product_matches_query


def _build_user_agent():
    """Build a UA string from the installed Chrome version for realistic headers."""
    full_version = _get_chrome_version()
    if full_version:
        return (
            f"Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 "
            f"(KHTML, like Gecko) Chrome/{full_version} Safari/537.36"
        )
    return (
        "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 "
        "(KHTML, like Gecko) Chrome/134.0.0.0 Safari/537.36"
    )


def _extract_walmart_cards_from_html(html, item):
    """
    Parse Walmart search HTML into normalized scraper rows (max 5 matches).
    """
    data = []
    soup = BeautifulSoup(html, "html.parser")
    cards = soup.find_all("div", attrs={"data-test-id": "gpt-product-tile-grid-container"})
    count = 0
    for card in cards:
        if count >= 5:
            break
        try:
            title_tag = card.find("h3", attrs={"data-automation-id": "product-title"})
            title = title_tag.get_text(strip=True) if title_tag else "Unknown"

            price = "N/A"
            price_container = card.find("div", attrs={"data-automation-id": "product-price"})

            if price_container:
                sr_text = price_container.find("span", class_="w_iUH7")
                if sr_text:
                    raw_price = sr_text.get_text(strip=True)
                    if "$" in raw_price:
                        price = "$" + raw_price.split("$")[-1]

                if price == "N/A":
                    price_flex = price_container.find("div", attrs={"data-test-id": "gpt-price-flex-container"})
                    if price_flex:
                        raw_text = price_flex.get_text(strip=True)
                        current_match = re.search(r"current price[:\s]*\$?([\d]+\.[\d]{2})", raw_text, re.IGNORECASE)
                        if current_match:
                            price = f"${current_match.group(1)}"
                        else:
                            price_matches = re.findall(r"\$?([\d]{1,2}\.[\d]{2})", raw_text)
                            if price_matches:
                                price = f"${price_matches[0]}"
                            elif "$" in raw_text:
                                price = "$" + raw_text.split("$")[-1].split()[0]

            unit = ""
            if "," in title:
                parts = title.split(",")
                if len(parts) > 1:
                    unit = parts[-1].strip()

            full_name = f"Walmart {title}"
            if not product_matches_query(full_name, item):
                continue

            scraper_error = (price == "N/A" or not title or title == "Unknown")
            data.append({
                "search_term": item,
                "product_name": full_name,
                "unit_size": unit,
                "price": price,
                "store": "Walmart",
                "date": datetime.now().strftime("%Y-%m-%d"),
                "scraper_error": scraper_error,
            })
            count += 1
        except (AttributeError, TypeError):
            continue
    return data


def _http_search(item):
    """Fetch Walmart search results via plain HTTP and parse the HTML."""
    search_url = f"https://www.walmart.com/search?q={quote_plus(item)}"
    headers = {
        "User-Agent": _build_user_agent(),
        "Accept-Language": "en-US,en;q=0.9",
        "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8",
        "Connection": "keep-alive",
    }
    req = Request(search_url, headers=headers)
    with urlopen(req, timeout=30) as resp:
        html = resp.read().decode("utf-8", errors="ignore")
    if "press and hold" in html.lower() or "robot or human" in html.lower():
        print(f"  HTTP request for '{item}' was challenged — returning empty.")
        return []
    return _extract_walmart_cards_from_html(html, item)


def run(zip_code, items):
    """
    Scrape Walmart for each item via HTTP.

    zip_code is accepted for interface compatibility with the other scrapers
    but is not used — Walmart returns local prices based on IP geolocation.
    """
    data = []
    for item in items:
        print(f"[Walmart HTTP] Searching for: {item}...")
        try:
            rows = _http_search(item)
            if rows:
                print(f"  {item}: {len(rows)} results")
            else:
                print(f"  {item}: no results")
            data.extend(rows)
        except Exception as e:
            print(f"  {item}: error — {e}")
    return data


if __name__ == "__main__":
    print(run("35401", ["eggs", "whole milk", "white bread"]))
