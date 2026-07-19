"""
figures.py — Plotly chart factory functions.
All figures share a consistent dark theme with transparent backgrounds so
they blend seamlessly with the card containers in custom.css.
"""

import plotly.graph_objects as go
import plotly.express as px
from dashboard import data_loader as dl

# ── Colour palette ─────────────────────────────────────────────────────────
ACCENT   = '#818cf8'   # indigo-400
SUCCESS  = '#34d399'   # emerald-400
WARNING  = '#fbbf24'   # amber-400
DANGER   = '#f87171'   # red-400
PINK     = '#f472b6'   # pink-400

SEG_COLORS: dict[str, str] = {
    'Champions':           '#f59e0b',
    'Loyal Customers':     '#10b981',
    'Potential Loyalists': '#3b82f6',
    'New Customers':       '#8b5cf6',
    'Promising':           '#06b6d4',
    'Need Attention':      '#f97316',
    'About To Sleep':      '#6b7280',
    'At Risk':             '#ef4444',
    "Can't Lose":          '#dc2626',
    'Hibernating':         '#374151',
}

# ── Shared layout defaults ─────────────────────────────────────────────────
_FONT   = dict(family='Inter, system-ui, sans-serif', color='#cbd5e1', size=12)
_TITLE  = dict(font=dict(size=15, color='#e2e8f0', family='Inter, system-ui, sans-serif'),
               x=0, xanchor='left', pad=dict(l=0))
_LEGEND = dict(bgcolor='rgba(0,0,0,0)', font=dict(color='#94a3b8', size=11),
               bordercolor='rgba(0,0,0,0)')
_XAXIS  = dict(gridcolor='rgba(148,163,184,0.07)', showgrid=True,
               zeroline=False, tickfont=dict(color='#64748b', size=11),
               linecolor='rgba(148,163,184,0.12)')
_YAXIS  = dict(gridcolor='rgba(148,163,184,0.07)', showgrid=True,
               zeroline=False, tickfont=dict(color='#64748b', size=11),
               linecolor='rgba(148,163,184,0.12)')


def _base_layout(**overrides) -> go.Layout:
    props = dict(
        paper_bgcolor='rgba(0,0,0,0)',
        plot_bgcolor='rgba(0,0,0,0)',
        font=_FONT,
        margin=dict(l=48, r=24, t=52, b=40),
        legend=_LEGEND,
        xaxis=_XAXIS,
        yaxis=_YAXIS,
        hoverlabel=dict(
            bgcolor='#1e293b',
            bordercolor='#334155',
            font=dict(color='#e2e8f0', size=12, family='Inter, sans-serif'),
        ),
    )
    props.update(overrides)
    return go.Layout(**props)


# ── 1. Revenue Trend ───────────────────────────────────────────────────────

def fig_revenue_trend(freq: str = 'M') -> go.Figure:
    """Line chart of revenue over time. freq: 'D' | 'W' | 'M'"""
    mapping = {'D': dl.DAILY, 'W': dl.WEEKLY, 'M': dl.MONTHLY}
    df = mapping.get(freq, dl.MONTHLY)
    period_col = df.columns[0]

    fig = go.Figure(layout=_base_layout(
        title=dict(text='Revenue Over Time', **{k: v for k, v in _TITLE.items() if k != 'text'}),
        yaxis=dict(**_YAXIS, tickprefix='£', tickformat=',.0f'),
        hovermode='x unified',
    ))

    fig.add_trace(go.Scatter(
        x=df[period_col],
        y=df['Revenue'],
        mode='lines',
        line=dict(color=ACCENT, width=2.5, shape='spline', smoothing=0.8),
        fill='tozeroy',
        fillcolor='rgba(129,140,248,0.10)',
        name='Revenue',
        hovertemplate='£%{y:,.0f}<extra></extra>',
    ))
    return fig


# ── 2. RFM Treemap ─────────────────────────────────────────────────────────

def fig_rfm_treemap() -> go.Figure:
    df = dl.SEGMENT_STATS.copy()
    colors = [SEG_COLORS.get(s, '#6b7280') for s in df['Segment Label']]

    fig = go.Figure(go.Treemap(
        labels=df['Segment Label'],
        parents=[''] * len(df),
        values=df['Customers'],
        customdata=df[['Total_Revenue', 'Avg_Monetary']].values,
        texttemplate='<b>%{label}</b><br>%{value} customers',
        hovertemplate=(
            '<b>%{label}</b><br>'
            'Customers: %{value:,}<br>'
            'Total Revenue: £%{customdata[0]:,.0f}<br>'
            'Avg CLV: £%{customdata[1]:,.0f}'
            '<extra></extra>'
        ),
        marker=dict(
            colors=colors,
            line=dict(width=2, color='#0f172a'),
            pad=dict(t=20, l=4, r=4, b=4),
        ),
        textfont=dict(family='Inter, sans-serif', size=13, color='white'),
        tiling=dict(packing='squarify'),
    ))
    fig.update_layout(
        paper_bgcolor='rgba(0,0,0,0)',
        plot_bgcolor='rgba(0,0,0,0)',
        font=_FONT,
        title=dict(text='Customer Segment Distribution', **{k: v for k, v in _TITLE.items() if k != 'text'}),
        margin=dict(l=0, r=0, t=48, b=0),
        hoverlabel=dict(bgcolor='#1e293b', bordercolor='#334155',
                        font=dict(color='#e2e8f0', size=12)),
    )
    return fig


