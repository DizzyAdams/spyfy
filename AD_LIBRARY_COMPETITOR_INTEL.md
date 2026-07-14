# SpyFy — Ad-Library Creative Scrape & Host Intel

> Source note: live `web_search`/`web_extract` were unavailable (no Firecrawl key on this
> profile), so competitor-endpoint specifics are from domain knowledge + the **actual SpyFy repo
> code** at `apps/workers-py/spyfy/{meta_library,tiktok_library,realtime_producer}.py` and
> `apps/web/server/realtime.js`. Findings below are concrete and actionable, with the exact
> gap already present in the repo called out.

---

## 0. THE GAP YOU ALREADY HAVE (read this first)

`meta_library.py` / `tiktok_library.py` **fake the creative** today. They never pull the
real image/MP4/CTA — they fall back to placeholder media:

- `image` / `thumb` → `https://picsum.photos/seed/.../640/384` (random stock, NOT the real creative)
- `videoUrl` → a **local cover file** `/videos/*.mp4` (deterministic by seed, not the real ad)
- Code comment (meta_library.py L428): *"a Ad Library raramente expõe a URL do arquivo de vídeo (só o snapshot/página)"* — this belief is **wrong for the API path**; the real URLs ARE in the API payload, the scraper just doesn't request them.
- The `ad_archive` Graph call lists fields `ad_creative_bodies`, `snapshot_url`, etc. but **omits `ad_creatives`** — the field that actually contains `url` (image) and `video_url` (MP4). That's the one-line fix.

**Fix priority:** request `ad_creatives` on Meta, parse `{url, video_url}` from it, and on TikTok request + parse `video_url`/`landing_page_url`. Stop calling `cover_image()` / `video_cover()` for real ads.

---

## 1. Facebook / Instagram Ad Library

**Public, official, no login wall — use this:**

```
GET https://graph.facebook.com/v19.0/ads_archive
  ?access_token=...          # any FB/Meta app token (no special permit needed for ad_archive)
  &search_terms=<keyword>
  &ad_reached_countries=["BR"]
  &ad_active_status=ACTIVE
  &media_type=ALL
  &fields=id,ad_archive_id,page_id,page_name,
           ad_creative_bodies,ad_creative_link_titles,
           ad_delivery_start_time,ad_delivery_country,
           impressions,spend,currency,publisher_platforms,
           snapshot_url,
           ad_creatives{url,video_url,thumbnail_url}   # <-- THE MISSING FIELD
  &limit=100
```

**Creative extraction from each row:**
- **Image URL:** `row.ad_creatives[0].url` (FB CDN `*.fbcdn.net` / `*.fbsbx.com`) — direct file, hotlink-safe.
- **Video MP4:** `row.ad_creatives[0].video_url` — direct `.mp4` on `fbcdn.net`. THIS is the real ad video; do not substitute a local file.
- **CTA / landing link:** `row.snapshot_url` is the Ad Library *page*. The actual outbound CTA destination is buried in the snapshot HTML, OR (more reliably) pull `ad_creatives[].link_url` / `ad_creative_link_titles` for the CTA *label*. To get the true landing URL you usually fetch `snapshot_url` and parse the `u=` redirect param, or better: parse `ad_creatives[].link_url` when present.
- **Advertiser:** `page_name` / `page_id`.
- **Dates:** `ad_delivery_start_time`; end date is only shown if the ad stopped (`ad_delivery_stop_time` not in the public archive — active ads have no stop date).
- **Spend/impressions:** `impressions` and `spend` are **ranges** (`{"lower_bound":N,"upper_bound":M}`), NOT exact. Parse to midpoint.
- **Format:** derive from `media_type` (VIDEO/IMAGE/CAROUSEL/MEMORY/LINK) → already done in `_MEDIA_TO_FORMAT`.

**Pagination / cursor:**
- Cursor-based. Response has `paging.next` (full URL). Loop until `next` is null or you hit `limit`. No offset.
- `limit` max 100.

