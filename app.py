import random
from datetime import datetime, timedelta
import streamlit as st
import pandas as pd
import main
import config
from lib.enrich import DEFAULT_CATEGORY_MAP

st.set_page_config(
    page_title="Smart Grocer",
    page_icon="🛒",
    layout="wide",
    initial_sidebar_state="expanded",
)

# Teal/light blue theme + clean styling
st.markdown("""
<style>
    @import url('https://fonts.googleapis.com/css2?family=DM+Sans:wght@400;500;600;700&display=swap');
    .stApp, [data-testid="stSidebar"] { font-family: 'DM Sans', sans-serif; }
    .block-container { padding: 2rem 2.5rem; max-width: 1400px; }
    h1 { font-size: 1.6rem !important; font-weight: 700 !important; color: #134e4a !important; }
    .savings-hero { font-size: 2rem !important; font-weight: 700 !important; color: #0d9488 !important; }
    .stButton > button[kind="primary"] { 
        background: linear-gradient(135deg, #0d9488 0%, #0f766e 100%) !important; 
        font-weight: 600 !important; border-radius: 10px !important; border: none !important;
        box-shadow: 0 2px 8px rgba(13,148,136,0.25) !important;
    }
    div[data-testid="stDataFrame"] { border-radius: 10px; overflow: hidden; box-shadow: 0 1px 4px rgba(0,0,0,0.06); }
    /* Dashboard cards: white containers */
    .dashboard-card { background: white; border-radius: 12px; padding: 1.25rem; margin-bottom: 1rem; box-shadow: 0 2px 8px rgba(0,0,0,0.06); border: 1px solid #e5e7eb; }
    /* Store comparison cards only (nested columns) */
    [data-testid="column"] [data-testid="column"] > div { background: white; border-radius: 12px; padding: 1.25rem; box-shadow: 0 2px 8px rgba(0,0,0,0.06); border: 1px solid #e5e7eb; margin: 0 0.5rem 1rem 0; }
    /* Rotating cart loading spinner */
    .loading-cart { text-align: center; padding: 2rem 1rem; }
    .cart-spinner { font-size: 3rem; display: inline-block; animation: cart-spin 2s linear infinite; }
    @keyframes cart-spin { from { transform: rotate(0deg); } to { transform: rotate(360deg); } }
    .grocery-fact-tip { margin-top: 1rem; padding: 0.75rem 1rem; background: rgba(255,255,255,0.7); border-radius: 8px; font-size: 0.9rem; color: #374151; }
    /* Sidebar: light teal, high-contrast text */
    [data-testid="stSidebar"] { background: #e0f2f1 !important; }
    [data-testid="stSidebar"] .stMarkdown { color: #134e4a !important; }
    [data-testid="stSidebar"] .stCaptionContainer { color: #115e59 !important; }
    [data-testid="stSidebar"] p { color: #115e59 !important; }
</style>
""", unsafe_allow_html=True)

GROCERY_FACTS = [
    "The average American household spends about $270–$350 per person per month on groceries.",
    "Unit pricing (price per oz or per lb) is required in many states so you can compare sizes.",
    "Store brands often cost 25–30% less than national brands with similar quality.",
    "Bananas are one of the most purchased grocery items in the U.S.",
    "Shopping with a list tends to reduce impulse buys and lower the total bill.",
]

# --- SIDEBAR: Branding + inputs + How it works ---
default_items = "Eggs\nMilk\nBread\nButter\nChicken Breast"
with st.sidebar:
    st.markdown("## Smart Grocer")
    st.caption("Your local price comparison tool")
    st.page_link("pages/2_How_it_works.py", label="How it works", icon="📄")
    st.markdown("---")
    st.markdown("### 1. Your Shopping Details")
    location = st.text_input(
        "Zip Code or Address",
        value="35401",
        placeholder="e.g., 35401 or Your Address",
        help="Used for local store prices.",
    )
    items_input = st.text_area(
        "Grocery List (one per line)",
        value=default_items,
        height=140,
        placeholder="e.g., Milk, Eggs, Bread, Apples, Chicken Breast...",
    )
    search_btn = st.button("🛒 FIND BEST PRICES", type="primary", use_container_width=True)
    with st.expander("Include Estimated Driving Costs? (Optional)", expanded=False):
        st.caption("Coming soon: Factor in drive time and fuel when comparing multi-store plans.")

# --- MAIN: Header ---
st.title("Smart Grocer – Your Local Price Comparison Tool")
st.markdown("")

# --- MAIN: Results (full width) ---
@st.fragment(run_every=timedelta(seconds=5))
def grocery_fact_section():
    st.caption("💡 " + random.choice(GROCERY_FACTS))

st.markdown("### 2. Best Shopping Plan & Savings")
content_placeholder = st.empty()

