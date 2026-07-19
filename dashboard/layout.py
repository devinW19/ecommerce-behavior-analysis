"""
layout.py — Full Dash layout: sidebar, topbar, and five content sections.
"""

from __future__ import annotations

from dash import html, dcc
import dash_bootstrap_components as dbc

from dashboard import data_loader as dl
from dashboard import figures as figs


# ── Formatting helpers ─────────────────────────────────────────────────────

def _fmt_currency(v: float) -> str:
    if v >= 1_000_000:
        return f'£{v / 1_000_000:.2f}M'
    if v >= 1_000:
        return f'£{v / 1_000:.1f}K'
    return f'£{v:,.0f}'


def _fmt_number(v: float) -> str:
    if v >= 1_000_000:
        return f'{v / 1_000_000:.2f}M'
    if v >= 1_000:
        return f'{v / 1_000:.1f}K'
    return f'{int(v):,}'


# ── KPI card component ────────────────────────────────────────────────────

def _kpi_card(
    title: str, value: str, icon: str, color: str, subtitle: str = ''
) -> dbc.Col:
    return dbc.Col(
        dbc.Card(
            dbc.CardBody([
                html.Div([
                    html.Div(
                        html.Span(className=f'fa {icon} kpi-icon',
                                  style={'color': color}),
                        className='kpi-icon-wrap',
                        style={'backgroundColor': f'{color}20'},
                    ),
                    html.Div([
                        html.P(title, className='kpi-label'),
                        html.H3(value, className='kpi-value'),
                        html.P(subtitle, className='kpi-subtitle'),
                    ], className='kpi-text'),
                ], className='kpi-inner'),
            ]),
            className='kpi-card',
        ),
        xs=12, sm=6, lg=3,
    )


# ── Sidebar ────────────────────────────────────────────────────────────────

_NAV_ITEMS = [
    ('overview', 'fa-chart-bar',   'Executive Overview'),
    ('rfm',      'fa-users',       'RFM Segmentation'),
    ('products', 'fa-box',         'Product Performance'),
    ('geo',      'fa-globe',       'Geographic Analysis'),
    ('trends',   'fa-chart-line',  'Time Trends'),
]

PAGES = [key for key, *_ in _NAV_ITEMS]

_sidebar = html.Div([
    # Brand
    html.Div([
        html.Span(className='fa fa-chart-pie sidebar-logo-icon'),
        html.Div([
            html.P('E-Commerce', className='sidebar-brand-main'),
            html.P('Intelligence', className='sidebar-brand-sub'),
        ]),
    ], className='sidebar-brand'),

    html.Hr(className='sidebar-divider'),

    # Navigation links
    html.Nav([
        html.A(
            [html.Span(className=f'fa {icon}'), html.Span(label)],
            id=f'nav-{key}',
            href='#',
            className='sidebar-nav-item' + (' active' if key == 'overview' else ''),
        )
        for key, icon, label in _NAV_ITEMS
    ], className='sidebar-nav'),

    html.Hr(className='sidebar-divider'),

    # Dataset metadata
    html.Div([
        html.P('Dataset',          className='sidebar-meta-label'),
        html.P('Online Retail II', className='sidebar-meta-value'),
        html.P('Period',                       className='sidebar-meta-label'),
        html.P('Dec 2009 – Dec 2010',          className='sidebar-meta-value'),
        html.P('Transactions',                 className='sidebar-meta-label'),
        html.P(f'{dl.TXN.shape[0]:,} rows',   className='sidebar-meta-value'),
        html.P('Customers',                    className='sidebar-meta-label'),
        html.P(f'{dl.TOTAL_CUSTOMERS:,}',      className='sidebar-meta-value'),
    ], className='sidebar-meta'),
], id='sidebar', className='sidebar')


# ── Section: Executive Overview ────────────────────────────────────────────

