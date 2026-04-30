import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from datetime import datetime

st.set_page_config(
    page_title="Price Trends – Smart Grocer",
    page_icon="📈",
    layout="wide",
    initial_sidebar_state="expanded",
)

st.markdown("""
<style>
    @import url('https://fonts.googleapis.com/css2?family=DM+Sans:wght@400;500;600;700&display=swap');
    .stApp, [data-testid="stSidebar"] { font-family: 'DM Sans', sans-serif; }
    .block-container { padding: 2rem 2.5rem; max-width: 1400px; }
    h1 { font-size: 1.6rem !important; font-weight: 700 !important; color: #134e4a !important; }
    .metric-card { background: white; border-radius: 12px; padding: 1.25rem; margin-bottom: 1rem; box-shadow: 0 2px 8px rgba(0,0,0,0.06); border: 1px solid #e5e7eb; text-align: center; }
    .metric-value { font-size: 1.75rem; font-weight: 700; color: #0d9488; margin: 0.25rem 0; }
    .metric-label { font-size: 0.85rem; color: #6b7280; margin: 0; }
    [data-testid="stSidebar"] { background: #e0f2f1 !important; }
    [data-testid="stSidebar"] .stMarkdown { color: #134e4a !important; }
    [data-testid="stSidebar"] p { color: #115e59 !important; }
</style>
""", unsafe_allow_html=True)

with st.sidebar:
    st.markdown("## Smart Grocer")
    st.caption("Your local price comparison tool")
    st.markdown("---")
    st.page_link("app.py", label="← Back to main", icon="🏠")
    st.page_link("pages/2_How_it_works.py", label="How it works", icon="📄")


@st.cache_data
def load_data():
    df = pd.read_csv("data/daily_basket_cleaned.csv", parse_dates=["date"])
    df = df.drop(columns=["is_imputed"], errors="ignore")
    return df


st.title("Price Trends")
st.markdown("Track grocery prices over time across Aldi, Publix, and Walmart.")

try:
    df = load_data()
except FileNotFoundError:
    st.error("Daily basket data not found. Run the daily basket scraper first.")
    st.stop()

if df.empty:
    st.warning("No price data available yet.")
    st.stop()

date_min = df["date"].min()
date_max = df["date"].max()
num_days = (date_max - date_min).days + 1
items = sorted(df["search_term"].unique())
stores = sorted(df["store"].unique())
categories = sorted(df["category"].dropna().unique())

st.markdown("### Overview")
col1, col2, col3, col4 = st.columns(4)
with col1:
    st.markdown(f"""
    <div class="metric-card">
        <p class="metric-label">Date Range</p>
        <p class="metric-value">{num_days} days</p>
        <p class="metric-label">{date_min.strftime('%b %d')} – {date_max.strftime('%b %d, %Y')}</p>
    </div>
    """, unsafe_allow_html=True)
with col2:
    st.markdown(f"""
    <div class="metric-card">
        <p class="metric-label">Items Tracked</p>
        <p class="metric-value">{len(items)}</p>
        <p class="metric-label">grocery staples</p>
    </div>
    """, unsafe_allow_html=True)
with col3:
    st.markdown(f"""
    <div class="metric-card">
        <p class="metric-label">Stores</p>
        <p class="metric-value">{len(stores)}</p>
        <p class="metric-label">{', '.join(stores)}</p>
    </div>
    """, unsafe_allow_html=True)
with col4:
    total_records = len(df)
    st.markdown(f"""
    <div class="metric-card">
        <p class="metric-label">Price Records</p>
        <p class="metric-value">{total_records:,}</p>
        <p class="metric-label">data points collected</p>
    </div>
    """, unsafe_allow_html=True)

st.markdown("---")

st.markdown("### Filters")
filter_col1, filter_col2, filter_col3 = st.columns(3)
with filter_col1:
    selected_items = st.multiselect(
        "Items",
        options=items,
        default=items[:3] if len(items) >= 3 else items,
        help="Select items to display in charts"
    )
with filter_col2:
    selected_stores = st.multiselect(
        "Stores",
        options=stores,
        default=stores,
        help="Select stores to compare"
    )
with filter_col3:
    selected_categories = st.multiselect(
        "Categories",
        options=categories,
        default=[],
        help="Filter by category (leave empty for all)"
    )

df_filtered = df.copy()
if selected_items:
    df_filtered = df_filtered[df_filtered["search_term"].isin(selected_items)]
if selected_stores:
    df_filtered = df_filtered[df_filtered["store"].isin(selected_stores)]
if selected_categories:
    df_filtered = df_filtered[df_filtered["category"].isin(selected_categories)]

if df_filtered.empty:
    st.warning("No data matches the selected filters.")
    st.stop()

st.markdown("---")

st.markdown("### Price Trends Over Time")

