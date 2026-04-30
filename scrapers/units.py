# scrapers/units.py
"""
Standardizes messy unit_size strings into comparable qty + unit (oz or count).
Used for cost-per-unit comparison (e.g. 1 gal vs 64 oz).
"""
import re


def _first_float(tokens):
    """Return the first token that parses as a positive float, or None."""
    for t in (tokens or []):
        try:
            v = float(t)
            if v > 0:
                return v
        except (ValueError, TypeError):
            continue
    return None


def standardize_unit(raw_unit_str):
    """
    Parses messy unit strings into a standardized dictionary.
    Returns: {'qty': float, 'unit': 'oz'|'count'} or None
    """
    if not isinstance(raw_unit_str, str):
        return None

    s = raw_unit_str.lower().strip()
    if not s:
        return None

    # Strip parenthetical content so "4 Sticks (Refrigerated)" parses as "4 Sticks"
    s = re.sub(r"\s*\([^)]*\)", "", s).strip()
    if not s:
        return None
    
    # Skip non-unit descriptors that shouldn't be parsed
    skip_patterns = ["shelf-stable", "shelf stable", "non-gmo", "organic", "natural"]
    for skip in skip_patterns:
        if s == skip:
            return None

    # --- CONVERSION LOGIC ---
    # 1. Handle "Dozen" -> 12 count
    if "dozen" in s:
        return {"qty": 12.0, "unit": "count"}

    # 2. Handle Gallons -> 128 oz
    if "gal" in s:
        val = _first_float(re.findall(r"[\d\.]+", s))
        if val is not None:
            return {"qty": val * 128.0, "unit": "oz"}
        return {"qty": 128.0, "unit": "oz"}

    # 3. Handle Pounds -> 16 oz
    if "lb" in s or "pound" in s:
        val = _first_float(re.findall(r"[\d\.]+", s))
        if val is not None:
            return {"qty": val * 16.0, "unit": "oz"}
        return {"qty": 16.0, "unit": "oz"}

    # 4. Handle "Pack" (often ambiguous, usually count)
    if "pack" in s:
        val = _first_float(re.findall(r"[\d\.]+", s))
        if val is not None:
            return {"qty": val, "unit": "count"}

    # 4b. Handle "each" (e.g. "1 each", "each")
    if "each" in s:
        val = _first_float(re.findall(r"[\d\.]+", s))
        return {"qty": val if val is not None else 1.0, "unit": "count"}

    # 5. Standard Ounces - handle various formats including "Fluid Ounce", "fl oz", "oz"
    # Check for ounce patterns (case-insensitive via lower())
    numbers = re.findall(r"[\d\.]+", s)
    val = _first_float(numbers)
    if val is not None:
        # "90 fluid ounce", "24.5 ounce", "fl oz", "oz"
        if "ounce" in s or "oz" in s:
            return {"qty": val, "unit": "oz"}
        if "ct" in s or "count" in s:
            return {"qty": val, "unit": "count"}

    # 4c. Handle "stick"/"sticks" (e.g. "4 Sticks", "4 Sticks (Refrigerated)")
    if "stick" in s:
        val = _first_float(re.findall(r"[\d\.]+", s))
        return {"qty": val if val is not None else 1.0, "unit": "count"}

    # 4d. Handle "bottle"/"bottles" (e.g. "Single Bottle", "6 Pack Bottles")
    if "bottle" in s:
        val = _first_float(re.findall(r"[\d\.]+", s))
        if val is None and ("single" in s or "1 " in s):
            val = 1.0
        return {"qty": val if val is not None else 1.0, "unit": "count"}

    # 4e. Handle "bag" - try to extract oz from it first (e.g. "16 oz bag")
    if "bag" in s:
        # Already handled by oz check above, but if no oz found:
        val = _first_float(re.findall(r"[\d\.]+", s))
        return {"qty": val if val is not None else 1.0, "unit": "count"}
    
    # 4f. Handle "loaf" for bread (e.g. "20 oz loaf")
    if "loaf" in s:
        val = _first_float(re.findall(r"[\d\.]+", s))
        if val is not None:
            return {"qty": val, "unit": "oz"}
        return {"qty": 1.0, "unit": "count"}

    return None