def overview_layout() -> html.Div:
    return html.Div([
        html.Div([
            html.H2('Executive Overview', className='section-title'),
            html.P(
                'Key performance indicators and revenue trends for the full analysis period.',
                className='section-subtitle',
            ),
        ], className='section-header'),

        dbc.Row([
            _kpi_card('Total Revenue',    _fmt_currency(dl.TOTAL_REVENUE),   'fa-sterling-sign', '#818cf8', 'Dec 2009 – Dec 2010'),
            _kpi_card('Total Orders',     _fmt_number(dl.TOTAL_ORDERS),      'fa-receipt',       '#34d399', 'Unique invoices'),
            _kpi_card('Unique Customers', _fmt_number(dl.TOTAL_CUSTOMERS),   'fa-users',         '#fb923c', 'Active buyers'),
            _kpi_card('Avg Order Value',  _fmt_currency(dl.AVG_ORDER_VALUE), 'fa-tag',           '#f472b6', 'Per invoice'),
        ], className='g-3 mb-4'),

        dbc.Row([
            dbc.Col(
                dbc.Card(dbc.CardBody(
                    dcc.Graph(id='overview-trend', figure=figs.fig_revenue_trend('M'),
                              config={'displayModeBar': False}, style={'height': '340px'}),
                ), className='chart-card'),
                lg=8,
            ),
            dbc.Col(
                dbc.Card(dbc.CardBody(
                    dcc.Graph(id='overview-country-bar', figure=figs.fig_country_bar(10),
                              config={'displayModeBar': False}, style={'height': '340px'}),
                ), className='chart-card'),
                lg=4,
            ),
        ], className='g-3'),
    ])


# ── Section: RFM Segmentation ──────────────────────────────────────────────

def rfm_layout() -> html.Div:
    from dashboard.figures import SEG_COLORS  # local import avoids top-level cycle

    seg_df = dl.SEGMENT_STATS

    table_rows = [
        html.Tr([
            html.Td(html.Span([
                html.Span('●', style={'color': SEG_COLORS.get(row['Segment Label'], '#6b7280'),
                                      'marginRight': '8px', 'fontSize': '1rem'}),
                row['Segment Label'],
            ])),
            html.Td(f"{int(row['Customers']):,}"),
            html.Td(f"{row['Avg_Recency']:.0f} d"),
            html.Td(f"{row['Avg_Frequency']:.1f}"),
            html.Td(f"£{row['Avg_Monetary']:,.0f}"),
            html.Td(f"£{row['Total_Revenue']:,.0f}"),
        ])
        for _, row in seg_df.iterrows()
    ]

    segment_table = dbc.Table(
        [html.Thead(html.Tr([
            html.Th('Segment'), html.Th('Customers'), html.Th('Avg Recency'),
            html.Th('Avg Freq'), html.Th('Avg CLV'), html.Th('Total Rev'),
        ]))] + [html.Tbody(table_rows)],
        className='segment-table',
        striped=False, bordered=False, hover=True, responsive=True, size='sm',
    )

    return html.Div([
        html.Div([
            html.H2('RFM Customer Segmentation', className='section-title'),
            html.P(
                'Customers scored by Recency, Frequency & Monetary value, '
                'classified into 10 behavioural segments.',
                className='section-subtitle',
            ),
        ], className='section-header'),

        dbc.Row([
            dbc.Col(
                dbc.Card(dbc.CardBody(
                    dcc.Graph(id='rfm-treemap', figure=figs.fig_rfm_treemap(),
                              config={'displayModeBar': False}, style={'height': '340px'}),
                ), className='chart-card'),
                lg=5,
            ),
            dbc.Col(
                dbc.Card(dbc.CardBody(
                    dcc.Graph(id='rfm-seg-bar', figure=figs.fig_segment_revenue(),
                              config={'displayModeBar': False}, style={'height': '340px'}),
                ), className='chart-card'),
                lg=7,
            ),
        ], className='g-3 mb-3'),

        dbc.Row([
            dbc.Col(
                dbc.Card(dbc.CardBody(
                    dcc.Graph(id='rfm-scatter', figure=figs.fig_rfm_scatter(),
                              config={'displayModeBar': False}, style={'height': '400px'}),
                ), className='chart-card'),
                lg=7,
            ),
            dbc.Col(
                dbc.Card([
                    dbc.CardHeader(
                        html.H6('Segment Health Table', className='mb-0',
                                style={'color': '#94a3b8', 'fontSize': '0.85rem',
                                       'fontWeight': '600', 'textTransform': 'uppercase',
                                       'letterSpacing': '0.06em'}),
                    ),
                    dbc.CardBody(
                        segment_table,
                        style={'overflowY': 'auto', 'maxHeight': '360px', 'padding': '0'},
                    ),
                ], className='chart-card'),
                lg=5,
            ),
        ], className='g-3'),
    ])


# ── Section: Product Performance ──────────────────────────────────────────

def products_layout() -> html.Div:
    return html.Div([
        html.Div([
            html.H2('Product Performance', className='section-title'),
            html.P(
                'Top 20 products ranked by total revenue and units sold across the full period.',
                className='section-subtitle',
            ),
        ], className='section-header'),

        dbc.Row([
            dbc.Col(
                dbc.Card(dbc.CardBody(
                    dcc.Graph(id='prod-rev', figure=figs.fig_top_products_revenue(),
                              config={'displayModeBar': False}),
                ), className='chart-card'),
                lg=6,
            ),
            dbc.Col(
                dbc.Card(dbc.CardBody(
                    dcc.Graph(id='prod-qty', figure=figs.fig_top_products_qty(),
                              config={'displayModeBar': False}),
                ), className='chart-card'),
                lg=6,
            ),
        ], className='g-3'),
    ])


