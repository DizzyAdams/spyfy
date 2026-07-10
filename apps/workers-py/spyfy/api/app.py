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
"""
from __future__ import annotations

import os
from datetime import datetime

from fastapi import FastAPI, HTTPException, Request

from .. import __version__
from ..events import EVENT_TYPES, DomainEvent, EventBus
from ..notifications import (Channel, Notification, NotificationPrefs, Priority)
from ..notifiers import (AppriseAdapter, NotificationDispatcher, NovuAdapter,
                         NtfyAdapter, WebhookAdapter)
from ..roi import AdSignals, NicheEconomics, estimate_offer
from ..webhooks import DedupStore, parse_event, verify_webhook
from .schemas import (EstimateRequest, EstimateResponse, Health, NotifyRequest,
                      NotifyResponse, WebhookAck)


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
    app.state.bus = bus
    app.state.dispatcher = dispatcher

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

    return app


app = create_app()
