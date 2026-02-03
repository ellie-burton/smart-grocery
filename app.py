import random
import streamlit as st
import pandas as pd
import main  # Imports your existing main.py logic

st.set_page_config(page_title="Smart Grocery 🛒", page_icon="🛒", layout="wide")

# Fun facts to show while waiting (or in sidebar)
GROCERY_FACTS = [
    "The average American household spends about $270–$350 per person per month on groceries.",
    "Unit pricing (price per oz or per lb) is required in many states so you can compare sizes.",
    "Store brands often cost 25–30% less than national brands with similar quality.",
    "Bananas are one of the most purchased grocery items in the U.S.",
    "Shopping with a list tends to reduce impulse buys and lower the total bill.",
    "Peak grocery spending in the U.S. often happens on weekends.",
]

# --- UI HEADER ---
st.title("🛒 Smart Grocery Price Finder")
st.markdown("Enter your list and location to find the best deals at **Aldi**, **Publix** and **Walmart**.")

# --- SIDEBAR INPUTS ---
with st.sidebar:
    st.header("Settings")
    location = st.text_input("Zip Code or Address", value="35401")
    
    st.subheader("Your Grocery List")
    default_items = "Eggs\nMilk\nBread\nButter\nChicken Breast"
    items_input = st.text_area("Enter items (one per line)", value=default_items, height=200)
    
    search_btn = st.button("🔍 Find Prices", type="primary")
    
    st.divider()
    st.caption("Did you know?")
    st.info(random.choice(GROCERY_FACTS))

# --- MAIN APP LOGIC ---
if search_btn:
    if not location or not items_input:
        st.error("Please enter both a location and a grocery list.")
    else:
        # 1. Prepare List
        grocery_list = [item.strip() for item in items_input.split('\n') if item.strip()]
        
        st.info(f"🚀 Starting scraper for **{len(grocery_list)} items** in **{location}**...")
        
        try:
            # 2. Run Scrapers (spinner shows while browsers run)
            with st.spinner("Finding prices at Aldi, Publix, and Walmart… This may take a minute."):
                results = main.run_scrapers_parallel(location, grocery_list)
            
            # 3. Analyze Results
            if not results:
                st.warning("No results found at all. Check the terminal for errors.")
            else:
                df = pd.DataFrame(results)
                # Use enriched clean_price for sorting and totals
                df["price_val"] = df["clean_price"].fillna(999.0)

                # Format price per unit for display (e.g. $0.03/oz)
                def fmt_price_per_unit(row):
                    ppu = row.get("price_per_unit")
                    ut = row.get("unit_type") or ""
                    if ppu is not None and ut:
                        return f"${ppu:.4f}/{ut}"
                    return "—"

                df["price_per_unit_fmt"] = df.apply(fmt_price_per_unit, axis=1)

                # --- MISSING ITEMS CHECK ---
                found_terms = df["search_term"].unique()
                missing_items = [item for item in grocery_list if item not in found_terms]

                if missing_items:
                    st.warning(f"⚠️ **Could not find prices for {len(missing_items)} items:** {', '.join(missing_items)}")
                    st.caption("Try renaming them (e.g., instead of 'Coke', try 'Coca-Cola').")

                # --- DISPLAY TABS ---
                tab1, tab2 = st.tabs(["🏆 Cheapest Basket", "📊 All Prices"])

                df = df.sort_values(by=["search_term", "price_val"])
                display_cols = [
                    "search_term",
                    "product_name",
                    "price",
                    "store",
                    "unit_size",
                    "price_per_unit_fmt",
                    "category",
                    "brand_type",
                ]

                with tab1:
                    st.subheader("Your Best Deal List")
                    cheapest_idx = df.groupby("search_term")["price_val"].idxmin()
                    cheapest_df = df.loc[cheapest_idx].copy()

                    st.dataframe(
                        cheapest_df[display_cols],
                        column_config={
                            "price": st.column_config.TextColumn("Price"),
                            "store": st.column_config.TextColumn("Best Store"),
                            "price_per_unit_fmt": st.column_config.TextColumn("Price/unit"),
                            "category": st.column_config.TextColumn("Category"),
                            "brand_type": st.column_config.TextColumn("Brand"),
                        },
                        hide_index=True,
                        use_container_width=True,
                    )

                    total = cheapest_df["price_val"].sum()
                    found_count = len(cheapest_df)
                    col1, col2 = st.columns(2)
                    col1.metric("Estimated Total", f"${total:.2f}")
                    col2.metric("Items Found", f"{found_count}/{len(grocery_list)}")

                with tab2:
                    st.subheader("Comparison of All Options")
                    st.dataframe(
                        df[display_cols],
                        column_config={
                            "price_per_unit_fmt": st.column_config.TextColumn("Price/unit"),
                        },
                        hide_index=True,
                        use_container_width=True,
                    )

        except Exception as e:
            st.error(f"An error occurred: {e}")