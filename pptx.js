const pptxgen = require("pptxgenjs");

const pres = new pptxgen();
pres.layout = "LAYOUT_16x9";
pres.title = "Smart Grocer: Statistical Analysis";

// Color palette — data-science / market research feel
const C = {
  navy:    "0D1B2A",   // primary dark (title bg)
  teal:    "028090",   // accent
  seafoam: "00A896",   // secondary accent
  cream:   "F5F5F0",   // light bg
  white:   "FFFFFF",
  slate:   "475569",   // body text
  muted:   "94A3B8",   // captions
  aldi:    "00529B",
  publix:  "3B8132",
  walmart: "FFC220",
  success: "16A34A",
  danger:  "DC2626",
};

const makeShadow = () => ({ type: "outer", blur: 8, offset: 3, angle: 135, color: "000000", opacity: 0.12 });

// ─────────────────────────────────────────────
// SLIDE 1 — Title
// ─────────────────────────────────────────────
{
  const s = pres.addSlide();
  s.background = { color: C.navy };

  // Teal accent bar left
  s.addShape(pres.shapes.RECTANGLE, { x: 0, y: 0, w: 0.18, h: 5.625, fill: { color: C.teal }, line: { color: C.teal } });

  // Decorative large circle
  s.addShape(pres.shapes.OVAL, { x: 6.8, y: -1.2, w: 5.5, h: 5.5, fill: { color: C.teal, transparency: 88 }, line: { color: C.teal, transparency: 80 } });
  s.addShape(pres.shapes.OVAL, { x: 7.5, y: -0.5, w: 4, h: 4, fill: { color: C.seafoam, transparency: 92 }, line: { color: C.seafoam, transparency: 85 } });

  s.addText("SMART GROCER", { x: 0.5, y: 1.1, w: 9, h: 0.5, fontSize: 13, bold: true, color: C.teal, charSpacing: 6, fontFace: "Calibri" });
  s.addText("Statistical Price Analysis", { x: 0.5, y: 1.65, w: 8.5, h: 1.1, fontSize: 48, bold: true, color: C.white, fontFace: "Georgia" });
  s.addText("Aldi · Publix · Walmart", { x: 0.5, y: 2.85, w: 8, h: 0.5, fontSize: 20, color: C.teal, fontFace: "Calibri" });

  s.addShape(pres.shapes.RECTANGLE, { x: 0.5, y: 3.55, w: 4.5, h: 0.03, fill: { color: C.slate, transparency: 50 }, line: { color: C.slate, transparency: 50 } });

  s.addText([
    { text: "Feb 3 – Mar 11, 2026  ·  ", options: {} },
    { text: "37 collection days  ·  ", options: {} },
    { text: "12 grocery items  ·  ", options: {} },
    { text: "1,258 observations", options: {} },
  ], { x: 0.5, y: 3.75, w: 9, h: 0.4, fontSize: 12, color: C.muted, fontFace: "Calibri" });
}

// ─────────────────────────────────────────────
// SLIDE 2 — Project Overview
// ─────────────────────────────────────────────
{
  const s = pres.addSlide();
  s.background = { color: C.cream };

  s.addShape(pres.shapes.RECTANGLE, { x: 0, y: 0, w: 10, h: 1.05, fill: { color: C.navy }, line: { color: C.navy } });
  s.addText("Project Overview", { x: 0.4, y: 0.18, w: 9, h: 0.65, fontSize: 28, bold: true, color: C.white, fontFace: "Georgia", margin: 0 });

  // 3 column cards
  const cards = [
    { title: "Goal", body: "Build a daily grocery price scraper and perform rigorous statistical analysis across three major retailers in the Southeast.", color: C.teal },
    { title: "Data", body: "1,332 raw rows scraped daily via automation. After cleaning (unit-uncertain exclusions), 1,258 rows spanning 37 unique dates.", color: C.aldi },
    { title: "Scope", body: "12 grocery items across 5 categories: Dairy, Meat, Produce, Pantry, and Household. All prices normalized to comparable units.", color: C.publix },
  ];

  cards.forEach((c, i) => {
    const x = 0.3 + i * 3.22;
    s.addShape(pres.shapes.RECTANGLE, { x, y: 1.25, w: 3.0, h: 3.85, fill: { color: C.white }, line: { color: "E2E8F0" }, shadow: makeShadow() });
    s.addShape(pres.shapes.RECTANGLE, { x, y: 1.25, w: 3.0, h: 0.07, fill: { color: c.color }, line: { color: c.color } });
    s.addText(c.title, { x: x + 0.18, y: 1.38, w: 2.65, h: 0.45, fontSize: 16, bold: true, color: C.navy, fontFace: "Calibri", margin: 0 });
    s.addText(c.body, { x: x + 0.18, y: 1.88, w: 2.65, h: 2.9, fontSize: 13, color: C.slate, fontFace: "Calibri", valign: "top" });
  });

  // Research questions strip
  s.addShape(pres.shapes.RECTANGLE, { x: 0, y: 5.15, w: 10, h: 0.47, fill: { color: C.teal, transparency: 10 }, line: { color: C.teal, transparency: 10 } });
  s.addText("7 Research Questions:  Basket cost · Category interactions · Price volatility · Day-of-week effect · Store brands · Multi-store optimization · Forecasting",
    { x: 0.3, y: 5.15, w: 9.5, h: 0.47, fontSize: 11, color: C.white, fontFace: "Calibri", valign: "middle" });
}

