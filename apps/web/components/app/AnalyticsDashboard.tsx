"use client";

import { motion } from "framer-motion";
import { TrendingUp, Activity, Target, Zap } from "lucide-react";
import { OFFERS } from "@/lib/data";
import { CountUp } from "../CountUp";
import { RadarChart } from "../illustrations/RadarChart";
import { scoreBand, formatNumber, cn } from "@/lib/utils";

const stats = [
  { icon: Activity, label: "Ofertas ativas (30d)", value: 1240, suffix: "", dec: 0, color: "#6E56CF" },
  { icon: TrendingUp, label: "Novas esta semana", value: 312, suffix: "", dec: 0, color: "#22D3EE" },
  { icon: Target, label: "Longevidade média", value: 47, suffix: "d", dec: 0, color: "#16A34A" },
  { icon: Zap, label: "Clonagens hoje", value: 38, suffix: "", dec: 0, color: "#F97316" },
];

// 14-day trend (synthetic)
const trend = [12, 18, 15, 22, 28, 24, 31, 35, 30, 42, 48, 44, 56, 63];

export function AnalyticsDashboard() {
  const max = Math.max(...trend);
  const w = 520;
  const h = 180;
  const pts = trend.map((v, i) => [(i / (trend.length - 1)) * w, h - (v / max) * (h - 20) - 10]);
  const line = pts.map((p) => p.join(",")).join(" ");
  const area = `0,${h} ${line} ${w},${h}`;

  const top = [...OFFERS].sort((a, b) => b.winningScore - a.winningScore).slice(0, 5);

  return (
    <div className="mx-auto max-w-6xl">
      <div className="mb-6">
        <h1 className="text-2xl font-bold tracking-tight">Market Analytics</h1>
        <p className="mt-1 text-sm text-muted">Tendências de nicho, saturação e concorrência em tempo quase real.</p>
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
    </div>
  );
}
