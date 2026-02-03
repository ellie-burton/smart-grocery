# lib/enrich.py
"""
Enriches raw scraper results with clean_price, normalized_qty, unit_type,
brand_type, category, and optional flags. Used before saving or displaying.
"""
import re

from scrapers.units import standardize_unit

# Private-label prefixes (case-insensitive); product name starting with these -> "Private"
PRIVATE_LABEL_PREFIXES = (
    "great value",
    "publix",
    "friendly farms",
    "simply nature",
    "choceur",
    "goldhen",
    "clancy",
    "baker's corner",
    "never any",
    "earth grown",
    "live gfree",
    "publix greenwise",
    "publix vital farms",
)

# When name starts with "Publix ", these national brands often follow -> "National"
NATIONAL_BRANDS_AFTER_PUBLIX = (
    "organic valley",
    "horizon",
    "nellies",
    "eggland's best",
    "eggland",
    "vital farms",
    "land o lakes",
    "nature's own",
    "just bare",
    "contadina",
    "finish",
    "pete & gerry's",
    "pete & gerry",
    "fresh express",
    "force of nature",
)

# Default category mapping: search_term (lower) -> category
# Used when no category_map is passed (e.g. from DAILY_BASKET in Phase 2).
DEFAULT_CATEGORY_MAP = {
    "milk": "Dairy",
    "whole milk": "Dairy",
    "eggs": "Dairy",
    "large eggs (12 count)": "Dairy",
    "butter": "Dairy",
    "salted butter": "Dairy",
    "bread": "Pantry",
    "white bread": "Pantry",
    "bananas": "Produce",
    "gala apples": "Produce",
    "iceberg lettuce": "Produce",
    "ground beef 80/20": "Meat",
    "chicken breast": "Meat",
    "spaghetti pasta": "Pantry",
    "tomato sauce": "Pantry",
    "dish soap": "Household",
    "pasta": "Pantry",
}


def clean_price(price_str):
    """
    Extract numeric price from strings like "Current price: $3.99" or "$3.99".
    Returns float or None if unparseable.
    """
    if price_str is None:
        return None
    s = str(price_str).lower().strip()
    s = s.replace("current price", "").replace("$", "").strip()
    # Remove any trailing text (e.g. "3.99 each")
    match = re.search(r"[\d]+\.?[\d]*", s)
    if match:
        try:
            return float(match.group())
        except ValueError:
            return None
    return None


def get_brand_type(product_name):
    """Returns 'Private' if product name starts with a known store brand, else 'National'."""
    if not product_name or not isinstance(product_name, str):
        return "Unknown"
    name_lower = product_name.lower().strip()
    # "Publix Organic Valley..." etc. are national brands sold at Publix
    if name_lower.startswith("publix "):
        rest = name_lower[7:].lstrip()
        for nb in NATIONAL_BRANDS_AFTER_PUBLIX:
            if rest.startswith(nb):
                return "National"
    for prefix in PRIVATE_LABEL_PREFIXES:
        if name_lower.startswith(prefix):
            return "Private"
    return "National"


def get_category(search_term, category_map=None):
    """Maps search_term to category. Uses category_map or DEFAULT_CATEGORY_MAP."""
    if not search_term:
        return "Other"
    key = search_term.lower().strip()
    mapping = category_map if category_map is not None else DEFAULT_CATEGORY_MAP
    return mapping.get(key, "Other")


def enrich_results(results, category_map=None):
    """
    Takes a list of raw scraper result dicts and adds:
    - clean_price (float)
    - normalized_qty (float or None)
    - unit_type ('oz'|'count'|None)
    - unit_uncertain (bool)
    - brand_type ('Private'|'National'|'Unknown')
    - category (str)
    - price_per_unit (float or None when comparable)

    Modifies each dict in place and returns the same list.
    """
    for row in results:
        # Clean price
        raw_price = row.get("price")
        cp = clean_price(raw_price)
        row["clean_price"] = cp if cp is not None else 999.0  # sentinel for sort

        # Unit standardization
        raw_unit = row.get("unit_size") or ""
        parsed = standardize_unit(raw_unit)
        if parsed:
            row["normalized_qty"] = parsed["qty"]
            row["unit_type"] = parsed["unit"]
            row["unit_uncertain"] = False
        else:
            row["normalized_qty"] = None
            row["unit_type"] = None
            row["unit_uncertain"] = True

        # Price per unit (only when we have comparable units)
        if row["normalized_qty"] and row["normalized_qty"] > 0 and row["clean_price"] is not None and row["clean_price"] < 999.0:
            row["price_per_unit"] = round(row["clean_price"] / row["normalized_qty"], 6)
        else:
            row["price_per_unit"] = None

        # Brand type
        row["brand_type"] = get_brand_type(row.get("product_name"))

        # Category
        row["category"] = get_category(row.get("search_term"), category_map)

    return results