if not search_btn:
    with content_placeholder.container():
        st.info("Enter your list and location, then click **FIND BEST PRICES** to see your personalized plan.")
        st.caption("You’ll get total savings, best single-store vs multi-store options, a price comparison chart, and an item-by-item breakdown.")
        grocery_fact_section()
else:
    if not location or not items_input:
        with content_placeholder.container():
            st.error("Please enter both a location and a grocery list.")
            grocery_fact_section()
    else:
        grocery_list = [item.strip() for item in items_input.split('\n') if item.strip()]
        category_map = {**DEFAULT_CATEGORY_MAP, **config.DAILY_BASKET_CATEGORY_MAP}
        try:
            # Loading: only rotating cart + status + refreshing fact (replaces previous content)
            with content_placeholder.container():
                st.markdown(f'''
                <div class="loading-cart">
                    <div class="cart-spinner">🛒</div>
                    <p style="margin-top: 0.75rem; color: #374151;">Searching <strong>{len(grocery_list)} items</strong> in <strong>{location}</strong>…</p>
                </div>
                ''', unsafe_allow_html=True)
                grocery_fact_section()
            with st.spinner(""):
                results = main.run_scrapers_parallel(location, grocery_list, category_map=category_map)
            with content_placeholder.container():
                if not results:
                    st.warning("No results found. Check your zip code and item names, then try again.")
                    grocery_fact_section()
                else:
                    df = pd.DataFrame(results)
                    df["price_val"] = df["clean_price"].fillna(999.0)
                    found_terms = df["search_term"].unique()
                    missing_items = [i for i in grocery_list if i not in found_terms]
                    if missing_items:
                        st.warning(f"Could not find prices for: **{', '.join(missing_items)}**. Try different names (e.g., 'Coca-Cola' instead of 'Coke').")

                    # Compute plan metrics
                    optimal_total = df.groupby("search_term")["price_val"].min().sum()
                    single_store_totals = {}
                    for store in df["store"].unique():
                        sub = df[df["store"] == store]
                        by_term = sub.groupby("search_term")["price_val"].min()
                        if set(by_term.index) >= set(found_terms):
                            single_store_totals[store] = by_term.sum()
                    best_single_store = min(single_store_totals, key=single_store_totals.get) if single_store_totals else None
                    best_single_total = single_store_totals.get(best_single_store, 0)
                    savings = max(0, best_single_total - optimal_total) if best_single_store else 0

                    # Results header
                    st.caption(f"Results for **{location}** – {datetime.now().strftime('%B %d, %Y')}")

                    # Total Estimated Savings (hero) – white card
                    st.markdown(f'''
                    <div class="dashboard-card">
                        <p style="margin: 0 0 0.25rem 0; font-size: 0.875rem; color: #4b5563;"><strong>TOTAL ESTIMATED SAVINGS</strong></p>
                        <p class="savings-hero" style="margin: 0 0 0.25rem 0;">${savings:.2f}</p>
                        <p style="margin: 0; font-size: 0.8rem; color: #9ca3af;">vs. buying everything at the best single store</p>
                    </div>
                    ''', unsafe_allow_html=True)

                    # Two store cards – white containers
                    card1, card2 = st.columns(2)
                    with card1:
                        st.markdown("**Best Single Store Option**")
                        st.markdown(f"**{best_single_store}**" if best_single_store else "—")
                        st.metric("Total cost", f"${best_single_total:.2f}", "")
                    with card2:
                        st.markdown("**Optimal Multi-Store Plan**")
                        st.metric("Total cost", f"${optimal_total:.2f}", f"Saves ${savings:.2f}" if savings > 0 else "Same as single store")
                        if savings > 0:
                            st.caption("Pick best price per item across stores.")
                    st.markdown("")

                    # Bar chart
                    st.markdown("**Price Comparison Chart**")
                    if single_store_totals:
                        chart_data = pd.DataFrame({
                            "Store": list(single_store_totals.keys()),
                            "Total cost": list(single_store_totals.values()),
                        }).sort_values("Total cost")
                        st.bar_chart(chart_data.set_index("Store"), use_container_width=True)
                    else:
                        st.caption("No single store had all items. See breakdown below.")
                    st.markdown("")

                    # Item-by-item pivot table with total cost / cost per unit toggle
                    st.markdown("**Item-by-Item Price Breakdown**")
                    view_mode = st.radio(
                        "View by",
                        options=["Total cost", "Cost per unit"],
                        index=0,
                        horizontal=True,
                        label_visibility="collapsed",
                    )
                    if view_mode == "Total cost":
                        pivot = df.groupby(["search_term", "store"])["price_val"].min().unstack(fill_value=0)
                        best_idx = df.groupby("search_term")["price_val"].idxmin()
                        best_source = best_idx.map(lambda i: df.loc[i, "store"])
                        pivot["Best source"] = best_source
                        pivot_display = pivot[["Aldi", "Publix", "Walmart", "Best source"]].copy()
                        for col in ["Aldi", "Publix", "Walmart"]:
                            pivot_display[col] = pivot_display[col].apply(lambda x: f"${x:.2f}" if x > 0 and x < 999 else "—")
                    else:
                        # Cost per unit: best price_per_unit per (search_term, store)
                        df_ppu = df.copy()
                        df_ppu["ppu_val"] = df_ppu["price_per_unit"].fillna(999.0) if "price_per_unit" in df.columns else 999.0
                        idx_best = df_ppu.groupby(["search_term", "store"])["ppu_val"].idxmin()
                        best_rows = df_ppu.loc[idx_best]
                        best_overall_idx = df_ppu.groupby("search_term")["ppu_val"].idxmin()
                        best_overall = df_ppu.loc[best_overall_idx]
                        pivot_display = best_rows.pivot(index="search_term", columns="store", values="ppu_val")
                        for col in ["Aldi", "Publix", "Walmart"]:
                            if col not in pivot_display.columns:
                                pivot_display[col] = 999.0
                        pivot_display = pivot_display.reindex(columns=["Aldi", "Publix", "Walmart"])
                        pivot_display["Best source"] = best_overall.set_index("search_term")["store"]
                        best_rows_idx = best_rows.set_index(["search_term", "store"]) if "unit_type" in best_rows.columns else None
                        def fmt_ppu(val, ut):
                            if val is None or val >= 999 or val <= 0:
                                return "—"
                            return f"${val:.4f}/{ut}" if ut else f"${val:.4f}"
                        for col in ["Aldi", "Publix", "Walmart"]:
                            for term in pivot_display.index:
                                val = pivot_display.loc[term, col]
                                ut = None
                                if best_rows_idx is not None and (term, col) in best_rows_idx.index:
                                    try:
                                        ut = best_rows_idx.loc[(term, col), "unit_type"]
                                    except (KeyError, TypeError):
                                        pass
                                pivot_display.loc[term, col] = fmt_ppu(val, ut)
                    st.dataframe(
                        pivot_display.reset_index().rename(columns={"search_term": "Item"}),
                        column_config={
                            "Item": st.column_config.TextColumn("Item", width="medium"),
                            "Aldi": st.column_config.TextColumn("Aldi", width="small"),
                            "Publix": st.column_config.TextColumn("Publix", width="small"),
                            "Walmart": st.column_config.TextColumn("Walmart", width="small"),
                            "Best source": st.column_config.TextColumn("Best", width="small"),
                        },
                        hide_index=True,
                        use_container_width=True,
                    )

                    # All results table: full raw data (all rows, all columns per retailer)
                    st.markdown("**All Results**")
                    all_results = df.copy()
                    if "price_per_unit" in df.columns:
                        def _fmt_ppu(r):
                            ppu, ut = r.get("price_per_unit"), r.get("unit_type")
                            if pd.notna(ppu) and ppu < 999 and ut:
                                return f"${ppu:.4f}/{ut}"
                            return "—"
                        all_results["price_per_unit_fmt"] = all_results.apply(_fmt_ppu, axis=1)
                    else:
                        all_results["price_per_unit_fmt"] = pd.Series(["—"] * len(df), index=df.index)
                    all_results["quality"] = all_results.apply(
                        lambda r: "⚠️" if (r.get("scraper_error") or r.get("name_match_uncertain")) else "—",
                        axis=1,
                    )
                    cols_display = ["search_term", "product_name", "price", "store", "unit_size", "price_per_unit_fmt", "quality", "category", "brand_type"]
                    all_cols = [c for c in cols_display if c in all_results.columns]
                    sort_by = ["search_term", "store"] + (["clean_price"] if "clean_price" in df.columns else [])
                    all_results = all_results.sort_values(sort_by)[all_cols]
                    st.dataframe(
                        all_results,
                        column_config={
                            "search_term": st.column_config.TextColumn("Search term", width="small"),
                            "product_name": st.column_config.TextColumn("Product", width="large"),
                            "price": st.column_config.TextColumn("Price", width="small"),
                            "store": st.column_config.TextColumn("Store", width="small"),
                            "unit_size": st.column_config.TextColumn("Size", width="small"),
                            "price_per_unit_fmt": st.column_config.TextColumn("Per unit", width="small"),
                            "quality": st.column_config.TextColumn("Quality", width="small"),
                            "category": st.column_config.TextColumn("Category", width="small"),
                            "brand_type": st.column_config.TextColumn("Brand", width="small"),
                        },
                        hide_index=True,
                        use_container_width=True,
                    )

                    grocery_fact_section()

        except Exception as e:
            with content_placeholder.container():
                st.error(f"Something went wrong: {e}")
                grocery_fact_section()