# ── 3. RFM Scatter ─────────────────────────────────────────────────────────

def fig_rfm_scatter() -> go.Figure:
    rfm = dl.RFM.copy()
    rfm['size_val'] = rfm['Monetary'].clip(lower=1) ** 0.38
    rfm['size_val'] = rfm['size_val'].clip(3, 18)

    fig = go.Figure(layout=_base_layout(
        title=dict(text='Recency vs Frequency by Segment',
                   **{k: v for k, v in _TITLE.items() if k != 'text'}),
        xaxis=dict(**_XAXIS, title='Recency (days since last purchase)'),
        yaxis=dict(**_YAXIS, title='Frequency (orders)'),
        margin=dict(l=64, r=40, t=52, b=52),
    ))

    for seg, grp in rfm.groupby('Segment Label'):
        fig.add_trace(go.Scatter(
            x=grp['Recency'],
            y=grp['Frequency'],
            mode='markers',
            name=seg,
            marker=dict(
                color=SEG_COLORS.get(seg, '#6b7280'),
                size=grp['size_val'],
                opacity=0.72,
                line=dict(width=0.4, color='rgba(255,255,255,0.15)'),
            ),
            customdata=grp['Monetary'].values,
            hovertemplate=(
                f'<b>{seg}</b><br>'
                'Recency: %{x}d<br>'
                'Frequency: %{y} orders<br>'
                'CLV: £%{customdata:,.0f}'
                '<extra></extra>'
            ),
        ))
    return fig


# ── 4. Segment Revenue Bar ─────────────────────────────────────────────────

def fig_segment_revenue() -> go.Figure:
    df = dl.SEGMENT_STATS.sort_values('Total_Revenue')
    colors = [SEG_COLORS.get(s, '#6b7280') for s in df['Segment Label']]

    fig = go.Figure(go.Bar(
        x=df['Total_Revenue'],
        y=df['Segment Label'],
        orientation='h',
        marker=dict(color=colors, opacity=0.9,
                    line=dict(width=0, color='rgba(0,0,0,0)')),
        text=df['Total_Revenue'].apply(lambda v: f'£{v/1000:.0f}K'),
        textposition='outside',
        textfont=dict(color='#94a3b8', size=11),
        hovertemplate='<b>%{y}</b><br>Revenue: £%{x:,.0f}<extra></extra>',
    ))
    fig.update_layout(_base_layout(
        title=dict(text='Revenue by Segment',
                   **{k: v for k, v in _TITLE.items() if k != 'text'}),
        xaxis=dict(**_XAXIS, tickprefix='£', tickformat=',.0f'),
        margin=dict(l=140, r=80, t=52, b=40),
    ))
    return fig


# ── 5. Top Products by Revenue ─────────────────────────────────────────────

def fig_top_products_revenue() -> go.Figure:
    df = dl.TOP_PRODUCTS_REV.sort_values('Revenue')

    fig = go.Figure(go.Bar(
        x=df['Revenue'],
        y=df['Description'],
        orientation='h',
        marker=dict(
            color=df['Revenue'],
            colorscale=[[0, '#312e81'], [0.5, '#6366f1'], [1, '#a5b4fc']],
            showscale=False,
            opacity=0.9,
        ),
        hovertemplate='<b>%{y}</b><br>Revenue: £%{x:,.0f}<extra></extra>',
    ))
    fig.update_layout(_base_layout(
        title=dict(text='Top 20 Products by Revenue',
                   **{k: v for k, v in _TITLE.items() if k != 'text'}),
        xaxis=dict(**_XAXIS, tickprefix='£', tickformat=',.0f'),
        height=580,
        margin=dict(l=260, r=40, t=52, b=40),
    ))
    return fig


# ── 6. Top Products by Quantity ────────────────────────────────────────────