// ─────────────────────────────────────────────
// SLIDE 3 — Data Pipeline
// ─────────────────────────────────────────────
{
  const s = pres.addSlide();
  s.background = { color: C.cream };

  s.addShape(pres.shapes.RECTANGLE, { x: 0, y: 0, w: 10, h: 1.05, fill: { color: C.navy }, line: { color: C.navy } });
  s.addText("Data Pipeline & Cleaning", { x: 0.4, y: 0.18, w: 9, h: 0.65, fontSize: 28, bold: true, color: C.white, fontFace: "Georgia", margin: 0 });

  const steps = [
    { step: "01", label: "Web Scraping", desc: "Daily automated scraping from Aldi (via Instacart), Publix, and Walmart storefronts" },
    { step: "02", label: "Price Parsing", desc: 'Numeric extraction from messy strings like "Current price: $3.99". Values above $500 rejected.' },
    { step: "03", label: "Unit Normalization", desc: "Gallons→128 oz, Pounds→16 oz, Dozens→12 count. Ambiguous units flagged as unit_uncertain." },
    { step: "04", label: "Brand Classification", desc: "Store-brand prefixes (Great Value, Friendly Farms, Publix…) → Private. All others → National." },
    { step: "05", label: "Fuzzy Match QA", desc: "Fuzzy-match score between query and returned product name. Rows below 0.5 threshold flagged." },
  ];

  steps.forEach((st, i) => {
    const x = 0.3;
    const y = 1.2 + i * 0.83;
    s.addShape(pres.shapes.RECTANGLE, { x, y, w: 0.52, h: 0.55, fill: { color: C.teal }, line: { color: C.teal } });
    s.addText(st.step, { x, y, w: 0.52, h: 0.55, fontSize: 13, bold: true, color: C.white, fontFace: "Calibri", align: "center", valign: "middle", margin: 0 });
    s.addText(st.label, { x: 1.0, y: y + 0.02, w: 2.8, h: 0.28, fontSize: 13, bold: true, color: C.navy, fontFace: "Calibri", margin: 0 });
    s.addText(st.desc, { x: 1.0, y: y + 0.28, w: 8.7, h: 0.4, fontSize: 11.5, color: C.slate, fontFace: "Calibri", margin: 0 });
    if (i < steps.length - 1) {
      s.addShape(pres.shapes.LINE, { x: 0.556, y: y + 0.55, w: 0, h: 0.26, line: { color: C.teal, width: 1.5 } });
    }
  });

  // Cleaning callout
  s.addShape(pres.shapes.RECTANGLE, { x: 6.1, y: 1.2, w: 3.6, h: 2.9, fill: { color: C.white }, line: { color: "E2E8F0" }, shadow: makeShadow() });
  s.addShape(pres.shapes.RECTANGLE, { x: 6.1, y: 1.2, w: 3.6, h: 0.07, fill: { color: C.seafoam }, line: { color: C.seafoam } });
  s.addText("Cleaning Summary", { x: 6.25, y: 1.33, w: 3.3, h: 0.35, fontSize: 13, bold: true, color: C.navy, fontFace: "Calibri", margin: 0 });

  const stats = [
    ["Raw rows", "1,332"],
    ["Excluded (unit_uncertain)", "74 (5.6%)"],
    ["Analysis rows", "1,258"],
    ["Scraper errors", "0"],
    ["Name match uncertain", "0"],
    ["Missing values", "0"],
  ];
  stats.forEach((r, i) => {
    const y = 1.75 + i * 0.38;
    s.addText(r[0], { x: 6.25, y, w: 2.3, h: 0.32, fontSize: 11.5, color: C.slate, fontFace: "Calibri", margin: 0 });
    s.addText(r[1], { x: 8.3, y, w: 1.3, h: 0.32, fontSize: 11.5, bold: true, color: C.teal, fontFace: "Calibri", align: "right", margin: 0 });
  });
}

// ─────────────────────────────────────────────
// SLIDE 4 — Basket Cost Overview (EDA)
// ─────────────────────────────────────────────
{
  const s = pres.addSlide();
  s.background = { color: C.cream };

  s.addShape(pres.shapes.RECTANGLE, { x: 0, y: 0, w: 10, h: 1.05, fill: { color: C.navy }, line: { color: C.navy } });
  s.addText("Exploratory Analysis: Basket Costs", { x: 0.4, y: 0.18, w: 9, h: 0.65, fontSize: 28, bold: true, color: C.white, fontFace: "Georgia", margin: 0 });

  // Mean basket cost cards
  const stores = [
    { name: "Aldi", mean: "$33.16", std: "±$0.34", color: C.aldi, rank: "Highest mean" },
    { name: "Publix", mean: "$32.99", std: "±$0.65", color: C.publix, rank: "Most variable" },
    { name: "Walmart", mean: "$32.95", std: "±$0.47", color: C.walmart, rank: "Lowest mean" },
  ];

  stores.forEach((st, i) => {
    const x = 0.3 + i * 3.22;
    s.addShape(pres.shapes.RECTANGLE, { x, y: 1.2, w: 3.0, h: 2.35, fill: { color: C.white }, line: { color: "E2E8F0" }, shadow: makeShadow() });
    s.addShape(pres.shapes.RECTANGLE, { x, y: 1.2, w: 3.0, h: 0.55, fill: { color: st.color }, line: { color: st.color } });
    s.addText(st.name, { x: x + 0.12, y: 1.25, w: 2.76, h: 0.45, fontSize: 18, bold: true, color: st.name === "Walmart" ? C.navy : C.white, fontFace: "Georgia", margin: 0 });
    s.addText(st.mean, { x: x + 0.12, y: 1.85, w: 2.76, h: 0.75, fontSize: 36, bold: true, color: C.navy, fontFace: "Georgia", align: "center", valign: "middle", margin: 0 });
    s.addText("mean basket cost", { x: x + 0.12, y: 2.62, w: 2.76, h: 0.3, fontSize: 11, color: C.muted, fontFace: "Calibri", align: "center" });
    s.addText(st.std + "  std dev", { x: x + 0.12, y: 2.95, w: 2.76, h: 0.3, fontSize: 11, color: C.slate, fontFace: "Calibri", align: "center" });
    s.addText(st.rank, { x: x + 0.12, y: 3.3, w: 2.76, h: 0.25, fontSize: 10, color: st.color, bold: true, fontFace: "Calibri", align: "center" });
  });

  // Key insight box
  s.addShape(pres.shapes.RECTANGLE, { x: 0.3, y: 3.75, w: 9.4, h: 1.62, fill: { color: C.white }, line: { color: "E2E8F0" }, shadow: makeShadow() });
  s.addShape(pres.shapes.RECTANGLE, { x: 0.3, y: 3.75, w: 0.07, h: 1.62, fill: { color: C.teal }, line: { color: C.teal } });
  s.addText("Key Observation", { x: 0.55, y: 3.83, w: 8.9, h: 0.3, fontSize: 13, bold: true, color: C.teal, fontFace: "Calibri", margin: 0 });
  s.addText(
    "All three retailers cluster within a surprisingly narrow $0.21 range on mean basket cost ($32.95–$33.16). However, this headline similarity masks significant item-level divergence — particularly in Meat and Dairy, where inter-store gaps exceed $5.50 per category. The Friedman test confirms the differences are statistically significant (p < 0.001).",
    { x: 0.55, y: 4.15, w: 9.0, h: 1.05, fontSize: 12, color: C.slate, fontFace: "Calibri", valign: "top" }
  );
}

