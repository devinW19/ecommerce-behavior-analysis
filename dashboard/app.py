"""
app.py — Dashboard entry point.
Run with: python dashboard/app.py  (from project root)
"""

import sys
import os

# Ensure project root is on the path when run directly
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from dashboard._app import app            # Dash instance
from dashboard import layout              # builds layout (triggers data_loader import)
from dashboard import callbacks           # registers all callbacks  # noqa: F401

app.layout = layout.create_layout()

if __name__ == '__main__':
    print('\n[dashboard] Starting E-Commerce Intelligence Dashboard')
    print('   Open  ->  http://127.0.0.1:8050\n')
    app.run(debug=False, port=8050, host='127.0.0.1')
