"""
callbacks.py — Registers all Dash interactive callbacks.
Imported by app.py after layout is set; never import app.py from here.
"""

from dash import Input, Output, callback_context, no_update
from dashboard._app import app
from dashboard import layout as L
from dashboard import figures as figs

# Pages in sidebar order — must match layout.PAGES
PAGES = L.PAGES

PAGE_MAP = {
    'overview': ('Executive Overview',    L.overview_layout),
    'rfm':      ('RFM Segmentation',     L.rfm_layout),
    'products': ('Product Performance',   L.products_layout),
    'geo':      ('Geographic Analysis',   L.geo_layout),
    'trends':   ('Time Trends',           L.trends_layout),
}


# ── Navigation ─────────────────────────────────────────────────────────────

@app.callback(
    [Output('page-content', 'children'),
     Output('page-title', 'children')] +
    [Output(f'nav-{p}', 'className') for p in PAGES],
    [Input(f'nav-{p}', 'n_clicks') for p in PAGES],
    prevent_initial_call=True,
)
def navigate(*_n_clicks):
    ctx = callback_context
    if not ctx.triggered:
        return no_update

    triggered_id = ctx.triggered[0]['prop_id'].split('.')[0]
    active = triggered_id.replace('nav-', '')

    title, layout_fn = PAGE_MAP.get(active, ('Executive Overview', L.overview_layout))
    content = layout_fn()

    classes = [
        'sidebar-nav-item active' if p == active else 'sidebar-nav-item'
        for p in PAGES
    ]
    return [content, title] + classes


# ── Revenue trend granularity toggle ──────────────────────────────────────

@app.callback(
    Output('dynamic-trend-chart', 'figure'),
    Input('freq-selector', 'value'),
    prevent_initial_call=True,
)
def update_trend_freq(freq: str):
    return figs.fig_revenue_trend(freq)
