"""
Generate figures for report.tex into report_fig/.
Mirrors the relevant analyses from analysis.ipynb and aligns labels with
slides_final.pdf.
"""
import os
from pathlib import Path

import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import matplotlib.ticker as mtick
import seaborn as sns
from scipy import stats

OUT = Path(__file__).resolve().parent / "report_fig"
OUT.mkdir(exist_ok=True, parents=True)

sns.set_theme(style="whitegrid", palette="muted", font_scale=1.05)
plt.rcParams["figure.dpi"] = 140
plt.rcParams["savefig.dpi"] = 200
plt.rcParams["savefig.bbox"] = "tight"

STORE_COLORS = {"Aldi": "#00529B", "Publix": "#3B8132", "Walmart": "#FFC220"}

df = pd.read_csv("data/daily_basket_cleaned.csv", parse_dates=["date"])

# Re-apply the same imputations done in analysis.ipynb so figures match.
milk_mask = (
    (df["store"] == "Publix") &
    (df["search_term"] == "Whole Milk") &
    (df["unit_uncertain"] == True)
)
df.loc[milk_mask, "normalized_qty"] = 128.0
df.loc[milk_mask, "unit_type"] = "oz"
df.loc[milk_mask, "unit_uncertain"] = False
df.loc[milk_mask, "price_per_unit"] = df.loc[milk_mask, "clean_price"] / 128.0

lettuce_mask = (
    (df["store"] == "Publix") &
    (df["search_term"] == "Iceberg Lettuce") &
    (df["unit_uncertain"] == True)
)
df.loc[lettuce_mask, "normalized_qty"] = 1.0
df.loc[lettuce_mask, "unit_type"] = "count"
df.loc[lettuce_mask, "unit_uncertain"] = False
df.loc[lettuce_mask, "price_per_unit"] = df.loc[lettuce_mask, "clean_price"] / 1.0

df["day_of_week"] = df["date"].dt.day_name()
stores = sorted(df["store"].unique())

basket = df.groupby(["date", "store"])["clean_price"].sum().reset_index()
basket.columns = ["date", "store", "basket_cost"]


def save(name):
    path = OUT / name
    plt.savefig(path)
    plt.close()
    print(f"wrote {path}")


# --- 1. Daily basket cost over time -------------------------------------
fig, ax = plt.subplots(figsize=(10, 4))
for store in stores:
    grp = basket[basket["store"] == store]
    ax.plot(grp["date"], grp["basket_cost"], marker="o", ms=4, label=store,
            color=STORE_COLORS[store], linewidth=1.5)
ax.set_title("Daily Total Basket Cost by Retailer")
ax.set_ylabel("Total Basket Cost ($)")
ax.set_xlabel("Date")
ax.yaxis.set_major_formatter(mtick.StrMethodFormatter("${x:,.2f}"))
ax.legend()
fig.autofmt_xdate()
save("01_daily_basket_cost.png")


# --- 2. Mean daily basket cost (bar; matches slide 14) -------------------
mean_basket = basket.groupby("store")["basket_cost"].mean().reindex(stores)
fig, ax = plt.subplots(figsize=(7, 4))
bars = ax.bar(mean_basket.index, mean_basket.values,
              color=[STORE_COLORS[s] for s in mean_basket.index],
              edgecolor="black", linewidth=0.5)
for bar, val in zip(bars, mean_basket.values):
    ax.text(bar.get_x() + bar.get_width() / 2, val + 0.4,
            f"${val:,.2f}", ha="center", va="bottom", fontweight="bold")
ax.set_title("Mean Daily Basket Cost by Retailer")
ax.set_ylabel("Mean Daily Basket Cost ($)")
ax.set_ylim(0, mean_basket.max() * 1.15)
ax.yaxis.set_major_formatter(mtick.StrMethodFormatter("${x:,.2f}"))
save("02_mean_basket_bar.png")


# --- 3. Mean shelf price per item by retailer ---------------------------
mean_prices = df.groupby(["search_term", "store"])["clean_price"].mean().unstack()
fig, ax = plt.subplots(figsize=(11, 5))
mean_prices.plot(kind="bar", ax=ax,
                 color=[STORE_COLORS[c] for c in mean_prices.columns])
