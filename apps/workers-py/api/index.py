# Handler serverless (Vercel Python / @vercel/python) para a SpyFy API.
# Vercel expoe api/index.py em /api/index; o wrapper strip o prefixo
# para o FastAPI rotear /health, /v1/... corretamente.
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from spyfy.api.app import create_app

_app = create_app()
PREFIX = "/api/index"


async def app(scope, receive, send):
    if scope.get("type") == "http":
        path = scope.get("path", "")
        # Alguns adapters (Vercel/ASGI) entregam a query string DENTRO do path.
        # Seja qual for o caso, garantimos que o prefixo /api/index seja stripado
        # e a query_string fique no lugar certo para o FastAPI rotear.
        scope = dict(scope)
        if "?" in path:
            path, _, qs = path.partition("?")
            scope["path"] = path
            if not scope.get("query_string"):
                scope["query_string"] = qs.encode()
        if path.startswith(PREFIX):
            scope["path"] = path[len(PREFIX):] or "/"
            rp = scope.get("raw_path")
            if isinstance(rp, (bytes, bytearray)):
                scope["raw_path"] = rp[len(PREFIX):] or b"/"
    await _app(scope, receive, send)


handler = app
