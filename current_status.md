# Smart Grocery – Current Status (Audit)

*Generated from repo audit and comparison with Proposal.md, README.md, IMPLEMENTATION_PLAN.md, next_steps.md, and DAILY_RUN.md.*

---

## 1. Repo audit

### 1.1 Structure

| Path | Purpose |
|------|--------|
| `app.py` | Streamlit entry point; zip + grocery list → parallel scrape → tabs (Cheapest Basket, All Prices) |
| `main.py` | `run_scrapers_parallel(zip_code, items, category_map)`; calls Aldi, Publix, Walmart; enriches via `lib.enrich` |
| `config.py` | `DAILY_BASKET` (12 items), `DAILY_BASKET_CATEGORY_MAP` |
| `run_daily_basket.py` | Runs fixed basket, appends enriched results to `data/daily_basket.csv`; zip from CLI or `SMART_GROCERY_ZIP` |
| `lib/enrich.py` | `enrich_results()`: clean_price, normalized_qty, unit_type, unit_uncertain, price_per_unit, brand_type, category; uses `scrapers.units.standardize_unit` |
| `scrapers/units.py` | `standardize_unit(raw_unit_str)` → `{qty, unit}` (oz/count); handles gal, lb, dozen, pack, oz, ct, stick, bottle, bag; strips parentheticals |
| `scrapers/aldi.py` | Selenium + BeautifulSoup; top 5 per item + keyword filter; location not used (no zip on Aldi) |
| `scrapers/publix.py` | Selenium; zip → delivery store; top 5 + keyword filter via `query_words` |
| `scrapers/walmart.py` | undetected_chromedriver; zip → store; top 5 + keyword filter |
| `scrapers/utils.py` | `setup_driver()`, Chrome version detection for driver |
| `pages/2_How_it_works.py` | Streamlit page: stores, search, cheapest basket, price per unit, daily basket |
| `data/daily_basket.csv` | Longitudinal output; has header and enriched columns |
| `old/` | Archived debug/legacy files (parallel.py, run_publix_debug.py, run_walmart_only.py, temp test.py, temp CSVs); see `old/README.md` |

### 1.2 Implemented features

- **Phase 1.1 – Unit standardization:** ✅ `scrapers/units.py` with `standardize_unit()` (gal→oz, lb→oz, dozen→count, pack/oz/ct).
- **Phase 1.2 – Data enrichment:** ✅ `lib/enrich.py`: clean_price, normalized_qty, unit_type, unit_uncertain, brand_type, category, price_per_unit; category from `DEFAULT_CATEGORY_MAP` or passed `category_map`.
- **Phase 1.3 – Cost per unit in UI:** ✅ `app.py` shows "Price/unit" column and uses it in Cheapest Basket and All Prices.
- **Phase 2.1 – Top 5 + keyword filter:** ✅ All three scrapers limit to 5 results per search term and apply keyword matching; only survivors stored.
- **Phase 2.2 – Daily basket:** ✅ `config.py` (DAILY_BASKET + category map), `run_daily_basket.py`, append to `data/daily_basket.csv`; `DAILY_RUN.md` documents Task Scheduler.
- **Phase 3.1 – How it works:** ✅ `pages/2_How_it_works.py` describes stores, search, cheapest basket, price per unit, daily basket.
- **Phase 3.2 – Spinner + facts:** ✅ `st.spinner("Finding prices…")` around scrape; `GROCERY_FACTS` in sidebar.
- **Phase 3.3 – README:** ✅ Python 3.9+, pip install, streamlit run, main.py, run_daily_basket.py, Chrome, optional env (zip); link to DAILY_RUN.md.

### 1.3 Gaps / quirks

