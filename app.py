import html
import random
from datetime import datetime

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
    @import url('https://fonts.googleapis.com/css2?family=DM+Sans:ital,opsz,wght@9..40,400;9..40,500;9..40,600;9..40,700&display=swap');
    .stApp, [data-testid="stSidebar"] { font-family: 'DM Sans', system-ui, sans-serif; }
    /* Main: neutral surface so sidebar reads as a distinct panel */
    .stApp {
        background: linear-gradient(165deg, #f8fafc 0%, #ffffff 42%, #f4fbfb 100%);
    }
    [data-testid="stMain"] .block-container {
        padding: 2rem 2.5rem 3rem;
        max-width: 1400px;
    }
    [data-testid="stMain"] h1 {
        font-size: 1.45rem !important;
        font-weight: 700 !important;
        letter-spacing: -0.02em;
        color: #134e4a !important;
        margin-bottom: 0.35rem !important;
        line-height: 1.25 !important;
    }
    [data-testid="stMain"] h3 {
        font-size: 1.05rem !important;
        font-weight: 600 !important;
        color: #115e59 !important;
        margin-top: 0.15rem !important;
        margin-bottom: 0.65rem !important;
    }
    .savings-hero { font-size: 2rem !important; font-weight: 700 !important; color: #0d9488 !important; }
    .stButton > button[kind="primary"] {
        background: linear-gradient(135deg, #0d9488 0%, #0f766e 100%) !important;
        font-weight: 600 !important;
        letter-spacing: 0.03em;
        border-radius: 10px !important;
        border: none !important;
        padding: 0.55rem 1rem !important;
        box-shadow: 0 2px 10px rgba(13, 148, 136, 0.28) !important;
        transition: box-shadow 0.15s ease, filter 0.15s ease;
    }
    .stButton > button[kind="primary"]:hover {
        box-shadow: 0 4px 16px rgba(13, 148, 136, 0.38) !important;
        filter: brightness(1.03);
    }
    div[data-testid="stDataFrame"] {
        border-radius: 12px;
        overflow: hidden;
        box-shadow: 0 1px 3px rgba(0, 0, 0, 0.06), 0 4px 14px rgba(13, 148, 136, 0.06);
        border: 1px solid #e2e8f0;
    }
    .dashboard-card {
        background: #fff;
        border-radius: 14px;
        padding: 1.35rem 1.4rem;
        margin-bottom: 1rem;
        box-shadow: 0 1px 3px rgba(0, 0, 0, 0.05), 0 6px 20px rgba(13, 148, 136, 0.07);
        border: 1px solid #e2e8f0;
    }
    [data-testid="column"] [data-testid="column"] > div {
        background: #fff;
        border-radius: 14px;
        padding: 1.35rem 1.25rem;
        box-shadow: 0 1px 3px rgba(0, 0, 0, 0.05), 0 6px 20px rgba(13, 148, 136, 0.06);
        border: 1px solid #e2e8f0;
        margin: 0 0.5rem 1rem 0;
    }
    .loading-cart { text-align: center; padding: 2.25rem 1rem; }
    .loading-cart .grocery-fact-tip {
        margin: 1.25rem auto 0 auto;
        max-width: 32rem;
        text-align: left;
    }
    .cart-spinner { font-size: 3rem; display: inline-block; animation: cart-spin 2s linear infinite; }
    @keyframes cart-spin { from { transform: rotate(0deg); } to { transform: rotate(360deg); } }
    .grocery-fact-tip {
        margin-top: 1.25rem;
        padding: 0.85rem 1.1rem;
        background: linear-gradient(135deg, #f0fdfa 0%, #ecfeff 100%);
        border-radius: 10px;
        font-size: 0.875rem;
        color: #334155;
        border: 1px solid #ccfbf1;
        border-left: 3px solid #14b8a6;
        line-height: 1.45;
    }
    /* Sidebar: teal panel with clear separation from main */
    [data-testid="stSidebar"] {
        background: linear-gradient(180deg, #e8f5f4 0%, #d8f0ee 55%, #cfece9 100%) !important;
        border-right: 1px solid rgba(19, 78, 74, 0.1);
        box-shadow: 6px 0 28px rgba(13, 148, 136, 0.07);
    }
    [data-testid="stSidebar"] > div:first-child {
        padding-top: 1.1rem;
    }
    .sidebar-brand {
        padding: 0.2rem 0 1.1rem 0;
        margin-bottom: 0.65rem;
        border-bottom: 1px solid rgba(19, 78, 74, 0.1);
    }
    .sidebar-brand .sidebar-title {
        font-size: 1.45rem;
        font-weight: 700;
        color: #134e4a;
        margin: 0;
        letter-spacing: -0.02em;
        line-height: 1.2;
    }
    .sidebar-brand .sidebar-tagline {
        font-size: 0.8125rem;
        font-weight: 500;
        color: #0f766e;
        opacity: 0.88;
        margin: 0.4rem 0 0 0;
        line-height: 1.35;
    }
    [data-testid="stSidebar"] .stMarkdown { color: #134e4a !important; }
    [data-testid="stSidebar"] .stCaptionContainer { color: #115e59 !important; }
    [data-testid="stSidebar"] p { color: #115e59 !important; }
    [data-testid="stSidebar"] h3 {
        font-size: 0.95rem !important;
        font-weight: 600 !important;
        color: #134e4a !important;
        margin-top: 0.5rem !important;
        margin-bottom: 0.5rem !important;
    }
    [data-testid="stSidebar"] hr {
        margin: 0.75rem 0 1rem 0;
        border: none;
        border-top: 1px solid rgba(19, 78, 74, 0.12);
    }
    [data-testid="stSidebar"] .stTextInput input,
    [data-testid="stSidebar"] .stTextArea textarea {
        border-radius: 10px !important;
        border: 1px solid rgba(19, 78, 74, 0.14) !important;
        background: rgba(255, 255, 255, 0.92) !important;
        padding: 0.5rem 0.65rem !important;
        font-size: 0.9375rem !important;
    }
    [data-testid="stSidebar"] .stTextInput input:focus,
    [data-testid="stSidebar"] .stTextArea textarea:focus {
        border-color: #0d9488 !important;
        box-shadow: 0 0 0 3px rgba(13, 148, 136, 0.15) !important;
    }
    /* Empty-state callout (replaces default blue st.info for this screen only) */
    .plan-callout {
        padding: 1rem 1.2rem;
        border-radius: 12px;
        border: 1px solid #99f6e4;
        background: linear-gradient(135deg, #f0fdfa 0%, #ecfeff 100%);
        color: #134e4a;
        font-size: 0.95rem;
        line-height: 1.55;
        box-shadow: 0 1px 2px rgba(0, 0, 0, 0.04);
        margin-bottom: 0.35rem;
    }
    /* Slightly round system alerts without overriding semantic colors */
    [data-testid="stMain"] div[data-testid="stAlert"] { border-radius: 12px !important; }
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
    st.markdown(
        """
        <div class="sidebar-brand">
            <p class="sidebar-title">Smart Grocer</p>
            <p class="sidebar-tagline">Your local price comparison tool</p>
        </div>
        """,
        unsafe_allow_html=True,
    )
    st.page_link("pages/3_Price_Trends.py", label="Price Trends", icon="📈")
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

# --- MAIN: Header ---
st.title("Smart Grocer – Your Local Price Comparison Tool")
st.caption("Compare prices across local stores and see where you save the most.")

# --- MAIN: Results (full width) ---
st.markdown("### 2. Best Shopping Plan & Savings")
content_placeholder = st.empty()

# Persist results so radio toggle (and other widget interactions) don't lose data on rerun
if "results_df" not in st.session_state:
    st.session_state.results_df = None
    st.session_state.results_location = None
    st.session_state.results_grocery_list = None

if search_btn:
    st.session_state.results_df = None  # Clear cache for new search

if not search_btn and st.session_state.results_df is None:
    with content_placeholder.container():
        st.markdown(
            """
            <div class="plan-callout">
                Enter your list and location, then click <strong>FIND BEST PRICES</strong>
                to see your personalized plan.
            </div>
            """,
            unsafe_allow_html=True,
        )
        st.caption(
            "You’ll get total savings, best single-store vs multi-store options, "
            "a price comparison chart, and an item-by-item breakdown."
        )
elif search_btn and (not location or not items_input):
    with content_placeholder.container():
        st.error("Please enter both a location and a grocery list.")
else:
    # Either fresh search (search_btn) or cached results (radio toggle, etc.)
    if search_btn:
        grocery_list = [item.strip() for item in items_input.split('\n') if item.strip()]
        category_map = {**DEFAULT_CATEGORY_MAP, **config.DAILY_BASKET_CATEGORY_MAP}
        try:
            _tip = html.escape(random.choice(GROCERY_FACTS))
            _load_line = (
                f"Searching <strong>{len(grocery_list)} items</strong> in "
                f"<strong>{html.escape(location)}</strong>…"
            )
            with content_placeholder.container():
                st.markdown(
                    f"""
                <div class="loading-cart">
                    <div class="cart-spinner">🛒</div>
                    <p style="margin-top: 0.75rem; color: #374151;">{_load_line}</p>
                    <div class="grocery-fact-tip">💡 <strong>Tip:</strong> {_tip}</div>
                </div>
                """,
                    unsafe_allow_html=True,
                )
            with st.spinner(""):
                results = main.run_scrapers_parallel(
                    location, grocery_list, category_map=category_map
                )
            if results:
                df = pd.DataFrame(results)
                df["price_val"] = df["clean_price"].fillna(999.0)
                st.session_state.results_df = df
                st.session_state.results_location = location
                st.session_state.results_grocery_list = grocery_list
            else:
                with content_placeholder.container():
                    st.warning("No results found. Check your zip code and item names, then try again.")
        except Exception as e:
            with content_placeholder.container():
                st.error(f"Something went wrong: {e}")
    else:
        # Cached results (e.g. user toggled radio)
        df = st.session_state.results_df
        location = st.session_state.results_location
        grocery_list = st.session_state.results_grocery_list

    # Show results (from fresh search or cache)
    if st.session_state.results_df is not None:
        df = st.session_state.results_df
        location = st.session_state.results_location
        grocery_list = st.session_state.results_grocery_list
        with content_placeholder.container():
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
            _ALL_STORES = ["Aldi", "Publix", "Walmart"]
            _present_stores = [s for s in _ALL_STORES if s in df["store"].values]

            if view_mode == "Total cost":
                pivot = df.groupby(["search_term", "store"])["price_val"].min().unstack(fill_value=0)
                for col in _ALL_STORES:
                    if col not in pivot.columns:
                        pivot[col] = 0
                best_idx = df.groupby("search_term")["price_val"].idxmin()
                best_source = best_idx.map(lambda i: df.loc[i, "store"])
                pivot["Best source"] = best_source
                pivot_display = pivot[_ALL_STORES + ["Best source"]].copy()
                for col in _ALL_STORES:
                    pivot_display[col] = pivot_display[col].apply(lambda x: f"${x:.2f}" if x > 0 and x < 999 else "—")
            else:
                # Cost per unit: best price_per_unit per (search_term, store)
                try:
                    df_ppu = df.copy()
                    df_ppu["ppu_val"] = df_ppu["price_per_unit"].fillna(999.0) if "price_per_unit" in df.columns else 999.0
                    idx_best = df_ppu.groupby(["search_term", "store"])["ppu_val"].idxmin()
                    if len(idx_best) == 0:
                        raise ValueError("No price-per-unit data")
                    best_rows = df_ppu.loc[idx_best].drop_duplicates(subset=["search_term", "store"]).copy()
                    best_overall_idx = df_ppu.groupby("search_term")["ppu_val"].idxmin()
                    best_overall = df_ppu.loc[best_overall_idx]
                    pivot_display = best_rows.pivot(index="search_term", columns="store", values="ppu_val")
                    for col in _ALL_STORES:
                        if col not in pivot_display.columns:
                            pivot_display[col] = 999.0
                    pivot_display = pivot_display.reindex(columns=_ALL_STORES)
                    best_src = best_overall.set_index("search_term")["store"].reindex(pivot_display.index)
                    pivot_display["Best source"] = best_src.fillna("—")
                    best_rows_idx = best_rows.set_index(["search_term", "store"]) if "unit_type" in best_rows.columns else None

                    def fmt_ppu(val, ut):
                        if val is None or (isinstance(val, (int, float)) and (pd.isna(val) or val >= 999 or val <= 0)):
                            return "—"
                        return f"${float(val):.4f}/{ut}" if ut else f"${float(val):.4f}"

                    for col in _ALL_STORES:
                        for term in pivot_display.index:
                            val = pivot_display.loc[term, col]
                            ut = None
                            if best_rows_idx is not None and (term, col) in best_rows_idx.index:
                                try:
                                    u = best_rows_idx.loc[(term, col), "unit_type"]
                                    ut = u if (u and not pd.isna(u)) else None
                                except (KeyError, TypeError):
                                    ut = None
                            pivot_display.loc[term, col] = fmt_ppu(val, ut)
                except Exception:
                    pivot = df.groupby(["search_term", "store"])["price_val"].min().unstack(fill_value=0)
                    for col in _ALL_STORES:
                        if col not in pivot.columns:
                            pivot[col] = 0
                    best_idx = df.groupby("search_term")["price_val"].idxmin()
                    best_source = best_idx.map(lambda i: df.loc[i, "store"])
                    pivot["Best source"] = best_source
                    pivot_display = pivot[_ALL_STORES + ["Best source"]].copy()
                    for col in _ALL_STORES:
                        pivot_display[col] = pivot_display[col].apply(lambda x: f"${x:.2f}" if x > 0 and x < 999 else "—")
                    st.warning("Cost per unit view unavailable for some items; showing total cost.")
            _col_config = {"Item": st.column_config.TextColumn("Item", width="medium")}
            for s in _ALL_STORES:
                _col_config[s] = st.column_config.TextColumn(s, width="small")
            _col_config["Best source"] = st.column_config.TextColumn("Best", width="small")
            st.dataframe(
                pivot_display.reset_index().rename(columns={"search_term": "Item"}),
                column_config=_col_config,
                hide_index=True,
                width="stretch",
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
                lambda r: "⚠️" if (r.get("scraper_error") or r.get("name_match_uncertain") or r.get("unit_uncertain")) else "—",
                axis=1,
            )

            def _fmt_clean_price_val(cp):
                if cp is None or (isinstance(cp, float) and pd.isna(cp)):
                    return "—"
                try:
                    v = float(cp)
                except (TypeError, ValueError):
                    return "—"
                if v >= 999:
                    return "—"
                return f"${v:.2f}"

            if "clean_price" in all_results.columns:
                all_results["clean_price_fmt"] = all_results["clean_price"].map(_fmt_clean_price_val)
            else:
                all_results["clean_price_fmt"] = "—"

            def _fmt_clean_unit_row(r):
                nq, ut = r.get("normalized_qty"), r.get("unit_type")
                if nq is None or (isinstance(nq, float) and pd.isna(nq)) or not ut:
                    return "—"
                try:
                    fq = float(nq)
                except (TypeError, ValueError):
                    return "—"
                num = str(int(fq)) if fq == int(fq) else f"{fq:g}"
                return f"{num} {ut}"

            if "normalized_qty" in all_results.columns and "unit_type" in all_results.columns:
                all_results["unit_clean_display"] = all_results.apply(_fmt_clean_unit_row, axis=1)
            else:
                all_results["unit_clean_display"] = "—"

            cols_display = [
                "search_term",
                "product_name",
                "price",
                "clean_price_fmt",
                "store",
                "unit_size",
                "unit_clean_display",
                "price_per_unit_fmt",
                "quality",
                "category",
                "brand_type",
            ]
            all_cols = [c for c in cols_display if c in all_results.columns]
            sort_by = ["search_term", "store"] + (["clean_price"] if "clean_price" in all_results.columns else [])
            all_results = all_results.sort_values(sort_by)[all_cols]
            st.dataframe(
                all_results,
                column_config={
                    "search_term": st.column_config.TextColumn("Search term", width="small"),
                    "product_name": st.column_config.TextColumn("Product", width="large"),
                    "price": st.column_config.TextColumn("Raw price", width="medium"),
                    "clean_price_fmt": st.column_config.TextColumn("Cleaned price", width="small"),
                    "store": st.column_config.TextColumn("Store", width="small"),
                    "unit_size": st.column_config.TextColumn("Raw unit size", width="medium"),
                    "unit_clean_display": st.column_config.TextColumn("Cleaned unit", width="small"),
                    "price_per_unit_fmt": st.column_config.TextColumn("Per unit", width="small"),
                    "quality": st.column_config.TextColumn("Quality", width="small"),
                    "category": st.column_config.TextColumn("Category", width="small"),
                    "brand_type": st.column_config.TextColumn("Brand", width="small"),
                },
                hide_index=True,
                width="stretch",
            )