tab_total, tab_item, tab_store = st.tabs(["Total Basket Cost", "By Item", "By Store"])

with tab_total:
    daily_totals = df_filtered.groupby(["date", "store"])["clean_price"].sum().reset_index()
    daily_totals.columns = ["Date", "Store", "Total Cost"]
    
    fig_total = px.line(
        daily_totals,
        x="Date",
        y="Total Cost",
        color="Store",
        markers=True,
        title="Daily Total Basket Cost by Store",
        color_discrete_map={"Aldi": "#0d9488", "Publix": "#f59e0b", "Walmart": "#3b82f6"}
    )
    fig_total.update_layout(
        hovermode="x unified",
        yaxis_title="Total Cost ($)",
        xaxis_title="",
        legend=dict(orientation="h", yanchor="bottom", y=1.02, xanchor="right", x=1)
    )
    fig_total.update_yaxes(tickprefix="$")
    st.plotly_chart(fig_total, width="stretch")
    
    avg_by_store = daily_totals.groupby("Store")["Total Cost"].mean().reset_index()
    avg_by_store.columns = ["Store", "Average Daily Cost"]
    avg_by_store["Average Daily Cost"] = avg_by_store["Average Daily Cost"].round(2)
    
    st.markdown("**Average Daily Basket Cost**")
    cols = st.columns(len(avg_by_store))
    for i, row in avg_by_store.iterrows():
        with cols[i]:
            st.metric(row["Store"], f"${row['Average Daily Cost']:.2f}")

with tab_item:
    if selected_items:
        item_to_show = st.selectbox("Select Item", options=selected_items, key="item_trend")
        df_item = df_filtered[df_filtered["search_term"] == item_to_show]
        
        fig_item = px.line(
            df_item,
            x="date",
            y="clean_price",
            color="store",
            markers=True,
            title=f"Price Trend: {item_to_show}",
            color_discrete_map={"Aldi": "#0d9488", "Publix": "#f59e0b", "Walmart": "#3b82f6"}
        )
        fig_item.update_layout(
            hovermode="x unified",
            yaxis_title="Price ($)",
            xaxis_title="",
            legend=dict(orientation="h", yanchor="bottom", y=1.02, xanchor="right", x=1)
        )
        fig_item.update_yaxes(tickprefix="$")
        st.plotly_chart(fig_item, width="stretch")
        
        item_stats = df_item.groupby("store")["clean_price"].agg(["mean", "min", "max", "std"]).round(2)
        item_stats.columns = ["Avg Price", "Min Price", "Max Price", "Std Dev"]
        item_stats = item_stats.reset_index()
        item_stats.columns = ["Store", "Avg Price", "Min Price", "Max Price", "Std Dev"]
        for col in ["Avg Price", "Min Price", "Max Price"]:
            item_stats[col] = item_stats[col].apply(lambda x: f"${x:.2f}")
        item_stats["Std Dev"] = item_stats["Std Dev"].apply(lambda x: f"${x:.2f}" if pd.notna(x) else "—")
        
        st.markdown(f"**Price Statistics: {item_to_show}**")
        st.dataframe(item_stats, hide_index=True, width="stretch")
    else:
        st.info("Select at least one item to view individual price trends.")

with tab_store:
    store_to_show = st.selectbox("Select Store", options=selected_stores, key="store_trend")
    df_store = df_filtered[df_filtered["store"] == store_to_show]
    
    fig_store = px.line(
        df_store,
        x="date",
        y="clean_price",
        color="search_term",
        markers=True,
        title=f"All Item Prices: {store_to_show}"
    )
    fig_store.update_layout(
        hovermode="x unified",
        yaxis_title="Price ($)",
        xaxis_title="",
        legend_title="Item",
        legend=dict(orientation="h", yanchor="bottom", y=1.02, xanchor="right", x=1)
    )
    fig_store.update_yaxes(tickprefix="$")
    st.plotly_chart(fig_store, width="stretch")

st.markdown("---")

st.markdown("### Price Comparison")

tab_current, tab_avg, tab_volatility = st.tabs(["Latest Prices", "Average Prices", "Price Volatility"])

with tab_current:
    latest_date = df_filtered["date"].max()
    df_latest = df_filtered[df_filtered["date"] == latest_date]
    
    pivot_latest = df_latest.pivot_table(
        index="search_term",
        columns="store",
        values="clean_price",
        aggfunc="first"
    ).reset_index()
    pivot_latest.columns.name = None
    pivot_latest = pivot_latest.rename(columns={"search_term": "Item"})
    
    for store in stores:
        if store in pivot_latest.columns:
            pivot_latest[store] = pivot_latest[store].apply(
                lambda x: f"${x:.2f}" if pd.notna(x) else "—"
            )
    
    st.markdown(f"**Prices as of {latest_date.strftime('%B %d, %Y')}**")
    st.dataframe(pivot_latest, hide_index=True, width="stretch")

