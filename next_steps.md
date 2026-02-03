Based on the preliminary data you uploaded, here is the official Data Collection Procedure for your Smart Grocer project.

1. Search Depth: Keep the "Top 5"
Verdict: Yes, keep collecting the top 5 results.

Why? Your data shows that search algorithms are imperfect.

Example: Searching for "Milk" at Aldi returned "Choceur Milk Mini Chocolate Bars" (irrelevant) and "Friendly Farms 2% Milk" (relevant).

If you only kept the Top 1, you might get the chocolate bar and ruin your dataset.

Procedure: Collect Top 5 → Apply your "Keyword Matching" filter → Store the survivors. This also allows you to compare "Name Brand" vs. "Store Brand" prices, which often appear next to each other in the top results.

2. Developing "Cost Per Unit" (The Hard Part)
Your raw unit_size data is messy (1 gal, 128 fl oz, 12 ct, 1 dozen). You need a Standardization Pipeline before you save this to your database.

The Strategy: Convert everything into one of two base units: Ounces (oz) or Count (ct).

Here is the Python logic you should add to your scraper processing step:

Python
import re

def standardize_unit(raw_unit_str):
    """
    Parses messy unit strings into a standardized dictionary.
    Returns: {'qty': float, 'unit': str} or None
    """
    if not isinstance(raw_unit_str, str):
        return None
        
    s = raw_unit_str.lower().strip()
    
    # --- CONVERSION LOGIC ---
    # 1. Handle "Dozen" -> 12 count
    if 'dozen' in s:
        return {'qty': 12.0, 'unit': 'count'}
        
    # 2. Handle Gallons -> 128 oz
    if 'gal' in s:
        # Check for half gallon (0.5 gal)
        numbers = re.findall(r"[\d\.]+", s)
        if numbers:
            val = float(numbers[0])
            return {'qty': val * 128.0, 'unit': 'oz'} # 1 gal = 128 oz
        return {'qty': 128.0, 'unit': 'oz'} # Assume 1 gal if no number

    # 3. Handle Pounds -> 16 oz
    if 'lb' in s or 'pound' in s:
        numbers = re.findall(r"[\d\.]+", s)
        if numbers:
            return {'qty': float(numbers[0]) * 16.0, 'unit': 'oz'}

    # 4. Handle "Pack" (often ambiguous, usually count)
    if 'pack' in s:
        numbers = re.findall(r"[\d\.]+", s)
        if numbers:
            return {'qty': float(numbers[0]), 'unit': 'count'}

    # 5. Standard Ounces / Counts
    # Extract the number
    numbers = re.findall(r"[\d\.]+", s)
    if not numbers:
        return None
    val = float(numbers[0])
    
    if 'oz' in s:
        return {'qty': val, 'unit': 'oz'}
    if 'ct' in s or 'count' in s:
        return {'qty': val, 'unit': 'count'}
        
    return None # Could not parse
Result: You can now calculate Price_Per_Unit = Price / qty and compare a "1 gal" jug (128 oz) directly against a "64 oz" carton.

3. The "Daily Query" (Longitudinal Basket)
To answer your statistical questions ("Is Tuesday cheaper?"), you cannot change the items every day. You must track a Fixed Control Basket.

The Procedure: Create a separate list in your code called DAILY_BASKET. Set your Windows Task Scheduler to run this specific list every morning.

Recommended "Daily Basket" (12 Items covering all categories):

Dairy: "Whole Milk", "Large Eggs (12 count)", "Salted Butter"

Produce: "Bananas", "Gala Apples", "Iceberg Lettuce"

Meat: "Ground Beef 80/20", "Chicken Breast"

Pantry: "White Bread", "Spaghetti Pasta", "Tomato Sauce"

Household: "Dish Soap"

Why these? They are commodities. Every store has them, so you will always get a data point for comparison.

4. Data Enrichment (Add these columns)
Before saving to the database, derive these fields to make your analysis easier later:

New Column	Logic / Source	Why?
clean_price	Remove Current price:, $, convert to float.	Essential for math.
normalized_qty	Result of the function above (e.g., 128.0).	Comparison.
unit_type	oz or count.	Comparison.
brand_type	
Private Label vs. National.


(If Product Name starts with "Great Value", "Publix", "Friendly Farms" → "Private", else "National")

Answers: "Is the generic brand gap closing?"
category	Inherited from your input list (e.g., Milk → Dairy).	Answers: "Is Walmart cheaper for meat but Publix cheaper for produce?"


Secondary: 

Make product name matching more robust

Add flags to data for scraper errors, uncertain name matching, uncertain unit sizes, etc.

More:
Create “How it works” page on UI

Add unit size standardization

Add ReadMe for local setup

Add fun grocery facts and spinner for UI while scraping