// ─────────────────────────────────────────────
// SLIDE 5 — Statistical Testing (RCBD)
// ─────────────────────────────────────────────
{
  const s = pres.addSlide();
  s.background = { color: C.cream };

  s.addShape(pres.shapes.RECTANGLE, { x: 0, y: 0, w: 10, h: 1.05, fill: { color: C.navy }, line: { color: C.navy } });
  s.addText("RCBD Analysis: Retailer Effect", { x: 0.4, y: 0.18, w: 9, h: 0.65, fontSize: 28, bold: true, color: C.white, fontFace: "Georgia", margin: 0 });

  // Method flow — left column
  s.addShape(pres.shapes.RECTANGLE, { x: 0.3, y: 1.18, w: 4.5, h: 4.2, fill: { color: C.white }, line: { color: "E2E8F0" }, shadow: makeShadow() });
  s.addShape(pres.shapes.RECTANGLE, { x: 0.3, y: 1.18, w: 4.5, h: 0.07, fill: { color: C.teal }, line: { color: C.teal } });
  s.addText("Testing Methodology", { x: 0.48, y: 1.3, w: 4.15, h: 0.35, fontSize: 14, bold: true, color: C.navy, fontFace: "Calibri", margin: 0 });

  const steps2 = [
    { num: "1", label: "Shapiro-Wilk Normality Test", result: "W=0.9369, p=0.0001 → NOT normal" },
    { num: "2", label: "Levene's Variance Test", result: "F=2.9983, p=0.054 → Variances OK" },
    { num: "3", label: "Non-parametric fallback", result: "Friedman Rank Sum Test selected" },
    { num: "4", label: "Post-hoc comparisons", result: "Wilcoxon + Bonferroni correction" },
  ];
  steps2.forEach((st, i) => {
    const y = 1.75 + i * 0.85;
    s.addShape(pres.shapes.OVAL, { x: 0.48, y: y + 0.06, w: 0.35, h: 0.35, fill: { color: C.teal }, line: { color: C.teal } });
    s.addText(st.num, { x: 0.48, y: y + 0.06, w: 0.35, h: 0.35, fontSize: 11, bold: true, color: C.white, fontFace: "Calibri", align: "center", valign: "middle", margin: 0 });
    s.addText(st.label, { x: 0.95, y, w: 3.7, h: 0.28, fontSize: 12, bold: true, color: C.navy, fontFace: "Calibri", margin: 0 });
    s.addText(st.result, { x: 0.95, y: y + 0.3, w: 3.7, h: 0.38, fontSize: 11, color: C.slate, fontFace: "Calibri", margin: 0, italic: true });
  });

  // Results — right column
  s.addShape(pres.shapes.RECTANGLE, { x: 5.15, y: 1.18, w: 4.55, h: 4.2, fill: { color: C.white }, line: { color: "E2E8F0" }, shadow: makeShadow() });
  s.addShape(pres.shapes.RECTANGLE, { x: 5.15, y: 1.18, w: 4.55, h: 0.07, fill: { color: C.seafoam }, line: { color: C.seafoam } });
  s.addText("Results", { x: 5.33, y: 1.3, w: 4.2, h: 0.35, fontSize: 14, bold: true, color: C.navy, fontFace: "Calibri", margin: 0 });

  // Friedman result
  s.addShape(pres.shapes.RECTANGLE, { x: 5.33, y: 1.73, w: 4.2, h: 1.0, fill: { color: C.cream }, line: { color: "E2E8F0" } });
  s.addText("Friedman Test", { x: 5.5, y: 1.8, w: 3.9, h: 0.25, fontSize: 11, bold: true, color: C.teal, fontFace: "Calibri", margin: 0 });
  s.addText("χ² = 17.08   p = 0.000195", { x: 5.5, y: 2.05, w: 3.9, h: 0.35, fontSize: 16, bold: true, color: C.navy, fontFace: "Calibri", margin: 0 });
  s.addText("✓  Significant at α = 0.05", { x: 5.5, y: 2.42, w: 3.9, h: 0.25, fontSize: 11, color: C.success, fontFace: "Calibri", margin: 0 });

  // Pairwise table
  s.addText("Post-hoc Pairwise (Bonferroni)", { x: 5.33, y: 2.85, w: 4.2, h: 0.28, fontSize: 12, bold: true, color: C.navy, fontFace: "Calibri", margin: 0 });

  const rows = [
    [{ text: "Comparison", options: { bold: true, color: C.white } }, { text: "Mean Diff", options: { bold: true, color: C.white } }, { text: "Sig.", options: { bold: true, color: C.white } }],
    ["Aldi vs Publix", "+$0.16", "ns"],
    ["Aldi vs Walmart", "+$0.20", "★"],
    ["Publix vs Walmart", "+$0.04", "ns"],
  ];
  s.addTable(rows, {
    x: 5.33, y: 3.18, w: 4.2, h: 1.95,
    border: { pt: 0.5, color: "E2E8F0" },
    fill: { color: C.white },
    colW: [2.2, 1.1, 0.9],
    rowH: 0.42,
    fontFace: "Calibri",
    fontSize: 12,
    align: "center",
    valign: "middle",
    autoPage: false,
  });
  // Override header row color manually by placing a rect behind it
  s.addShape(pres.shapes.RECTANGLE, { x: 5.33, y: 3.18, w: 4.2, h: 0.42, fill: { color: C.navy }, line: { color: C.navy } });
  s.addText([
    { text: "Comparison", options: { w: 2.2 } },
    { text: "Mean Diff", options: {} },
    { text: "Sig.", options: {} },
  ], { x: 5.33, y: 3.18, w: 4.2, h: 0.42, fontSize: 12, bold: true, color: C.white, fontFace: "Calibri", align: "center", valign: "middle" });
}

