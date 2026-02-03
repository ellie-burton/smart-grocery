# config.py
"""
Fixed "Daily Basket" for longitudinal price tracking.
Run the same 12 items daily to answer questions like "Is Tuesday cheaper?"
"""

# 12 commodity items; every store carries them for reliable comparison.
DAILY_BASKET = [
    # Dairy
    "Whole Milk",
    "Large Eggs (12 count)",
    "Salted Butter",
    # Produce
    "Bananas",
    "Gala Apples",
    "Iceberg Lettuce",
    # Meat
    "Ground Beef 80/20",
    "Chicken Breast",
    # Pantry
    "White Bread",
    "Spaghetti Pasta",
    "Tomato Sauce",
    # Household
    "Dish Soap",
]

# Category for each basket item (used by enrichment when running the daily basket).
DAILY_BASKET_CATEGORY_MAP = {
    "whole milk": "Dairy",
    "large eggs (12 count)": "Dairy",
    "salted butter": "Dairy",
    "bananas": "Produce",
    "gala apples": "Produce",
    "iceberg lettuce": "Produce",
    "ground beef 80/20": "Meat",
    "chicken breast": "Meat",
    "white bread": "Pantry",
    "spaghetti pasta": "Pantry",
    "tomato sauce": "Pantry",
    "dish soap": "Household",
}
