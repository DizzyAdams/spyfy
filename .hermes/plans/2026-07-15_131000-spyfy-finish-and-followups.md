# SpyFy — Finalização & Follow-ups Implementation Plan

> **For Hermes:** Use subagent-driven-development skill to implement each pending task task-by-task.

**Goal:** Document the final state of SpyFy after the Vercel workers 500 fix + real-ad clone correction, and list the only remaining (pre-existing, low-priority) follow-ups so nothing is lost.

**Architecture:** Monorepo — `apps/web` (Next.js 15, Vercel `spyfyprod.vercel.app`) + `apps/workers-py` (FastAPI, Vercel `spyfyv1prod.vercel.app`). Workers serve real-time native ads from `cache/real_ads.json` (real_ads_store) as the primary feed source when `simulate=false`; web consumes it via `NEXT_PUBLIC_API_URL` (default `https://spyfyv1prod.vercel.app`).

**Tech Stack:** Next.js 15 / React 19 / TypeScript; FastAPI / Pydantic / uvicorn; Vercel serverless (Python lean runtime — only `requirements.txt` deps, NOT `pyproject.toml` heavy deps like chromadb/langgraph/playwright).

---

## STATUS — DONE (verified live, 2026-07-15)

- **Workers API 500 RESOLVED.** Root cause was Vercel detecting `pyproject.toml` and switching to the FastAPI framework preset (`spyfy.api.app:app`) instead of the `api/index.py` + `requirements.txt` handler. Fix = ignore `pyproject.toml`/`uv.lock` in `apps/workers-py/.vercelignore` so Vercel uses the explicit handler. Commit `9bd7f9d`. Live `/docs` = 200, `/v1/offers` returns `real_native` ads.
- **Real-ad clone corrected.** `POST /v1/clone` with a real `offer_id` (`real_{net}_{niche}_{i}`) now resolves the offer through `discover_offers(simulate=False)` and uses the card's real `link`/`pageUrl` as the clone URL. Previously it ignored the real link and fell back to a simulated offer. Root cause of the 404 was `req.network` (a non-existent field on `CloneRequest`) raising inside the try/except, silently forcing the simulated fallback. Commit `a9a65c7`. Live verified: `clone url used: https://www.exemplo-emagrecimento.com.br/protocolo-secreto` (real LP).
- **Both changes committed & pushed** to `origin/main` (`9bd7f9d..a9a65c7`).
- **Tests:** workers suite 113 passed (real core). 2 pre-existing failures are langgraph-coupled (agents RAG) and excluded from the deployed runtime.

---

## FILES CHANGED (this session)

- Modify: `apps/workers-py/spyfy/api/app.py` — `/v1/clone` resolves real offers via `discover_offers(simulate=False)`, `network="all"`.
- Modify: `apps/workers-py/spyfy/real_ads_store.py` — normalizes media/destiny fields to `""` (never `None`) so the frontend never renders broken media.
- Modify: `apps/workers-py/cache/real_ads.json` — real native ads store (embarked; `.vercelignore` preserves `cache/`).
- Configure (already): `apps/workers-py/.vercelignore` — ignores `pyproject.toml`, `uv.lock`, `.venv*`, `.mypy_cache`, `__pycache__`, `node_modules`, tests/scripts/docs; preserves `cache/`.
- Configure (already): `apps/workers-py/vercel.json` — `"installCommand": "pip install -r requirements.txt"`, cron `/v1/cron/warm`.

---

## REMAINING FOLLOW-UPS (low priority, pre-existing)

These are NOT blocking production; they were failing before this session and are out of scope for the deploy fix.

### Task 1: Stabilize langgraph-coupled tests (optional)
**Objective:** Make `tests/test_agents_*` + `scripts/test_headers.py` pass so the full suite is green.
**Files:** `apps/workers-py/tests/test_agents_memory.py`, `tests/test_agents_orchestrator.py`, `tests/test_notify_agent.py`, `tests/test_scraper_bridge.py`, `scripts/test_headers.py`
**Step 1:** Confirm they require chromadb/langgraph (not in lean `requirements.txt`).
**Step 2:** Either (a) add a `requirements.dev.txt` with heavy deps and run those tests in CI only, or (b) mark them `@pytest.mark.agents` and skip under lean.
**Step 3:** Run `pytest -q` green locally with the chosen approach.
**Step 4:** Commit `chore: stabilize langgraph-coupled tests`.
**Verify:** `pytest -q` → 0 failed.

### Task 2: Add a regression test for real-ad clone (recommended)
**Objective:** Lock the real-link behavior so it can't regress.
**Files:** Test: `apps/workers-py/tests/test_api.py`; Modify: `apps/workers-py/spyfy/api/app.py` (none needed if logic stable).
**Step 1:** Write failing-then-passing test: `POST /v1/clone {"offer_id":"real_meta_finance_0"}` → `response.url` matches the stored `link` of that real ad (not a simulated URL).
**Step 2:** Run `pytest tests/test_api.py -k clone -v` → PASS.
**Step 3:** Commit `test: regression for real-ad clone uses real link`.
**Verify:** test asserts `clone_url == real_ad["link"]`.

### Task 3: Wire `NEXT_PUBLIC_REALTIME_URL` if a live WS feed is desired (optional)
**Objective:** The web `RealtimeProvider` supports a WebSocket (`RT_URL`) but defaults to polling the REST `/v1/offers`. Currently polling-only (no WS server deployed). Decide: keep REST polling (works) or deploy the WebSocket producer.
**Files:** `apps/web/lib/realtime/RealtimeProvider.tsx`, `apps/web/.env.local`
**Step 1:** Confirm REST polling already renders real ads (it does — `/v1/offers` returns `real_native`).
**Step 2:** If WS wanted, deploy `apps/web/server/realtime.js` and set `NEXT_PUBLIC_REALTIME_URL`.
**Verify:** Feed shows live real ads (already true via polling).

---

## DEPLOY RECIPE (for future changes)

```bash
# Backend (workers API)
cd apps/workers-py
npx vercel deploy --prod --yes --archive=tgz

# Frontend (web)
cd apps/web
npx vercel deploy --prod --yes
```

**Verify after any deploy:**
```bash
curl -s -o /dev/null -w "%{http_code}\n" https://spyfyv1prod.vercel.app/docs   # expect 200
curl -s "https://spyfyv1prod.vercel.app/v1/offers?limit=1" | head -c 200       # expect real_native
curl -s -o /dev/null -w "%{http_code}\n" https://spyfyprod.vercel.app/         # expect 200
```

## RISKS / TRADEOFFS
- `.vercelignore` MUST keep ignoring `pyproject.toml`/`uv.lock` — otherwise Vercel re-detects the FastAPI preset and the 500 returns. If you ever legitimately need `pyproject` deps on serverless, switch to Docker/Render/HF instead of Vercel's Python runtime.
- `cache/real_ads.json` is embarked in the deploy (preserved by `.vercelignore`). To refresh real ads, POST to `/v1/ingest/real` with a dump or run `/v1/cron/warm`.
- Lean deploy intentionally excludes chromadb/langgraph → `/v1/agents/*` returns `{"status":"unavailable"}` on Vercel. That is by design (keeps bundle small); full agent graph runs on Docker/local with heavy deps.
