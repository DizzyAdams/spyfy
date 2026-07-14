"use client";

import { useEffect, useState } from "react";
import { motion } from "framer-motion";
import { TrendingUp, Activity, Target, Zap, Server } from "lucide-react";
import { OFFERS } from "@/lib/data";
import { getMetrics, isApiConfigured, type OfferMetrics } from "@/lib/api";
import { CountUp } from "../CountUp";
import { RadarChart } from "../illustrations/RadarChart";
import { scoreBand, formatNumber, cn } from "@/lib/utils";
import { RoiEstimator } from "./RoiEstimator";

// 14-day trend (synthetic)
const trend = [12, 18, 15, 22, 28, 24, 31, 35, 30, 42, 48, 44, 56, 63];

type TopRow = {
  id?: string;
  headline?: string;
  advertiser?: string;
  niche?: string;
  winningScore: number;
  estImpressions: number;
  estRoiPct?: number;
  winProb?: number;
};

export function AnalyticsDashboard() {
  const [metrics, setMetrics] = useState<OfferMetrics | null>(null);
  const [ready, setReady] = useState(false);

  useEffect(() => {
    let alive = true;
    if (!isApiConfigured()) return;
    getMetrics({ simulate: false })
      .then((m) => {
        if (alive && m) {
          setMetrics(m);
          setReady(true);
        }
      })
      .catch(() => {});
    return () => {
      alive = false;
    };
  }, []);

  const total = metrics?.total ?? 1240;
  const stats = [
    {
      icon: Activity,
      label: "Ofertas ativas (30d)",
      value: total,
      suffix: "",
      dec: 0,
      color: "#6E56CF",
    },
    {
      icon: TrendingUp,
      label: "ROI médio estimado",
      value: metrics?.avgRoiPct ?? 0,
      suffix: "%",
      dec: 1,
      color: "#22D3EE",
    },
    {
      icon: Target,
      label: "Longevidade média",
      value: metrics?.avgLongevityDays ?? 47,
      suffix: "d",
      dec: 0,
      color: "#16A34A",
    },
    {
      icon: Zap,
      label: "Win-prob média",
      value: (metrics?.avgWinProb ?? 0) * 100,
      suffix: "%",
      dec: 0,
      color: "#F97316",
    },
  ];

  const max = Math.max(...trend);
  const w = 520;
  const h = 180;
  const pts = trend.map((v, i) => [
    (i / (trend.length - 1)) * w,
    h - (v / max) * (h - 20) - 10,
  ]);
  const line = pts.map((p) => p.join(",")).join(" ");
  const area = `0,${h} ${line} ${w},${h}`;

  const top: TopRow[] = ready && (metrics?.topScaled?.length ?? 0) > 0
    ? metrics!.topScaled.map((o) => ({
        id: o.id,
        headline: o.headline,
        advertiser: o.advertiser,
        niche: o.niche,
        winningScore: o.winningScore ?? 0,
        estImpressions: o.estImpressions ?? 0,
        estRoiPct: o.estRoiPct,
        winProb: o.winProb,
      }))
    : [...OFFERS]
        .sort((a, b) => b.winningScore - a.winningScore)
        .slice(0, 5)
        .map((o) => ({
          id: o.id,
          headline: o.headline,
          advertiser: o.advertiser,
          niche: o.niche,
          winningScore: o.winningScore,
          estImpressions: o.estImpressions,
          estRoiPct: undefined,
          winProb: undefined,
        }));

  return (
    <div className="mx-auto max-w-6xl">
      <div className="mb-6">
        <div className="flex flex-wrap items-center justify-between gap-3">
          <h1 className="text-2xl font-bold tracking-tight">Market Analytics</h1>
          {isApiConfigured() && (
            <span
              className={cn("chip", ready ? "!text-[var(--success)]" : "!text-[var(--muted)]")}
              title="Backend SpyFy (FastAPI) — métricas de mercado ao vivo"
            >
              <Server size={13} />
              {ready ? `API · ${formatNumber(metrics?.total ?? 0)} ofertas` : "API…"}
            </span>
          )}
        </div>
        <p className="mt-1 text-sm text-muted">
          Tendências de nicho, saturação e concorrência
          {ready ? " com dados reais das Ad Libraries" : " (demo)"}.
        </p>
      </div>

      <div className="grid grid-cols-2 gap-4 lg:grid-cols-4">
        {stats.map((s, i) => (
          <motion.div
            key={s.label}
            initial={{ opacity: 0, y: 14 }}
            animate={{ opacity: 1, y: 0 }}
            transition={{ duration: 0.4, delay: i * 0.06 }}
            className="bento p-5"
          >
            <div className="mb-3 grid h-9 w-9 place-items-center rounded-lg" style={{ background: `${s.color}1f`, color: s.color }}>
              <s.icon size={18} />
            </div>
            <p className="text-2xl font-bold tracking-tight">
              <CountUp to={s.value} suffix={s.suffix} decimals={s.dec} />
            </p>
            <p className="mt-1 text-xs text-muted">{s.label}</p>
          </motion.div>
        ))}
      </div>

      <div className="mt-4 grid gap-4 lg:grid-cols-[1fr_1fr]">
        <div className="bento p-5">
          <h3 className="mb-1 text-sm font-semibold text-text">Trend radar — capacidades</h3>
          <p className="mb-2 text-xs text-muted">SpyFy vs. incumbentes (0–100)</p>
          <div className="flex justify-center">
            <RadarChart
              axes={[
                { label: "Multi-rede", value: 1 },
                { label: "Longevidade", value: 0.95 },
                { label: "VSL", value: 1 },
                { label: "Clona funil", value: 1 },
                { label: "IA", value: 0.9 },
                { label: "Tempo real", value: 1 },
              ]}
            />
          </div>
        </div>

        <div className="bento p-5">
          <h3 className="mb-1 text-sm font-semibold text-text">Ofertas escalando (14d)</h3>
          <p className="mb-4 text-xs text-muted">Detecção de sinal de crescimento por regressão</p>
          <svg viewBox={`0 0 ${w} ${h}`} className="w-full" role="img" aria-label="Tendência de ofertas escalando">
            <defs>
              <linearGradient id="trendG" x1="0" y1="0" x2="0" y2="1">
                <stop offset="0" stopColor="#6E56CF" stopOpacity="0.4" />
                <stop offset="1" stopColor="#6E56CF" stopOpacity="0" />
              </linearGradient>
            </defs>
            <motion.polygon points={area} fill="url(#trendG)" initial={{ opacity: 0 }} whileInView={{ opacity: 1 }} viewport={{ once: true }} transition={{ duration: 0.8 }} />
            <motion.polyline
              points={line}
              fill="none"
              stroke="#6E56CF"
              strokeWidth={2.5}
              strokeLinejoin="round"
              strokeLinecap="round"
              initial={{ pathLength: 0 }}
              whileInView={{ pathLength: 1 }}
              viewport={{ once: true }}
              transition={{ duration: 1.2, ease: [0.22, 1, 0.36, 1] }}
            />
          </svg>
        </div>
      </div>

      <div className="bento mt-4 p-5">
        <h3 className="mb-4 text-sm font-semibold text-text">Top ofertas por winning score</h3>
        <div className="space-y-2">
          {top.map((o, i) => {
            const band = scoreBand(o.winningScore);
            return (
              <div key={o.id} className="flex items-center gap-3 rounded-lg border border-border bg-surface/40 px-3 py-2.5">
                <span className="grid h-7 w-7 place-items-center rounded-lg bg-primary/15 text-xs font-bold text-primary">{i + 1}</span>
                <div className="min-w-0 flex-1">
                  <p className="truncate text-sm font-medium text-text">{o.headline}</p>
                  <p className="text-xs text-muted">{o.advertiser} · {o.niche}</p>
                </div>
                <span className="hidden text-xs text-muted sm:block">{formatNumber(o.estImpressions)} impr.</span>
                {o.estRoiPct !== undefined && (
                  <span className="hidden text-xs font-semibold text-[var(--success)] sm:block">
                    ROI {o.estRoiPct}%
                  </span>
                )}
                {o.winProb !== undefined && (
                  <span className="hidden text-xs text-muted sm:block">
                    win {(o.winProb * 100).toFixed(0)}%
                  </span>
                )}
                <span className="w-28">
                  <span className={cn("inline-flex items-center gap-1 rounded-full px-2 py-1 text-xs font-semibold")} style={{ color: band.color, background: `color-mix(in srgb, ${band.color} 16%, transparent)` }}>
                    {band.label} · {o.winningScore.toFixed(1)}
                  </span>
                </span>
              </div>
            );
          })}
        </div>
      </div>

      <div className="mt-4 grid gap-4 lg:grid-cols-[1fr_1.2fr]">
        {ready && metrics?.bySignal && (
          <div className="bento p-5">
            <h3 className="mb-1 text-sm font-semibold text-text">Distribuição de sinais</h3>
            <p className="mb-4 text-xs text-muted">Cold · Aquecendo · Escalando · Hot (amostra ao vivo)</p>
            <div className="space-y-2.5">
              {(["hot", "scaling", "warming", "cold"] as const).map((k) => {
                const v = metrics!.bySignal[k] ?? 0;
                const pct = total ? Math.round((v / total) * 100) : 0;
                const color =
                  k === "hot" ? "#F97316" : k === "scaling" ? "#22D3EE" : k === "warming" ? "#FACC15" : "#94A3B8";
                const label = k === "hot" ? "🔥 Hot" : k === "scaling" ? "📈 Escalando" : k === "warming" ? "🌡️ Aquecendo" : "❄️ Fria";
                return (
                  <div key={k} className="flex items-center gap-3">
                    <span className="w-28 shrink-0 text-xs text-muted">{label}</span>
                    <span className="relative h-2.5 flex-1 overflow-hidden rounded-full bg-border/40">
                      <motion.span
                        className="absolute inset-y-0 left-0 rounded-full"
                        style={{ background: color }}
                        initial={{ width: 0 }}
                        whileInView={{ width: `${pct}%` }}
                        viewport={{ once: true }}
                        transition={{ duration: 0.7, ease: [0.22, 1, 0.36, 1] }}
                      />
                    </span>
                    <span className="w-10 shrink-0 text-right font-mono text-xs tabular-nums text-text">{v}</span>
                  </div>
                );
              })}
            </div>
            {metrics?.scalingShare !== undefined && (
              <p className="mt-4 text-xs text-muted">
                <span className="font-semibold text-[var(--success)]">
                  {(metrics.scalingShare * 100).toFixed(0)}%
                </span>{" "}
                das ofertas estão em fase de escala (scaling/hot).
              </p>
            )}
          </div>
        )}

        <div className="bento p-5">
          <RoiEstimator />
        </div>
      </div>
    </div>
  );
}