ax.set_title("Mean Shelf Price per Item by Retailer")
ax.set_ylabel("Mean Price ($)")
ax.set_xlabel("")
ax.yaxis.set_major_formatter(mtick.StrMethodFormatter("${x:,.2f}"))
plt.xticks(rotation=35, ha="right")
save("03_mean_price_per_item.png")


# --- 5. Category x retailer interaction plot (slide 17/18) --------------
cat_store = df.groupby(["date", "category", "store"])["clean_price"].sum().reset_index()
interaction = cat_store.groupby(["category", "store"])["clean_price"].mean().reset_index()
fig, ax = plt.subplots(figsize=(9, 4.5))
for store in stores:
    sub = interaction[interaction["store"] == store]
    ax.plot(sub["category"], sub["clean_price"], marker="o", label=store,
            color=STORE_COLORS[store], linewidth=2.5, markersize=8)
ax.set_title("Category x Retailer Interaction")
ax.set_ylabel("Mean Daily Category Cost ($)")
ax.set_xlabel("Category")
ax.yaxis.set_major_formatter(mtick.StrMethodFormatter("${x:,.2f}"))
ax.legend()
meat = interaction[interaction["category"] == "Meat"]
if not meat.empty:
    top = meat.loc[meat["clean_price"].idxmax()]
    bot = meat.loc[meat["clean_price"].idxmin()]
    spread = top["clean_price"] - bot["clean_price"]
    mid = (top["clean_price"] + bot["clean_price"]) / 2
    ax.annotate(
        f"${spread:.2f} spread",
        xy=("Meat", mid), xytext=(0.78, 0.88),
        textcoords="axes fraction",
        arrowprops=dict(arrowstyle="->", color="gray", lw=1.2),
        fontsize=10, fontweight="bold", ha="center",
        bbox=dict(boxstyle="round,pad=0.3", fc="lightyellow", ec="gray", alpha=0.9),
    )
save("05_category_interaction.png")


# --- 6. Category-level cost distribution (5 panels) ---------------------
cats = sorted(df["category"].unique())
fig, axes = plt.subplots(1, len(cats), figsize=(16, 4), sharey=False)
for ax, cat in zip(axes, cats):
    grp = cat_store[cat_store["category"] == cat]
    sns.boxplot(data=grp, x="store", y="clean_price",
                palette=STORE_COLORS, ax=ax, order=stores)
    ax.set_title(cat)
    ax.set_xlabel("")
    ax.set_ylabel("Daily Category Cost ($)" if ax is axes[0] else "")
    ax.yaxis.set_major_formatter(mtick.StrMethodFormatter("${x:,.2f}"))
plt.suptitle("Daily Category Cost Distribution by Retailer", y=1.02, fontsize=13)
save("06_category_boxplots.png")


# --- 7. Coefficient of variation by category (matches slide 20) ---------
# CV of daily category total cost across the 37 dates, per (category, store)
cat_cv = (
    cat_store.groupby(["category", "store"])["clean_price"]
    .agg(["mean", "std"])
    .reset_index()
)
cat_cv["cv"] = cat_cv["std"] / cat_cv["mean"]
cv_pivot = cat_cv.pivot(index="category", columns="store", values="cv").reindex(columns=stores)

fig, ax = plt.subplots(figsize=(9, 4.5))
cv_pivot.plot(kind="bar", ax=ax,
              color=[STORE_COLORS[c] for c in cv_pivot.columns])
ax.set_title("Daily Category-Cost Volatility (CV) by Retailer")
ax.set_ylabel("Coefficient of Variation")
ax.set_xlabel("")
ax.yaxis.set_major_formatter(mtick.PercentFormatter(1.0))
plt.xticks(rotation=0)
ax.legend(title=None)
save("07_cv_by_category.png")

# Print the table to confirm slide alignment
print("\nCV by category x store (slide table):")
print(cv_pivot.round(4))


# --- 8. Item-level CV ---------------------------------------------------
cv = (
    df.groupby(["search_term", "store"])["clean_price"]
    .agg(["mean", "std"])
    .reset_index()
)
cv["cv"] = cv["std"] / cv["mean"]
cv_item = cv.pivot(index="search_term", columns="store", values="cv").reindex(columns=stores)
fig, ax = plt.subplots(figsize=(11, 5))
cv_item.plot(kind="bar", ax=ax,
             color=[STORE_COLORS[c] for c in cv_item.columns])
