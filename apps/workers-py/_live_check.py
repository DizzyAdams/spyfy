import sys, traceback, urllib.request, time
ROOT = r"C:\Users\forrydev\Desktop\SpyFy\apps\workers-py"
sys.path.insert(0, ROOT)
from spyfy.api.app import app
import threading, uvicorn
port = 8099
def run():
    uvicorn.run(app, host="127.0.0.1", port=port, log_level="warning")
threading.Thread(target=run, daemon=True).start()
time.sleep(4)
eps = {
  "health": "/health",
  "version": "/v1/version",
  "offers": "/v1/offers?limit=2&simulate=true",
  "offer_detail": "/v1/offers/ofr_meta_finance_0",
  "categories": "/v1/categories",
  "metrics": "/v1/metrics?simulate=true",
  "ingest_status": "/v1/ingest/status",
}
for name, ep in eps.items():
    try:
        with urllib.request.urlopen(f"http://127.0.0.1:{port}{ep}", timeout=15) as resp:
            body = resp.read().decode("utf-8", "replace")
            print(f"[{name}] -> {resp.status} ({len(body)} B): {body[:120]}")
    except Exception as e:
        print(f"[{name}] ERROR: {e}")
