import streamlit as st
import pandas as pd
import main  # Imports your existing main.py logic

st.set_page_config(page_title="Smart Grocery 🛒", page_icon="🛒", layout="wide")

# --- UI HEADER ---
st.title("🛒 Smart Grocery Price Finder")
st.markdown("Enter your list and location to find the best deals at **Publix** and **Walmart**.")

# --- SIDEBAR INPUTS ---
with st.sidebar:
    st.header("Settings")
    location = st.text_input("Zip Code or Address", value="35401")
    
    st.subheader("Your Grocery List")
    default_items = "Eggs\nMilk\nBread\nButter\nChicken Breast"
    items_input = st.text_area("Enter items (one per line)", value=default_items, height=200)
    
    search_btn = st.button("🔍 Find Prices", type="primary")

# --- MAIN APP LOGIC ---
if search_btn:
    if not location or not items_input:
        st.error("Please enter both a location and a grocery list.")
    else:
        # 1. Prepare List
        grocery_list = [item.strip() for item in items_input.split('\n') if item.strip()]
        
        st.info(f"🚀 Starting scraper for **{len(grocery_list)} items** in **{location}**...")
        
        status_text = st.empty()
        status_text.text("Spinning up browsers...")
        
        try:
            # 2. Run Scrapers
            results = main.run_scrapers_parallel(location, grocery_list)
            status_text.empty()
            
            # 3. Analyze Results
            if not results:
                st.warning("No results found at all. Check the terminal for errors.")
            else:
                df = pd.DataFrame(results)
                
                # Clean Price Column
                def clean_price(p):
                    try:
                        return float(str(p).replace('$', '').replace('current price', '').strip())
                    except:
                        return 999.0
                
                df['price_val'] = df['price'].apply(clean_price)
                
                # --- MISSING ITEMS CHECK ---
                found_terms = df['search_term'].unique()
                missing_items = [item for item in grocery_list if item not in found_terms]
                
                if missing_items:
                    st.warning(f"⚠️ **Could not find prices for {len(missing_items)} items:** {', '.join(missing_items)}")
                    st.caption("Try renaming them (e.g., instead of 'Coke', try 'Coca-Cola').")

                # --- DISPLAY TABS ---
                tab1, tab2 = st.tabs(["🏆 Cheapest Basket", "📊 All Prices"])
                
                # Sort dataframe
                df = df.sort_values(by=['search_term', 'price_val'])
                display_cols = ['search_term', 'product_name', 'price', 'store', 'unit_size']

                with tab1:
                    st.subheader("Your Best Deal List")
                    
                    # Group by search term and pick the row with the minimum price
                    cheapest_idx = df.groupby('search_term')['price_val'].idxmin()
                    cheapest_df = df.loc[cheapest_idx].copy()
                    
                    # Show table
                    st.dataframe(
                        cheapest_df[display_cols],
                        column_config={
                            "price": st.column_config.TextColumn("Price"),
                            "store": st.column_config.TextColumn("Best Store"),
                        },
                        hide_index=True,
                        use_container_width=True
                    )
                    
                    # Calculate Total
                    total = cheapest_df['price_val'].sum()
                    found_count = len(cheapest_df)
                    
                    col1, col2 = st.columns(2)
                    col1.metric("Estimated Total", f"${total:.2f}")
                    col2.metric("Items Found", f"{found_count}/{len(grocery_list)}")

                with tab2:
                    st.subheader("Comparison of All Options")
                    st.dataframe(
                        df[display_cols],
                        hide_index=True,
                        use_container_width=True
                    )

        except Exception as e:
            st.error(f"An error occurred: {e}")