// ─────────────────────────────────────────────
// SLIDE 6 — Category Interaction
// ─────────────────────────────────────────────
{
  const s = pres.addSlide();
  s.background = { color: C.cream };

  s.addShape(pres.shapes.RECTANGLE, { x: 0, y: 0, w: 10, h: 1.05, fill: { color: C.navy }, line: { color: C.navy } });
  s.addText("Category × Retailer Interaction", { x: 0.4, y: 0.18, w: 9, h: 0.65, fontSize: 28, bold: true, color: C.white, fontFace: "Georgia", margin: 0 });

  s.addText("Friedman test repeated within each category — retailer effect is significant across ALL five categories (p < 0.001).",
    { x: 0.4, y: 1.12, w: 9.2, h: 0.45, fontSize: 13, color: C.slate, fontFace: "Calibri" });

  // Category bar chart — Meat dominates, use horizontal bars with store breakdown
  const categories = [
    { cat: "Meat", aldi: 12.5, publix: 17.5, walmart: 12.0 },
    { cat: "Dairy", aldi: 10.0, publix: 5.1, walmart: 8.1 },
    { cat: "Pantry", aldi: 5.3, publix: 3.4, walmart: 3.2 },
    { cat: "Produce", aldi: 5.2, publix: 2.5, walmart: 3.9 },
    { cat: "Household", aldi: 2.7, publix: 2.1, walmart: 2.7 },
  ];

  s.addChart(pres.charts.BAR, [
    { name: "Aldi", labels: categories.map(c => c.cat), values: categories.map(c => c.aldi) },
    { name: "Publix", labels: categories.map(c => c.cat), values: categories.map(c => c.publix) },
    { name: "Walmart", labels: categories.map(c => c.cat), values: categories.map(c => c.walmart) },
  ], {
    x: 0.3, y: 1.65, w: 6.0, h: 3.75,
    barDir: "col",
    barGrouping: "clustered",
    chartColors: [C.aldi, C.publix, C.walmart],
    chartArea: { fill: { color: C.white }, roundedCorners: false },
    catAxisLabelColor: C.slate,
    valAxisLabelColor: C.slate,
    valGridLine: { color: "E2E8F0", size: 0.5 },
    catGridLine: { style: "none" },
    showLegend: true,
    legendPos: "b",
    legendColor: C.slate,
    showTitle: true,
    title: "Mean Daily Category Cost by Retailer ($)",
    titleColor: C.navy,
    titleFontSize: 12,
  });

  // Highlights column
  s.addShape(pres.shapes.RECTANGLE, { x: 6.55, y: 1.65, w: 3.15, h: 3.75, fill: { color: C.white }, line: { color: "E2E8F0" }, shadow: makeShadow() });
  s.addShape(pres.shapes.RECTANGLE, { x: 6.55, y: 1.65, w: 3.15, h: 0.07, fill: { color: C.teal }, line: { color: C.teal } });
  s.addText("Key Category Insights", { x: 6.72, y: 1.77, w: 2.8, h: 0.33, fontSize: 13, bold: true, color: C.navy, fontFace: "Calibri", margin: 0 });

  const insights = [
    { cat: "Meat", note: "Largest spread: $5.58 between retailers. Publix Chicken Breast averages $9.43 vs Aldi at $5.37.", color: C.danger },
    { cat: "Dairy", note: "Aldi $10/day vs Publix $5.10 — driven by whole milk and butter price positioning.", color: C.aldi },
    { cat: "Pantry", note: "Highest price volatility by CV. Tomato sauce saw –43% decline at Publix.", color: C.seafoam },
    { cat: "Household", note: "Most price-stable category overall. Dish soap CV < 3% at all retailers.", color: C.muted },
  ];
  insights.forEach((ins, i) => {
    const y = 2.12 + i * 0.82;
    s.addShape(pres.shapes.RECTANGLE, { x: 6.72, y, w: 0.07, h: 0.62, fill: { color: ins.color }, line: { color: ins.color } });
    s.addText(ins.cat, { x: 6.88, y: y + 0.02, w: 2.65, h: 0.24, fontSize: 12, bold: true, color: C.navy, fontFace: "Calibri", margin: 0 });
    s.addText(ins.note, { x: 6.88, y: y + 0.27, w: 2.65, h: 0.5, fontSize: 10.5, color: C.slate, fontFace: "Calibri", margin: 0 });
  });
}

