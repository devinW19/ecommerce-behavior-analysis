"""
_app.py — Dash application instance (no imports from other dashboard modules
          to avoid circular imports).
"""

import dash
import dash_bootstrap_components as dbc

app = dash.Dash(
    __name__,
    external_stylesheets=[
        dbc.themes.CYBORG,
        dbc.icons.FONT_AWESOME,
    ],
    title="E-Commerce Intelligence",
    suppress_callback_exceptions=True,
    meta_tags=[
        {"name": "viewport", "content": "width=device-width, initial-scale=1"},
    ],
)

server = app.server  # expose Flask server for production deploys
