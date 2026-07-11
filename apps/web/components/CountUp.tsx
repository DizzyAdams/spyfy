"use client";

import { useEffect, useMemo, useRef, useState } from "react";
import { animate, useReducedMotion } from "framer-motion";
import { EXPOCSS } from "@/lib/motion";

export function CountUp({
  to,
  duration = 1.1,
  decimals = 0,
  prefix = "",
  suffix = "",
}: {
  to: number;
  duration?: number;
  decimals?: number;
  prefix?: string;
  suffix?: string;
}) {
  const ref = useRef<HTMLSpanElement>(null);
  const reduce = useReducedMotion();

  const format = (v: number) =>
    v.toLocaleString("pt-BR", {
      minimumFractionDigits: decimals,
      maximumFractionDigits: decimals,
    });

  // Reserve the final width so surrounding layout never shifts mid-count.
  // Memoized so its reference is stable across per-frame re-renders (avoids
  // restarting the animation on every tick).
  const finalText = useMemo(
    () => `${prefix}${format(to)}${suffix}`,
    [to, prefix, suffix, decimals],
  );
  const [text, setText] = useState(
    reduce ? finalText : `${prefix}${format(0)}${suffix}`,
  );

  useEffect(() => {
    if (reduce) {
      setText(finalText);
      return;
    }
    const controls = animate(0, to, {
      duration,
      ease: EXPOCSS,
      onUpdate: (v) => setText(`${prefix}${format(v)}${suffix}`),
    });
    return () => controls.stop();
  }, [to, duration, decimals, prefix, suffix, reduce, finalText]);

  return (
    <span
      ref={ref}
      className="relative inline-block font-mono tabular-nums leading-none"
    >
      <span aria-hidden className="invisible">
        {finalText}
      </span>
      <span className="absolute inset-0 whitespace-nowrap">{text}</span>
    </span>
  );
}
