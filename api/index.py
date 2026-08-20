"""
api/index.py — Vercel serverless entry point for BloodSetu FastAPI backend.

Vercel's Python runtime calls this module's `app` object via ASGI.
SQLite DB is stored in /tmp (the only writable directory on Vercel serverless).
Note: data persists only for the warm-container lifetime — fine for demo/portfolio.
Swap DB_PATH for a hosted DB (e.g. Turso, PlanetScale, Supabase) for production.
"""

import sys
import os

# Put the project root on the Python path so database.py, utils.py etc. resolve
ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
if ROOT not in sys.path:
    sys.path.insert(0, ROOT)

# Point SQLite to /tmp — the only writable directory in Vercel serverless
os.environ.setdefault("DB_PATH", "/tmp/bloodsetu.db")

# Patch database module before any other import reads DB_PATH
import database as _db  # noqa: E402
_db.DB_PATH = os.environ["DB_PATH"]

# Import the FastAPI application from backend.py at the project root.
# Vercel's Python runtime looks for a top-level `app` or `handler` in this file.
from backend import app  # noqa: F401, E402
