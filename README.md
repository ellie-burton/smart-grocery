# Smart Grocery

Compare grocery prices across **Aldi**, **Publix**, and **Walmart** by entering a list and location. Uses a Streamlit UI and optional daily-basket script for longitudinal tracking.

## Requirements

- **Python 3.9+**
- **Chrome** (used by the scrapers; the app matches your installed Chrome version for the driver)
- Optional: a virtual environment (e.g. `.venv` or conda)

## Local setup

1. Clone the repo and open a terminal in the project root.
2. (Recommended) Create and activate a venv:
   - Windows: `python -m venv .venv` then `.venv\Scripts\activate`
   - macOS/Linux: `python3 -m venv .venv` then `source .venv/bin/activate`
3. Install dependencies:
   ```bash
   pip install -r requirements.txt
   ```
4. Run the app:
   ```bash
   streamlit run app.py
   ```
   Then open the URL shown (usually http://localhost:8501).

## What you can run

| Command | What it does |
|---------|--------------|
| `streamlit run app.py` | Start the web UI (enter list + zip, get prices). |
| `python test.py [zip] "item1,item2"` | Run all three scrapers from the CLI; saves to `data/temp_results.csv`. |
| `python run_daily_basket.py [zip]` | Run the fixed 12-item daily basket; appends to `data/daily_basket.csv`. |
| `python main.py` | Run scrapers with default zip and list (no CSV). |

Optional: set **SMART_GROCERY_ZIP** in the environment to use a default zip for the daily basket.

## Tests

Unit tests cover **unit standardization** (`scrapers/units.py`) and **product name matching** (`scrapers/match.py`). From the project root:

```bash
pip install -r requirements.txt
python -m pytest tests/ -v
```

**Tip:** If you use conda, run these commands in Command Prompt (or your terminal) with the `base` env active so `python` and `pip` are on your PATH.

## Daily basket (longitudinal data)

A fixed 12-item list (milk, eggs, butter, bananas, chicken breast, etc.) can be run on a **schedule** to answer "Is Tuesday cheaper?" or compare stores over time.

- Run once: `python run_daily_basket.py [zip]`
- Results append to `data/daily_basket.csv`
- To run **daily automatically**, see **[DAILY_RUN.md](DAILY_RUN.md)** for Windows Task Scheduler setup.
