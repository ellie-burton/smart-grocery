# Smart Grocery – Implementation Plan

This plan maps the ideas in `next_steps.md` to concrete tasks and file changes.

---

## Phase 1: Data pipeline & unit standardization

### 1.1 Unit standardization module

**Goal:** Parse messy `unit_size` strings into comparable `normalized_qty` + `unit_type` (oz or count).

**Tasks:**

| # | Task | Details |
|---|------|--------|
| 1 | Add `standardize_unit()` | Create `scrapers/units.py` (or `lib/units.py`) with the logic from `next_steps.md`: handle dozen→12 ct, gal→128 oz, lb→16 oz, pack, oz, ct. Return `{'qty': float, 'unit': 'oz'|'count'}` or `None`. |
| 2 | Add tests | Optional: small unit tests for "1 gal", "0.5 gal", "12 ct", "1 dozen", "20 oz", "1 lb", etc. |

**Files:** New `scrapers/units.py` (or `lib/units.py`).

---

### 1.2 Data enrichment (new columns)

**Goal:** Before saving or displaying, add: `clean_price`, `normalized_qty`, `unit_type`, `brand_type`, `category`, and optional flags.

**Tasks:**

| # | Task | Details |
|---|------|--------|
| 1 | Centralize cleaning | In one place (e.g. `main.py` or new `lib/enrich.py`): parse price string → `clean_price` (float). |
| 2 | Apply unit standardization | For each row, call `standardize_unit(unit_size)` → set `normalized_qty`, `unit_type`; if `None`, set flag `unit_uncertain=True`. |
| 3 | Add `brand_type` | If product name starts with "Great Value", "Publix", "Friendly Farms", "Simply Nature", etc. → `"Private"`, else `"National"`. |
| 4 | Add `category` | Map each `search_term` to a category (e.g. from a small mapping: Milk→Dairy, Eggs→Dairy, Bread→Pantry). Either from a config dict or from the basket list (see Phase 2). |
| 5 | Optional flags | Add `scraper_error`, `name_match_uncertain`, `unit_uncertain` if you have that info from scrapers. |

**Where to apply:** In `main.py` before returning results, or in `app.py` right after `main.run_scrapers_parallel()` when building the DataFrame. Prefer one place (e.g. a `enrich_results(results, category_map)` in `main.py` or `lib/enrich.py`) so CLI and UI both get enriched data.

**Files:** `main.py` and/or new `lib/enrich.py`, `app.py` (use new columns in display).

---

### 1.3 Cost per unit in UI

**Goal:** Compare "1 gal" vs "64 oz" by price per unit.

**Tasks:**

| # | Task | Details |
|---|------|--------|
| 1 | Compute `price_per_unit` | When `normalized_qty` is present: `price_per_unit = clean_price / normalized_qty`. |
| 2 | Show in tables | Add column "Price/unit" (e.g. $/oz or $/ct) in "Cheapest Basket" and "All Prices" tabs; optionally sort by price per unit for comparable items. |

**Files:** `app.py` (and any CLI output in `main.py` if you want it there too).

---

## Phase 2: Search depth & daily basket

### 2.1 Enforce “Top 5 + keyword filter” everywhere

**Goal:** All stores return up to 5 results per search term, with keyword matching; store only “survivors.”

**Tasks:**

| # | Task | Details |
|---|------|--------|
| 1 | Audit scrapers | Confirm Aldi, Publix, Walmart each: (a) take up to 5 results per search, (b) apply keyword/flexible matching (like Aldi’s `query_words`). |
| 2 | Align logic | If Publix or Walmart don’t limit to 5 or don’t filter by keywords, add the same pattern (top 5, then filter; keep survivors). |

**Files:** `scrapers/aldi.py`, `scrapers/publix.py`, `scrapers/walmart.py`.

---

### 2.2 Fixed “Daily Basket” for longitudinal data

**Goal:** A fixed list of 12 items run on a schedule (e.g. daily) to answer “Is Tuesday cheaper?” etc.

**Tasks:**

| # | Task | Details |
|---|------|--------|
| 1 | Define `DAILY_BASKET` | In `main.py` or a new `config.py`: list of 12 search terms: "Whole Milk", "Large Eggs (12 count)", "Salted Butter", "Bananas", "Gala Apples", "Iceberg Lettuce", "Ground Beef 80/20", "Chicken Breast", "White Bread", "Spaghetti Pasta", "Tomato Sauce", "Dish Soap". |
| 2 | Category map for basket | Same module: map each term to category (Dairy, Produce, Meat, Pantry, Household) for the `category` enrichment field. |
| 3 | Daily run script | Add `run_daily_basket.py`: load `DAILY_BASKET`, call `run_scrapers_parallel(zip_code, DAILY_BASKET)`, enrich results, then append to `data/grocery_prices.csv` (or a dedicated `data/daily_basket.csv`) with timestamp. |
| 4 | Document Task Scheduler | In README or a short `DAILY_RUN.md`: how to set a Windows Task Scheduler task to run `run_daily_basket.py` (e.g. with a fixed zip and Python path) every morning. |

