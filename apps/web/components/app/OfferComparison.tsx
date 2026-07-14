"use client";

import { motion, useReducedMotion } from "framer-motion";
import {
  Gauge,
  CalendarDays,
  Eye,
  Radio,
  Monitor,
  Building2,
  Globe,
  TrendingUp,
  ArrowLeftRight,
  BarChartHorizontal,
} from "lucide-react";
import { Offer, NETWORKS, OFFERS } from "@/lib/data";
import { scoreBand, formatNumber, scaleIndex, spendBand, cn } from "@/lib/utils";
import { EXPOCSS, fadeIn, staggerContainer, revealUp } from "@/lib/motion";

/* ── types ─────────────────────────────────────────── */

interface BarProps {
  label: string;
  value: number;
  max: number;
  color: string;
  suffix?: string;
}

interface OfferComparisonProps {
  offers?: Offer[];
}

/* ── helpers ────────────────────────────────────────── */

const FORMAT_LABELS: Record<string, string> = {
  video: "Vídeo",
  image: "Imagem",
  carousel: "Carrossel",
};

const NET_LABELS: Record<string, string> = {};
NETWORKS.forEach((n) => {
  NET_LABELS[n.key] = n.label;
});

const NET_COLORS: Record<string, string> = {};
NETWORKS.forEach((n) => {
  NET_COLORS[n.key] = n.color;
});

/** Normalize a metric so the best offer gets 100% bar width. */
function normalised(offers: Offer[], fn: (o: Offer) => number): number[] {
  const vals = offers.map(fn);
  const max = Math.max(...vals, 1);
  return vals.map((v) => (v / max) * 100);
}

/* ── sub-components ────────────────────────────────── */

function StatBar({ label, value, max, color, suffix = "" }: BarProps) {
  const pct = max > 0 ? (value / max) * 100 : 0;
  return (
    <div className="flex flex-col gap-1.5">
      <div className="flex items-center justify-between text-xs">
        <span className="text-muted">{label}</span>
        <span className="font-mono tabular-nums text-text">
          {formatNumber(value)}
          {suffix}
        </span>
      </div>
      <div className="h-2 overflow-hidden rounded-full bg-bg">
        <motion.div
          initial={{ width: 0 }}
          animate={{ width: `${pct}%` }}
          transition={{ duration: 0.8, ease: EXPOCSS, delay: 0.1 }}
          className="h-full rounded-full"
          style={{ background: color }}
        />
      </div>
    </div>
  );
}

function Divider() {
  return <div className="mx-3 hidden w-px self-stretch bg-border lg:block" aria-hidden />;
}

function OfferColumn({
  offer,
  index,
  maxScore,
  maxLong,
  maxImp,
}: {
  offer: Offer;
  index: number;
  maxScore: number;
  maxLong: number;
  maxImp: number;
}) {
  const reduce = useReducedMotion();
  const band = scoreBand(offer.winningScore);
  const net = NETWORKS.find((n) => n.key === offer.network);
  const scale = scaleIndex(offer);
  const spend = spendBand(offer.estImpressions, offer.longevityDays);

  return (
    <motion.div
      variants={staggerContainer}
      initial="hidden"
      animate="show"
      className="flex flex-1 flex-col gap-5 rounded-2xl border border-border bg-surface/40 p-5"
    >
      {/* Header — offer identity */}
      <div className="flex items-start justify-between gap-3">
        <div className="min-w-0 flex-1">
          <h3 className="truncate font-display text-base font-semibold leading-snug tracking-tight text-text">
            {offer.headline}
          </h3>
          <div className="mt-2 flex flex-wrap items-center gap-2">
            <span className="chip" style={{ color: net?.color }}>
              <span className="h-1.5 w-1.5 rounded-full" style={{ background: net?.color }} />
              {NET_LABELS[offer.network] ?? offer.network}
            </span>
            <span className="chip">{FORMAT_LABELS[offer.format] ?? offer.format}</span>
            <span className="chip">{offer.country}</span>
          </div>
        </div>
        {/* Score badge */}
        <span
          className="inline-flex shrink-0 items-center gap-1.5 rounded-full border border-white/10 bg-black/45 px-3 py-1.5 text-[11px] font-semibold backdrop-blur-md"
          style={{ color: band.color }}
        >
          <Gauge size={13} aria-hidden />
          {band.label}
          <span className="font-mono tabular-nums">{offer.winningScore.toFixed(1)}</span>
        </span>
      </div>

      {/* Advertiser + scale index row */}
      <div className="flex items-center justify-between gap-3 text-xs">
        <span className="flex items-center gap-1.5 text-muted">
          <Building2 size={13} className="text-faint" aria-hidden />
          {offer.advertiser}
        </span>
        <span
          className="chip"
          style={{
            color: "var(--violet-soft)",
            borderColor: "rgba(167, 139, 250, 0.35)",
            background: "rgba(167, 139, 250, 0.12)",
          }}
        >
          <TrendingUp size={12} aria-hidden />
          Escala {scale}
        </span>
      </div>

      {/* Metric bars */}
      <div className="flex flex-col gap-3.5">
        <StatBar
          label="Winning Score"
          value={offer.winningScore}
          max={maxScore}
          color={band.color}
        />
        <StatBar
          label="Longevidade"
          value={offer.longevityDays}
          max={maxLong}
          color="var(--violet-soft)"
          suffix="d"
        />
        <StatBar
          label="Impressões"
          value={offer.estImpressions}
          max={maxImp}
          color="var(--warning)"
        />
      </div>

      {/* Spend + longevity chip */}
      <div className="flex items-center justify-between gap-3 rounded-xl border border-border bg-bg/40 px-3.5 py-2.5 text-xs">
        <span className="flex items-center gap-1.5 text-muted">
          <CalendarDays size={13} className="text-faint" aria-hidden />
          <span className="font-mono tabular-nums text-text">{offer.longevityDays}d</span>
          ativa
        </span>
        <span className="font-mono text-[11px] text-faint tabular-nums">
          ~R{formatNumber(spend.daily)}/dia · {spend.label}
        </span>
      </div>
    </motion.div>
  );
}