**Rate limits (reality):**
- Tied to the app token's Graph rate limit: **~200 calls / user / hour** baseline, bursts allowed; 429 = back off + retry. Add exponential backoff.
- The ad_archive endpoint is **heavily cached** by Meta — results can lag real-time by minutes/hours and the same query returns near-identical sets. Don't poll faster than ~5–10 min.
- No cost. A free FB app token works. This is the **cheapest, most stable** source — prefer it over web-scrape.

**Web-scrape fallback (no token):** `https://www.facebook.com/ads/library/?q=<kw>&active_status=ACTIVE&country=BR&media_type=all`. The real creative URLs are inside `<script type="application/json">` blobs (your `_iter_ad_nodes` already walks these) but the **public HTML does NOT expose the raw MP4** — only the snapshot page. So: token path for real media, scrape path only for text + snapshot link. Your current code already does exactly this; the *improvement* is adding the token + `ad_creatives` field.

---

## 2. TikTok Ad Library / Creative Center

**Official API (preferred):**
```
GET https://ads.tiktok.com/open_api/v1.3/ad_library/get/
  ?query=<keyword>
  &region=BR
  &page_size=100
  &ad_format=ALL
  Header: Access-Token: <TikTok Marketing/Ads API token>
```
Response: `data.list[]` (your `_search_api` already reads `data.list`/`data.ads`).

**Creative extraction per row:**
- **Video + thumbnail:** `row.video_url` (direct `.mp4` on `v19.tiktokcdn.com`) and `row.thumbnail_url` (image on tiktokcdn).
- **Landing page / CTA link:** `row.landing_page_url` — **this is the real outbound CTA**, use it directly as `ctaUrl`. (Your `_web_node_to_offer` already maps `landingPageUrl` → `snapshot`; just rename to `ctaUrl` and keep the raw URL.)
- **Advertiser:** `row.advertiser_name`.
- **Dates:** `row.start_date` (`create_time` on some versions).
- **CTA label:** `row.cta` / `row.button_text` when present.

**Web-scrape fallback:** `https://ads.tiktok.com/ad-library/?q=<kw>&region=br`. JSON blobs carry `adId`/`advertiserName`/`landingPageUrl` (your `_regex_node` already grabs these). Real MP4 is generally **not** in the public HTML — use the API for video.

**Creative Center** (`creativecenter.tiktok.com`) is a *curated* inspiration gallery (trending sounds, templates), not the full ad archive — useful for "top ads" lists but NOT a complete scrape source. Skip for coverage; mine Ad Library.

**Rate limits:** Tiktok Open API is stricter — ~**100 req/min** per app, daily quota caps. Use the token path; cache results; don't re-scrape same query < 1h.

---

## 3. What commercial ad-spy tools actually display (the schema to match)

Reverse-engineered "offer" schema from BigSpy / AdSpy / PowerAdSpy / Anstrex / SpyFu.
All of them show, per creative card:

| Field | Example | Notes |
|---|---|---|
| `advertiser` / `page_name` | "NutriCorp" | handle + sometimes follower count |
| `network` | meta / tiktok / pinterest / gads / native | source filter |
| `format` | video / image / carousel | |
| `headline` + `body` | ad copy text | full body, not truncated |
| `image` (creative still) | CDN url | the thumbnail/preview |
| `videoUrl` (mp4) | CDN url | **playable inline** — core differentiator |
| `carousel` | [img,img,img] | array when format=carousel |
| `ctaLabel` | "Learn More", "Shop Now" | button text |
| `ctaUrl` | landing page | **the money field** — outbound link |
| `startDate` / `endDate` | ISO dates | runtime / "last seen" |
| `country` | BR / US / … | geo filter |
| `impressions` / `spend` (range) | "1M–5M", "$5k–$10k" | always a band, never exact |
| `firstSeen` / `lastSeen` | dates | for "winning" scoring |
| `tags` / `niche` | "weight loss" | for filter + search |
| `transcript` | VSL captions | for video ads (ASR) |
| `similarAds` / `byAdvertiser` | related | cross-link |