with tab_avg:
    pivot_avg = df_filtered.pivot_table(
        index="search_term",
        columns="store",
        values="clean_price",
        aggfunc="mean"
    ).round(2).reset_index()
    pivot_avg.columns.name = None
    pivot_avg = pivot_avg.rename(columns={"search_term": "Item"})
    
    for store in stores:
        if store in pivot_avg.columns:
            pivot_avg[store] = pivot_avg[store].apply(
                lambda x: f"${x:.2f}" if pd.notna(x) else "—"
            )
    
    st.markdown("**Average Price Over Time Period**")
    st.dataframe(pivot_avg, hide_index=True, width="stretch")

with tab_volatility:
    pivot_std = df_filtered.pivot_table(
        index="search_term",
        columns="store",
        values="clean_price",
        aggfunc="std"
    ).round(3).reset_index()
    pivot_std.columns.name = None
    pivot_std = pivot_std.rename(columns={"search_term": "Item"})
    
    for store in stores:
        if store in pivot_std.columns:
            pivot_std[store] = pivot_std[store].apply(
                lambda x: f"${x:.3f}" if pd.notna(x) else "—"
            )
    
    st.markdown("**Price Standard Deviation (Higher = More Variable)**")
    st.dataframe(pivot_std, hide_index=True, width="stretch")

st.markdown("---")

st.markdown("### Category Analysis")

cat_col1, cat_col2 = st.columns(2)

with cat_col1:
    cat_avg = df_filtered.groupby(["category", "store"])["clean_price"].mean().reset_index()
    cat_avg.columns = ["Category", "Store", "Avg Price"]
    
    fig_cat = px.bar(
        cat_avg,
        x="Category",
        y="Avg Price",
        color="Store",
        barmode="group",
        title="Average Price by Category & Store",
        color_discrete_map={"Aldi": "#0d9488", "Publix": "#f59e0b", "Walmart": "#3b82f6"}
    )
    fig_cat.update_yaxes(tickprefix="$")
    fig_cat.update_layout(legend=dict(orientation="h", yanchor="bottom", y=1.02, xanchor="right", x=1))
    st.plotly_chart(fig_cat, width="stretch")

with cat_col2:
    cat_totals = df_filtered.groupby("category")["clean_price"].sum().reset_index()
    cat_totals.columns = ["Category", "Total Spend"]
    
    fig_pie = px.pie(
        cat_totals,
        values="Total Spend",
        names="Category",
        title="Spend Distribution by Category",
        color_discrete_sequence=px.colors.qualitative.Set2
    )
    fig_pie.update_traces(textposition="inside", textinfo="percent+label")
    st.plotly_chart(fig_pie, width="stretch")

st.markdown("---")

st.markdown("### Day-of-Week Analysis")

df_filtered["day_of_week"] = df_filtered["date"].dt.day_name()
day_order = ["Monday", "Tuesday", "Wednesday", "Thursday", "Friday", "Saturday", "Sunday"]
df_filtered["day_of_week"] = pd.Categorical(df_filtered["day_of_week"], categories=day_order, ordered=True)

dow_avg = df_filtered.groupby(["day_of_week", "store"], observed=True)["clean_price"].mean().reset_index()
dow_avg.columns = ["Day", "Store", "Avg Price"]

fig_dow = px.bar(
    dow_avg,
    x="Day",
    y="Avg Price",
    color="Store",
    barmode="group",
    title="Average Item Price by Day of Week",
    color_discrete_map={"Aldi": "#0d9488", "Publix": "#f59e0b", "Walmart": "#3b82f6"}
)
fig_dow.update_yaxes(tickprefix="$")
fig_dow.update_layout(legend=dict(orientation="h", yanchor="bottom", y=1.02, xanchor="right", x=1))
st.plotly_chart(fig_dow, width="stretch")

st.markdown("---")

with st.expander("View Raw Data"):
    st.markdown("**All Price Records**")
    display_cols = ["date", "search_term", "product_name", "store", "clean_price", "unit_size", "category", "brand_type"]
    available_cols = [c for c in display_cols if c in df_filtered.columns]
    df_display = df_filtered[available_cols].copy()
    df_display = df_display.sort_values(["date", "search_term", "store"], ascending=[False, True, True])
    df_display["clean_price"] = df_display["clean_price"].apply(lambda x: f"${x:.2f}" if pd.notna(x) else "—")
    df_display = df_display.rename(columns={
        "date": "Date",
        "search_term": "Item",
        "product_name": "Product",
        "store": "Store",
        "clean_price": "Price",
        "unit_size": "Size",
        "category": "Category",
        "brand_type": "Brand Type"
    })
    st.dataframe(df_display, hide_index=True, width="stretch", height=400)

st.divider()
st.caption("Smart Grocery – Track grocery price trends over time.")