- **requirements.txt:** ✅ Populated (streamlit, pandas, selenium, beautifulsoup4, undetected-chromedriver, webdriver-manager).
- **test.py:** ✅ Root-level `test.py`; README command `python test.py [zip] "item1,item2"` saves to `data/temp_results.csv`.
- **parallel.py / temp:** Debug and legacy scripts moved to `old/` (parallel.py, run_publix_debug.py, run_walmart_only.py, legacy test.py, temp CSVs). `temp/` folder removed.
- **Category in UI:** ✅ App now passes a combined `category_map` (DEFAULT_CATEGORY_MAP + DAILY_BASKET_CATEGORY_MAP) to `run_scrapers_parallel`, so user-entered items get a category instead of "Other" when they match (e.g. Eggs, Milk, Bread, Chicken Breast).
- **Phase 4.1 (matching):** Done: `scrapers/match.py` with normalize, synonyms (count/ct, oz, lb, gal, 2%/reduced fat, etc.), singular/plural, and `match_score()`; all three scrapers use `product_matches_query()`. Extensive tests in `tests/test_units.py` and `tests/test_match.py`.
- **Phase 4.2 (robustness):** ✅ Done: scrapers set `scraper_error` (e.g. when price is N/A or title Unknown); enrichment sets `name_match_uncertain` from `match_score` &lt; 0.5 and preserves `scraper_error`; UI shows Quality column (⚠️) in Cheapest Basket and All Prices when any flag is True.

---

## 2. Deltas: what still needs to be implemented

Based on **Proposal.md**, **IMPLEMENTATION_PLAN.md**, **next_steps.md**, **README.md**, and **DAILY_RUN.md**.

### 2.1 From Proposal.md (vision vs current)

| Proposal item | Current state | Delta |
|---------------|---------------|--------|
| Location-based prices (zip/address) for Aldi, Publix, Walmart | Publix and Walmart use zip; Aldi does not use zip (national search). | Document or add Aldi location if desired; address (vs zip) not implemented. |
| “Best Shopping Plan” (most cost-effective retailer or set) | ✅ UI shows “Best Shopping Plan”: best single store (name + total), cheapest basket total, and savings from mixing stores. | Fuel/time (e.g. Routes API) not implemented. |
| SQLite database for validated data | Data written to CSV only (`daily_basket.csv`, temp CSVs). | Persist to SQLite as in proposal if needed for analysis/UI. |
| Scheduled daily query of standard item set | Implemented via `run_daily_basket.py` + Task Scheduler (DAILY_RUN.md). | ✅ Done. |
| Statistical analysis (RCBD, ANOVA, etc.) | Not in repo. | Analysis and final report/presentation are out of scope of current codebase. |
| Google Routes API (driving time, fuel) | Not implemented. | Optional extension. |

### 2.2 From IMPLEMENTATION_PLAN.md and next_steps.md

| Plan / next step | Status | Remaining work |
|------------------|--------|----------------|
| Unit standardization (Phase 1.1) | ✅ Done | — |
| Data enrichment (Phase 1.2) | ✅ Done | — |
| Cost per unit in UI (Phase 1.3) | ✅ Done | — |
| Top 5 + keyword filter (Phase 2.1) | ✅ Done | — |
| DAILY_BASKET, category map, run_daily_basket, Task Scheduler doc (Phase 2.2) | ✅ Done | — |
| How it works page (Phase 3.1) | ✅ Done | — |
| Spinner + grocery facts (Phase 3.2) | ✅ Done | — |
| README local setup + daily run (Phase 3.3) | ✅ Done | — |
| **Phase 4.1 – Robust product name matching** | ✅ Done | Synonyms (e.g. “2% milk” ↔ “reduced fat”), ignore punctuation, “12 count” vs “12 ct”; optional scoring; consider `scrapers/match.py`. |
| **Phase 4.2 – Scraper/data quality flags** | ✅ Done | Scrapers set `scraper_error`; enrichment sets `name_match_uncertain` from match_score; Quality column (⚠️) in UI. |
| Optional unit tests for standardize_unit | ✅ Done | Covered in `tests/test_units.py` and `tests/test_match.py`. |

### 2.3 From README.md and DAILY_RUN.md

| Doc | Issue | Action |
|-----|--------|--------|
| README | `python test.py [zip] "item1,item2"` | ✅ Done: root `test.py` added; saves to `data/temp_results.csv`. |
| README | Dependencies | ✅ Done: `requirements.txt` populated. |
| DAILY_RUN.md | — | Matches current behavior (run_daily_basket.py, append, Task Scheduler). No code deltas. |

### 2.4 Summary checklist: what to implement next