/* ── main component ────────────────────────────────── */

export function OfferComparison({ offers = OFFERS.slice(0, 3) }: OfferComparisonProps) {
  const reduce = useReducedMotion();

  const maxScore = Math.max(...offers.map((o) => o.winningScore));
  const maxLong = Math.max(...offers.map((o) => o.longevityDays));
  const maxImp = Math.max(...offers.map((o) => o.estImpressions));

  return (
    <motion.section
      initial={reduce ? false : "hidden"}
      animate="show"
      variants={revealUp}
      className="flex flex-col gap-6"
    >
      {/* Section header */}
      <div className="flex items-center gap-3">
        <div className="flex h-9 w-9 items-center justify-center rounded-xl border border-border bg-surface/60">
          <ArrowLeftRight size={17} className="text-violet-soft" />
        </div>
        <div>
          <h1 className="font-display text-lg font-semibold text-text">
            Comparação de Ofertas
          </h1>
          <p className="text-sm text-muted">
            Side-by-side das ofertas com maior score — métricas, rede e performance
          </p>
        </div>
      </div>

      {/* Legend bar */}
      <div className="flex flex-wrap items-center gap-4 rounded-xl border border-border bg-surface/30 px-4 py-2.5 text-xs text-muted">
        <span className="flex items-center gap-1.5">
          <BarChartHorizontal size={13} className="text-violet-soft" aria-hidden />
          Barras proporcionais ao líder da categoria
        </span>
        <span className="flex items-center gap-1.5">
          <Radio size={13} className="text-faint" aria-hidden />
          Dados baseados nas últimas 24h
        </span>
      </div>

      {/* Columns */}
      <div className="flex flex-col gap-4 lg:flex-row">
        {offers.map((offer, i) => (
          <OfferColumn
            key={offer.id}
            offer={offer}
            index={i}
            maxScore={maxScore}
            maxLong={maxLong}
            maxImp={maxImp}
          />
        ))}
      </div>

      {/* Summary table */}
      <motion.div
        variants={fadeIn}
        className="overflow-hidden rounded-2xl border border-border bg-surface/30"
      >
        <div className="border-b border-border bg-surface/40 px-5 py-3">
          <h2 className="flex items-center gap-2 font-display text-sm font-semibold text-text">
            <Eye size={15} className="text-violet-soft" aria-hidden />
            Resumo Comparativo
          </h2>
        </div>
        <div className="overflow-x-auto">
          <table className="w-full text-left text-sm">
            <thead>
              <tr className="border-b border-border text-xs font-medium uppercase tracking-wider text-faint">
                <th className="px-5 py-3">Métrica</th>
                {offers.map((o) => (
                  <th key={o.id} className="px-5 py-3 font-medium">
                    {o.headline.length > 30
                      ? o.headline.slice(0, 30) + "…"
                      : o.headline}
                  </th>
                ))}
              </tr>
            </thead>
            <tbody className="divide-y divide-border">
              <Row label="Advertiser" values={offers.map((o) => o.advertiser)} />
              <Row label="Rede" values={offers.map((o) => NET_LABELS[o.network] ?? o.network)} />
              <Row label="Formato" values={offers.map((o) => FORMAT_LABELS[o.format] ?? o.format)} />
              <Row label="País" values={offers.map((o) => o.country)} />
              <Row
                label="Winning Score"
                values={offers.map((o) => o.winningScore.toFixed(1))}
                highlight
              />
              <Row
                label="Longevidade"
                values={offers.map((o) => `${o.longevityDays} dias`)}
              />
              <Row
                label="Impressões"
                values={offers.map((o) => formatNumber(o.estImpressions))}
              />
              <Row
                label="Índice de Escala"
                values={offers.map((o) => scaleIndex(o).toFixed(1))}
              />
              <Row
                label="Gasto Estimado"
                values={offers.map((o) => {
                  const sp = spendBand(o.estImpressions, o.longevityDays);
                  return `~R$${formatNumber(sp.daily)}/dia`;
                })}
              />
            </tbody>
          </table>
        </div>
      </motion.div>
    </motion.section>
  );
}

function Row({
  label,
  values,
  highlight = false,
}: {
  label: string;
  values: string[];
  highlight?: boolean;
}) {
  return (
    <tr className={cn("transition-colors hover:bg-surface/30", highlight && "bg-accent/[0.03]")}>
      <td className="px-5 py-3 font-medium text-text">{label}</td>
      {values.map((v, i) => (
        <td
          key={i}
          className={cn(
            "px-5 py-3 font-mono text-xs tabular-nums",
            highlight ? "text-text" : "text-muted"
          )}
        >
          {v}
        </td>
      ))}
    </tr>
  );
}

export default OfferComparison;
