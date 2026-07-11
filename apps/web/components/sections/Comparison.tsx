"use client";

import { motion, useReducedMotion } from "framer-motion";
import { Check, Minus, X } from "lucide-react";
import { EXPOCSS, revealUp } from "@/lib/motion";
import { cn } from "@/lib/utils";

type CellValue = boolean | "partial";
type Tool = "SpyFy" | "AdSpy" | "BigSpy" | "Minea";

const TOOLS: Tool[] = ["SpyFy", "AdSpy", "BigSpy", "Minea"];

const ROWS: { label: string; sub?: string; values: Record<Tool, CellValue> }[] = [
  {
    label: "Multi-rede",
    sub: "Meta, TikTok, Google, YouTube…",
    values: { SpyFy: true, AdSpy: false, BigSpy: true, Minea: "partial" },
  },
  {
    label: "Longevidade real",
    sub: "Dias rodando no ar",
    values: { SpyFy: true, AdSpy: "partial", BigSpy: "partial", Minea: "partial" },
  },
  {
    label: "Transcrição de VSL",
    sub: "Com marcação de estrutura",
    values: { SpyFy: true, AdSpy: false, BigSpy: false, Minea: false },
  },
  {
    label: "Clona Landing Page",
    values: { SpyFy: true, AdSpy: false, BigSpy: false, Minea: false },
  },
  {
    label: "Clona funil completo",
    sub: "LP + VSL + checkout + upsell",
    values: { SpyFy: true, AdSpy: false, BigSpy: false, Minea: false },
  },
  {
    label: "Sub-agents de IA",
    sub: "Briefing, QA e variações",
    values: { SpyFy: true, AdSpy: false, BigSpy: false, Minea: false },
  },
  {
    label: "Alertas em tempo real",
    values: { SpyFy: true, AdSpy: false, BigSpy: false, Minea: false },
  },
];

// Reconciliation: color is NEVER the only signal — each cell shows an icon
// (shape) AND a text label (Sim / Não / Parcial).
function Cell({ value }: { value: CellValue }) {
  if (value === true) {
    return (
      <div className="flex flex-col items-center gap-1">
        <Check size={18} className="text-success" aria-hidden />
        <span className="text-xs font-semibold text-success">Sim</span>
        <span className="sr-only">Sim</span>
      </div>
    );
  }
  if (value === false) {
    return (
      <div className="flex flex-col items-center gap-1">
        <X size={17} className="text-danger" aria-hidden />
        <span className="text-xs font-semibold text-danger">Não</span>
        <span className="sr-only">Não</span>
      </div>
    );
  }
  return (
    <div className="flex flex-col items-center gap-1">
      <Minus size={18} className="text-warning" aria-hidden />
      <span className="text-xs font-semibold text-warning">Parcial</span>
      <span className="sr-only">Parcial</span>
    </div>
  );
}

export function Comparison() {
  const reduce = useReducedMotion();

  return (
    <section id="comparativo" className="mx-auto max-w-7xl px-5 py-24">
      <motion.div
        variants={reduce ? undefined : revealUp}
        initial={reduce ? false : "hidden"}
        whileInView={reduce ? undefined : "show"}
        viewport={{ once: true }}
        className="mb-10 max-w-2xl"
      >
        <span className="chip mb-4 !text-primary">Por que o SpyFy</span>
        <h2 className="font-display text-3xl font-bold tracking-tight sm:text-4xl">
          O único que acha a oferta{" "}
          <span className="gradient-text">e entrega o funil</span>
        </h2>
      </motion.div>

      <motion.div
        variants={reduce ? undefined : revealUp}
        initial={reduce ? false : "hidden"}
        whileInView={reduce ? undefined : "show"}
        viewport={{ once: true }}
        className="overflow-x-auto rounded-2xl border border-border bg-surface/40"
      >
        <table className="w-full min-w-[680px] border-collapse text-sm">
          <caption className="sr-only">
            Comparativo de funcionalidades entre SpyFy, AdSpy, BigSpy e Minea.
          </caption>
          <thead>
            <tr className="border-b border-border">
              <th scope="col" className="p-4 text-left font-medium text-muted">
                Funcionalidade
              </th>
              {TOOLS.map((tool) => {
                const isUs = tool === "SpyFy";
                return (
                  <th
                    key={tool}
                    scope="col"
                    className={cn(
                      "relative p-4 text-center",
                      isUs && "border-x border-primary/30 bg-primary/[0.07]"
                    )}
                  >
                    {isUs && (
                      <div
                        aria-hidden
                        className="pointer-events-none absolute left-1/2 top-1/2 h-12 w-28 -translate-x-1/2 -translate-y-1/2 rounded-full bg-primary/30 blur-2xl"
                      />
                    )}
                    <span
                      className={cn(
                        "relative font-display text-sm font-semibold",
                        isUs ? "text-primary" : "text-text"
                      )}
                    >
                      {tool}
                    </span>
                    {isUs && (
                      <span className="relative mt-1 block font-mono text-[10px] uppercase tracking-wider text-violet-soft">
                        você
                      </span>
                    )}
                  </th>
                );
              })}
            </tr>
          </thead>
          <tbody>
            {ROWS.map((row, ri) => (
              <tr
                key={row.label}
                className={cn(
                  "border-b border-border/50 last:border-0",
                  ri % 2 === 1 && "bg-surface/30"
                )}
              >
                <th scope="row" className="p-4 text-left align-middle">
                  <span className="block text-sm font-medium text-text">
                    {row.label}
                  </span>
                  {row.sub && (
                    <span className="mt-0.5 block text-xs text-muted">{row.sub}</span>
                  )}
                </th>
                {TOOLS.map((tool) => {
                  const isUs = tool === "SpyFy";
                  return (
                    <td
                      key={tool}
                      className={cn(
                        "p-4 align-middle",
                        isUs && "border-x border-primary/30 bg-primary/[0.07]"
                      )}
                    >
                      <Cell value={row.values[tool]} />
                    </td>
                  );
                })}
              </tr>
            ))}
          </tbody>
        </table>
      </motion.div>
    </section>
  );
}