// ─────────────────────────────────────────────
// SLIDE 7 — Price Volatility
// ─────────────────────────────────────────────
{
  const s = pres.addSlide();
  s.background = { color: C.cream };

  s.addShape(pres.shapes.RECTANGLE, { x: 0, y: 0, w: 10, h: 1.05, fill: { color: C.navy }, line: { color: C.navy } });
  s.addText("Price Volatility Analysis", { x: 0.4, y: 0.18, w: 9, h: 0.65, fontSize: 28, bold: true, color: C.white, fontFace: "Georgia", margin: 0 });

  s.addText("Coefficient of Variation (CV = std/mean) measures relative price stability across items and retailers.",
    { x: 0.4, y: 1.12, w: 9.2, h: 0.38, fontSize: 13, color: C.slate, fontFace: "Calibri" });

  // Overall CV big stats
  const cvStats = [
    { store: "Walmart", cv: "107.2%", label: "Most volatile overall", color: C.walmart },
    { store: "Publix", cv: "91.7%", label: "Moderate volatility", color: C.publix },
    { store: "Aldi", cv: "72.4%", label: "Most price-stable", color: C.aldi },
  ];
  cvStats.forEach((st, i) => {
    const x = 0.3 + i * 3.22;
    s.addShape(pres.shapes.RECTANGLE, { x, y: 1.58, w: 3.0, h: 1.5, fill: { color: C.white }, line: { color: "E2E8F0" }, shadow: makeShadow() });
    s.addShape(pres.shapes.RECTANGLE, { x, y: 1.58, w: 3.0, h: 0.07, fill: { color: st.color }, line: { color: st.color } });
    s.addText(st.store, { x: x + 0.12, y: 1.68, w: 2.76, h: 0.3, fontSize: 13, bold: true, color: C.navy, fontFace: "Calibri", align: "center" });
    s.addText(st.cv, { x: x + 0.12, y: 2.0, w: 2.76, h: 0.55, fontSize: 28, bold: true, color: st.color === C.walmart ? "B8860B" : st.color, fontFace: "Georgia", align: "center" });
    s.addText(st.label, { x: x + 0.12, y: 2.58, w: 2.76, h: 0.3, fontSize: 10.5, color: C.muted, fontFace: "Calibri", align: "center" });
  });

  // Category CV table
  s.addShape(pres.shapes.RECTANGLE, { x: 0.3, y: 3.2, w: 5.5, h: 2.15, fill: { color: C.white }, line: { color: "E2E8F0" }, shadow: makeShadow() });
  s.addShape(pres.shapes.RECTANGLE, { x: 0.3, y: 3.2, w: 5.5, h: 0.07, fill: { color: C.teal }, line: { color: C.teal } });
  s.addText("CV by Category & Retailer", { x: 0.48, y: 3.32, w: 5.15, h: 0.3, fontSize: 13, bold: true, color: C.navy, fontFace: "Calibri", margin: 0 });

  const cvTable = [
    [{ text: "Category", options: { bold: true, color: C.white } }, { text: "Aldi", options: { bold: true, color: C.white } }, { text: "Publix", options: { bold: true, color: C.white } }, { text: "Walmart", options: { bold: true, color: C.white } }],
    ["Produce", "64.2%", "70.1%", "77.5%"],
    ["Pantry", "39.4%", "32.9%", "43.3%"],
    ["Dairy", "25.0%", "13.9%", "16.8%"],
    ["Meat", "16.7%", "2.9%", "19.2%"],
    ["Household", "1.2%", "1.2%", "2.6%"],
  ];
  s.addTable(cvTable, {
    x: 0.3, y: 3.65, w: 5.5, h: 1.58,
    border: { pt: 0.5, color: "E2E8F0" },
    fill: { color: C.white },
    colW: [1.7, 1.27, 1.27, 1.26],
    rowH: 0.3,
    fontFace: "Calibri",
    fontSize: 12,
    align: "center",
    valign: "middle",
    autoPage: false,
  });
  s.addShape(pres.shapes.RECTANGLE, { x: 0.3, y: 3.65, w: 5.5, h: 0.3, fill: { color: C.slate }, line: { color: C.slate } });
  s.addText("Category         Aldi        Publix      Walmart", { x: 0.48, y: 3.65, w: 5.15, h: 0.3, fontSize: 11.5, bold: true, color: C.white, fontFace: "Calibri", valign: "middle", margin: 0 });

  // Noise vs shift callout
  s.addShape(pres.shapes.RECTANGLE, { x: 6.05, y: 3.2, w: 3.65, h: 2.15, fill: { color: C.white }, line: { color: "E2E8F0" }, shadow: makeShadow() });
  s.addShape(pres.shapes.RECTANGLE, { x: 6.05, y: 3.2, w: 3.65, h: 0.07, fill: { color: C.seafoam }, line: { color: C.seafoam } });
  s.addText("Volatility Types", { x: 6.22, y: 3.32, w: 3.3, h: 0.3, fontSize: 13, bold: true, color: C.navy, fontFace: "Calibri", margin: 0 });
  s.addText([
    { text: "Measurement Noise: ", options: { bold: true } },
    { text: "Frequent small jitter (Bananas CV 13.6%, 79 direction changes). Prices oscillate in a narrow band.", options: {} },
  ], { x: 6.22, y: 3.7, w: 3.3, h: 0.8, fontSize: 11.5, color: C.slate, fontFace: "Calibri" });
  s.addText([
    { text: "Structural Shift: ", options: { bold: true } },
    { text: "Discrete jumps (Salted Butter at Publix –37.2% total; Tomato Sauce –43.1%). Low direction changes, large single jump.", options: {} },
  ], { x: 6.22, y: 4.52, w: 3.3, h: 0.75, fontSize: 11.5, color: C.slate, fontFace: "Calibri" });
}

