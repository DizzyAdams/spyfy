"""Schemas Pydantic da SpyFy API."""
from __future__ import annotations

from pydantic import BaseModel, Field


class Health(BaseModel):
    status: str = "ok"
    service: str = "spyfy-api"
    version: str


class EstimateRequest(BaseModel):
    first_seen: str = Field(..., description="ISO datetime")
    last_seen: str = Field(..., description="ISO datetime")
    creative_variants: int = 1
    est_impressions_low: int = 0
    est_impressions_high: int = 0
    engagement: int = 0
    networks: int = 1
    countries: int = 1
    # economia do nicho (opcional)
    avg_ticket: float | None = None
    cvr: float | None = None
    ctr: float | None = None
    cpm: float | None = None


class EstimateResponse(BaseModel):
    longevity_days: int
    est_impressions: int
    est_daily_spend: float
    est_daily_revenue: float
    est_daily_profit: float
    est_roas: float
    est_roi_pct: float
    winning_score: float
    scaling_signal: str
    confidence: float
    notes: list[str]


class NotifyRequest(BaseModel):
    event_id: str
    type: str
    plan: str = "pro"
    user_id: str
    email: str | None = None
    hour_local: int = 12
    sent_today: int = 0
    data: dict = Field(default_factory=dict)


class NotifyResponse(BaseModel):
    suppressed: bool
    reason: str
    delivered: list[str]
    failed: list[str]


class WebhookAck(BaseModel):
    ok: bool
    dedup: bool = False


class AgentRunRequest(BaseModel):
    """Dispara o pipeline autônomo de mineração -> enriquecimento (LangGraph)."""
    objective: str = "Encontrar ofertas vencedoras"
    niche: str | None = None
    network: str | None = None
    country: str | None = None
    min_score: float = 0.0
    count: int = 3
    simulate: bool = True
    thread_id: str | None = None


class RagQueryRequest(BaseModel):
    """Consulta a memória RAG de ofertas (recuperação semântica)."""
    text: str
    n: int = 5


class ErrorBody(BaseModel):
    code: str
    message: str


class RealAdsIngest(BaseModel):
    """Corpo de POST /v1/ingest/real.

    Dois modos (ver app.py):
      - ads: lista de anúncios nativos REAIS coletados (dump) -> grava direto.
      - cookie / session_cookie: sessão logada (Meta) p/ raspar de verdade.
    """

    ads: list[dict] | None = None
    cookie: str | None = None
    session_cookie: str | None = None
    niche: str | None = "keto"
    network: str | None = "meta"
