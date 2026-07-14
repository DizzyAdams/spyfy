import sys, traceback, urllib.request, time
ROOT = r"C:\Users\forrydev\Desktop\SpyFy\apps\workers-py"
sys.path.insert(0, ROOT)
try:
    from spyfy.api.app import app
    print("APP IMPORT OK | app =", type(app).__name__)
    paths = sorted({r.path for r in app.routes})
    print("ROUTES:", len(paths))
    for p in paths:
        print("  ", p)
except Exception:
    traceback.print_exc()
    sys.exit(1)

import threading, uvicorn
port = 8099
def run():
    uvicorn.run(app, host="127.0.0.1", port=port, log_level="warning")
t = threading.Thread(target=run, daemon=True)
t.start()
time.sleep(4)
for ep in ["/health", "/v1/version", "/v1/offers?limit=2&simulate=true", "/v1/offers/ofr_meta_finance_0", "/v1/categories", "/v1/metrics?simulate=true"]:
    try:
        with urllib.request.urlopen(f"http://127.0.0.1:{port}{ep}", timeout=15) as resp:
            body = resp.read().decode("utf-8", "replace")
            print(f"\n[{ep}] -> {resp.status} ({len(body)} bytes)")
            print(body[:350])
    except Exception as e:
        print(f"\n[{ep}] ERROR: {e}")