// ─────────────────────────────────────────────
// SLIDE 8 — Day-of-Week & Brand Analysis
// ─────────────────────────────────────────────
{
  const s = pres.addSlide();
  s.background = { color: C.cream };

  s.addShape(pres.shapes.RECTANGLE, { x: 0, y: 0, w: 10, h: 1.05, fill: { color: C.navy }, line: { color: C.navy } });
  s.addText("Day-of-Week Effect & Brand Analysis", { x: 0.4, y: 0.18, w: 9, h: 0.65, fontSize: 28, bold: true, color: C.white, fontFace: "Georgia", margin: 0 });

  // Day-of-week left
  s.addShape(pres.shapes.RECTANGLE, { x: 0.3, y: 1.2, w: 4.55, h: 4.15, fill: { color: C.white }, line: { color: "E2E8F0" }, shadow: makeShadow() });
  s.addShape(pres.shapes.RECTANGLE, { x: 0.3, y: 1.2, w: 4.55, h: 0.07, fill: { color: C.teal }, line: { color: C.teal } });
  s.addText("Day-of-Week Effect", { x: 0.48, y: 1.32, w: 4.2, h: 0.32, fontSize: 14, bold: true, color: C.navy, fontFace: "Calibri", margin: 0 });

  // Result callout
  s.addShape(pres.shapes.RECTANGLE, { x: 0.48, y: 1.72, w: 4.2, h: 0.85, fill: { color: C.cream }, line: { color: "E2E8F0" } });
  s.addText("Kruskal-Wallis Test", { x: 0.62, y: 1.78, w: 3.9, h: 0.25, fontSize: 11, bold: true, color: C.slate, fontFace: "Calibri", margin: 0 });
  s.addText("H = 0.30   p = 0.9995", { x: 0.62, y: 2.03, w: 3.9, h: 0.3, fontSize: 15, bold: true, color: C.navy, fontFace: "Calibri", margin: 0 });
  s.addText("✗  NOT significant at α = 0.05", { x: 0.62, y: 2.36, w: 3.9, h: 0.22, fontSize: 11, color: C.muted, fontFace: "Calibri", margin: 0 });

  s.addText("Per-store results:", { x: 0.48, y: 2.68, w: 4.2, h: 0.28, fontSize: 12, bold: true, color: C.navy, fontFace: "Calibri", margin: 0 });
  const perStore = [
    { name: "Aldi", h: "1.260", p: "0.9738", color: C.aldi },
    { name: "Publix", h: "0.934", p: "0.9880", color: C.publix },
    { name: "Walmart", h: "1.695", p: "0.9455", color: C.walmart },
  ];
  perStore.forEach((ps, i) => {
    const y = 3.02 + i * 0.48;
    s.addShape(pres.shapes.RECTANGLE, { x: 0.48, y, w: 0.07, h: 0.32, fill: { color: ps.color }, line: { color: ps.color } });
    s.addText(`${ps.name}:  H = ${ps.h}   p = ${ps.p}   ns`, { x: 0.62, y, w: 4.0, h: 0.32, fontSize: 12, color: C.slate, fontFace: "Calibri", valign: "middle", margin: 0 });
  });

  s.addShape(pres.shapes.RECTANGLE, { x: 0.48, y: 4.58, w: 4.2, h: 0.65, fill: { color: C.teal, transparency: 88 }, line: { color: C.teal, transparency: 50 } });
  s.addText("Grocery prices in this dataset do not vary systematically by day of week — there is no \"cheapest day\" to shop.",
    { x: 0.62, y: 4.62, w: 3.95, h: 0.58, fontSize: 11.5, color: C.navy, fontFace: "Calibri", italic: true });

  // Brand analysis right
  s.addShape(pres.shapes.RECTANGLE, { x: 5.15, y: 1.2, w: 4.55, h: 4.15, fill: { color: C.white }, line: { color: "E2E8F0" }, shadow: makeShadow() });
  s.addShape(pres.shapes.RECTANGLE, { x: 5.15, y: 1.2, w: 4.55, h: 0.07, fill: { color: C.seafoam }, line: { color: C.seafoam } });
  s.addText("Store Brand vs. National Brand", { x: 5.33, y: 1.32, w: 4.2, h: 0.32, fontSize: 14, bold: true, color: C.navy, fontFace: "Calibri", margin: 0 });

  const brandData = [
    { store: "Aldi", priv: 16.7, natl: 83.3, note: "Primarily National (via Instacart names)", color: C.aldi },
    { store: "Publix", priv: 80.0, natl: 20.0, note: "Primarily Private labels", color: C.publix },
    { store: "Walmart", priv: 0, natl: 100.0, note: "100% National in this dataset", color: C.walmart },
  ];
  brandData.forEach((bd, i) => {
    const y = 1.72 + i * 1.05;
    s.addText(bd.store, { x: 5.33, y, w: 1.5, h: 0.3, fontSize: 12, bold: true, color: C.navy, fontFace: "Calibri", margin: 0 });
    // Private bar
    const privW = (bd.priv / 100) * 3.6;
    const natlW = (bd.natl / 100) * 3.6;
    if (privW > 0) s.addShape(pres.shapes.RECTANGLE, { x: 5.33, y: y + 0.32, w: privW, h: 0.3, fill: { color: "4C72B0" }, line: { color: "4C72B0" } });
    if (natlW > 0) s.addShape(pres.shapes.RECTANGLE, { x: 5.33 + privW, y: y + 0.32, w: natlW, h: 0.3, fill: { color: "DD8452" }, line: { color: "DD8452" } });
    s.addText(`Private ${bd.priv}%  /  National ${bd.natl}%`, { x: 5.33, y: y + 0.64, w: 4.2, h: 0.25, fontSize: 10.5, color: C.muted, fontFace: "Calibri", margin: 0 });
    s.addText(bd.note, { x: 5.33, y: y + 0.82, w: 4.2, h: 0.22, fontSize: 10, color: C.slate, fontFace: "Calibri", italic: true, margin: 0 });
  });

  s.addShape(pres.shapes.RECTANGLE, { x: 5.33, y: 4.6, w: 4.2, h: 0.62, fill: { color: C.seafoam, transparency: 88 }, line: { color: C.seafoam, transparency: 50 } });
  s.addText("⚠ Caveat: Private-label items appear costlier only because they come primarily from Publix (priciest store) — this is a store effect, not a true brand premium.",
    { x: 5.45, y: 4.63, w: 4.0, h: 0.58, fontSize: 10.5, color: C.navy, fontFace: "Calibri" });
}

// ─────────────────────────────────────────────
// SLIDE 9 — Multi-Store Optimization
// ─────────────────────────────────────────────
{
  const s = pres.addSlide();
  s.background = { color: C.cream };

  s.addShape(pres.shapes.RECTANGLE, { x: 0, y: 0, w: 10, h: 1.05, fill: { color: C.navy }, line: { color: C.navy } });
  s.addText("Multi-Store Optimization", { x: 0.4, y: 0.18, w: 9, h: 0.65, fontSize: 28, bold: true, color: C.white, fontFace: "Georgia", margin: 0 });

  s.addText("Can shoppers save by cherry-picking the cheapest item from each store instead of shopping at one retailer?",
    { x: 0.4, y: 1.12, w: 9.2, h: 0.42, fontSize: 13, color: C.slate, fontFace: "Calibri" });

  // Big savings stat
  s.addShape(pres.shapes.RECTANGLE, { x: 0.3, y: 1.62, w: 9.4, h: 1.58, fill: { color: C.teal }, line: { color: C.teal } });
  s.addText("$6.20", { x: 0.5, y: 1.68, w: 4.2, h: 1.1, fontSize: 72, bold: true, color: C.white, fontFace: "Georgia", align: "center", valign: "middle", margin: 0 });
  s.addText("average daily savings from split-basket shopping\nvs. buying everything at the single cheapest store", { x: 4.8, y: 1.82, w: 4.7, h: 0.9, fontSize: 18, color: C.white, fontFace: "Calibri", valign: "middle" });
  s.addText("Max single-day savings: $7.12", { x: 4.8, y: 2.72, w: 4.7, h: 0.3, fontSize: 12, color: C.white, fontFace: "Calibri", italic: true });

  // Basket comparison
  const basket_compare = [
    { label: "Optimal (split) basket", val: "$26.35", color: C.danger },
    { label: "Best single store (Walmart)", val: "$32.95", color: C.walmart },
    { label: "Aldi full basket", val: "$33.16", color: C.aldi },
    { label: "Publix full basket", val: "$32.99", color: C.publix },
  ];
  basket_compare.forEach((b, i) => {
    const x = 0.3;
    const y = 3.38 + i * 0.5;
    const barW = (parseFloat(b.val.replace("$", "")) / 40) * 5.8;
    s.addText(b.label, { x, y, w: 3.3, h: 0.38, fontSize: 12, color: C.slate, fontFace: "Calibri", valign: "middle", margin: 0 });
    s.addShape(pres.shapes.RECTANGLE, { x: 3.65, y: y + 0.05, w: barW, h: 0.28, fill: { color: b.color }, line: { color: b.color } });
    s.addText(b.val, { x: 3.65 + barW + 0.1, y, w: 1.2, h: 0.38, fontSize: 12, bold: true, color: C.navy, fontFace: "Calibri", valign: "middle", margin: 0 });
  });

  s.addShape(pres.shapes.RECTANGLE, { x: 0.3, y: 5.27, w: 9.4, h: 0.2, fill: { color: C.cream }, line: { color: C.cream } });
  s.addText("Note: Savings assume the consumer can visit all three retailers — real-world feasibility depends on geography and time cost.",
    { x: 0.4, y: 5.27, w: 9.2, h: 0.25, fontSize: 10, color: C.muted, fontFace: "Calibri", italic: true });
}

