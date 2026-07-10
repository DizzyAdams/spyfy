"use client";

import { motion } from "framer-motion";

interface Step {
  label: string;
  stack?: string;
}

// Animated funnel: LP -> VSL -> Checkout -> Upsell -> Thank You
export function FunnelDiagram({ steps }: { steps: Step[] }) {
  const total = steps.length;
  return (
    <div className="flex flex-col items-center gap-1.5">
      {steps.map((s, i) => {
        const w = 100 - (i * (60 / Math.max(total - 1, 1)));
        return (
          <motion.div
            key={i}
            initial={{ opacity: 0, scaleX: 0.6, y: 6 }}
            whileInView={{ opacity: 1, scaleX: 1, y: 0 }}
            viewport={{ once: true }}
            transition={{ duration: 0.4, delay: i * 0.08, ease: [0.22, 1, 0.36, 1] }}
            style={{ width: `${w}%` }}
            className="flex items-center justify-between gap-3 rounded-lg border border-border bg-surface-2 px-4 py-2.5 text-left"
          >
            <span className="flex items-center gap-2 text-sm font-medium">
              <span className="grid h-5 w-5 place-items-center rounded-full bg-primary/20 text-[11px] font-bold text-primary">
                {i + 1}
              </span>
              {s.label}
            </span>
            {s.stack && <span className="chip !py-1 text-[11px]">{s.stack}</span>}
          </motion.div>
        );
      })}
    </div>
  );
}
