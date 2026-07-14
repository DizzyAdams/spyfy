"use client";

import { useEffect, useState } from "react";
import { AnimatePresence, motion, useReducedMotion } from "framer-motion";
import { cn } from "@/lib/utils";
import { fadeIn } from "@/lib/motion";

type State = "idle" | "loading" | "online" | "offline";

/**
 * Pill de status do backend SpyFy (FastAPI). Faz um fetch same-origin
 * via `/api/health` (Next.js API route proxy) para evitar CORS, e mostra
 * o estado ao vivo. Degrada graciosamente quando a API não está configurada
 * ou está fora do ar — nunca quebra a renderização.
 */
export function BackendStatus({ className }: { className?: string }) {
  const [state, setState] = useState<State>("loading");
  const [version, setVersion] = useState("");
  const reduce = useReducedMotion();

  useEffect(() => {
    let alive = true;
    const probe = async () => {
      try {
        const res = await fetch("/api/health");
        const data = await res.json();
        if (!alive) return;
        if (data.status === "unconfigured") {
          setState("idle");
          setVersion("");
        } else if (data.status === "ok") {
          setState("online");
          setVersion(data.version || "");
        } else {
          setState("offline");
          setVersion(data.version || "");
        }
      } catch {
        if (!alive) return;
        setState("offline");
      }
    };
    void probe();
    // Polling ao vivo: reflete online/offline em tempo real (UX "perfeito").
    const t = setInterval(() => void probe(), 20000);
    return () => {
      alive = false;
      clearInterval(t);
    };
  }, []);

  const map = {
    idle: {
      label: "Backend: não configurado",
      dot: "bg-muted",
      tone: "text-muted",
    },
    loading: {
      label: "Conectando ao backend…",
      dot: "bg-accent",
      tone: "text-muted",
    },
    online: {
      label: `Backend online${version ? " · v" + version : ""}`,
      dot: "bg-success",
      tone: "text-text",
    },
    offline: {
      label: "Backend offline",
      dot: "bg-warning",
      tone: "text-muted",
    },
  } as const;
  const s = map[state];

  return (
    <span
      role="status"
      aria-live="polite"
      className={cn(
        "inline-flex items-center gap-2 rounded-full border border-border/60 bg-surface/40 px-3 py-1 text-xs",
        s.tone,
        className,
      )}
    >
      <AnimatePresence mode="wait" initial={false}>
        <motion.span
          key={state}
          variants={fadeIn}
          initial={reduce ? false : "hidden"}
          animate="show"
          aria-hidden
          className={cn(
            "h-2 w-2 rounded-full",
            s.dot,
            state === "loading" && !reduce && "animate-pulse",
          )}
        />
      </AnimatePresence>
      {s.label}
    </span>
  );
}
