"use client";

import { useId } from "react";
import { motion, useReducedMotion } from "framer-motion";
import { EXPOCSS } from "@/lib/motion";
import { cn } from "@/lib/utils";

export interface FunnelStep {
  label: string;
  /** Optional tech/medium annotation shown as a mono metric (e.g. "ClickFunnels"). */
  stack?: string;
  /** Absolute volume or score at this stage — sizes the band. */
  value?: number;
  /** Conversion % from the previous stage (0..100). Overrides the derived ratio. */
  pct?: number;
}

export interface FunnelDiagramProps {
  steps: FunnelStep[];
  className?: string;
}

const MAX_HALF = 42;
const BAND_H = 16;
const GAP = 13;
const TOP_PAD = 12;
const VB_W = 200;
const CX = VB_W / 2;

// Premium segmented funnel: Anúncio → LP → VSL → Checkout → Upsell.
// Widths scale from stage volume; conversion % is rendered between bands.
export function FunnelDiagram({ steps, className }: FunnelDiagramProps) {
  const reduce = useReducedMotion();
  const uid = useId().replace(/[:]/g, "");
  const gradId = `funnel-grad-${uid}`;

  const n = steps.length;

  if (!steps || n === 0) {
    return (
      <div
        className={cn("flex items-center justify-center py-10 text-sm text-muted", className)}
        role="img"
        aria-label="Funil de conversão — sem etapas"
      >
        Sem etapas de funil ainda.
      </div>
    );
  }

  const H = TOP_PAD * 2 + n * BAND_H + (n - 1) * GAP;

  const maxVal = steps.some((s) => typeof s.value === "number")
    ? Math.max(...steps.map((s) => s.value ?? 0), 1)
    : 1;

  let prevHalf = MAX_HALF;
  const half = steps.map((s, i) => {
    if (i === 0) return MAX_HALF;
    if (typeof s.value === "number") {
      const h = Math.max(0.08, (s.value / maxVal) * MAX_HALF);
      prevHalf = h;
      return h;
    }
    const ret = typeof s.pct === "number" ? s.pct / 100 : 0.7;
    prevHalf = Math.max(0.08 * MAX_HALF, prevHalf * ret);
    return prevHalf;
  });

  const conv = steps.map((s, i) => {
    if (i === 0) return null;
    if (typeof s.value === "number" && typeof steps[i - 1].value === "number") {
      return Math.round((s.value / (steps[i - 1].value || 1)) * 100);
    }
    if (typeof s.pct === "number") return Math.round(s.pct);
    return Math.round((half[i] / (half[i - 1] || 1)) * 100);
  });

  const barY = (i: number) => TOP_PAD + i * (BAND_H + GAP);

  return (
    <div className={cn("w-full", className)}>
      <svg
        viewBox={`0 0 ${VB_W} ${H}`}
        width="100%"
        style={{ height: "auto", display: "block" }}
        preserveAspectRatio="xMidYMid meet"
        role="img"
        aria-label={`Funil de conversão com ${n} etapas`}
      >
        <title>Funil de conversão</title>
        <defs>
          <linearGradient id={gradId} gradientUnits="userSpaceOnUse" x1="0" y1={TOP_PAD} x2="0" y2={H - TOP_PAD}>
            <stop offset="0%" stopColor="var(--violet)" />
            <stop offset="100%" stopColor="var(--cyan)" />
          </linearGradient>
        </defs>

        {/* flow spine */}
        <line
          x1={CX}
          y1={barY(0) + BAND_H / 2}
          x2={CX}
          y2={barY(n - 1) + BAND_H / 2}
          stroke="var(--border)"
          strokeWidth={0.6}
          strokeDasharray="1 3"
        />

        {/* stages */}
        {steps.map((s, i) => {
          const y = barY(i);
          const w = half[i] * 2;
          return (
            <g key={i}>
              <motion.rect
                x={CX - half[i]}
                y={y}
                width={w}
                height={BAND_H}
                rx={BAND_H / 2}
                fill={`url(#${gradId})`}
                fillOpacity={0.9}
                stroke="var(--border-strong)"
                strokeWidth={0.6}
                initial={reduce ? { scaleX: 1, opacity: 1 } : { scaleX: 0, opacity: 0 }}
                whileInView={{ scaleX: 1, opacity: 1 }}
                viewport={{ once: true }}
                transition={{ duration: 0.7, ease: EXPOCSS, delay: i * 0.09 }}
                style={{ transformBox: "fill-box", transformOrigin: "center" }}
              />
              <text
                x={CX - MAX_HALF - 7}
                y={y + BAND_H / 2}
                textAnchor="end"
                dominantBaseline="central"
                fill="var(--text)"
                fontSize={5}
                className="font-display"
              >
                <tspan fill="var(--faint)" fontFamily="var(--font-mono)">
                  {String(i + 1).padStart(2, "0")}{" "}
                </tspan>
                {s.label}
              </text>
              <text
                x={CX + MAX_HALF + 7}
                y={y + BAND_H / 2}
                textAnchor="start"
                dominantBaseline="central"
                fill="var(--muted)"
                fontSize={4}
                fontFamily="var(--font-mono)"
              >
                {s.stack ?? "—"}
              </text>
            </g>
          );
        })}

        {/* conversion markers between stages */}
        {conv.map((c, i) =>
          i === 0 || c == null ? null : (
            <motion.g
              key={`c-${i}`}
              initial={reduce ? { opacity: 1 } : { opacity: 0 }}
              whileInView={{ opacity: 1 }}
              viewport={{ once: true }}
              transition={{ duration: 0.5, delay: 0.25 + i * 0.09 }}
            >
              <path
                d={`M${CX} ${barY(i - 1) + BAND_H + 1} L${CX} ${barY(i) - 1} M${CX - 2} ${barY(i) - 3.5} L${CX} ${barY(i) - 1} L${CX + 2} ${barY(i) - 3.5}`}
                stroke="var(--muted)"
                strokeWidth={0.7}
                fill="none"
                strokeLinecap="round"
                strokeLinejoin="round"
              />
              <text
                x={CX + 6}
                y={barY(i - 1) + BAND_H + GAP / 2}
                textAnchor="start"
                dominantBaseline="central"
                fill="var(--muted)"
                fontSize={3.6}
                fontFamily="var(--font-mono)"
              >
                {c}%
              </text>
            </motion.g>
          )
        )}
      </svg>
    </div>
  );
}
