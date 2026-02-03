# Daily Basket – Scheduled Run

This project can run the **fixed 12-item daily basket** on a schedule (e.g. every morning) to build longitudinal price data. Use Windows Task Scheduler to run `run_daily_basket.py` automatically.

## Prerequisites

- Python and project dependencies installed (`pip install -r requirements.txt`).
- Chrome installed (used by the scrapers).
- Optional: set default zip in environment variable `SMART_GROCERY_ZIP`, or pass zip as an argument (see below).

## Run manually

From the project root:

```bash
python run_daily_basket.py
```

With a specific zip:

```bash
python run_daily_basket.py 35401
```

Results are **appended** to `data/daily_basket.csv`. Each run adds one day’s rows (enriched with clean_price, normalized_qty, category, etc.).

## Windows Task Scheduler

1. **Open Task Scheduler**  
   - Press `Win + R`, type `taskschd.msc`, Enter.

2. **Create a new task**  
   - Action → Create Task (not “Create Basic Task” so you can set the working directory).

3. **General tab**  
   - Name: e.g. `Smart Grocery Daily Basket`  
   - Optionally: “Run whether user is logged on or not” (requires password).  
   - “Run with highest privileges” is not required.

4. **Triggers tab**  
   - New → set “Daily” at the time you want (e.g. 7:00 AM).  
   - Repeat as needed.

5. **Actions tab**  
   - New → Action: “Start a program”.  
   - **Program/script:** full path to Python, e.g.  
     `C:\Users\YourName\AppData\Local\Programs\Python\Python312\python.exe`  
     (Find yours with `where python` or `where py` in a terminal.)  
   - **Add arguments:**  
     `run_daily_basket.py`  
   - **Start in:** project root, e.g.  
     `C:\Users\ekate\Documents\GitHub\smart-grocery`

6. **Conditions / Settings**  
   - Uncheck “Start the task only if the computer is on AC power” if you want it to run on battery.  
   - Optionally allow the task to run on demand (right‑click → Run).

## Zip code

- Default zip is `35401` if you don’t set anything.
- To fix the zip for the scheduled task:  
  - In the task’s **Actions** tab, set **Add arguments** to:  
    `run_daily_basket.py 35401`  
  - Or set the environment variable `SMART_GROCERY_ZIP=35401` in the task (Task → Properties → General → “Run with highest privileges” area has no env UI; instead you can create a small wrapper script that sets the env and calls `run_daily_basket.py`, or pass the zip in arguments as above).

## Output

- File: `data/daily_basket.csv`
- Rows are appended; columns include: search_term, product_name, unit_size, price, store, date, clean_price, normalized_qty, unit_type, price_per_unit, brand_type, category, etc.
- Use this file for analyses like “Is Tuesday cheaper?” or “Publix vs Walmart by category over time.”
