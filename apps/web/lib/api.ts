// Cliente tipado da API SpyFy (FastAPI).
// A base URL vem de NEXT_PUBLIC_API_URL (configurada no Vercel / .env.local).
// Toda chamada é defensiva: em caso de falha retorna `null` para a UI
// poder degradar graciosamente (ex.: mostrar "backend offline") em vez de quebrar.

import { type Offer } from "@/lib/data";

export interface ApiHealth {
  status: string;
  service: string;
  version: string;
}

export interface EstimateRequest {
  first_seen: string;
  last_seen: string;
  creative_variants?: number;
  est_impressions_low?: number;
  est_impressions_high?: number;
  engagement?: number;
  networks?: number;
  countries?: number;
  avg_ticket?: number | null;
  cvr?: number | null;
  ctr?: number | null;
  cpm?: number | null;
}

export interface EstimateResponse {
  longevity_days: number;
  est_impressions: number;
  est_daily_spend: number;
  est_daily_revenue: number;
  est_daily_profit: number;
  est_roas: number;
  est_roi_pct: number;
  winning_score: number;
  scaling_signal: string;
  confidence: number;
  notes: string[];
}

export interface NotifyRequest {
  event_id: string;
  type: string;
  plan?: string;
  user_id: string;
  email?: string | null;
  hour_local?: number;
  sent_today?: number;
  data?: Record<string, unknown>;
}

export interface NotifyResponse {
  suppressed: boolean;
  reason: string;
  delivered: string[];
  failed: string[];
}

const FALLBACK_API = "https://workers-py.vercel.app";
const API_URL = (process.env.NEXT_PUBLIC_API_URL || FALLBACK_API).replace(/\/$/, "");

/** Verdadeiro quando a env NEXT_PUBLIC_API_URL está definida. */
export const isApiConfigured = (): boolean => API_URL.length > 0;

async function apiFetch<T>(
  path: string,
  init?: RequestInit,
  timeoutMs = 8000,
): Promise<T | null> {
  if (!API_URL) return null;
  const ctrl = new AbortController();
  const timer = setTimeout(() => ctrl.abort(), timeoutMs);
  try {
    const res = await fetch(`${API_URL}${path}`, {
      ...init,
      signal: ctrl.signal,
      headers: {
        "Content-Type": "application/json",
        ...(init?.headers ?? {}),
      },
    });
    if (!res.ok) return null;
    return (await res.json()) as T;
  } catch {
    return null;
  } finally {
    clearTimeout(timer);
  }
}

export const getHealth = () => apiFetch<ApiHealth>("/health");

export const getVersion = async (): Promise<string | null> =>
  (await apiFetch<{ version: string }>("/v1/version"))?.version ?? null;

export const getEventTypes = async (): Promise<string[] | null> =>
  (await apiFetch<{ types: string[] }>("/v1/events/types"))?.types ?? null;

export const estimateOffer = (body: EstimateRequest) =>
  apiFetch<EstimateResponse>("/v1/offers/estimate", {
    method: "POST",
    body: JSON.stringify(body),
  });

export const postNotify = (body: NotifyRequest) =>
  apiFetch<NotifyResponse>("/v1/notify", {
    method: "POST",
    body: JSON.stringify(body),
  });

// --- Ofertas reais + métricas de mercado (backend /v1/offers, /v1/metrics) ---

export interface OfferMetrics {
  total: number;
  byNetwork: Record<string, number>;
  byNiche: Record<string, number>;
  bySignal: Record<string, number>;
  avgWinningScore: number;
  avgLongevityDays: number;
  avgRoiPct: number;
  avgDailyProfit: number;
  avgWinProb: number;
  scalingShare: number;
  topScaled: Array<{
    id?: string;
    headline?: string;
    advertiser?: string;
    network?: string;
    niche?: string;
    winningScore?: number;
    scalingSignal?: string;
    estRoiPct?: number;
    winProb?: number;
    estImpressions?: number;
  }>;
  generatedAt?: string;
}

export interface OffersQuery {
  niche?: string;
  network?: string;
  country?: string;
  limit?: number;
  simulate?: boolean;
}

function toQueryString(params: Record<string, string | number | boolean | undefined>): string {
  const sp = new URLSearchParams();
  for (const [k, v] of Object.entries(params)) {
    if (v !== undefined && v !== "") sp.set(k, String(v));
  }
  const s = sp.toString();
  return s ? `?${s}` : "";
}

/** Melhores / mais escaladas ofertas das Ad Libraries (enriquecidas com ROI/win-prob). */
export const getOffers = (params: OffersQuery = {}) =>
  apiFetch<{ count: number; offers: Offer[]; simulate: boolean }>(
    `/v1/offers${toQueryString(params as Record<string, string | number | boolean | undefined>)}`,
  );

/** Métricas de mercado agregadas (redes, nichos, sinais, ROI, top escalando). */
export const getMetrics = (params: { niche?: string; country?: string; simulate?: boolean } = {}) =>
  apiFetch<OfferMetrics>(
    `/v1/metrics${toQueryString(params as Record<string, string | number | boolean | undefined>)}`,
  );
