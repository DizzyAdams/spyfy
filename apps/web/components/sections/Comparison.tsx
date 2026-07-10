"use client";

import { motion } from "framer-motion";
import { Check, Minus, X } from "lucide-react";
import { COMPETITORS, type Competitor } from "@/lib/data";

function Cell({ v }: { v: boolean | string }) {
  if (v === true) return <Check size={16} className="mx-auto text-success" />;
  if (v === false) return <X size={15} className="mx-auto text-muted/50" />;
  return <span className="text-xs text-muted">{v}</span>;
}

const cols: { key: keyof Competitor; label: string }[] = [
  { key: "multi", label: "Multi-rede" },
  { key: "longevity", label: "Longevidade real" },
  { key: "vsl", label: "Transcrição VSL" },
  { key: "cloneLP", label: "Clona LP" },
  { key: "cloneFunnel", label: "Clona funil" },
  { key: "agents", label: "Sub-agents IA" },
  { key: "realtime", label: "Tempo real" },
];

export function Comparison() {
  return (
    <section id="comparativo" className="mx-auto max-w-7xl px-5 py-24">
      <motion.div
        initial={{ opacity: 0, y: 16 }}
        whileInView={{ opacity: 1, y: 0 }}
        viewport={{ once: true }}
        transition={{ duration: 0.6 }}
        className="mb-10 max-w-2xl"
      >
        <span className="chip mb-4 !text-primary">Por que o SpyFy</span>
        <h2 className="text-3xl font-bold tracking-tight sm:text-4xl">
          O único que acha a oferta <span className="gradient-text">E entrega o funil</span>
        </h2>
      </motion.div>

      <motion.div
        initial={{ opacity: 0, y: 20 }}
        whileInView={{ opacity: 1, y: 0 }}
        viewport={{ once: true }}
        transition={{ duration: 0.6 }}
        className="overflow-x-auto rounded-2xl border border-border bg-surface/40"
      >
        <table className="w-full min-w-[640px] border-collapse text-sm">
          <thead>
            <tr className="border-b border-border text-left">
              <th className="p-4 font-medium text-muted">Ferramenta</th>
              {cols.map((c) => (
                <th key={c.key} className="p-4 text-center font-medium text-muted">
                  {c.label}
                </th>
              ))}
            </tr>
          </thead>
          <tbody>
            {COMPETITORS.map((row) => (
              <tr
                key={row.name}
                className={`border-b border-border/50 last:border-0 ${
                  row.isUs ? "bg-primary/10" : ""
                }`}
              >
                <td className={`p-4 font-semibold ${row.isUs ? "text-primary" : "text-text"}`}>
                  {row.name}
                  {row.isUs && <span className="ml-2 chip !text-primary !py-0.5">você</span>}
                </td>
                {cols.map((c) => (
                  <td key={c.key} className="p-4">
                    <Cell v={row[c.key] as boolean | string} />
                  </td>
                ))}
              </tr>
            ))}
          </tbody>
        </table>
      </motion.div>
    </section>
  );
}