ax.set_title("Item-Level Price Volatility (CV) by Retailer")
ax.set_ylabel("Coefficient of Variation")
ax.set_xlabel("")
ax.yaxis.set_major_formatter(mtick.PercentFormatter(1.0))
plt.xticks(rotation=35, ha="right")
ax.legend(title=None)
save("08_cv_by_item.png")


# --- 9. Day-of-week boxplot --------------------------------------------
basket_dow = basket.copy()
basket_dow["day_of_week"] = basket_dow["date"].dt.day_name()
day_order = ["Monday", "Tuesday", "Wednesday", "Thursday", "Friday", "Saturday", "Sunday"]
basket_dow["day_of_week"] = pd.Categorical(
    basket_dow["day_of_week"], categories=day_order, ordered=True
)
fig, ax = plt.subplots(figsize=(10, 4.5))
sns.boxplot(data=basket_dow, x="day_of_week", y="basket_cost", hue="store",
            palette=STORE_COLORS, ax=ax)
ax.set_title("Basket Cost by Day of Week and Retailer")
ax.set_ylabel("Total Basket Cost ($)")
ax.set_xlabel("")
ax.yaxis.set_major_formatter(mtick.StrMethodFormatter("${x:,.2f}"))
save("09_day_of_week.png")


# --- 10. Optimal split basket vs best single store ---------------------
cheapest = df.loc[df.groupby(["date", "search_term"])["clean_price"].idxmin()]
optimal_basket = cheapest.groupby("date")["clean_price"].sum().reset_index()
optimal_basket.columns = ["date", "optimal_cost"]
comparison = basket.pivot(index="date", columns="store", values="basket_cost").reset_index()
comparison = comparison.merge(optimal_basket, on="date")
comparison["best_single_store"] = comparison[stores].min(axis=1)

fig, ax = plt.subplots(figsize=(10, 4.5))
ax.plot(comparison["date"], comparison["best_single_store"],
        label="Best Single Store", linewidth=2, color="gray")
ax.plot(comparison["date"], comparison["optimal_cost"],
        label="Optimal Split Basket", linewidth=2, linestyle="--", color="#C44E52")
ax.fill_between(comparison["date"], comparison["optimal_cost"],
                comparison["best_single_store"], alpha=0.2, color="#C44E52")
ax.set_title("Best Single Store vs. Optimal Split Basket")
ax.set_ylabel("Basket Cost ($)")
ax.yaxis.set_major_formatter(mtick.StrMethodFormatter("${x:,.2f}"))
ax.legend()
fig.autofmt_xdate()
save("10_split_vs_single.png")


# --- 11. Cheapest retailer per item (stacked bar) ----------------------
win_counts = cheapest.groupby(["search_term", "store"]).size().unstack(fill_value=0)
win_counts = win_counts.reindex(columns=stores).fillna(0)
fig, ax = plt.subplots(figsize=(11, 5))
win_counts.plot(kind="bar", stacked=True, ax=ax,
                color=[STORE_COLORS[c] for c in win_counts.columns])
ax.set_title("Cheapest Retailer Frequency by Item")
ax.set_ylabel("Number of Days as Cheapest")
ax.set_xlabel("")
ax.legend(title=None)
plt.xticks(rotation=35, ha="right")
save("11_cheapest_by_item.png")


# --- 12. RCBD residual diagnostics (Q-Q + histogram) -------------------
rcbd = df.groupby(["search_term", "store"])["clean_price"].mean().unstack()
rcbd.columns.name = None
grand_mean = rcbd.values.mean()
row_means = rcbd.mean(axis=1).values
col_means = rcbd.mean(axis=0).values
residuals = rcbd.values - row_means[:, None] - col_means[None, :] + grand_mean

fig, axes = plt.subplots(1, 2, figsize=(11, 4))
axes[0].hist(residuals.flatten(), bins=14, edgecolor="black", alpha=0.75,
             color="#0d9488")
axes[0].set_title("Histogram of RCBD Residuals")
axes[0].set_xlabel("Residual")
axes[0].set_ylabel("Frequency")
stats.probplot(residuals.flatten(), dist="norm", plot=axes[1])
axes[1].set_title("Q-Q Plot of RCBD Residuals")
plt.tight_layout()
save("12_rcbd_residuals.png")

print("\nAll figures written to:", OUT)
