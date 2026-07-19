# E-Commerce Behavior Analysis

An end-to-end data analysis and business intelligence project built on the **Online Retail II** dataset. The project cleans 1M+ rows of raw transaction data, performs RFM customer segmentation, and surfaces insights through an interactive business dashboard.

---

## The Problem

Raw e-commerce data is noisy — full of cancellations, missing customer IDs, and negative quantities — making it difficult to identify loyal, high-value customers and act on them.

## The Solution

A Python pipeline that:
1. **Cleans** 1.04 million rows down to 407,664 valid transactions
2. **Engineers** RFM (Recency, Frequency, Monetary) features per customer
3. **Segments** 4,312 customers into 10 actionable behavioural groups
4. **Visualises** all insights in an interactive BI dashboard

---

## Business Dashboard

An interactive **Plotly Dash** dashboard with 5 sections:

| Section | What it shows |
|---|---|
| **Executive Overview** | Total revenue (£8.83M), orders, customers, AOV, monthly trend, top countries |
| **RFM Segmentation** | Treemap, scatter plot, revenue-by-segment bar, segment health table |
| **Product Performance** | Top 20 products by revenue and units sold |
| **Geographic Analysis** | Choropleth world map, country leaderboard across 37 markets |
| **Time Trends** | Daily / Weekly / Monthly revenue toggle, order volume heatmap |

### Run the dashboard

```bash
# 1. Create and activate virtual environment
python -m venv venv
venv\Scripts\activate        # Windows
# source venv/bin/activate   # macOS / Linux

# 2. Install dependencies
pip install -r requirements_dashboard.txt

# 3. Launch
python dashboard/app.py
```

Open **http://127.0.0.1:8050** in your browser.

---

## Project Structure

```
ecommerce-behavior-analysis/
├── data/
│   ├── online_retail_II.xlsx        # Raw source data (UCI / Kaggle)
│   ├── cleaned_retail_data.csv      # 407,664 cleaned transactions
│   └── rfm_segments.csv             # 4,312 customers with RFM scores & labels
├── notebooks/
│   └── 01_data_cleaning.ipynb       # Data cleaning & RFM segmentation pipeline
├── dashboard/
│   ├── _app.py                      # Dash application instance
│   ├── data_loader.py               # CSV loading & all pre-computed aggregations
│   ├── figures.py                   # Plotly chart factory functions (9 charts)
│   ├── layout.py                    # Full sidebar layout & 5 section renderers
│   ├── callbacks.py                 # Interactive callbacks (navigation, filters)
│   ├── app.py                       # Entry point
│   └── assets/
│       └── custom.css               # Dark-mode brand stylesheet
├── requirements_dashboard.txt
├── .gitignore
└── README.md
```

---

## Dataset

- **Source:** [Online Retail II — UCI Machine Learning Repository](https://archive.ics.uci.edu/dataset/502/online+retail+ii)
- **Period:** December 2009 – December 2010
- **Geography:** United Kingdom (primary) + 36 international markets
- **Raw size:** ~1.04 million rows

---

## RFM Segments

Customers are scored 1–5 on Recency, Frequency, and Monetary value, then mapped to 10 segments:

| Segment | Description |
|---|---|
| **Champions** | Bought recently, buy often, spend the most |
| **Loyal Customers** | Buy regularly with high spend |
| **Potential Loyalists** | Recent customers with growing frequency |
| **New Customers** | Bought very recently for the first time |
| **Promising** | Recent shoppers, not yet frequent |
| **Need Attention** | Above-average recency, frequency & monetary — fading |
| **About to Sleep** | Below-average recency — may be losing interest |
| **At Risk** | Used to buy often but haven't returned |
| **Can't Lose** | Used to buy very frequently but gone a long time |
| **Hibernating** | Low recency, frequency, and monetary |

---

## Tech Stack

| Layer | Tools |
|---|---|
| Language | Python 3.13 |
| Data | Pandas, NumPy |
| Visualisation | Plotly, Plotly Express |
| Dashboard | Plotly Dash, Dash Bootstrap Components |
| Notebook | Jupyter |
| Version Control | Git / GitHub |
