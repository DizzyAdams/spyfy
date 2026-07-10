"""Proxy reverso mínimo com basic auth (sem Docker).

Fica na frente do web (Next.js :3000) para expor publicamente via túnel
(ngrok/cloudflared) SEM deixar a aplicação aberta. Usuário/senha vêm de env.

Uso: BASIC_AUTH_USER=spyfy BASIC_AUTH_PASSWORD=xxx python basic_auth_proxy.py
"""
import base64
import http.client
import os
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer

USER = os.getenv("BASIC_AUTH_USER", "spyfy")
PASS = os.getenv("BASIC_AUTH_PASSWORD", "")
UP_HOST, UP_PORT = "localhost", 3000


def authorized(auth_header: str | None) -> bool:
    if not auth_header:
        return False
    try:
        scheme, b64 = auth_header.split(" ", 1)
        if scheme.lower() != "basic":
            return False
        decoded = base64.b64decode(b64).decode()
        u, _, p = decoded.partition(":")
        return u == USER and p == PASS
    except Exception:
        return False


class Handler(BaseHTTPRequestHandler):
    def _handle(self) -> None:
        if not authorized(self.headers.get("Authorization")):
            self.send_response(401)
            self.send_header("WWW-Authenticate", 'Basic realm="SpyFy"')
            self.end_headers()
            self.wfile.write(b"unauthorized")
            return
        body = None
        length = int(self.headers.get("Content-Length", 0) or 0)
        if length:
            body = self.rfile.read(length)
        fwd = {
            k: v
            for k, v in self.headers.items()
            if k.lower()
            not in ("host", "connection", "authorization", "content-length", "transfer-encoding")
        }
        conn = http.client.HTTPConnection(UP_HOST, UP_PORT, timeout=30)
        try:
            conn.request(self.command, self.path, body=body, headers=fwd)
            resp = conn.getresponse()
            self.send_response(resp.status)
            for k, v in resp.getheaders():
                if k.lower() in ("connection", "transfer-encoding"):
                    continue
                self.send_header(k, v)
            self.end_headers()
            self.wfile.write(resp.read())
        finally:
            conn.close()

    do_GET = _handle
    do_POST = _handle
    do_HEAD = _handle
    do_PUT = _handle
    do_DELETE = _handle
    do_PATCH = _handle
    log_message = lambda self, *a: None  # noqa: E731


if __name__ == "__main__":
    port = int(os.getenv("PROXY_PORT", "8080"))
    print(f"basic-auth proxy :{port} -> {UP_HOST}:{UP_PORT} (user={USER})", flush=True)
    ThreadingHTTPServer(("0.0.0.0", port), Handler).serve_forever()
