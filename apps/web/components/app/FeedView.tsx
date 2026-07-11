"use client";

import { useMemo, useState } from "react";
import { motion, AnimatePresence, useReducedMotion } from "framer-motion";
import { SlidersHorizontal, Activity, Users, Layers } from "lucide-react";
import { NETWORKS, type Network } from "@/lib/data";
import { OfferCard } from "../OfferCard";
import { LiveBadge } from "./LiveBadge";
import { cn } from "@/lib/utils";
import { useRealtime } from "@/lib/realtime/RealtimeProvider";

const niches = [
  "Todos",
  "Emagrecimento",
  "Finanças",
  "Beleza / Nutra",
  "Relacionamento",
  "Marketing / SaaS",
  "Investimentos",
];

const countries = ["all", "BR", "US", "PT", "MX", "AR", "CO"];

function LiveTicker({ text, reduce }: { text: string; reduce: boolean | null }) {
  if (!text) return null;
  return (
    <div className="relative flex-1 overflow-hidden rounded-full border border-border bg-surface/50 px-3 py-1.5">
      <span className="pointer-events-none absolute left-3 top-1/2 z-10 -translate-y-1/2 text-[10px] font-bold uppercase tracking-widest text-accent">
        Radar
      </span>
      <div className="ml-12 overflow-hidden whitespace-nowrap">
        {reduce ? (
          <span className="text-xs text-muted">{text}</span>
        ) : (
          <motion.span
            key={text}
            className="inline-block text-xs text-muted"
            initial={{ x: "100%" }}
            animate={{ x: "-100%" }}
            transition={{ duration: 11, ease: "linear", repeat: Infinity }}
          >
            {text}
          </motion.span>
        )}
      </div>
    </div>
  );
}

export function FeedView() {
  const { status, offers, stats, filters, query, newIds, setFilters, search } =
    useRealtime();
  const [sort, setSort] = useState<"score" | "longevity">("score");
  const reduce = useReducedMotion();

  const results = useMemo(() => {
    let r = offers.filter((o) =>
      filters.network === "all" ? true : o.network === filters.network
    );
    r = r.filter((o) => (filters.niche === "Todos" ? true : o.niche === filters.niche));
    r = r.filter((o) =>
      filters.country === "all" ? true : o.country === filters.country
    );
    const q = query.trim().toLowerCase();
    if (q) {
      r = r.filter((o) =>
        `${o.headline} ${o.advertiser} ${o.niche} ${o.cta}`.toLowerCase().includes(q)
      );
    }
    return [...r].sort((a, b) =>
      sort === "score"
        ? b.winningScore - a.winningScore
        : b.longevityDays - a.longevityDays
    );
  }, [offers, filters, query, sort]);

  /* ===== GRID BELOW ===== */

  return (
    <div>
      <div className="mb-5 flex flex-wrap items-center justify-between gap-3">
        <div>
          <h1 className="text-2xl font-bold tracking-tight">Discovery Feed</h1>
          <p className="mt-1 text-sm text-muted">
            {results.length} ofertas · Radar{" "}
            <span className="text-text">em tempo real</span> · ordenadas por{" "}
            <span className="text-text">
              {sort === "score" ? "winning score" : "longevidade"}
            </span>
          </p>
        </div>
        <LiveBadge status={status} />
      </div>

      {/* Live stats + ticker */}
      <div className="mb-6 flex flex-wrap items-center gap-3">
        <LiveTicker text={offers[0]?.headline ?? ""} reduce={reduce} />
        <div className="flex flex-wrap items-center gap-2">
          <span className="chip !text-accent" title="Ofertas mineradas por minuto">
            <Activity size={13} /> {stats?.perMin ?? 0}/min
          </span>
          <span className="chip" title="Total indexado pelo Radar">
            <Layers size={13} /> {formatCount(stats?.totalMined ?? 0)}
          </span>
          <span className="chip" title="Conexões ativas no Radar">
            <Users size={13} /> {stats?.connections ?? 0} online
          </span>
        </div>
      </div>

      {/* Filters */}
      <div className="sticky top-16 z-30 -mx-5 mb-6 border-b border-border bg-bg/85 px-5 py-3 backdrop-blur">
        <div className="flex flex-wrap items-center gap-2">
          <span className="mr-1 inline-flex items-center gap-1.5 text-xs text-muted">
            <SlidersHorizontal size={14} /> Rede:
          </span>
          <button
            onClick={() => setFilters({ network: "all" })}
            className={cn("chip cursor-pointer", filters.network === "all" && "!text-text !border-primary/50")}
          >
            Todas
          </button>
          {NETWORKS.map((n) => (
            <button
              key={n.key}
              onClick={() => setFilters({ network: n.key })}
              className={cn("chip cursor-pointer", filters.network === n.key && "!text-text !border-primary/50")}
              style={{ color: filters.network === n.key ? n.color : undefined }}
            >
              {n.label}
            </button>
          ))}

          <span className="mx-2 h-4 w-px bg-border" />

          <select
            value={filters.niche}
            onChange={(e) => setFilters({ niche: e.target.value })}
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
            value={filters.country}
            onChange={(e) => setFilters({ country: e.target.value })}
            className="rounded-full border border-border bg-surface/60 px-3 py-1 text-xs text-text outline-none"
            aria-label="País"
          >
            {countries.map((c) => (
              <option key={c} value={c}>
                {c === "all" ? "Todos os países" : c}
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
            <OfferCard key={o.id} offer={o} index={i} isNew={newIds.has(o.id)} />
          ))}
        </AnimatePresence>
      </motion.div>

      {results.length === 0 && (
        <div className="rounded-2xl border border-dashed border-border p-12 text-center text-muted">
          Nenhuma oferta para esses filtros.{" "}
          <button
            onClick={() => {
              setFilters({ network: "all", niche: "Todos", country: "all" });
              search("");
            }}
            className="ml-1 text-primary underline"
          >
            Limpar filtros
          </button>
        </div>
      )}
    </div>
  );
}

function formatCount(n: number): string {
  if (n >= 1_000_000) return (n / 1_000_000).toFixed(1).replace(/\.0$/, "") + "M";
  if (n >= 1_000) return (n / 1_000).toFixed(1).replace(/\.0$/, "") + "k";
  return String(n);
}