**Files:** New `config.py` (or extend `main.py`), new `run_daily_basket.py`, `README.md` or `DAILY_RUN.md`.

---

## Phase 3: UX & polish

### 3.1 “How it works” page

**Goal:** One page in the UI explaining the app.

**Tasks:**

| # | Task | Details |
|---|------|--------|
| 1 | Add page | Use Streamlit’s multi-page pattern: add `pages/2_How_it_works.py` (or a single “How it works” section/expander on the main page) with short explanation: what stores, how search works (top 5 + keyword match), what “cheapest basket” means, optional note about unit comparison and daily basket. |

**Files:** `pages/2_How_it_works.py` and/or `app.py`.

---

### 3.2 Loading experience: spinner + grocery facts

**Goal:** Show a spinner and fun grocery facts while scrapers run.

**Tasks:**

| # | Task | Details |
|---|------|--------|
| 1 | Spinner | In `app.py`, wrap the `run_scrapers_parallel()` call in `st.spinner("Finding prices…")` (or a custom message). |
| 2 | Facts | Define a list of short “grocery facts” (e.g. “The average American spends about $X on groceries per month.”). Each few seconds (or each time the user triggers a run), show a random fact in the sidebar or above the results. |

**Files:** `app.py`, optionally a small `data/grocery_facts.txt` or list in code.

---

### 3.3 README for local setup

**Goal:** New contributors can run the app and daily script locally.

**Tasks:**

| # | Task | Details |
|---|------|--------|
| 1 | Expand README | Add: Python version (e.g. 3.9+), `pip install -r requirements.txt`, how to run `streamlit run app.py`, how to run `python main.py` and `python run_daily_basket.py`, note about Chrome/ChromeDriver, optional env vars (e.g. zip for daily run). |
| 2 | Daily run | Link or summarize Task Scheduler steps from `DAILY_RUN.md`. |

**Files:** `README.md`.

---

## Phase 4: Robustness (secondary)

### 4.1 More robust product name matching

**Goal:** Fewer false positives/negatives from search.

**Tasks:**

| # | Task | Details |
|---|------|--------|
| 1 | Improve matching | Consider: synonyms (e.g. “2% milk” ↔ “reduced fat”), ignoring punctuation, handling “12 count” vs “12 ct” in the query. Implement in scrapers or in a shared `scrapers/match.py` used by all. |
| 2 | Optional scoring | Score each result by keyword overlap and optionally cap or rank by score. |

**Files:** `scrapers/utils.py` or new `scrapers/match.py`, then each scraper.

---

### 4.2 Scraper and data quality flags

**Goal:** Persist and show when data might be unreliable.

**Tasks:**

| # | Task | Details |
|---|------|--------|
| 1 | Set flags in scrapers | Where a scraper catches an error or detects ambiguous HTML, add a field e.g. `scraper_error=True` or `name_match_uncertain=True` on that row. |
| 2 | Set `unit_uncertain` | When `standardize_unit()` returns `None`, set `unit_uncertain=True` in enrichment. |
| 3 | Show in UI | In “All Prices” (or a filter), optionally show a small indicator for rows with any flag. |

**Files:** `scrapers/*.py`, enrichment code, `app.py`.

---

## Suggested order of implementation

1. **Phase 1.1** – Unit standardization module (needed for 1.2 and 1.3).  
2. **Phase 1.2** – Data enrichment (clean_price, normalized_qty, unit_type, brand_type, category).  
3. **Phase 1.3** – Cost per unit in UI.  
4. **Phase 2.1** – Verify Top 5 + keyword filter in all scrapers.  
5. **Phase 2.2** – DAILY_BASKET, category map, `run_daily_basket.py`, and Task Scheduler doc.  
6. **Phase 3.1** – “How it works” page.  
7. **Phase 3.2** – Spinner + grocery facts.  
8. **Phase 3.3** – README for local setup.  
9. **Phase 4** – Matching and flags as time allows.

---

## File summary

| File | Action |
|------|--------|
| `scrapers/units.py` or `lib/units.py` | **New** – `standardize_unit()` |
| `lib/enrich.py` or in `main.py` | **New** or **Edit** – enrichment + category map |
| `config.py` | **New** – DAILY_BASKET + category map |
| `run_daily_basket.py` | **New** – daily script, append to CSV |
| `main.py` | **Edit** – call enrichment; optionally use config for basket |
| `app.py` | **Edit** – use enriched columns, price per unit, spinner, facts |
| `scrapers/aldi.py`, `publix.py`, `walmart.py` | **Edit** – Top 5 + filter; optional flags |
| `pages/2_How_it_works.py` | **New** – How it works |
| `README.md` | **Edit** – local setup + daily run |
| `DAILY_RUN.md` | **New** (optional) – Task Scheduler steps |

This plan is ready to execute step-by-step; start with Phase 1.1 and 1.2 for the highest impact.
