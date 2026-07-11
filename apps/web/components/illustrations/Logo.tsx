"use client";

import { useId } from "react";
import { motion, useReducedMotion } from "framer-motion";
import { cn } from "@/lib/utils";

export interface LogoProps {
  /** Controls sizing + color via Tailwind (e.g. `text-2xl text-primary`). */
  className?: string;
  /** `mark` = glyph only · `wordmark` = word only · `full` = glyph + word. */
  variant?: "mark" | "wordmark" | "full";
}

const EXPO: [number, number, number, number] = [0.16, 1, 0.3, 1];

/**
 * SpyFy brand mark — a recon/signal glyph: a precision aperture "eye" that has
 * locked onto a violet→cyan signal, ringed by a slowly sweeping radar reticle
 * (the rest of the field = noise). Everything is drawn in `currentColor` so it
 * adapts to light/dark; only the lens uses the signature duotone gradient.
 */
export default function Logo({ className, variant = "full" }: LogoProps) {
  const reduce = useReducedMotion();
  const uid = useId().replace(/[:]/g, "");
  const gradId = `spyfy-signal-${uid}`;

  const showMark = variant === "mark" || variant === "full";
  const showWord = variant === "wordmark" || variant === "full";

  return (
    <span
      className={cn(
        "inline-flex select-none items-center align-middle text-current",
        variant === "full" && "gap-[0.5em]",
        className,
      )}
    >
      {showMark && (
        <motion.span
          className="relative inline-flex h-[1.1em] w-[1.1em] shrink-0"
          initial={reduce ? false : { opacity: 0, scale: 0.92 }}
          animate={{ opacity: 1, scale: 1 }}
          transition={{ duration: 0.5, ease: EXPO }}
          whileHover={
            reduce
              ? undefined
              : { scale: 1.06, transition: { type: "spring", stiffness: 300, damping: 20 } }
          }
        >
          <motion.svg
            viewBox="0 0 32 32"
            className="h-full w-full overflow-visible"
            fill="none"
            role={showWord ? undefined : "img"}
            aria-label={showWord ? undefined : "SpyFy"}
            aria-hidden={showWord ? true : undefined}
          >
            <defs>
              {/* Lens glint: cyan highlight → violet core */}
              <radialGradient id={gradId} cx="35%" cy="28%" r="78%">
                <stop offset="0%" stopColor="#2DD4FF" />
                <stop offset="100%" stopColor="#7C5CFF" />
              </radialGradient>
            </defs>

            {/* ── Rotating radar reticle (sweep) ───────────────────────── */}
            <motion.g
              style={{ transformBox: "view-box", transformOrigin: "16px 16px" }}
              animate={reduce ? undefined : { rotate: 360 }}
              transition={{ duration: 16, ease: "linear", repeat: Infinity }}
            >
              <circle
                cx="16"
                cy="16"
                r="14.5"
                stroke="currentColor"
                strokeWidth="1"
                opacity="0.28"
              />
              {/* Instrumentation ticks (N/E/S/W + diagonals) */}
              <path
                d="M16 3 L16 1.5 M29 16 L30.5 16 M16 29 L16 30.5 M3 16 L1.5 16
                   M25.19 6.81 L26.25 5.75 M6.81 25.19 L5.75 26.25
                   M6.81 6.81 L5.75 5.75 M25.19 25.19 L26.25 26.25"
                stroke="currentColor"
                strokeWidth="1.1"
                strokeLinecap="round"
                opacity="0.5"
              />
              {/* Radar beam wedge + leading edge */}
              <path d="M16 16 L16 2 A14 14 0 0 1 19.39 2.42 Z" fill="currentColor" opacity="0.07" />
              <path
                d="M16 16 L16 2"
                stroke="currentColor"
                strokeWidth="1.25"
                strokeLinecap="round"
                opacity="0.85"
              />
            </motion.g>

            {/* ── Static aperture "eye" (the instrument) ───────────────── */}
            <path
              d="M6 16 Q16 6 26 16 Q16 26 6 16 Z"
              stroke="currentColor"
              strokeWidth="1.5"
              strokeLinejoin="round"
              fill="none"
            />

            {/* Lens + locked signal */}
            <circle cx="16" cy="16" r="4.8" fill={`url(#${gradId})`} />
            <circle
              cx="16"
              cy="16"
              r="4.8"
              stroke="currentColor"
              strokeWidth="0.75"
              opacity="0.5"
              fill="none"
            />
            <motion.circle
              cx="16"
              cy="16"
              r="1.6"
              fill="currentColor"
              style={{ transformBox: "view-box", transformOrigin: "16px 16px" }}
              animate={reduce ? undefined : { opacity: [0.55, 1, 0.55], scale: [1, 1.35, 1] }}
              transition={{ duration: 2.4, ease: "easeInOut", repeat: Infinity }}
            />

            {/* Faint "noise" the eye is filtering out */}
            <g fill="currentColor" opacity="0.25">
              <circle cx="24.5" cy="11" r="0.9" />
              <circle cx="7.5" cy="21" r="0.9" />
              <circle cx="23" cy="23" r="0.9" />
            </g>
          </motion.svg>
        </motion.span>
      )}

      {showWord && (
        <span className="font-display text-[1em] font-semibold leading-none tracking-tight text-current">
          Spy<span className="gradient-text">Fy</span>
        </span>
      )}
    </span>
  );
}