// ─────────────────────────────────────────────
// SLIDE 10 — Price Forecasting
// ─────────────────────────────────────────────
{
  const s = pres.addSlide();
  s.background = { color: C.cream };

  s.addShape(pres.shapes.RECTANGLE, { x: 0, y: 0, w: 10, h: 1.05, fill: { color: C.navy }, line: { color: C.navy } });
  s.addText("Price Trend Forecasting", { x: 0.4, y: 0.18, w: 9, h: 0.65, fontSize: 28, bold: true, color: C.white, fontFace: "Georgia", margin: 0 });

  // R² summary
  s.addShape(pres.shapes.RECTANGLE, { x: 0.3, y: 1.18, w: 3.2, h: 4.18, fill: { color: C.white }, line: { color: "E2E8F0" }, shadow: makeShadow() });
  s.addShape(pres.shapes.RECTANGLE, { x: 0.3, y: 1.18, w: 3.2, h: 0.07, fill: { color: C.teal }, line: { color: C.teal } });
  s.addText("Linear Trend R² Summary", { x: 0.48, y: 1.3, w: 2.85, h: 0.32, fontSize: 13, bold: true, color: C.navy, fontFace: "Calibri", margin: 0 });

  const r2stats = [
    { label: "Mean R²", val: "0.153" },
    { label: "Median R²", val: "0.027" },
    { label: "R² > 0.3", val: "6 / 34" },
    { label: "R² < 0.05", val: "20 / 34" },
  ];
  r2stats.forEach((r, i) => {
    const y = 1.72 + i * 0.62;
    s.addShape(pres.shapes.RECTANGLE, { x: 0.48, y, w: 2.85, h: 0.52, fill: { color: C.cream }, line: { color: "E2E8F0" } });
    s.addText(r.label, { x: 0.6, y: y + 0.04, w: 2.6, h: 0.22, fontSize: 11, color: C.muted, fontFace: "Calibri", margin: 0 });
    s.addText(r.val, { x: 0.6, y: y + 0.24, w: 2.6, h: 0.25, fontSize: 14, bold: true, color: C.teal, fontFace: "Calibri", margin: 0 });
  });

  s.addText("Most grocery prices follow step-function patterns — flat for days or weeks, then a discrete jump — rather than smooth linear drift.",
    { x: 0.48, y: 4.2, w: 2.85, h: 0.95, fontSize: 11, color: C.slate, fontFace: "Calibri", italic: true });

  // Rising / Falling tables
  s.addShape(pres.shapes.RECTANGLE, { x: 3.75, y: 1.18, w: 6.0, h: 4.18, fill: { color: C.white }, line: { color: "E2E8F0" }, shadow: makeShadow() });
  s.addShape(pres.shapes.RECTANGLE, { x: 3.75, y: 1.18, w: 6.0, h: 0.07, fill: { color: C.seafoam }, line: { color: C.seafoam } });
  s.addText("Notable Price Trends", { x: 3.93, y: 1.3, w: 5.65, h: 0.32, fontSize: 13, bold: true, color: C.navy, fontFace: "Calibri", margin: 0 });

  s.addText("↑  Fastest Rising", { x: 3.93, y: 1.72, w: 5.65, h: 0.28, fontSize: 12, bold: true, color: C.danger, fontFace: "Calibri", margin: 0 });
  const rising = [
    { item: "Chicken Breast", store: "Walmart", chg: "+10.0%", slope: "+$0.16/wk", r2: "0.70" },
    { item: "Gala Apples", store: "Aldi", chg: "+23.1%", slope: "+$0.10/wk", r2: "0.95" },
    { item: "Ground Beef 80/20", store: "Walmart", chg: "+5.7%", slope: "+$0.07/wk", r2: "0.68" },
  ];
  rising.forEach((r, i) => {
    const y = 2.07 + i * 0.4;
    s.addShape(pres.shapes.RECTANGLE, { x: 3.93, y, w: 5.5, h: 0.34, fill: { color: i % 2 === 0 ? C.cream : C.white }, line: { color: "E2E8F0" } });
    s.addText(r.item, { x: 4.0, y: y + 0.04, w: 2.2, h: 0.26, fontSize: 11.5, color: C.slate, fontFace: "Calibri", margin: 0 });
    s.addText(r.store, { x: 6.2, y: y + 0.04, w: 1.0, h: 0.26, fontSize: 11, color: C.muted, fontFace: "Calibri", margin: 0 });
    s.addText(r.chg, { x: 7.2, y: y + 0.04, w: 0.9, h: 0.26, fontSize: 11.5, bold: true, color: C.danger, fontFace: "Calibri", margin: 0 });
    s.addText(`R²=${r.r2}`, { x: 8.1, y: y + 0.04, w: 1.2, h: 0.26, fontSize: 11, color: C.muted, fontFace: "Calibri", margin: 0 });
  });

  s.addShape(pres.shapes.LINE, { x: 3.93, y: 3.3, w: 5.5, h: 0, line: { color: "E2E8F0", width: 1 } });
  s.addText("↓  Fastest Falling", { x: 3.93, y: 3.38, w: 5.65, h: 0.28, fontSize: 12, bold: true, color: C.success, fontFace: "Calibri", margin: 0 });
  const falling = [
    { item: "Salted Butter", store: "Publix", chg: "–37.2%", slope: "–$0.25/wk", r2: "0.70" },
    { item: "Tomato Sauce", store: "Publix", chg: "–43.1%", slope: "–$0.05/wk", r2: "0.07" },
    { item: "Chicken Breast", store: "Aldi", chg: "0.0%", slope: "–$0.04/wk", r2: "0.30" },
  ];
  falling.forEach((r, i) => {
    const y = 3.73 + i * 0.4;
    s.addShape(pres.shapes.RECTANGLE, { x: 3.93, y, w: 5.5, h: 0.34, fill: { color: i % 2 === 0 ? C.cream : C.white }, line: { color: "E2E8F0" } });
    s.addText(r.item, { x: 4.0, y: y + 0.04, w: 2.2, h: 0.26, fontSize: 11.5, color: C.slate, fontFace: "Calibri", margin: 0 });
    s.addText(r.store, { x: 6.2, y: y + 0.04, w: 1.0, h: 0.26, fontSize: 11, color: C.muted, fontFace: "Calibri", margin: 0 });
    s.addText(r.chg, { x: 7.2, y: y + 0.04, w: 0.9, h: 0.26, fontSize: 11.5, bold: true, color: C.success, fontFace: "Calibri", margin: 0 });
    s.addText(`R²=${r.r2}`, { x: 8.1, y: y + 0.04, w: 1.2, h: 0.26, fontSize: 11, color: C.muted, fontFace: "Calibri", margin: 0 });
  });
}

