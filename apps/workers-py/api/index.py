"""Vercel FastAPI entrypoint (default location: api/index.py).

Exposes a top-level ``app`` (FastAPI instance) so Vercel's FastAPI detector
picks it up automatically. The frontend calls this deployment's URL via
NEXT_PUBLIC_API_URL — no local machine or tunnel required.
"""
import os
import sys

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
if ROOT not in sys.path:
    sys.path.insert(0, ROOT)

from spyfy.api.app import create_app  # noqa: E402

app = create_app()
