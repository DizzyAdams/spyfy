"""Vercel FastAPI entrypoint (default location: api/index.py).

Exposes a top-level ``app`` (FastAPI instance) AND a ``handler`` (Mangum
wrapper) so Vercel's Python runtime can invoke the ASGI app. The frontend
calls this deployment's URL via NEXT_PUBLIC_API_URL — no local machine or
tunnel required.
"""
import os
import sys

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
if ROOT not in sys.path:
    sys.path.insert(0, ROOT)

from spyfy.api.app import create_app  # noqa: E402

app = create_app()

# Mangum adapta o ASGI app do FastAPI para o runtime serverless da Vercel.
# Sem isso, a função falha com FUNCTION_INVOCATION_FAILED.
from mangum import Mangum  # noqa: E402

handler = Mangum(app, lifespan="off")
