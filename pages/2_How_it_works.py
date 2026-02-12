# How it works

import streamlit as st

with st.sidebar:
    st.markdown("## Smart Grocer")
    st.caption("Your local price comparison tool")
    st.markdown("---")
    st.page_link("app.py", label="← Back to main", icon="🏠")

st.title("How it works")
st.markdown("A short guide to how Smart Grocery finds and compares prices.")

st.header("Stores")
st.markdown("""
The app searches **Aldi**, **Publix**, and **Walmart** using your zip code (or address) so prices reflect your local stores. Each store’s website is opened in the background; you’ll see browser windows while the search runs.
""")

st.header("Search")
st.markdown("""
- You enter a **grocery list** (one item per line) and a **location**.
- For each item, we search that term on each store’s site.
- We keep up to **5 results per item per store** and then filter by **keyword match** so results actually relate to what you searched (e.g. “milk” won’t keep chocolate bars).
- That gives you a set of real product options with prices.
""")

st.header("Cheapest basket")
st.markdown("""
The **Cheapest Basket** tab shows, for each item on your list, the **single cheapest option** we found across all stores. The **Estimated Total** is the sum of those best prices. The **All Prices** tab shows every result so you can compare store-by-store and by price per unit.
""")

st.header("Price per unit")
st.markdown("""
When we can parse the size (e.g. 1 gal, 64 oz, 12 ct), we compute **price per unit** ($/oz or $/ct). That lets you compare a gallon jug to a half-gallon carton fairly. If the size is missing or unreadable, we show “—” for price per unit.
""")

st.header("Daily basket (longitudinal data)")
st.markdown("""
A fixed list of 12 common items (milk, eggs, butter, bananas, chicken breast, etc.) can be run on a **schedule** (e.g. daily via Windows Task Scheduler). Results are appended to `data/daily_basket.csv`. Over time you can answer questions like “Is Tuesday cheaper?” or “How do store prices change by category?” See **DAILY_RUN.md** in the project for setup.
""")

st.divider()
st.caption("Smart Grocery – compare prices across Aldi, Publix, and Walmart.")
