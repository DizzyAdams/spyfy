"""
SpyFy API — FastAPI app (deploy-ready)
======================================
Amarra os engines: Scale/ROI, Notifications, Webhooks e Event Bus.
Endpoints:
  GET  /health
  GET  /v1/version
  POST /v1/offers/estimate         -> ROI/escala/winning score
  POST /v1/notify                  -> roteia+entrega notificação (dispatcher)
  POST /v1/webhooks/{provider}     -> recebe webhook assinado (NexusTracker/Darkfy)
  GET  /v1/events/types            -> catálogo de eventos
  POST /v1/agents/run              -> pipeline autônomo (scout->enrich->copy->roi->dedup->guard->alert)
  POST /v1/agents/rag/query        -> recuperação semântica na memória RAG
  GET  /v1/agents/rag/count        -> nº de ofertas indexadas na memória RAG
"""
from __future__ import annotations

import os
from datetime import datetime

from fastapi import FastAPI, HTTPException, Query, Request
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel

from .. import __version__
# agents importados LAZY (dentro de /v1/agents/*) para permitir um deploy leve
# (ex.: Vercel serverless, ~250MB) sem chromadb/langgraph instalados. Quando
# essas deps estao presentes (Docker/Render/HF/local), os endpoints funcionam 100%.
from ..offers_service import (NICHE_KEY, compute_metrics, discover_offers,
                              get_offer_by_id)
from ..events import EVENT_TYPES, DomainEvent, EventBus
from ..notifications import (Channel, Notification, NotificationPrefs, Priority)
from ..notifiers import (AppriseAdapter, NotificationDispatcher, NovuAdapter,
                         NtfyAdapter, WebhookAdapter)
from ..roi import AdSignals, NicheEconomics, estimate_offer
from ..webhooks import DedupStore, parse_event, verify_webhook
from ..payments import register_payment_routes
from .schemas import (AgentRunRequest, EstimateRequest, EstimateResponse, Health,
                      NotifyRequest, NotifyResponse, RagQueryRequest, RealAdsIngest,
                      WebhookAck)


class CloneRequest(BaseModel):
    """Corpo de POST /v1/clone (A11 Cloner)."""

    offer_id: str | None = None
    url: str | None = None
    niche: str | None = None
    country: str = "BR"


def build_dispatcher() -> NotificationDispatcher:
    return NotificationDispatcher({
        "novu": NovuAdapter(api_key=os.getenv("NOVU_API_KEY", "")),
        "apprise": AppriseAdapter(),
        "ntfy": NtfyAdapter(base_url=os.getenv("NTFY_URL", "https://ntfy.spyfy.io")),
        "native": WebhookAdapter(secret=os.getenv("WEBHOOK_SECRET", "dev")),
    })