// ─────────────────────────────────────────────
// SLIDE 11 — Summary of Findings
// ─────────────────────────────────────────────
{
  const s = pres.addSlide();
  s.background = { color: C.cream };

  s.addShape(pres.shapes.RECTANGLE, { x: 0, y: 0, w: 10, h: 1.05, fill: { color: C.navy }, line: { color: C.navy } });
  s.addText("Summary of Findings", { x: 0.4, y: 0.18, w: 9, h: 0.65, fontSize: 28, bold: true, color: C.white, fontFace: "Georgia", margin: 0 });

  const findings = [
    { num: "1", title: "Retailer Effect", body: "Statistically SIGNIFICANT (Friedman χ²=17.08, p<0.001). Aldi $33.16, Publix $32.99, Walmart $32.95 — only Aldi vs Walmart difference holds post-hoc.", color: C.teal },
    { num: "2", title: "Category Interaction", body: "Retailer effect is significant in ALL 5 categories. Meat has the largest spread ($5.58). Line patterns cross between stores, confirming no single cheapest retailer for all goods.", color: C.seafoam },
    { num: "3", title: "Price Volatility", body: "Walmart most volatile overall (CV 107%). Produce most volatile by category; Household most stable. All top volatile items classified as measurement noise, not structural shifts.", color: C.aldi },
    { num: "4", title: "Day-of-Week", body: "NOT significant (H=0.30, p=0.9995). There is no cheapest day to shop at any of the three retailers.", color: C.publix },
    { num: "5", title: "Multi-Store Savings", body: "Split-basket shopping saves an average of $6.20/day vs. the best single store, with a max of $7.12. Walmart wins most items most often.", color: C.danger },
    { num: "6", title: "Forecasting", body: "Most prices (20/34) have R² < 0.05 — groceries follow step-function pricing, not linear trends. Change-point detection or ARIMA would improve future forecasts.", color: C.slate },
  ];

  findings.forEach((f, i) => {
    const col = i % 2;
    const row = Math.floor(i / 2);
    const x = 0.3 + col * 4.85;
    const y = 1.18 + row * 1.5;
    s.addShape(pres.shapes.RECTANGLE, { x, y, w: 4.6, h: 1.38, fill: { color: C.white }, line: { color: "E2E8F0" }, shadow: makeShadow() });
    s.addShape(pres.shapes.RECTANGLE, { x, y, w: 0.07, h: 1.38, fill: { color: f.color }, line: { color: f.color } });
    s.addText(`${f.num}. ${f.title}`, { x: x + 0.2, y: y + 0.1, w: 4.25, h: 0.3, fontSize: 13, bold: true, color: C.navy, fontFace: "Calibri", margin: 0 });
    s.addText(f.body, { x: x + 0.2, y: y + 0.42, w: 4.25, h: 0.9, fontSize: 11, color: C.slate, fontFace: "Calibri", valign: "top" });
  });
}

// ─────────────────────────────────────────────
// SLIDE 12 — Closing / Next Steps
// ─────────────────────────────────────────────
{
  const s = pres.addSlide();
  s.background = { color: C.navy };

  s.addShape(pres.shapes.OVAL, { x: -1.5, y: 3.5, w: 6, h: 6, fill: { color: C.teal, transparency: 88 }, line: { color: C.teal, transparency: 80 } });
  s.addShape(pres.shapes.OVAL, { x: 7.5, y: -1.5, w: 5, h: 5, fill: { color: C.seafoam, transparency: 90 }, line: { color: C.seafoam, transparency: 85 } });

  s.addText("CONCLUSIONS & NEXT STEPS", { x: 0.6, y: 0.7, w: 8.8, h: 0.4, fontSize: 12, bold: true, color: C.teal, charSpacing: 5, fontFace: "Calibri" });
  s.addText("What We Learned", { x: 0.6, y: 1.12, w: 8.8, h: 0.75, fontSize: 36, bold: true, color: C.white, fontFace: "Georgia" });

  s.addShape(pres.shapes.LINE, { x: 0.6, y: 1.95, w: 4, h: 0, line: { color: C.teal, width: 1.5 } });

  const bullets = [
    "All three retailers are within $0.21 of each other on total basket cost — but category-level divergences are dramatic",
    "Meat is the highest-leverage category for savvy shoppers — a $5.58 spread per grocery trip",
    "There is no statistically meaningful day-of-week pricing effect across any retailer",
    "Split-basket optimization yields ~$6.20/day savings; Walmart wins most individual items",
    "Grocery prices are step-functions, not trends — future modeling should use change-point detection",
  ];
  bullets.forEach((b, i) => {
    s.addText([{ text: b, options: { bullet: true } }], {
      x: 0.6, y: 2.12 + i * 0.55, w: 8.8, h: 0.5, fontSize: 13, color: i < 2 ? C.teal : C.white, fontFace: "Calibri"
    });
  });

  s.addText("Data: Feb 3 – Mar 11, 2026  ·  Aldi · Publix · Walmart  ·  12 items  ·  1,258 observations",
    { x: 0.6, y: 5.25, w: 9, h: 0.28, fontSize: 10, color: C.muted, fontFace: "Calibri" });
}

pres.writeFile({ fileName: "SmartGrocer_Analysis.pptx" });
console.log("Done");