# lib/enrich.py
"""
Enriches raw scraper results with clean_price, normalized_qty, unit_type,
brand_type, category, and optional flags. Used before saving or displaying.
"""
import re

from scrapers.units import standardize_unit
from scrapers.match import match_score

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
    Extract numeric price from strings like "Current price: $3.99", "$3.99",
    or messy formats like "$448current price $4.48".
    Returns float or None if unparseable.
    """
    if price_str is None:
        return None
    s = str(price_str).strip()
    
    # First, try to find "current price: $X.XX" or "current price $X.XX" pattern
    current_match = re.search(r'current price[:\s]*\$?([\d]+\.[\d]{2})', s, re.IGNORECASE)
    if current_match:
        try:
            return float(current_match.group(1))
        except ValueError:
            pass
    
    # Try to find "Now $X.XX" pattern (sale prices)
    now_match = re.search(r'now[:\s]*\$?([\d]+\.[\d]{2})', s, re.IGNORECASE)
    if now_match:
        try:
            return float(now_match.group(1))
        except ValueError:
            pass
    
    # Standard parsing: find price with dollar sign
    s_lower = s.lower()
    s_clean = s_lower.replace("current price", "").replace("$", "").strip()
    
    # Prefer prices with decimal (more likely to be actual prices, not quantities)
    decimal_match = re.search(r'(\d{1,3}\.\d{2})\b', s_clean)
    if decimal_match:
        try:
            val = float(decimal_match.group(1))
            if val < 500:  # Sanity check: grocery items rarely exceed $500
                return val
        except ValueError:
            pass
    
    # Fallback: any number
    match = re.search(r'[\d]+\.?[\d]*', s_clean)
    if match:
        try:
            val = float(match.group())
            if val < 500:
                return val
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


def _extract_unit_phrase_from_text(text):
    """
    Try to find a unit phrase in product name/title when scraper left unit_size empty.
    E.g. "Pete & Gerry's Organic Eggs Large 12 Ct" -> "12 Ct"
    Returns None if no recognizable pattern.
    """
    if not text or not isinstance(text, str):
        return None
    
    # Match: number (optional decimal) + optional space + unit word
    # Expanded to handle more patterns like "Fluid Ounce", "Ounce", etc.
    m = re.search(
        r"\b(\d+\.?\d*)\s*(?:fl(?:uid)?\s*)?(?:oz|ounce|ct|count|gal|gallon|lb|pound|sticks?|bottles?|loaf)\b",
        text,
        re.IGNORECASE,
    )
    if m:
        unit_part = m.group(0).split()[-1].lower()
        # Normalize "ounce" to "oz"
        if unit_part == "ounce":
            unit_part = "oz"
        return f"{m.group(1)} {unit_part}"
    
    # Also try to find "X Count" or "X Ct" pattern (common for eggs)
    count_match = re.search(r"\b(\d+)\s*(?:ct|count)\b", text, re.IGNORECASE)
    if count_match:
        return f"{count_match.group(1)} ct"
    
    return None


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
    - scraper_error (bool, preserved from scraper or default False)
    - name_match_uncertain (bool, from match_score threshold)
    - brand_type ('Private'|'National'|'Unknown')
    - category (str)
    - price_per_unit (float or None when comparable)

    Modifies each dict in place and returns the same list.
    """
    NAME_MATCH_UNCERTAIN_THRESHOLD = 0.5  # below this score -> name_match_uncertain
    for row in results:
        if row.get("scraper_error") is None:
            row["scraper_error"] = False
        # Clean price
        raw_price = row.get("price")
        cp = clean_price(raw_price)
        row["clean_price"] = cp if cp is not None else 999.0  # sentinel for sort

        # Unit standardization: use unit_size first; if unparseable, try to extract from product_name
        raw_unit = row.get("unit_size") or ""
        parsed = standardize_unit(raw_unit)
        if not parsed:
            fallback = _extract_unit_phrase_from_text(row.get("product_name"))
            if fallback:
                parsed = standardize_unit(fallback)
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

        # Name match confidence (low score -> uncertain)
        score = match_score(row.get("product_name"), row.get("search_term"))
        row["name_match_uncertain"] = score < NAME_MATCH_UNCERTAIN_THRESHOLD

    return results
