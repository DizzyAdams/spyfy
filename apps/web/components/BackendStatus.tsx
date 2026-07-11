"use client";

import { useEffect, useState } from "react";
import { cn } from "@/lib/utils";
import { getHealth, getVersion, isApiConfigured } from "@/lib/api";

type State = "idle" | "loading" | "online" | "offline";

/**
 * Pill de status do backend SpyFy (FastAPI). Consulta `/health` e
 * `/v1/version` da API configurada em NEXT_PUBLIC_API_URL e mostra o
 * estado ao vivo. Degrada graciosamente quando a API não está configurada
 * ou está fora do ar — nunca quebra a renderização.
 */
export function BackendStatus({ className }: { className?: string }) {
  const [state, setState] = useState<State>(
    isApiConfigured() ? "loading" : "idle",
  );
  const [version, setVersion] = useState("");

  useEffect(() => {
    if (!isApiConfigured()) {
      setState("idle");
      return;
    }
    let alive = true;
    void (async () => {
      const [health, ver] = await Promise.all([getHealth(), getVersion()]);
      if (!alive) return;
      if (health && health.status === "ok") {
        setState("online");
        setVersion(ver || health.version || "");
      } else {
        setState("offline");
      }
    })();
    return () => {
      alive = false;
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
      dot: "bg-accent animate-pulse",
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
      <span aria-hidden className={cn("h-2 w-2 rounded-full", s.dot)} />
      {s.label}
    </span>
  );
}
