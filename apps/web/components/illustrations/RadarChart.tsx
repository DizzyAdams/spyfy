"use client";

import { useId, useState } from "react";
import { motion, useReducedMotion } from "framer-motion";
import { EXPOCSS } from "@/lib/motion";
import { cn } from "@/lib/utils";

export interface RadarAxis {
  /** Axis name, e.g. "Longebilidade". */
  label: string;
  /** Normalized magnitude, 0..1. Values are clamped to [0,1] for rendering. */
  value: number;
}

export interface RadarChartProps {
  axes: RadarAxis[];
  /** Optional solid override for stroke + vertices (default = violet→cyan duotone). */
  color?: string;
  size?: number;
  className?: string;
}

const RINGS = [0.2, 0.4, 0.6, 0.8, 1];
const clamp01 = (v: number) => Math.min(1, Math.max(0, v));

// Premium animated radar / spider chart for the analytics comparison view.
export function RadarChart({ axes, color, size = 260, className }: RadarChartProps) {
  const reduce = useReducedMotion();
  const uid = useId().replace(/[:]/g, "");
  const fillId = `radar-fill-${uid}`;
  const strokeId = `radar-stroke-${uid}`;
  const glowId = `radar-glow-${uid}`;

  const cx = size / 2;
  const cy = size / 2;
  const pad = size * 0.17;
  const r = size / 2 - pad;
  const n = axes.length;

  const pointAt = (i: number, radius: number): [number, number] => {
    const a = -Math.PI / 2 + (2 * Math.PI * i) / Math.max(n, 1);
    return [cx + Math.cos(a) * radius, cy + Math.sin(a) * radius];
  };

  const ringPoints = (level: number) =>
    axes.map((_, i) => pointAt(i, r * level).join(",")).join(" ");

  const dataPoints = axes.map((ax, i) => pointAt(i, r * clamp01(ax.value)));
  const dataPolygon = dataPoints.map((p) => p.join(",")).join(" ");

  if (!axes || n < 3) {
    return (
      <div
        className={cn("flex items-center justify-center", className)}
        style={{ width: size, height: size }}
        role="img"
        aria-label="Radar de capacidades — sem dados suficientes"
      >
        <svg width={size} height={size} viewBox={`0 0 ${size} ${size}`} className="select-none">
          <circle cx={cx} cy={cy} r={r} fill="none" stroke="var(--border)" strokeDasharray="3 5" />
          <text
            x={cx}
            y={cy}
            textAnchor="middle"
            dominantBaseline="middle"
            fill="var(--muted)"
            fontSize={11}
            fontFamily="var(--font-mono)"
          >
            sem dados
          </text>
        </svg>
      </div>
    );
  }

  const stroke = color ?? `url(#${strokeId})`;
  const fill = color ?? `url(#${fillId})`;
  const vertexStroke = color ?? "var(--cyan)";

  return (
    <svg
      width={size}
      height={size}
      viewBox={`0 0 ${size} ${size}`}
      className={cn("block select-none", className)}
      style={{ overflow: "visible" }}
      role="img"
      aria-label={`Radar de capacidades com ${n} eixos`}
    >
      <title>Radar de capacidades</title>
      <defs>
        <linearGradient id={fillId} x1="0%" y1="100%" x2="100%" y2="0%">
          <stop offset="0%" stopColor="var(--violet)" stopOpacity={0.5} />
          <stop offset="100%" stopColor="var(--cyan)" stopOpacity={0.1} />
        </linearGradient>
        <linearGradient id={strokeId} x1="0%" y1="100%" x2="100%" y2="0%">
          <stop offset="0%" stopColor="var(--violet)" />
          <stop offset="100%" stopColor="var(--cyan)" />
        </linearGradient>
        <radialGradient id={glowId} cx="50%" cy="50%" r="50%">
          <stop offset="0%" stopColor="var(--violet)" stopOpacity={0.2} />
          <stop offset="100%" stopColor="var(--violet)" stopOpacity={0} />
        </radialGradient>
      </defs>

      {/* atmospheric core glow */}
      <circle cx={cx} cy={cy} r={r} fill={`url(#${glowId})`} />

      {/* concentric grid */}
      {RINGS.map((level) => (
        <polygon
          key={level}
          points={ringPoints(level)}
          fill="none"
          stroke="var(--border)"
          strokeWidth={level === 1 ? 1.25 : 1}
          opacity={level === 1 ? 0.9 : 0.5}
        />
      ))}

      {/* spokes */}
      {axes.map((_, i) => {
        const [x, y] = pointAt(i, r);
        return (
          <line key={i} x1={cx} y1={cy} x2={x} y2={y} stroke="var(--border)" strokeWidth={1} opacity={0.5} />
        );
      })}

      {/* data fill (fade in) */}
      <motion.polygon
        points={dataPolygon}
        fill={fill}
        fillOpacity={color ? 0.18 : 1}
        stroke="none"
        initial={reduce ? { opacity: 1 } : { opacity: 0 }}
        whileInView={{ opacity: 1 }}
        viewport={{ once: true }}
        transition={{ duration: 0.8, ease: EXPOCSS, delay: 0.15 }}
      />

      {/* data outline (draw-in via pathLength) */}
      <motion.polygon
        points={dataPolygon}
        fill="none"
        stroke={stroke}
        strokeWidth={2}
        strokeLinejoin="round"
        initial={reduce ? { pathLength: 1, opacity: 1 } : { pathLength: 0, opacity: 0 }}
        whileInView={{ pathLength: 1, opacity: 1 }}
        viewport={{ once: true }}
        transition={{ duration: 1.1, ease: EXPOCSS }}
      />

      {/* axis labels */}
      {axes.map((ax, i) => {
        const [lx, ly] = pointAt(i, r + pad * 0.62);
        const anchor = lx > cx + 4 ? "start" : lx < cx - 4 ? "end" : "middle";
        const baseline = ly < cy ? "alphabetic" : ly > cy ? "hanging" : "middle";
        const dy = ly < cy ? -2 : ly > cy ? 2 : 0;
        return (
          <text
            key={`l-${i}`}
            x={lx}
            y={ly + dy}
            textAnchor={anchor}
            dominantBaseline={baseline}
            fill="var(--muted)"
            fontSize={11}
            className="font-display"
          >
            {ax.label}
          </text>
        );
      })}

      {/* vertices + tooltips */}
      {dataPoints.map(([x, y], i) => (
        <Vertex
          key={`v-${i}`}
          x={x}
          y={y}
          label={axes[i].label}
          value={axes[i].value}
          stroke={vertexStroke}
          reduce={!!reduce}
          delay={0.55 + i * 0.07}
        />
      ))}
    </svg>
  );
}

