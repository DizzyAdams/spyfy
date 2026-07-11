"use client";

import { motion, useReducedMotion } from "framer-motion";
import { Radio, Wifi, WifiOff } from "lucide-react";
import { cn } from "@/lib/utils";
import type { ConnectionStatus } from "@/lib/realtime/types";

const META: Record<
  ConnectionStatus,
  { label: string; Icon: typeof Radio; cls: string; dot: string }
> = {
  live: {
    label: "AO VIVO",
    Icon: Radio,
    cls: "text-success border-success/40 bg-success/10",
    dot: "bg-success",
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

export function LiveBadge({
  status,
  className,
}: {
  status: ConnectionStatus;
  className?: string;
}) {
  const reduce = useReducedMotion();
  const { Icon, cls, dot, label } = META[status];
  return (
    <span
      className={cn(
        "inline-flex items-center gap-1.5 rounded-full border px-2.5 py-1 text-[11px] font-semibold tracking-wide",
        cls,
        className
      )}
      title={`Radar em tempo real: ${label}`}
      role="status"
      aria-live="polite"
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
    </span>
  );
}