**Key takeaway:** the three fields that make a card look "real" vs fake are **`videoUrl` (real mp4), `image` (real still), and `ctaUrl` (real landing link)**. SpyFy currently has NONE of these real for scraped ads — fixing §0 closes 80% of the gap.

---

## 4. Practical scrape strategy for a small team (what's realistic to self-host)

| Approach | Pros | Cons | Verdict for SpyFy |
|---|---|---|---|
| **Official endpoints** (Meta Graph `ads_archive` + TikTok `open_api/ad_library`) | Legal, stable, cheap, returns real MP4/image URLs, no anti-bot war | Needs 1 app token each; ranges not exact; cached/laggy | **PRIMARY. Your repo already calls both — just add `ad_creatives` (Meta) and `video_url`/`landing_page_url` (TikTok).** |
| **Headless browser** (Playwright/Puppeteer on the ad-library web UIs) | Gets what the JSON API hides | Heavy (2–4GB RAM/worker), easy IP/UA bans, breaks on UI change, illegal-ish ToS gray zone, $ to run | **Secondary fallback only**, and even then the public HTML lacks raw MP4 — so low ROI. Skip unless API fails. |
| **Third-party ad-spy APIs** (BigSpy/AdSpy resale, proxy APIs) | Turnkey data | $$$, ToS risk, they already watermark/host media you can't re-host cleanly | **Avoid** — defeats the "self-host scraped media" goal. |
| **Proxy pool** (for endpoint calls) | Avoids per-IP rate caps | $ | **Optional** — only if you scale > a few hundred queries/day. `proxy_pool.py` already exists in repo. |

**Recommendation:** Endpoint-first. One Meta app token + one TikTok API token (both free to create). Scrape on a cron (every 15–60 min per query, respecting rate limits + caching). Headless browser = only if both APIs die.

---

## 5. How to HOST served media so Next.js renders it (no hotlink blocks)

**The problem:** `fbcdn.net` / `tiktokcdn.com` creative URLs are **sometimes** hotlinkable but:
- can 403 on cross-origin / referer checks,
- can expire (signed URLs),
- TikTok CDN **does** serve `Access-Control-Allow-Origin: *` on video, Meta usually fine for `<img>` but not guaranteed.

**Reliable self-host pipeline (recommended for SpyFy):**

1. **Download-on-scrape:** when you get a real `image`/`videoUrl`, **fetch + store it** in object storage (don't rely on the source URL at render time).
2. **Storage:** put media in **Cloudflare R2** (or S3/Bunny/Supabase Storage). Your deploy target is Vercel → **R2 is the natural fit**: zero egress cost, S3-compatible, first-10GB free.
3. **Serve via CDN:** front the bucket with **Cloudflare CDN** (custom domain `cdn.spyfyprod.vercel.app` or your own). Set `Access-Control-Allow-Origin: *` + `Cache-Control: public, max-age=31536000, immutable` on the bucket objects. This kills hotlink/referer blocks and CORS.
4. **Next.js render:** store the R2/CDN URL in the offer (`image`, `videoUrl`, `thumb`) and render with plain `<img src>` / `<video src>` — no Vercel `/public` copy needed (Vercel /public can't hold GBs of video and isn't meant for dynamic media).
5. **Local dev fallback:** keep the existing `/videos/*.mp4` + `picsum` covers **only as placeholders** when a real URL couldn't be fetched (don't present them as real ads).

**Concrete bucket layout:**
```
r2://spyfy-media/
  meta/<ad_archive_id>.jpg
  meta/<ad_archive_id>.mp4
  tiktok/<ad_id>.mp4
  tiktok/<ad_id>.jpg
```
And the offer stores `https://cdn.spyfyprod.vercel.app/meta/<id>.mp4`.

**Why not base-path `/public/videos`:** Vercel `/public` is bundled into the deployment; you can't write to it at runtime from the scraper, and it's not for large/ever-growing media. Object storage + CDN is the correct architecture. (Your current `/videos/*.mp4` local covers are fine *as placeholders only*.)

---

## 6. RECOMMENDED OFFER CARD SCHEMA (what SpyFy must store)