def create_app(dispatcher: NotificationDispatcher | None = None) -> FastAPI:
    app = FastAPI(title="SpyFy API", version=__version__)
    bus = EventBus()
    dispatcher = dispatcher or build_dispatcher()
    dedup = DedupStore()
    # Memória RAG compartilhada — criada lazy no primeiro uso de /v1/agents/*
    # (importa chromadb/langgraph sob demanda, permitindo deploy leve sem essas deps).
    app.state.bus = bus
    app.state.dispatcher = dispatcher
    app.state.memory = None

    # ── Payment routes (multi-gateway + anti-fraude) ─────────────
    register_payment_routes(app)

    # CORS: permite que o frontend (Vercel em produção + localhost em dev)
    # chame a API a partir do navegador. Origens configuráveis via CORS_ORIGINS.
    app.add_middleware(
        CORSMiddleware,
        allow_origins=os.getenv(
            "CORS_ORIGINS",
            "https://spyfyprod.vercel.app,http://localhost:3000,http://localhost:8080",
        ).split(","),
        allow_methods=["*"],
        allow_headers=["*"],
    )

    @app.get("/health", response_model=Health)
    def health() -> Health:
        return Health(version=__version__)

    @app.get("/v1/version")
    def version() -> dict:
        return {"version": __version__}

    @app.get("/v1/events/types")
    def event_types() -> dict:
        return {"types": sorted(EVENT_TYPES)}

    @app.post("/v1/offers/estimate", response_model=EstimateResponse)
    def estimate(req: EstimateRequest) -> EstimateResponse:
        try:
            sig = AdSignals(
                first_seen=datetime.fromisoformat(req.first_seen),
                last_seen=datetime.fromisoformat(req.last_seen),
                creative_variants=req.creative_variants,
                est_impressions_low=req.est_impressions_low,
                est_impressions_high=req.est_impressions_high,
                engagement=req.engagement,
                networks=req.networks, countries=req.countries,
            )
        except ValueError as exc:
            raise HTTPException(422, f"data invalida: {exc}")

        econ = NicheEconomics()
        for f in ("avg_ticket", "cvr", "ctr", "cpm"):
            v = getattr(req, f)
            if v is not None:
                setattr(econ, f, v)

        e = estimate_offer(sig, econ)
        return EstimateResponse(
            longevity_days=e.longevity_days, est_impressions=e.est_impressions,
            est_daily_spend=e.est_daily_spend, est_daily_revenue=e.est_daily_revenue,
            est_daily_profit=e.est_daily_profit, est_roas=e.est_roas,
            est_roi_pct=e.est_roi_pct, winning_score=e.winning_score,
            scaling_signal=e.scaling_signal, confidence=e.confidence, notes=e.notes,
        )

    @app.post("/v1/notify", response_model=NotifyResponse)
    def notify(req: NotifyRequest) -> NotifyResponse:
        prefs = NotificationPrefs(enabled_channels={
            Channel.IN_APP, Channel.EMAIL, Channel.PUSH})
        notif = Notification(req.event_id, req.type,
                             req.data.get("title", "SpyFy"),
                             req.data.get("body", ""),
                             Priority(req.data.get("priority", "normal")),
                             req.data)
        recipient = {"user_id": req.user_id, "email": req.email,
                     "hour_local": req.hour_local, "ntfy_topic": f"user-{req.user_id}"}
        report = dispatcher.dispatch(
            plan=req.plan, prefs=prefs, notif=notif, recipient=recipient,
            hour_local=req.hour_local, sent_today=req.sent_today)
        return NotifyResponse(
            suppressed=report.route.suppressed, reason=report.route.reason,
            delivered=[c.value for c in report.delivered],
            failed=[c.value for c in report.failed])

    @app.post("/v1/webhooks/{provider}", response_model=WebhookAck)
    async def webhook(provider: str, request: Request) -> WebhookAck:
        raw = (await request.body()).decode()
        sig = request.headers.get("x-spyfy-signature", "")
        ts = request.headers.get("x-spyfy-timestamp", "0")
        secret = os.getenv(f"WEBHOOK_SECRET_{provider.upper()}",
                           os.getenv("WEBHOOK_SECRET", "dev"))
        if not verify_webhook(raw, sig, ts, secret):
            raise HTTPException(401, "invalid signature")
        event = parse_event(raw)
        if dedup.seen(event["event_id"]):
            return WebhookAck(ok=True, dedup=True)
        bus.publish(DomainEvent(event["event_id"], event["type"],
                                event.get("data", {})))
        return WebhookAck(ok=True)

    @app.post("/v1/webhooks/inbound/{source}", response_model=WebhookAck)
    async def generic_webhook(source: str, request: Request, token: str = Query(None)) -> WebhookAck:
        """Webhook generico para receber dados de outros projetos sem HMAC."""
        expected_token = os.getenv("INBOUND_WEBHOOK_TOKEN", "dev_token")
        provided_token = token or request.headers.get("x-webhook-token", "")
        if provided_token != expected_token:
            raise HTTPException(401, "invalid token")
        
        try:
            payload = await request.json()
        except Exception:
            raise HTTPException(400, "invalid json payload")
            
        event_id = payload.get("event_id", f"evt_{int(datetime.now().timestamp() * 1000)}")
        event_type = payload.get("type", f"inbound.{source}")
        event_data = payload.get("data", payload)
        
        if dedup.seen(event_id):
            return WebhookAck(ok=True, dedup=True)
            
        bus.publish(DomainEvent(event_id, event_type, event_data))
        return WebhookAck(ok=True)

    @app.post("/v1/agents/run")
    async def agent_run(req: AgentRunRequest) -> dict:
        """Dispara o grafo autônomo (LangGraph) de mineração -> enriquecimento.

        Conecta o orquestrador ao EventBus e à memória RAG da aplicação: os
        alertas (A13) são publicados no bus e as ofertas ficam indexadas para
        recuperação semântica. Roda offline por padrão (sem LLM).
        """
        try:
            from ..agents import MEMBERS, OfferMemory, run_offer_pipeline
        except Exception:
            return {"status": "unavailable",
                    "detail": "engine de agentes (chromadb/langgraph) nao instalado neste deploy"}
        if app.state.memory is None:
            app.state.memory = OfferMemory()
        final = await run_offer_pipeline(
            req.objective,
            niche=req.niche, network=req.network, country=req.country,
            min_score=req.min_score, memory=app.state.memory, bus=bus,
            simulate=req.simulate, count=req.count, thread_id=req.thread_id,
        )
        final["members"] = MEMBERS  # documenta a topologia disponível
        return final

    @app.post("/v1/agents/rag/query")
    def rag_query(req: RagQueryRequest) -> dict:
        """Recuperação semântica (RAG) sobre a memória de ofertas indexadas."""
        try:
            from ..agents import OfferMemory
        except Exception:
            return {"query": req.text, "count": 0, "hits": [],
                    "detail": "memoria RAG (chromadb) nao instalada neste deploy"}
        if app.state.memory is None:
            app.state.memory = OfferMemory()
        hits = app.state.memory.query(req.text, n=req.n)
        return {"query": req.text, "count": len(hits), "hits": hits}

    @app.get("/v1/agents/rag/count")
    def rag_count() -> dict:
        """Nº de ofertas indexadas na memória RAG (long-term memory)."""
        if app.state.memory is None:
            return {"count": 0}
        return {"count": app.state.memory.count()}

    @app.get("/v1/offers")
    def list_offers(
        niche: str | None = Query(default=None, description="Rótulo de nicho (PT)"),
        network: str | None = Query(default=None, description="meta|tiktok|google|…|all"),
        country: str = Query(default="BR"),
        limit: int = Query(default=24, ge=1, le=100),
        simulate: bool = Query(
            default=False,
            description="True=fallback estruturado offline; False=tenta Ad Library real (precisa token)",
        ),
        token: str = Query(default="", description="Token da Ad Library (Meta) quando simulate=false"),
    ) -> dict:
        """Melhores / mais escaladas ofertas das Ad Libraries.

        Minera as redes (Meta/Google/TikTok reais quando há token, com
        fallback estruturado offline) e enriquece cada oferta com escala,
        ROI e win-probability, ranqueando por ``winningScore``.
        """
        offers = discover_offers(
            niche=niche, network=network, country=country,
            limit=limit, simulate=simulate, token=token,
        )
        return {
            "count": len(offers),
            "niche": niche,
            "network": network or "all",
            "country": country,
            "simulate": simulate,
            "offers": offers,
        }

    @app.post("/v1/ingest")
    def ingest(
        niche: str = Query(default="keto", description="Nicho a raspar"),
        network: str = Query(default="meta", description="meta|tiktok|google|native"),
        country: str = Query(default="BR"),
        limit: int = Query(default=10, ge=1, le=50),
    ) -> dict:
        """Roda a ferramenta headless própria (browser_scraper) para popular o
        cache de anúncios REAIS. Sem browser/sessão disponível, retorna
        ``scraped: 0`` (pipeline continua funcional via fallback)."""
        from ..browser_scraper import scrape_native_ads, BrowserScrapeUnavailable

        try:
            offers = scrape_native_ads(niche, network, country, limit)
            return {
                "ok": True,
                "scraped": len(offers),
                "network": network,
                "niche": niche,
                "source": "browser_scraper",
                "sample": offers[:3],
            }
        except BrowserScrapeUnavailable as e:
            return {"ok": False, "scraped": 0, "reason": str(e),
                    "network": network, "niche": niche}
        except Exception as e:  # noqa: BLE001
            return {"ok": False, "scraped": 0, "reason": repr(e),
                    "network": network, "niche": niche}

    @app.post("/v1/ingest/real")
    def ingest_real(payload: "RealAdsIngest"):
        """Ingere anúncios nativos REAIS na loja do SpyFy.

        Dois modos (competidor: recolha real via sessão logada ou dump):
          A) cookie de sessão logada (Meta) + nicho -> roda browser_scraper com
             a sessão autenticada e grava os cards reais. Requer browser no env.
          B) corpo ``{ "ads": [ {headline, advertiser, network, niche,
             country, image, videoUrl, format, pageUrl, cta}, ... ] }`` -> grava
             direto. Caminho que funciona em qualquer deploy (Vercel), bastando
             colar um lote de anúncios nativos coletados.

        Sempre retorna 200 (não quebra o pipeline); `added` diz quantos entraram.
        """
        from ..real_ads_store import add_real_ads, count as _cnt

        ads = payload.ads
        if isinstance(ads, list) and ads:
            added = add_real_ads(ads)
            return {"ok": True, "added": added, "source": "dump",
                    "total_real": _cnt()}

        cookie = payload.cookie or payload.session_cookie or ""
        niche = payload.niche or "keto"
        network = payload.network or "meta"
        if cookie:
            try:
                from ..browser_scraper import scrape_native_ads_session
                offers = scrape_native_ads_session(
                    niche, network, cookie, country="BR", limit=20)
                added = add_real_ads(offers)
                return {"ok": True, "added": added, "source": "session",
                        "total_real": _cnt(),
                        "network": network, "niche": niche}
            except Exception as e:  # noqa: BLE001
                return {"ok": False, "added": 0, "reason": repr(e),
                        "network": network, "niche": niche}

        return {"ok": False, "added": 0,
                "reason": "envie 'ads' (dump) ou 'cookie' (sessão logada)"}

    @app.get("/v1/ingest/status")
    def ingest_status() -> dict:
        """Quantos anúncios nativos REAIS estão na loja."""
        from ..real_ads_store import count, load_all
        ads = load_all()
        by_net = {}
        for a in ads:
            by_net[a.get("network", "meta")] = by_net.get(a.get("network", "meta"), 0) + 1
        return {"ok": True, "real_ads": count(), "byNetwork": by_net}

    @app.post("/v1/radar/ingest")
    async def radar_ingest(request: Request) -> dict:
        """Ingestão em tempo real do Radar (realtime_producer / WebSocket).

        Aceita:
          { "offer": {...} }  |  { "offers": [ {...}, ... ] }  |  [ {...}, ... ]
        Normaliza e grava na loja de anúncios REAIS (real_ads_store), que é a
        fonte primária do feed (discover_offers com simulate=false). Retorna
        sempre 200 (não quebra o pipeline realtime).
        """
        from ..real_ads_store import add_real_ads, count as _cnt

        try:
            payload = await request.json()
        except Exception:
            return {"ok": False, "added": 0, "reason": "JSON inválido"}

        if isinstance(payload, list):
            ads = payload
        elif isinstance(payload, dict):
            ads = payload.get("offers") or ([payload.get("offer")] if payload.get("offer") else [])
        else:
            ads = []
        if isinstance(ads, list) and ads:
            added = add_real_ads(ads)
            return {"ok": True, "added": added, "source": "radar", "total_real": _cnt()}
        return {"ok": False, "added": 0, "reason": "corpo vazio/inválido"}


    @app.get("/v1/cron/warm")
    def cron_warm() -> dict:
        """Aquecimento periódico do feed (Vercel Cron a cada 30min).

        - Re-minera as redes principais via discover_offers (fallback
          estruturado offline-safe) para manter o feed sempre populado.
        - Puxa a fonte REAL pública (TikTok Creative Center trends, sem
          token/sessão) e grava na loja de anúncios reais, para que o feed
          traga dados reais da Ad Library mesmo no serverless (onde o
          Scrapling/browser não cabem). Não quebra se uma rede falhar.
        """
        try:
            for key in ("keto", "finance", "beauty", "marketing"):
                discover_offers(niche=key, limit=12, simulate=True)
            # exercita agregação de métricas (offline-safe)
            compute_metrics(discover_offers(niche="finance", limit=24, simulate=True))

            # Fonte REAL pública (sem token): TikTok Creative Center.
            added_real = 0
            try:
                from ..tiktok_trends_source import fetch_tiktok_trends
                real = fetch_tiktok_trends("trends", "BR")
                if real:
                    from ..real_ads_store import add_real_ads
                    added_real = add_real_ads(real)
            except Exception:  # noqa: BLE001
                pass

            return {"ok": True, "warmed": True, "addedRealTrends": added_real}
        except Exception as e:  # noqa: BLE001
            return {"ok": False, "reason": repr(e)}

    @app.get("/v1/cron/collect-ads")
    def cron_collect_ads() -> dict:
        """Frota de mini-bots de extração nativa REAL (Vercel Cron).

        Roda UMA rodada da frota (``spyfy.ad_fleet.collect_once``) que varre
        a grade (nicho, rede) fazendo fetch real das Ad Libraries nativas e
        grava na loja de anúncios reais. É o substituto serverless-safe dos
        "mini-bots sempre online": o Cron dispara isso a cada N minutos,
        mantendo a loja sempre fresca sem precisar de processo persistente.
        Não quebra se uma rede cair (cada bot é isolado).
        """
        try:
            from ..ad_fleet import collect_once

            return collect_once(count=3, country="BR")
        except Exception as e:  # noqa: BLE001
            return {"ok": False, "reason": repr(e)}

    @app.get("/v1/metrics")
    def metrics(
        niche: str | None = Query(default=None),
        country: str = Query(default="BR"),
        simulate: bool = Query(default=False),
        token: str = Query(default=""),
    ) -> dict:
        """Métricas de mercado agregadas (redes, nichos, sinais, ROI, top escalando)."""
        offers = discover_offers(
            niche=niche, country=country, limit=60,
            simulate=simulate, token=token,
        )
        return compute_metrics(offers)

    @app.post("/v1/clone")
    def clone(req: CloneRequest) -> dict:
        """Clona uma LP/oferta (A11 Cloner).

        Recebe `offer_id` (oferta real coletada OU simulada) ou `url`
        (fetch real com fallback gracioso) e devolve um *clone bundle*
        estruturado + HTML reconstruído pronto para exportar.

        CORREÇÃO: quando `offer_id` aponta para um anúncio REAL
        (store de anúncios nativos), usamos o `link`/`pageUrl` real do
        card como `url` do clone — assim o clone abre a LP de verdade,
        não um offer simulado.
        """
        from ..clone import clone_offer

        offer = None
        clone_url: str | None = req.url
        if req.offer_id:
            # Resolve o offer pelo mesmo pipeline do feed (`discover_offers`),
            # que atribui o `id` canônico `real_{net}_{niche}_{i}` / `ofr_...`.
            # Assim o clone pega o LINK REAL do anúncio (não um offer simulado).
            try:
                from ..offers_service import discover_offers

                found = discover_offers(
                    niche=req.niche,
                    network="all",
                    country=req.country,
                    limit=200,
                    simulate=False,
                )
                real_hit = next(
                    (a for a in found if a.get("id") == req.offer_id), None
                )
                if real_hit is not None:
                    offer = real_hit
                    clone_url = (
                        real_hit.get("link")
                        or real_hit.get("pageUrl")
                        or real_hit.get("snapshotUrl")
                        or clone_url
                    )
            except Exception:  # noqa: BLE001
                pass
            # Fallback: oferta simulada (mantém comportamento anterior).
            if offer is None:
                offer = get_offer_by_id(req.offer_id, simulate=True)
                if offer is None:
                    raise HTTPException(404, "oferta não encontrada")
        niche = req.niche or (offer or {}).get("niche")
        return clone_offer(
            url=clone_url, offer=offer, niche=niche, country=req.country
        )

    @app.get("/v1/categories")
    def categories() -> dict:
        """Catálogo de categorias (nichos PT) suportadas + redes + contagens.

        Útil para o frontend montar filtros "melhores anúncios por categoria"
        e mostrar quantas ofertas o SpyFy está ranqueando em cada nicho.
        """
        labels = sorted(set(NICHE_KEY.keys()))
        out = []
        for label in labels:
            try:
                offers = discover_offers(niche=label, limit=12, simulate=True)
            except Exception:  # noqa: BLE001
                offers = []
            best = max((float(o.get("winningScore", 0)) for o in offers), default=0.0)
            out.append(
                {
                    "label": label,
                    "key": NICHE_KEY.get(label, "finance"),
                    "available": len(offers) > 0,
                    "count": len(offers),
                    "topScore": round(best, 1),
                }
            )
        return {"categories": out, "networks": ["meta", "tiktok", "google", "youtube", "native", "pinterest"]}

    @app.get("/v1/offers/{offer_id}")
    def get_offer(offer_id: str) -> dict:
        """Detalhe de uma oferta específica (ID determinístico)."""
        o = get_offer_by_id(offer_id, simulate=True)
        if o is None:
            raise HTTPException(404, "oferta não encontrada")
        return o

    return app


app = create_app()
