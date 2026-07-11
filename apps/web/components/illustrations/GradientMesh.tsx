"use client";

import { motion, useReducedMotion } from "framer-motion";
import { EXPOCSS } from "@/lib/motion";

// A single drifting plasma blob definition.
type PlasmaBlob = {
  position: string;
  size: string;
  background: string;
  drift: { x: number[]; y: number[]; scale: number[] };
  duration: number;
};

// Volumetric plasma / aurora — layered, low-opacity radial fields in the
// signature violet → cyan duotone. Colors come from design tokens via
// color-mix (no raw hex), and the blobs additive-blend (screen) inside an
// isolated layer so they glow like light rather than stacking as paint.
const PLASMA: PlasmaBlob[] = [
  {
    position: "left-[-14%] top-[-16%]",
    size: "h-[58vmax] w-[58vmax]",
    background:
      "radial-gradient(circle at 50% 50%, color-mix(in srgb, var(--violet) 58%, transparent), transparent 68%)",
    drift: { x: [0, 90, -44, 0], y: [0, -64, 34, 0], scale: [1, 1.16, 0.94, 1] },
    duration: 28,
  },
  {
    position: "right-[-18%] top-[6%]",
    size: "h-[52vmax] w-[52vmax]",
    background:
      "radial-gradient(circle at 50% 50%, color-mix(in srgb, var(--cyan) 46%, transparent), transparent 66%)",
    drift: { x: [0, -78, 32, 0], y: [0, 52, -30, 0], scale: [1, 1.12, 0.96, 1] },
    duration: 32,
  },
  {
    position: "left-[16%] bottom-[-24%]",
    size: "h-[54vmax] w-[54vmax]",
    background:
      "radial-gradient(circle at 50% 50%, color-mix(in srgb, var(--violet-soft) 42%, transparent), transparent 64%)",
    drift: { x: [0, 46, -54, 0], y: [0, 44, 64, 0], scale: [1, 1.14, 1, 1] },
    duration: 36,
  },
];

// Full-bleed living background: volumetric plasma + faint grid + filmic grain
// + vignette. GPU-cheap (transform/opacity only) and reduced-motion aware.
export function GradientMesh({ className = "" }: { className?: string }) {
  const reduceMotion = useReducedMotion();

  return (
    <div
      aria-hidden="true"
      className={`pointer-events-none absolute inset-0 -z-10 overflow-hidden bg-[var(--bg)] ${className}`}
    >
      {/* Volumetric plasma / aurora — isolated so blobs blend only with each other */}
      <div
        className="absolute inset-0"
        style={{ isolation: "isolate", opacity: reduceMotion ? 0.5 : 1 }}
      >
        {PLASMA.map((blob, i) => (
          <motion.div
            key={i}
            className={`absolute ${blob.position} ${blob.size} rounded-full`}
            style={{
              background: blob.background,
              filter: "blur(80px)",
              mixBlendMode: "screen",
              willChange: "transform",
            }}
            animate={reduceMotion ? { x: 0, y: 0, scale: 1 } : blob.drift}
            transition={{
              duration: blob.duration,
              repeat: reduceMotion ? 0 : Infinity,
              ease: EXPOCSS,
            }}
          />
        ))}
      </div>

      {/* Faint reactive grid */}
      <div className="grid-bg absolute inset-0 opacity-70" />

      {/* Filmic grain */}
      <div className="grain absolute inset-0" />

      {/* Vignette — pull focus to the center, let the canvas fall into the dark */}
      <div
        className="absolute inset-0"
        style={{
          background:
            "radial-gradient(ellipse 100% 100% at 50% 45%, transparent 36%, rgba(0,0,0,0.5) 74%, rgba(0,0,0,0.86) 100%)",
        }}
      />
    </div>
  );
}

export default GradientMesh;

