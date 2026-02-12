# tests/test_match.py
"""
Extensive tests for scrapers.match: normalization, synonyms, singular/plural,
punctuation, scoring, and rejection of irrelevant results.
"""
import pytest

try:
    from scrapers.match import (
        normalize_for_match,
        get_query_tokens,
        product_matches_query,
        match_score,
    )
except ImportError:
    import sys
    from pathlib import Path
    sys.path.insert(0, str(Path(__file__).resolve().parent.parent))
    from scrapers.match import (
        normalize_for_match,
        get_query_tokens,
        product_matches_query,
        match_score,
    )


# ---- normalize_for_match ----
@pytest.mark.parametrize("text,expected", [
    ("Friendly Farms 2% Milk", "friendly farms 2% milk"),
    ("Great Value Whole Milk, 1 gal", "great value whole milk 1 gal"),
    ("Large Eggs (12 count)", "large eggs 12 count"),
    ("", ""),
    ("  a  b  ", "a b"),
])
def test_normalize_for_match(text, expected):
    assert normalize_for_match(text) == expected


def test_normalize_for_match_handles_none_and_non_string():
    assert normalize_for_match(None) == ""
    assert normalize_for_match("") == ""
    assert normalize_for_match(123) == ""


# ---- get_query_tokens ----
def test_get_query_tokens_strips_punctuation_and_parentheses():
    tokens = get_query_tokens("Large Eggs (12 count)")
    assert "large" in tokens
    assert "eggs" in tokens
    assert "12" in tokens
    assert "count" in tokens


def test_get_query_tokens_drops_stopwords():
    tokens = get_query_tokens("milk and eggs for the day")
    assert "and" not in tokens
    assert "the" not in tokens
    assert "for" not in tokens


def test_get_query_tokens_empty():
    assert get_query_tokens("") == []
    assert get_query_tokens("   ") == []


# ---- product_matches_query: positive cases ----
@pytest.mark.parametrize("product_name,search_term", [
    ("Friendly Farms Whole Milk, 1 gal", "Whole Milk"),
    ("Friendly Farms 2% Milk", "2% milk"),
    ("Friendly Farms 2% Milk", "reduced fat milk"),
    ("Goldhen Large Eggs 12 ct", "Large Eggs (12 count)"),
    ("Goldhen Large Eggs 12 count", "eggs 12 ct"),
    ("Organic Bananas", "Bananas"),
    ("Organic Bananas", "banana"),
    ("Gala Apples", "Gala Apples"),
    ("Iceberg Lettuce", "Iceberg Lettuce"),
    ("Ground Beef 80/20", "Ground Beef 80/20"),
    ("Chicken Breast", "Chicken Breast"),
    ("White Bread", "White Bread"),
    ("Spaghetti Pasta", "Spaghetti Pasta"),
    ("Tomato Sauce", "Tomato Sauce"),
    ("Dish Soap", "Dish Soap"),
    ("Choceur Milk Mini Chocolate Bars", "chocolate"),
])
def test_product_matches_query_true(product_name, search_term):
    assert product_matches_query(product_name, search_term) is True


# ---- product_matches_query: negative cases (no false positives) ----
def test_product_matches_query_irrelevant_products():
    assert product_matches_query("Orange Juice", "Whole Milk") is False
    assert product_matches_query("Coca-Cola Soda", "Milk") is False
    assert product_matches_query("Turkey Breast", "Chicken Breast") is False


# ---- match_score ----
def test_match_score_full_match():
    assert match_score("Friendly Farms Whole Milk, 1 gal", "Whole Milk") >= 0.99


def test_match_score_partial_match():
    score = match_score("Goldhen Large Eggs 12 ct", "Large Eggs (12 count)")
    assert score >= 0.5
    assert score <= 1.0


def test_match_score_no_match():
    assert match_score("Orange Juice", "Whole Milk") == 0.0


def test_match_score_empty_query():
    assert match_score("Anything", "") == 0.0


def test_match_score_empty_product():
    assert match_score("", "Milk") == 0.0


# ---- Synonyms: 12 count / 12 ct ----
@pytest.mark.parametrize("product_name", [
    "Large Eggs 12 ct",
    "Large Eggs 12 count",
    "Eggs 12-count",
])
def test_query_12_count_matches_product_ct_or_count(product_name):
    assert product_matches_query(product_name, "Large Eggs (12 count)") is True


# ---- Singular/plural ----
@pytest.mark.parametrize("product_name,search_term", [
    ("Organic Bananas", "banana"),
    ("Organic Banana", "bananas"),
    ("Gala Apples", "apple"),
    ("Gala Apple", "apples"),
])
def test_singular_plural(product_name, search_term):
    assert product_matches_query(product_name, search_term) is True


# ---- Punctuation in product name ----
def test_punctuation_ignored():
    assert product_matches_query("Milk, 1 gal", "Milk") is True
    assert product_matches_query("Eggs (12-count)", "Eggs 12 count") is True
