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


class ErrorBody(BaseModel):
    code: str
    message: str
