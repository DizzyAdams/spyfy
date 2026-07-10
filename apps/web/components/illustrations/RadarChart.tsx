"use client";

import { motion } from "framer-motion";

interface Axis {
  label: string;
  value: number; // 0..1
}

// Lightweight animated radar chart (SVG) for the analytics comparison.
export function RadarChart({
  axes,
  color = "#6E56CF",
  size = 240,
}: {
  axes: Axis[];
  color?: string;
  size?: number;
}) {
  const cx = size / 2;
  const cy = size / 2;
  const r = size / 2 - 34;
  const n = axes.length;
  const pointAt = (i: number, radius: number) => {
    const angle = (Math.PI * 2 * i) / n - Math.PI / 2;
    return [cx + Math.cos(angle) * radius, cy + Math.sin(angle) * radius] as const;
  };
  const dataPts = axes.map((a, i) => pointAt(i, r * Math.max(0.05, a.value)));
  const polygon = dataPts.map((p) => p.join(",")).join(" ");

  return (
    <svg width={size} height={size} viewBox={`0 0 ${size} ${size}`} role="img" aria-label="Radar de capacidades">
      {[0.25, 0.5, 0.75, 1].map((ring) => (
        <polygon
          key={ring}
          points={axes.map((_, i) => pointAt(i, r * ring).join(",")).join(" ")}
          fill="none"
          stroke="rgba(255,255,255,0.08)"
          strokeWidth={1}
        />
      ))}
      {axes.map((_, i) => {
        const [x, y] = pointAt(i, r);
        return <line key={i} x1={cx} y1={cy} x2={x} y2={y} stroke="rgba(255,255,255,0.08)" strokeWidth={1} />;
      })}
      <motion.polygon
        points={polygon}
        fill={color}
        fillOpacity={0.18}
        stroke={color}
        strokeWidth={2}
        initial={{ opacity: 0, scale: 0.7 }}
        whileInView={{ opacity: 1, scale: 1 }}
        viewport={{ once: true }}
        transition={{ duration: 0.7, ease: [0.22, 1, 0.36, 1] }}
        style={{ transformOrigin: "center" }}
      />
      {axes.map((a, i) => {
        const [x, y] = pointAt(i, r + 16);
        return (
          <text key={i} x={x} y={y} fill="var(--muted)" fontSize={10} textAnchor="middle" dominantBaseline="middle">
            {a.label}
          </text>
        );
      })}
    </svg>
  );
}