1. ~~**requirements.txt**~~ – Done.
2. ~~**test.py / README**~~ – Done (root `test.py` in place).
3. ~~**Phase 4.1**~~ – Done: `scrapers/match.py` (normalize, synonyms, singular/plural, scoring); scrapers use it; extensive tests in `tests/test_units.py` and `tests/test_match.py`.
4. ~~**Phase 4.2**~~ – Done: scraper_error in scrapers, name_match_uncertain in enrichment, Quality column in UI.
5. ~~**Category in UI**~~ – Done: app passes combined category_map.
6. ~~**Best Shopping Plan**~~ – Done: best single store + cheapest basket (mix) + savings in app.
7. ~~**Optional**~~ – Unit tests (in `tests/test_units.py`).
8. **Optional (Proposal)** – SQLite persistence; “Best Shopping Plan” (single store or multi-store); address support; Google Routes API; statistical analysis pipeline.

---

## 3. Quality warnings (data/sample.csv): issues and solutions

Investigation of **data/sample.csv** showed ⚠️ in the Quality column whenever **unit_uncertain** was True (i.e. `standardize_unit(unit_size)` returned `None`), so price-per-unit could not be computed and the row was flagged.

### 3.1 Issues identified

| Example row | unit_size value | Cause of ⚠️ |
|-------------|-----------------|-------------|
| Bread (Walmart Great Value White Sandwich Bread) | `Bag` | No handler for "bag"; no number. |
| Bread (Walmart Dave's Killer Bread) | *(empty)* | Empty unit string → always `None`. |
| Butter (Walmart Country Crock … 4 Sticks) | `4 Sticks (Refrigerated)` | Parenthetical and "sticks" not parsed. |
| Butter (Walmart Land O Lakes … 4 Sticks) | `4 Sticks` | "stick"/"sticks" not recognized. |
| Eggs (Walmart Pete & Gerry's Organic … 12 Ct) | *(empty)* | Scraper did not extract unit; empty → `None`. |
| Milk (Walmart Feastables … Single Bottle) | `Single Bottle` | "bottle" and "single" (→ 1) not recognized. |

So the root cause was **unhandled unit patterns** in `scrapers/units.py`: stick(s), bottle(s), bag, and parenthetical text (e.g. "(Refrigerated)").

### 3.2 Solutions implemented

1. **Strip parenthetical content** before parsing (e.g. `4 Sticks (Refrigerated)` → `4 Sticks`) so the main unit phrase can be matched.
2. **Stick / sticks** – Treat as count (e.g. `4 Sticks` → `{qty: 4, unit: "count"}`).
3. **Bottle / bottles** – Treat as count; interpret "Single Bottle" as 1 count when no number is present.
4. **Bag** – Treat as count (e.g. `Bag` → 1 count); if a number is present (e.g. `2 bag`), use it.
5. **Order of checks** – Run the **oz / count** block (number + "oz" or "ct"/"count") *before* stick/bottle/bag so strings like `20 oz bag` parse as 20 oz, not 20 count.
6. **Empty unit_size** – Left as `None` (no change); rows with missing unit from the scraper still correctly show ⚠️.

**Files changed:** `scrapers/units.py` (parsing logic and order); `tests/test_units.py` (tests for stick, bottle, bag, and parentheticals).

### 3.3 Unit fallback from product name

When **unit_size** is empty (e.g. Walmart’s “Pete & Gerry's Organic Eggs Large 12 Ct” has no comma, so the scraper leaves unit blank), enrichment now tries **`_extract_unit_phrase_from_text(product_name)`**: it looks for a pattern like `12 Ct`, `16 oz`, `1 gal` in the title and runs `standardize_unit()` on it. That row then gets a valid normalized_qty/unit_type and no longer flags ⚠️ for unit_uncertain.

**File:** `lib/enrich.py` (`_extract_unit_phrase_from_text`, used in `enrich_results` when `unit_size` is empty).

### 3.4 Remaining ⚠️ after fixes

- Rows where **unit_size is empty** and the **product name contains no recognizable unit phrase** will still show ⚠️.
- Rows where **scraper_error** or **name_match_uncertain** is True are unchanged; those flags are set by scrapers and enrichment as designed.

---

*End of current status and deltas.*
