"""
api/index.py — Vercel serverless entry point for BloodSetu FastAPI backend.

Vercel's Python runtime calls this module's `app` object via ASGI.
The DB_PATH is set to /tmp/bloodsetu.db so it lives in Vercel's writable
tmp filesystem (data persists for the lifetime of the warm container only —
acceptable for a demo/portfolio project; swap for a hosted DB for production).
"""

import sys, os

# Make the project root importable so database.py, utils.py etc. resolve
ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
if ROOT not in sys.path:
    sys.path.insert(0, ROOT)

# Point SQLite to /tmp (only writable dir on Vercel serverless)
os.environ.setdefault("DB_PATH", "/tmp/bloodsetu.db")

# Patch database.py to read DB_PATH from env
import database as _db
_db.DB_PATH = os.environ["DB_PATH"]

# Import the FastAPI app (defined in api.py at project root)
from api import app  # noqa: F401 — Vercel picks up `app`
