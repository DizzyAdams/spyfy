"use client";

import { useMemo, useState } from "react";
import { motion, AnimatePresence } from "framer-motion";
import { SlidersHorizontal, X } from "lucide-react";
import { OFFERS, NETWORKS, type Network } from "@/lib/data";
import { OfferCard } from "../OfferCard";
import { cn } from "@/lib/utils";

const niches = ["Todos", "Emagrecimento", "Finanças", "Beleza / Nutra", "Relacionamento", "Marketing / SaaS", "Investimentos"];

export function FeedView() {
  const [net, setNet] = useState<Network | "all">("all");
  const [niche, setNiche] = useState("Todos");
  const [sort, setSort] = useState<"score" | "longevity">("score");

  const results = useMemo(() => {
    let r = OFFERS.filter((o) => (net === "all" ? true : o.network === net));
    r = r.filter((o) => (niche === "Todos" ? true : o.niche === niche));
    r = [...r].sort((a, b) =>
      sort === "score" ? b.winningScore - a.winningScore : b.longevityDays - a.longevityDays
    );
    return r;
  }, [net, niche, sort]);

  return (
    <div>
      <div className="mb-6">
        <h1 className="text-2xl font-bold tracking-tight">Discovery Feed</h1>
        <p className="mt-1 text-sm text-muted">
          {results.length} ofertas · ordenadas por{" "}
          <span className="text-text">{sort === "score" ? "winning score" : "longevidade"}</span>
        </p>
      </div>

      {/* Filters */}
      <div className="sticky top-16 z-30 -mx-5 mb-6 border-b border-border bg-bg/85 px-5 py-3 backdrop-blur">
        <div className="flex flex-wrap items-center gap-2">
          <span className="mr-1 inline-flex items-center gap-1.5 text-xs text-muted">
            <SlidersHorizontal size={14} /> Rede:
          </span>
          <button
            onClick={() => setNet("all")}
            className={cn("chip cursor-pointer", net === "all" && "!text-text !border-primary/50")}
          >
            Todas
          </button>
          {NETWORKS.map((n) => (
            <button
              key={n.key}
              onClick={() => setNet(n.key)}
              className={cn("chip cursor-pointer", net === n.key && "!text-text !border-primary/50")}
              style={{ color: net === n.key ? n.color : undefined }}
            >
              {n.label}
            </button>
          ))}
          <span className="mx-2 h-4 w-px bg-border" />
          <select
            value={niche}
            onChange={(e) => setNiche(e.target.value)}
            className="rounded-full border border-border bg-surface/60 px-3 py-1 text-xs text-text outline-none"
            aria-label="Nicho"
          >
            {niches.map((n) => (
              <option key={n} value={n}>
                {n}
              </option>
            ))}
          </select>
          <select
            value={sort}
            onChange={(e) => setSort(e.target.value as "score" | "longevity")}
            className="rounded-full border border-border bg-surface/60 px-3 py-1 text-xs text-text outline-none"
            aria-label="Ordenar por"
          >
            <option value="score">Winning score</option>
            <option value="longevity">Longevidade</option>
          </select>
        </div>
      </div>

      <motion.div layout className="grid grid-cols-1 gap-4 sm:grid-cols-2 xl:grid-cols-3">
        <AnimatePresence mode="popLayout">
          {results.map((o, i) => (
            <OfferCard key={o.id} offer={o} index={i} />
          ))}
        </AnimatePresence>
      </motion.div>

      {results.length === 0 && (
        <div className="rounded-2xl border border-dashed border-border p-12 text-center text-muted">
          Nenhuma oferta para esses filtros. <button onClick={() => { setNet("all"); setNiche("Todos"); }} className="ml-1 text-primary underline">Limpar filtros</button>
        </div>
      )}
    </div>
  );
}