def fig_top_products_qty() -> go.Figure:
    df = dl.TOP_PRODUCTS_QTY.sort_values('Quantity')

    fig = go.Figure(go.Bar(
        x=df['Quantity'],
        y=df['Description'],
        orientation='h',
        marker=dict(
            color=df['Quantity'],
            colorscale=[[0, '#064e3b'], [0.5, '#10b981'], [1, '#6ee7b7']],
            showscale=False,
            opacity=0.9,
        ),
        hovertemplate='<b>%{y}</b><br>Units Sold: %{x:,}<extra></extra>',
    ))
    fig.update_layout(_base_layout(
        title=dict(text='Top 20 Products by Units Sold',
                   **{k: v for k, v in _TITLE.items() if k != 'text'}),
        xaxis=dict(**_XAXIS, tickformat=','),
        height=580,
        margin=dict(l=260, r=40, t=52, b=40),
    ))
    return fig


# ── 7. Choropleth World Map ────────────────────────────────────────────────

def fig_choropleth() -> go.Figure:
    df = dl.COUNTRY_REV.copy()

    fig = px.choropleth(
        df,
        locations='Country',
        locationmode='country names',
        color='Revenue',
        color_continuous_scale='Plasma',
        hover_name='Country',
        hover_data={'Revenue': ':,.0f', 'Country': False},
    )
    fig.update_traces(
        hovertemplate='<b>%{hovertext}</b><br>Revenue: £%{z:,.0f}<extra></extra>',
    )
    fig.update_layout(
        paper_bgcolor='rgba(0,0,0,0)',
        font=_FONT,
        title=dict(text='Revenue by Country',
                   **{k: v for k, v in _TITLE.items() if k != 'text'}),
        geo=dict(
            bgcolor='rgba(0,0,0,0)',
            showframe=False,
            showcoastlines=True,
            coastlinecolor='rgba(148,163,184,0.15)',
            landcolor='#1e293b',
            oceancolor='#0f172a',
            showocean=True,
            showland=True,
            projection_type='natural earth',
            showlakes=False,
        ),
        coloraxis_colorbar=dict(
            tickprefix='£',
            tickformat=',.0f',
            tickfont=dict(color='#94a3b8', size=10),
            title=dict(text='Revenue', font=dict(color='#94a3b8', size=11)),
            thickness=12,
            len=0.7,
        ),
        margin=dict(l=0, r=0, t=48, b=0),
        hoverlabel=dict(bgcolor='#1e293b', bordercolor='#334155',
                        font=dict(color='#e2e8f0', size=12)),
    )
    return fig


# ── 8. Country Leaderboard Bar ────────────────────────────────────────────

def fig_country_bar(top_n: int = 12) -> go.Figure:
    df = dl.COUNTRY_REV.head(top_n).sort_values('Revenue')

    fig = go.Figure(go.Bar(
        x=df['Revenue'],
        y=df['Country'],
        orientation='h',
        marker=dict(
            color=df['Revenue'],
            colorscale=[[0, '#4c0519'], [0.5, '#e11d48'], [1, '#fb7185']],
            showscale=False,
            opacity=0.9,
        ),
        hovertemplate='<b>%{y}</b><br>Revenue: £%{x:,.0f}<extra></extra>',
    ))
    fig.update_layout(_base_layout(
        title=dict(text=f'Top {top_n} Countries by Revenue',
                   **{k: v for k, v in _TITLE.items() if k != 'text'}),
        xaxis=dict(**_XAXIS, tickprefix='£', tickformat=',.0f'),
        margin=dict(l=130, r=24, t=52, b=40),
        height=420,
    ))
    return fig


# ── 9. Order Volume Heatmap ────────────────────────────────────────────────

def fig_order_heatmap() -> go.Figure:
    pivot = dl.HEATMAP_PIVOT

    fig = go.Figure(go.Heatmap(
        z=pivot.values,
        x=[f'{h:02d}:00' for h in range(24)],
        y=dl.DAY_NAMES,
        colorscale='Viridis',
        hovertemplate='%{y} %{x}<br>Orders: %{z:,}<extra></extra>',
        colorbar=dict(
            tickfont=dict(color='#94a3b8', size=10),
            title=dict(text='Orders', font=dict(color='#94a3b8', size=11)),
            thickness=12,
        ),
        xgap=1,
        ygap=1,
    ))
    fig.update_layout(
        paper_bgcolor='rgba(0,0,0,0)',
        plot_bgcolor='rgba(0,0,0,0)',
        font=_FONT,
        title=dict(text='Order Volume — Day of Week × Hour of Day',
                   **{k: v for k, v in _TITLE.items() if k != 'text'}),
        xaxis=dict(side='bottom', tickfont=dict(color='#64748b', size=10),
                   gridcolor='rgba(0,0,0,0)', linecolor='rgba(0,0,0,0)'),
        yaxis=dict(tickfont=dict(color='#64748b', size=11),
                   gridcolor='rgba(0,0,0,0)', linecolor='rgba(0,0,0,0)'),
        margin=dict(l=48, r=16, t=52, b=40),
        height=320,
        hoverlabel=dict(bgcolor='#1e293b', bordercolor='#334155',
                        font=dict(color='#e2e8f0', size=12)),
    )
    return fig
