# scrapers/match.py
"""
Robust product-name matching for grocery search results.
Handles: punctuation normalization, synonyms (e.g. 2% milk ↔ reduced fat),
"12 count" vs "12 ct", singular/plural, and optional match scoring.
Used by Aldi, Publix, and Walmart scrapers for consistent filtering.
"""
import re

# Stopwords to ignore when building query tokens (short and non-discriminative)
_STOPWORDS = frozenset(("the", "and", "for", "with", "each", "per"))

# Synonym groups: each key maps to a set of equivalent terms (including itself).
# Only add groups where terms are truly interchangeable (units, abbreviations).
_SYNONYM_GROUPS = [
    frozenset(("count", "ct", "cnt")),
    frozenset(("ounce", "oz", "ounces")),
    frozenset(("pound", "lb", "pounds", "lbs")),
    frozenset(("gallon", "gal", "gallons", "gals")),
    frozenset(("reduced", "fat", "2%", "2 percent", "lowfat", "low-fat", "low fat", "lite", "light")),
    frozenset(("large", "lg")),
    frozenset(("medium", "med")),
    frozenset(("dozen", "12")),
]

# Build a map: token -> set of all synonyms in its group (including token itself)
_SYNONYM_MAP = {}
for group in _SYNONYM_GROUPS:
    for term in group:
        _SYNONYM_MAP[term] = group


def normalize_for_match(text):
    """
    Normalize text for matching: lowercase, remove punctuation, collapse spaces.
    """
    if not text or not isinstance(text, str):
        return ""
    # Replace common punctuation with space, then collapse spaces
    s = text.lower().strip()
    s = re.sub(r"[\'\"\,\-\/\(\)]", " ", s)
    s = re.sub(r"\s+", " ", s)
    return s.strip()


def _tokenize(normalized_text):
    """Split normalized text into words (min length 1 for numbers like '12')."""
    if not normalized_text:
        return []
    return [t for t in normalized_text.split() if t]


def _expand_token(token):
    """Return set of variants for this token (singular/plural + synonyms)."""
    variants = {token}
    # Singular/plural
    if len(token) > 1 and token.endswith("s") and not token.endswith("ss"):
        variants.add(token[:-1])  # bananas -> banana
    elif not token.endswith("s"):
        variants.add(token + "s")  # banana -> bananas
    # Synonyms
    if token in _SYNONYM_MAP:
        variants |= _SYNONYM_MAP[token]
    return variants


def get_query_tokens(search_term):
    """
    Normalize search term and return list of significant tokens (excluding stopwords).
    Parentheses and punctuation are stripped so "Large Eggs (12 count)" yields
    tokens like large, eggs, 12, count (and synonym 'ct' can match "12 ct" in product).
    """
    norm = normalize_for_match(search_term)
    tokens = _tokenize(norm)
    return [t for t in tokens if t not in _STOPWORDS and len(t) >= 1]


def product_matches_query(product_name, search_term, min_token_match=None):
    """
    Return True if product_name is considered a match for the search_term.
    Uses normalized token overlap and synonym expansion. Requires at least
    min_token_match query tokens (or their synonyms) to appear in the product.
    If min_token_match is None, requires 2 for multi-word queries (to reduce
    false positives like "Turkey Breast" matching "Chicken Breast") else 1.
    """
    if not product_name or not search_term:
        return False
    query_tokens = get_query_tokens(search_term)
    if not query_tokens:
        return normalize_for_match(search_term) in normalize_for_match(product_name)
    if min_token_match is None:
        min_token_match = 2 if len(query_tokens) >= 2 else 1
    product_norm = normalize_for_match(product_name)
    product_tokens = set(_tokenize(product_norm))
    product_str = product_norm
    matched = 0
    for qt in query_tokens:
        variants = _expand_token(qt)
        for v in variants:
            if v in product_tokens or v in product_str:
                matched += 1
                break
    return matched >= min_token_match


def match_score(product_name, search_term):
    """
    Return a score in [0.0, 1.0]: fraction of query tokens (or synonyms) that
    appear in the product. Use for ranking when keeping top 5.
    """
    if not product_name or not search_term:
        return 0.0
    query_tokens = get_query_tokens(search_term)
    if not query_tokens:
        return 1.0 if normalize_for_match(search_term) in normalize_for_match(product_name) else 0.0
    product_norm = normalize_for_match(product_name)
    product_tokens = set(_tokenize(product_norm))
    product_str = product_norm
    matched = 0
    for qt in query_tokens:
        variants = _expand_token(qt)
        for v in variants:
            if v in product_tokens or v in product_str:
                matched += 1
                break
    return matched / len(query_tokens) if query_tokens else 0.0
