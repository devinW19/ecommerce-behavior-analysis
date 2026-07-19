"""
data_loader.py — Loads both CSVs once at import time and pre-computes
                 all aggregations used by the dashboard charts.
"""

import os
import pandas as pd
import numpy as np

DATA_DIR = os.path.join(os.path.dirname(__file__), '..', 'data')

# ── Country name normalisation (for choropleth compatibility) ──────────────
_COUNTRY_FIX = {
    'EIRE': 'Ireland',
    'RSA': 'South Africa',
    'Channel Islands': 'United Kingdom',
    'Unspecified': None,
}


def _load_txn() -> pd.DataFrame:
    print('[data_loader] Loading transaction data...')
    df = pd.read_csv(
        os.path.join(DATA_DIR, 'cleaned_retail_data.csv'),
        dtype={
            'Invoice': str,
            'StockCode': str,
            'Description': str,
            'Quantity': 'int32',
            'Price': 'float32',
            'Customer ID': 'float32',
            'Country': str,
            'TotalSum': 'float32',
        },
        low_memory=False,
    )
    df['InvoiceDate'] = pd.to_datetime(df['InvoiceDate'])
    df['Month']      = df['InvoiceDate'].dt.to_period('M').dt.to_timestamp()
    df['Week']       = df['InvoiceDate'].dt.to_period('W').dt.to_timestamp()
    df['Date']       = df['InvoiceDate'].dt.normalize()
    df['DayOfWeek']  = df['InvoiceDate'].dt.dayofweek   # 0=Mon … 6=Sun
    df['Hour']       = df['InvoiceDate'].dt.hour
    df['Country_Clean'] = df['Country'].map(lambda c: _COUNTRY_FIX.get(c, c))
    print(f'[data_loader] Loaded {len(df):,} transactions')
    return df


def _load_rfm() -> pd.DataFrame:
    print('[data_loader] Loading RFM data...')
    rfm = pd.read_csv(os.path.join(DATA_DIR, 'rfm_segments.csv'))
    rfm['Segment Label'] = (
        rfm['segment']
        .str.replace('_', ' ', regex=False)
        .str.title()
        .str.replace('Cant Loose', "Can't Lose")
    )
    print(f'[data_loader] Loaded {len(rfm):,} customers')
    return rfm


# ── Raw DataFrames ─────────────────────────────────────────────────────────
TXN: pd.DataFrame = _load_txn()
RFM: pd.DataFrame = _load_rfm()

# ── KPIs ───────────────────────────────────────────────────────────────────
TOTAL_REVENUE   = float(TXN['TotalSum'].sum())
TOTAL_ORDERS    = int(TXN['Invoice'].nunique())
TOTAL_CUSTOMERS = int(TXN['Customer ID'].nunique())
AVG_ORDER_VALUE = TOTAL_REVENUE / TOTAL_ORDERS

# ── Time series ────────────────────────────────────────────────────────────
MONTHLY: pd.DataFrame = (
    TXN.groupby('Month')['TotalSum'].sum()
    .reset_index().rename(columns={'TotalSum': 'Revenue'})
)
WEEKLY: pd.DataFrame = (
    TXN.groupby('Week')['TotalSum'].sum()
    .reset_index().rename(columns={'TotalSum': 'Revenue'})
)
DAILY: pd.DataFrame = (
    TXN.groupby('Date')['TotalSum'].sum()
    .reset_index().rename(columns={'TotalSum': 'Revenue'})
)

# ── Products ───────────────────────────────────────────────────────────────
TOP_PRODUCTS_REV: pd.DataFrame = (
    TXN.groupby('Description')['TotalSum'].sum()
    .nlargest(20).reset_index()
    .rename(columns={'TotalSum': 'Revenue'})
)
TOP_PRODUCTS_QTY: pd.DataFrame = (
    TXN.groupby('Description')['Quantity'].sum()
    .nlargest(20).reset_index()
)

# ── Countries ──────────────────────────────────────────────────────────────
COUNTRY_REV: pd.DataFrame = (
    TXN[TXN['Country_Clean'].notna()]
    .groupby('Country_Clean')['TotalSum'].sum()
    .reset_index()
    .rename(columns={'Country_Clean': 'Country', 'TotalSum': 'Revenue'})
    .sort_values('Revenue', ascending=False)
)

UK_REVENUE    = float(COUNTRY_REV.loc[COUNTRY_REV['Country'] == 'United Kingdom', 'Revenue'].sum())
INTL_REVENUE  = TOTAL_REVENUE - UK_REVENUE
NUM_COUNTRIES = len(COUNTRY_REV)

# ── Segments ───────────────────────────────────────────────────────────────
SEGMENT_STATS: pd.DataFrame = (
    RFM.groupby('Segment Label').agg(
        Customers=('Customer ID', 'count'),
        Avg_Recency=('Recency', 'mean'),
        Avg_Frequency=('Frequency', 'mean'),
        Avg_Monetary=('Monetary', 'mean'),
        Total_Revenue=('Monetary', 'sum'),
    )
    .reset_index()
    .round(2)
    .sort_values('Total_Revenue', ascending=False)
)

# ── Heatmap pivot ──────────────────────────────────────────────────────────
_heatmap_raw = (
    TXN.groupby(['DayOfWeek', 'Hour'])['Invoice']
    .count().reset_index()
    .rename(columns={'Invoice': 'Orders'})
)
HEATMAP_PIVOT: pd.DataFrame = (
    _heatmap_raw
    .pivot(index='DayOfWeek', columns='Hour', values='Orders')
    .reindex(range(7))
    .fillna(0)
)
DAY_NAMES = ['Mon', 'Tue', 'Wed', 'Thu', 'Fri', 'Sat', 'Sun']

print('[data_loader] All aggregations ready -- dashboard starting...')