Extends the existing `normalizeOffer` shape in `apps/web/server/realtime.js` with the
real-creative fields competitors show. Keep all current fields; add/repurpose these:

```ts
interface Offer {
  id: string;                 // meta_<adArchiveId> | tiktok_<adId>
  headline: string;            // ad_creative_link_titles[0] or first sentence of body
  body: string;               // full ad copy (ad_creative_bodies)
  advertiser: string;         // page_name / advertiser_name
  advertiserId?: string;      // page_id / ad_id owner
  network: 'meta' | 'tiktok' | 'google' | 'youtube' | 'native' | 'pinterest';
  format: 'video' | 'image' | 'carousel';
  niche: string;              // tag / category

  // ===== REAL CREATIVE MEDIA (the fix) =====
  image: string;             // REAL still: ad_creatives[].url (meta) | thumbnail_url (tt)
  thumb: string;             // same as image, or a 640x384 crop
  videoUrl?: string;         // REAL mp4: ad_creatives[].video_url (meta) | video_url (tt)
  carousel?: string[];        // [img,img,img] when format=carousel

  // ===== CTA / FUNNEL =====
  ctaLabel?: string;         // "Learn More" / "Shop Now" / cta button text
  ctaUrl?: string;          // REAL landing page: landing_page_url (tt) | ad_creatives[].link_url (meta)
  snapshotUrl: string;        // ad_library page (provenance / "view source")
  funnel?: { type: 'lp'|'vsl'|'checkout'|'upsell'|'ty'; label: string; stack?: string }[];

  // ===== METRICS (always ranges) =====
  estImpressions: number;     // midpoint of impressions range (or 0)
  estSpendLow?: number;
  estSpendHigh?: number;
  startDate?: string;         // ISO
  endDate?: string | null;    // null = still running
  firstSeen?: string;
  lastSeen?: string;
  country: string;           // BR / US / ...

  // ===== DERIVED (keep current) =====
  longevityDays: number;
  winningScore: number;
  thumbnailHue?: number;
  gradient?: [string, string];
  bullets?: string[];        // derived from body
  vslSeconds?: number;
  transcript?: { t: string; label: string; text: string }[];
  source: 'meta_ad_library' | 'tiktok_ad_library' | ...;
}
```

**Minimal "must-have to match competitors":**
`videoUrl` (real mp4) · `image` (real still) · `ctaUrl` (real landing) · `ctaLabel` · `advertiser` · `headline`/`body` · `format` · `startDate`/`endDate` · `country` · `estImpressions`.

---

## 7. ACTION CHECKLIST (small team, this week)

1. **Meta** (`meta_library.py`): add `ad_creatives{url,video_url,thumbnail_url,link_url}` to `fields`; in `_api_to_offer`, set `image = ad_creatives[0].url`, `videoUrl = ad_creatives[0].video_url`, `ctaUrl = ad_creatives[0].link_url or snapshot redirect`, `thumb = thumbnail_url or url`. Stop defaulting to `cover_image()`.
2. **TikTok** (`tiktok_library.py`): in `_api_to_offer`/`_web_node_to_offer`, set `videoUrl = video_url`, `image = thumbnail_url or cover`, `ctaUrl = landing_page_url`, `ctaLabel = cta/button_text`. Stop defaulting to `video_cover()` local file.
3. **Add download+store step** in `offers_service.py` / a new `media_store.py`: fetch each real `image`/`videoUrl`, PUT to **R2**, rewrite the offer URL to the **CDN URL**. Keep `/videos/*.mp4` + picsum ONLY as fallback when fetch fails.
4. **Provision R2 + Cloudflare CDN** (`cdn.spyfyprod.vercel.app`), set CORS `*` + immutable cache headers on the bucket.
5. **Next.js** already renders `image`/`videoUrl`/`thumb` from `normalizeOffer` — once the URLs are real CDN URLs it just works. No frontend change needed beyond confirming `<video>` uses `videoUrl`.
6. **Rate-limit**: add backoff to both clients; cache per-query results ≥ 15 min; don't poll faster.
