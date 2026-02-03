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

    # 5. Standard Ounces (oz, fl oz) / Counts (ct, count)
    numbers = re.findall(r"[\d\.]+", s)
    val = _first_float(numbers)
    if val is None:
        return None

    if "oz" in s:  # covers "fl oz" as well
        return {"qty": val, "unit": "oz"}
    if "ct" in s or "count" in s:
        return {"qty": val, "unit": "count"}

    return None
