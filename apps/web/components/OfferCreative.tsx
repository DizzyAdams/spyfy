"use client";

import { motion } from "framer-motion";

// Generated SVG "creative" thumbnail — stands in for the ad creative image.
export function OfferCreative({
  hue,
  gradient,
  label,
  format,
  className = "",
}: {
  hue: number;
  gradient: [string, string];
  label: string;
  format: string;
  className?: string;
}) {
  const id = `g${hue}`;
  return (
    <div className={`relative overflow-hidden ${className}`} style={{ background: "#0b0d12" }}>
      <svg viewBox="0 0 400 240" className="h-full w-full" preserveAspectRatio="xMidYMid slice" aria-hidden="true">
        <defs>
          <linearGradient id={id} x1="0" y1="0" x2="1" y2="1">
            <stop offset="0" stopColor={gradient[0]} />
            <stop offset="1" stopColor={gradient[1]} />
          </linearGradient>
        </defs>
        <rect width="400" height="240" fill={`url(#${id})`} opacity="0.9" />
        <circle cx="320" cy="50" r="90" fill="#fff" opacity="0.08" />
        <circle cx="70" cy="210" r="70" fill="#000" opacity="0.12" />
        {/* abstract bars */}
        <g opacity="0.25" fill="#fff">
          <rect x="40" y="150" width="18" height="50" rx="4" />
          <rect x="66" y="120" width="18" height="80" rx="4" />
          <rect x="92" y="100" width="18" height="100" rx="4" />
          <rect x="118" y="135" width="18" height="65" rx="4" />
        </g>
        <motion.g
          initial={{ opacity: 0.4 }}
          animate={{ opacity: [0.4, 0.7, 0.4] }}
          transition={{ duration: 3, repeat: Infinity, ease: "easeInOut" }}
        >
          <circle cx="300" cy="170" r="46" fill="#fff" opacity="0.16" />
        </motion.g>
      </svg>
      <span className="absolute left-3 top-3 chip !bg-black/40 !text-white">{format}</span>
      <span className="absolute bottom-3 left-3 right-3 truncate text-sm font-semibold text-white drop-shadow">
        {label}
      </span>
    </div>
  );
}
