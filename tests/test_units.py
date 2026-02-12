# tests/test_units.py
"""
Extensive tests for scrapers.units.standardize_unit().
Validates that messy unit_size strings are parsed into comparable qty + unit (oz or count).
"""
import pytest

# Allow running from project root or from tests/
try:
    from scrapers.units import standardize_unit
except ImportError:
    import sys
    from pathlib import Path
    sys.path.insert(0, str(Path(__file__).resolve().parent.parent))
    from scrapers.units import standardize_unit


# ---- Gallons ----
@pytest.mark.parametrize("raw,expected_qty,expected_unit", [
    ("1 gal", 128.0, "oz"),
    ("1 gallon", 128.0, "oz"),
    ("1.0 gal", 128.0, "oz"),
    ("0.5 gal", 64.0, "oz"),
    ("0.5 gallon", 64.0, "oz"),
    ("2 gal", 256.0, "oz"),
])
def test_standardize_unit_gallons(raw, expected_qty, expected_unit):
    result = standardize_unit(raw)
    assert result is not None
    assert result["qty"] == expected_qty
    assert result["unit"] == expected_unit


def test_standardize_unit_gallon_no_number():
    result = standardize_unit("gal")
    assert result is not None
    assert result["qty"] == 128.0
    assert result["unit"] == "oz"


# ---- Dozen / count ----
@pytest.mark.parametrize("raw,expected_qty,expected_unit", [
    ("1 dozen", 12.0, "count"),
    ("dozen", 12.0, "count"),
    ("12 ct", 12.0, "count"),
    ("12 count", 12.0, "count"),
    ("12-count", 12.0, "count"),
    ("24 ct", 24.0, "count"),
    ("18 count", 18.0, "count"),
])
def test_standardize_unit_dozen_and_count(raw, expected_qty, expected_unit):
    result = standardize_unit(raw)
    assert result is not None
    assert result["qty"] == expected_qty
    assert result["unit"] == expected_unit


# ---- Pounds ----
@pytest.mark.parametrize("raw,expected_qty,expected_unit", [
    ("1 lb", 16.0, "oz"),
    ("1 pound", 16.0, "oz"),
    ("2 lbs", 32.0, "oz"),
    ("0.5 lb", 8.0, "oz"),
    ("1.5 pounds", 24.0, "oz"),
])
def test_standardize_unit_pounds(raw, expected_qty, expected_unit):
    result = standardize_unit(raw)
    assert result is not None
    assert result["qty"] == expected_qty
    assert result["unit"] == expected_unit


# ---- Ounces ----
@pytest.mark.parametrize("raw,expected_qty,expected_unit", [
    ("20 oz", 20.0, "oz"),
    ("64 fl oz", 64.0, "oz"),
    ("128 fl oz", 128.0, "oz"),
    ("16 oz", 16.0, "oz"),
    ("0.5 oz", 0.5, "oz"),
])
def test_standardize_unit_ounces(raw, expected_qty, expected_unit):
    result = standardize_unit(raw)
    assert result is not None
    assert result["qty"] == expected_qty
    assert result["unit"] == expected_unit


# ---- Pack / each ----
@pytest.mark.parametrize("raw,expected_qty,expected_unit", [
    ("1 pack", 1.0, "count"),
    ("2 pack", 2.0, "count"),
    ("6 pack", 6.0, "count"),
    ("1 each", 1.0, "count"),
    ("each", 1.0, "count"),
])
def test_standardize_unit_pack_and_each(raw, expected_qty, expected_unit):
    result = standardize_unit(raw)
    assert result is not None
    assert result["qty"] == expected_qty
    assert result["unit"] == expected_unit


# ---- Stick / bottle / bag (from sample.csv quality fixes) ----
@pytest.mark.parametrize("raw,expected_qty,expected_unit", [
    ("4 Sticks", 4.0, "count"),
    ("4 Sticks (Refrigerated)", 4.0, "count"),
    ("Single Bottle", 1.0, "count"),
    ("Bag", 1.0, "count"),
    ("20 oz bag", 20.0, "oz"),  # oz takes precedence when present
])
def test_standardize_unit_stick_bottle_bag(raw, expected_qty, expected_unit):
    result = standardize_unit(raw)
    assert result is not None
    assert result["qty"] == expected_qty
    assert result["unit"] == expected_unit


# ---- Edge / invalid ----
@pytest.mark.parametrize("raw", [
    None,
    "",
    "   ",
    "unknown",
    "bunch",
    "bag",
    "box",  # no number
])
def test_standardize_unit_returns_none(raw):
    result = standardize_unit(raw)
    assert result is None


def test_standardize_unit_non_string():
    assert standardize_unit(123) is None
    assert standardize_unit([]) is None


def test_standardize_unit_case_insensitive():
    assert standardize_unit("1 GAL") == {"qty": 128.0, "unit": "oz"}
    assert standardize_unit("12 CT") == {"qty": 12.0, "unit": "count"}
    assert standardize_unit("1 Dozen") == {"qty": 12.0, "unit": "count"}
