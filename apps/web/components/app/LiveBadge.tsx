"use client";

import { AnimatePresence, motion, useReducedMotion } from "framer-motion";
import { Radio, Wifi, WifiOff } from "lucide-react";
import { cn } from "@/lib/utils";
import type { ConnectionStatus } from "@/lib/realtime/types";
import { fadeIn } from "@/lib/motion";

const META: Record<
  ConnectionStatus,
  { label: string; Icon: typeof Radio; cls: string; dot: string }
> = {
  live: {
    label: "AO VIVO",
    Icon: Radio,
    cls: "text-success border-success/40 bg-success/10",
    dot: "bg-success shadow-[0_0_10px_var(--accent)]",
  },
  connecting: {
    label: "Conectando",
    Icon: Wifi,
    cls: "text-warning border-warning/40 bg-warning/10",
    dot: "bg-warning",
  },
  offline: {
    label: "Offline",
    Icon: WifiOff,
    cls: "text-muted border-border bg-surface/60",
    dot: "bg-muted",
  },
};

// Compact uptime formatter: "3m" when >= 60s, otherwise "42s".
function formatUptime(sec?: number): string {
  if (typeof sec !== "number" || Number.isNaN(sec)) return "0s";
  if (sec >= 60) return `${Math.floor(sec / 60)}m`;
  return `${sec}s`;
}

export function LiveBadge({
  status,
  className,
  perMin,
  uptimeSec,
}: {
  status: ConnectionStatus;
  className?: string;
  perMin?: number;
  uptimeSec?: number;
}) {
  const reduce = useReducedMotion();
  const { Icon, cls, dot, label } = META[status];
  // Only surface telemetry when we're genuinely live and have a real perMin.
  const showTelemetry = status === "live" && typeof perMin === "number";
  const telemetryLabel = showTelemetry
    ? `, ${perMin} por minuto, online ${formatUptime(uptimeSec)}`
    : "";
  return (
    <span
      className={cn(
        "inline-flex items-center gap-1.5 rounded-full border px-2.5 py-1 text-[11px] font-semibold tracking-wide",
        // Stretch into a compact two-line pill only when telemetry is shown.
        showTelemetry && "flex-col items-start gap-0.5 rounded-xl",
        cls,
        className
      )}
      title={`Radar em tempo real: ${label}${telemetryLabel}`}
      aria-label={`Radar em tempo real: ${label}${telemetryLabel}`}
      role="status"
      aria-live="polite"
    >
      <AnimatePresence mode="wait" initial={false}>
        <motion.span
          key={status}
          variants={fadeIn}
          initial={reduce ? false : "hidden"}
          animate="show"
          className="inline-flex items-center gap-1.5"
        >
          <span className="relative flex h-2 w-2">
            {status === "live" && !reduce && (
              <motion.span
                className={cn("absolute inline-flex h-full w-full rounded-full opacity-75", dot)}
                animate={{ scale: [1, 2.2], opacity: [0.7, 0] }}
                transition={{ duration: 1.4, repeat: Infinity, ease: "easeOut" }}
              />
            )}
            <span className={cn("relative inline-flex h-2 w-2 rounded-full", dot)} />
          </span>
          {label}
        </motion.span>
      </AnimatePresence>
      {showTelemetry && (
        <span className="font-mono text-[10px] font-medium leading-none text-muted/80">
          {perMin}/min · online {formatUptime(uptimeSec)}
        </span>
      )}
    </span>
  );
}
