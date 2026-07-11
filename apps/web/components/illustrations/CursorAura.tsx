"use client";

import { useEffect } from "react";
import { motion, useMotionValue, useSpring, useReducedMotion } from "framer-motion";

/**
 * CursorAura — a living, site-wide spotlight.
 *
 * A soft violet→cyan radial glow that tracks the cursor on a damped spring,
 * giving the whole console a "precision instrument with a light source"
 * feel. Pure transform/opacity (GPU-cheap), `mix-blend-mode: screen` so it
 * reads as light rather than paint, and fully disabled under
 * prefers-reduced-motion. Sits at z-[-1] behind all content.
 */
export function CursorAura() {
  const reduce = useReducedMotion();
  const rawX = useMotionValue(0);
  const rawY = useMotionValue(0);
  const x = useSpring(rawX, { stiffness: 55, damping: 22, mass: 0.7 });
  const y = useSpring(rawY, { stiffness: 55, damping: 22, mass: 0.7 });

  useEffect(() => {
    if (reduce) return;
    // Start centered so touch / no-move devices don't show a corner glow.
    rawX.set(window.innerWidth / 2);
    rawY.set(window.innerHeight / 2);

    let frame = 0;
    function onMove(e: MouseEvent) {
      // Coalesce to a single rAF for smoothness.
      if (frame) return;
      frame = requestAnimationFrame(() => {
        rawX.set(e.clientX);
        rawY.set(e.clientY);
        frame = 0;
      });
    }
    window.addEventListener("mousemove", onMove, { passive: true });
    return () => {
      window.removeEventListener("mousemove", onMove);
      if (frame) cancelAnimationFrame(frame);
    };
  }, [reduce, rawX, rawY]);

  if (reduce) return null;

  return (
    <div aria-hidden className="pointer-events-none fixed inset-0 z-[-1]">
      {/* Wide, soft field — the ambient "light source" */}
      <motion.div
        className="absolute h-[44rem] w-[44rem] rounded-full"
        style={{
          x,
          y,
          marginLeft: "-22rem",
          marginTop: "-22rem",
          background:
            "radial-gradient(circle at 50% 50%, color-mix(in srgb, var(--violet) 16%, transparent), color-mix(in srgb, var(--cyan) 8%, transparent) 40%, transparent 68%)",
          filter: "blur(36px)",
          mixBlendMode: "screen",
        }}
      />
      {/* Tight, brighter core — the "locked signal" reticle light */}
      <motion.div
        className="absolute h-[12rem] w-[12rem] rounded-full"
        style={{
          x,
          y,
          marginLeft: "-6rem",
          marginTop: "-6rem",
          background:
            "radial-gradient(circle at 50% 50%, color-mix(in srgb, var(--cyan) 22%, transparent), transparent 60%)",
          filter: "blur(18px)",
          mixBlendMode: "screen",
        }}
      />
    </div>
  );
}

export default CursorAura;
