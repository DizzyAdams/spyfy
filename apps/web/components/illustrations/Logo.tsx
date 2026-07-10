"use client";

import { motion } from "framer-motion";

export function Logo({ size = 28 }: { size?: number }) {
  return (
    <span className="inline-flex items-center gap-2 font-semibold tracking-tight">
      <motion.svg
        width={size}
        height={size}
        viewBox="0 0 32 32"
        fill="none"
        initial={{ rotate: -8, opacity: 0 }}
        animate={{ rotate: 0, opacity: 1 }}
        transition={{ duration: 0.5, ease: [0.22, 1, 0.36, 1] }}
        aria-hidden="true"
      >
        <defs>
          <linearGradient id="sf-g" x1="0" y1="0" x2="32" y2="32">
            <stop stopColor="#6E56CF" />
            <stop offset="1" stopColor="#22D3EE" />
          </linearGradient>
        </defs>
        <rect x="2" y="2" width="28" height="28" rx="8" fill="url(#sf-g)" />
        <circle cx="16" cy="16" r="7.5" fill="none" stroke="#0B0D12" strokeWidth="2.4" />
        <circle cx="16" cy="16" r="2.4" fill="#0B0D12" />
        <path d="M16 2.5 V6 M16 26 V29.5 M2.5 16 H6 M26 16 H29.5" stroke="#0B0D12" strokeWidth="2.4" strokeLinecap="round" />
      </motion.svg>
      <span className="text-[17px]">
        Spy<span className="gradient-text">Fy</span>
      </span>
    </span>
  );
}