function Vertex({
  x,
  y,
  label,
  value,
  stroke,
  reduce,
  delay,
}: {
  x: number;
  y: number;
  label: string;
  value: number;
  stroke: string;
  reduce: boolean;
  delay: number;
}) {
  const [active, setActive] = useState(false);
  const pct = Math.round(clamp01(value) * 100);
  const above = y > 46;
  const boxY = above ? y - 36 : y + 12;
  const lineEnd = above ? y - 11 : y + 11;
  const short = label.length > 13 ? `${label.slice(0, 12)}…` : label;

  return (
    <g
      tabIndex={0}
      role="button"
      aria-label={`${label}: ${pct}%`}
      style={{ cursor: "pointer" }}
      onMouseEnter={() => setActive(true)}
      onMouseLeave={() => setActive(false)}
      onFocus={() => setActive(true)}
      onBlur={() => setActive(false)}
    >
      <motion.circle
        cx={x}
        cy={y}
        r={active ? 5 : 3.5}
        fill="var(--bg)"
        stroke={stroke}
        strokeWidth={2}
        initial={reduce ? { scale: 1, opacity: 1 } : { scale: 0, opacity: 0 }}
        whileInView={{ scale: 1, opacity: 1 }}
        viewport={{ once: true }}
        animate={{ scale: active ? 1.15 : 1 }}
        transition={{ duration: 0.4, ease: EXPOCSS, delay }}
        style={{ transformBox: "fill-box", transformOrigin: "center" }}
      />
      {active && (
        <g pointerEvents="none">
          <line x1={x} y1={y} x2={x} y2={lineEnd} stroke={stroke} strokeWidth={1} opacity={0.5} />
          <rect x={x - 32} y={boxY} width={64} height={24} rx={5} fill="var(--surface-3)" stroke="var(--border-strong)" />
          <text
            x={x}
            y={boxY + 9}
            textAnchor="middle"
            dominantBaseline="middle"
            fill="var(--muted)"
            fontSize={8}
            fontFamily="var(--font-mono)"
          >
            {short}
          </text>
          <text
            x={x}
            y={boxY + 19}
            textAnchor="middle"
            dominantBaseline="middle"
            fill="var(--text)"
            fontSize={11}
            fontFamily="var(--font-mono)"
          >
            {pct}%
          </text>
        </g>
      )}
      <circle cx={x} cy={y} r={12} fill="transparent" pointerEvents="all" />
    </g>
  );
}