# ── Section: Geographic Analysis ──────────────────────────────────────────

def geo_layout() -> html.Div:
    uk_pct   = 100.0 * dl.UK_REVENUE / dl.TOTAL_REVENUE
    intl_pct = 100.0 - uk_pct

    return html.Div([
        html.Div([
            html.H2('Geographic Analysis', className='section-title'),
            html.P(
                f'Revenue distributed across {dl.NUM_COUNTRIES} countries worldwide.',
                className='section-subtitle',
            ),
        ], className='section-header'),

        dbc.Row([
            _kpi_card('UK Revenue',          _fmt_currency(dl.UK_REVENUE),   'fa-sterling-sign', '#818cf8', f'{uk_pct:.1f}% of total'),
            _kpi_card('International Rev.',  _fmt_currency(dl.INTL_REVENUE), 'fa-globe',         '#34d399', f'{intl_pct:.1f}% of total'),
            _kpi_card('Active Markets',      str(dl.NUM_COUNTRIES),          'fa-map-location-dot', '#fb923c', 'Unique countries'),
            _kpi_card('Top Market',          'United Kingdom',               'fa-trophy',        '#f472b6', 'Largest contributor'),
        ], className='g-3 mb-3'),

        dbc.Row([
            dbc.Col(
                dbc.Card(dbc.CardBody(
                    dcc.Graph(id='geo-choropleth', figure=figs.fig_choropleth(),
                              config={'displayModeBar': False}, style={'height': '420px'}),
                ), className='chart-card'),
                lg=8,
            ),
            dbc.Col(
                dbc.Card(dbc.CardBody(
                    dcc.Graph(id='geo-country-bar', figure=figs.fig_country_bar(15),
                              config={'displayModeBar': False}, style={'height': '420px'}),
                ), className='chart-card'),
                lg=4,
            ),
        ], className='g-3'),
    ])


# ── Section: Time Trends ───────────────────────────────────────────────────

def trends_layout() -> html.Div:
    return html.Div([
        html.Div([
            html.H2('Time Series & Trends', className='section-title'),
            html.P(
                'Revenue patterns by day, week, and month — plus order volume by time of day.',
                className='section-subtitle',
            ),
        ], className='section-header'),

        dbc.Row([
            dbc.Col(
                dbc.Card([
                    dbc.CardBody([
                        html.Div([
                            html.Span('Granularity:', className='freq-label'),
                            dbc.RadioItems(
                                id='freq-selector',
                                options=[
                                    {'label': 'Daily',   'value': 'D'},
                                    {'label': 'Weekly',  'value': 'W'},
                                    {'label': 'Monthly', 'value': 'M'},
                                ],
                                value='M',
                                inline=True,
                                className='freq-radio',
                                inputClassName='freq-radio-input',
                                labelClassName='freq-radio-label',
                            ),
                        ], className='freq-controls'),
                        dcc.Graph(
                            id='dynamic-trend-chart',
                            figure=figs.fig_revenue_trend('M'),
                            config={'displayModeBar': False},
                            style={'height': '340px'},
                        ),
                    ]),
                ], className='chart-card'),
                lg=12,
            ),
        ], className='g-3 mb-3'),

        dbc.Row([
            dbc.Col(
                dbc.Card(dbc.CardBody(
                    dcc.Graph(id='heatmap-chart', figure=figs.fig_order_heatmap(),
                              config={'displayModeBar': False}),
                ), className='chart-card'),
                lg=12,
            ),
        ], className='g-3'),
    ])


# ── Root layout ────────────────────────────────────────────────────────────

def create_layout() -> html.Div:
    return html.Div([
        dcc.Store(id='active-page', data='overview'),

        _sidebar,

        html.Div([
            # Top bar
            html.Div([
                html.Div([
                    html.H1(id='page-title', children='Executive Overview',
                            className='topbar-title'),
                    html.P('UK Online Retail II · Dec 2009 – Dec 2010',
                           className='topbar-subtitle'),
                ]),
                html.Div([
                    html.Span(className='fa fa-circle status-dot'),
                    html.Span('Live Data', className='status-label'),
                ], className='status-badge'),
            ], className='topbar'),

            # Page content (swapped by callbacks)
            html.Div(
                id='page-content',
                children=overview_layout(),
                className='page-content',
            ),
        ], className='main-area'),
    ], className='dashboard-root')
