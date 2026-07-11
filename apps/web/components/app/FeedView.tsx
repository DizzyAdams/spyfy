"use client";

import { useMemo, useState, useEffect, useCallback } from "react";
import { motion, AnimatePresence, useReducedMotion } from "framer-motion";
import { SlidersHorizontal, Activity, Users, Layers, WifiOff, Search, X, Server } from "lucide-react";
import { NETWORKS, type Network, type Offer } from "@/lib/data";
import { OfferCard } from "../OfferCard";
import { LiveBadge } from "./LiveBadge";
import { cn } from "@/lib/utils";
import { useRealtime } from "@/lib/realtime/RealtimeProvider";
import { getOffers, isApiConfigured } from "@/lib/api";

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

// Friendly network label for the ticker (falls back to the raw key).
function networkLabel(key: Network): string {
  return NETWORKS.find((n) => n.key === key)?.label ?? key;
}

function LiveTicker({ recent, reduce }: { recent: Offer[]; reduce: boolean | null }) {
  const [idx, setIdx] = useState(0);

  // Rotate through the latest few offers (~3.5s). Under reduced motion we
  // freeze to the most recent offer (index 0) and never start the interval.
  useEffect(() => {
    if (reduce || recent.length <= 1) return;
    const t = setInterval(() => setIdx((i) => (i + 1) % recent.length), 3500);
    return () => clearInterval(t);
  }, [reduce, recent.length]);

  // Keep the cursor in range as the recent list grows/shrinks.
  useEffect(() => {
    setIdx((i) => Math.min(i, Math.max(recent.length - 1, 0)));
  }, [recent.length]);

  const current = recent[reduce ? 0 : idx] ?? recent[0];
  const text = current
    ? `${current.headline} · ${networkLabel(current.network)} · ${Math.round(current.winningScore)}`
    : "";
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

// First-load placeholder that mirrors the OfferCard silhouette (rounded-2xl
// surface, aspect-[5/3] creative block, a couple of text lines). The shimmer
// is gated behind prefers-reduced-motion: when reduced we render static muted
// blocks with no pulse.
function SkeletonCard({ reduce }: { reduce: boolean | null }) {
  return (
    <div className="surface bento relative flex flex-col overflow-hidden rounded-2xl border border-border">
      <div
        aria-hidden
        className={cn(
          "aspect-[5/3] w-full rounded-t-2xl bg-border/40",
          !reduce && "animate-pulse"
        )}
      />
      <div className="flex flex-col gap-3 p-4">
        <div className="flex gap-2">
          <div className={cn("h-5 w-16 rounded-full bg-border/40", !reduce && "animate-pulse")} />
          <div className={cn("h-5 w-20 rounded-full bg-border/40", !reduce && "animate-pulse")} />
        </div>
        <div className={cn("h-4 w-3/4 rounded bg-border/40", !reduce && "animate-pulse")} />
        <div className={cn("h-4 w-1/2 rounded bg-border/40", !reduce && "animate-pulse")} />
        <div className="mt-auto flex items-center justify-between pt-2">
          <div className={cn("h-8 w-24 rounded bg-border/40", !reduce && "animate-pulse")} />
          <div className={cn("h-8 w-8 rounded bg-border/40", !reduce && "animate-pulse")} />
        </div>
      </div>
    </div>
  );
}

// On-brand notice shown when the realtime layer is offline. Cached offers stay
// visible beneath it (per the banner copy), so this is purely a status affordance.
function OfflineBanner({ onRetry }: { onRetry: () => void }) {
  return (
    <div
      role="alert"
      className="mb-6 flex flex-col items-center gap-4 rounded-2xl border border-border bg-surface/60 px-6 py-10 text-center"
    >
      <span className="grid h-12 w-12 place-items-center rounded-full border border-border bg-surface text-muted">
        <WifiOff size={22} aria-hidden />
      </span>
      <div>
        <p className="font-display text-base font-semibold text-text">
          Radar offline — mostrando ofertas em cache
        </p>
        <p className="mt-1 text-sm text-muted">
          Não foi possível conectar ao servidor de tempo real. Verifique a conexão e tente de novo.
        </p>
      </div>
      <button
        type="button"
        onClick={onRetry}
        className="btn btn-primary focus-visible:ring-2 focus-visible:ring-[var(--ring)] focus-visible:ring-offset-2 focus-visible:ring-offset-[var(--bg)]"
      >
        Tentar de novo
      </button>
    </div>
  );
}

export function FeedView() {
  const { status, offers, stats, filters, query, newIds, setFilters, search, loadedOnce } =
    useRealtime();
  const [sort, setSort] = useState<"score" | "longevity">("score");
  const reduce = useReducedMotion();

  // Ofertas REAIS vindo do backend (/v1/offers) — as melhores / mais
  // escaladas das Ad Libraries, enriquecidas com ROI/win-prob. O feed
  // mescla essas com o stream de realtime (offline-safe: se a API não
  // estiver configurada, o feed fica só com o realtime/cache).
  const [apiOffers, setApiOffers] = useState<Offer[]>([]);
  const [apiReady, setApiReady] = useState(false);
  useEffect(() => {
    let alive = true;
    if (!isApiConfigured()) return;
    getOffers({ limit: 120, simulate: true })
      .then((res) => {
        if (alive && res && res.offers.length) {
          setApiOffers(res.offers);
          setApiReady(true);
        }
      })
      .catch(() => {});
    return () => {
      alive = false;
    };
  }, []);

  // First-load skeletons show only during the initial connecting phase (before
  // the realtime layer confirms a live feed or goes offline).
  const showSkeletons = status === "connecting" && !loadedOnce;
  const isOffline = status === "offline";

  // Re-send the active subscription/search so the socket path re-opens.
  const reconnect = useCallback(() => {
    if (query.trim()) search(query);
    else setFilters(filters);
  }, [query, search, setFilters, filters]);

  // Base exibida = ofertas da API (reais, ranqueadas) mescladas com o
  // realtime, dedup por id e ordenadas por winning score.
  const base = useMemo<Offer[]>(() => {
    if (!apiOffers.length) return offers;
    const byId = new Map<string, Offer>();
    for (const o of [...apiOffers, ...offers]) {
      const prev = byId.get(o.id);
      // prioriza a oferta da API, mas mantém a mais recente do realtime
      byId.set(o.id, prev && prev.source !== "library" ? prev : o);
    }
    return [...byId.values()].sort((a, b) => b.winningScore - a.winningScore);
  }, [apiOffers, offers]);

  // The 4 most recent offers drive the rotating live signal (base[0] is newest).
  const recent = useMemo(() => base.slice(0, 4), [base]);

  const results = useMemo(() => {
    let r = base.filter((o) =>
      filters.network === "all" ? true : o.network === filters.network
    );
    r = r.filter((o) => (filters.niche === "Todos" ? true : o.niche === filters.niche));
    r = r.filter((o) =>
      filters.country === "all" ? true : o.country === filters.country
    );
    const q = query.trim().toLowerCase();
    if (q) {
      r = r.filter((o) =>
        `${o.headline} ${o.advertiser} ${o.niche} ${o.cta} ${
          (o.bullets ?? []).join(" ")
        } ${(o.funnel ?? []).map((f) => f.label).join(" ")} ${
          o.format
        } ${o.country}`.toLowerCase().includes(q)
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
            {results.length} ofertas ·{" "}
            {apiReady ? (
              <span className="text-text">Ad Libraries ao vivo</span>
            ) : (
              <span className="text-text">Radar em tempo real</span>
            )}{" "}
            · ordenadas por{" "}
            <span className="text-text">
              {sort === "score" ? "winning score" : "longevidade"}
            </span>
          </p>
        </div>
        <div className="flex items-center gap-2">
          {isApiConfigured() && (
            <span
              className={cn(
                "chip",
                apiReady ? "!text-[var(--success)]" : "!text-[var(--muted)]",
              )}
              title="Backend SpyFy (FastAPI) — ofertas reais das Ad Libraries"
            >
              <Server size={13} />
              {apiReady ? `API · ${apiOffers.length}` : "API…"}
            </span>
          )}
          <LiveBadge
            status={status}
            perMin={stats?.perMin}
            uptimeSec={stats?.uptimeSec}
          />
        </div>
      </div>

      {/* Live stats + ticker */}
      <div className="mb-6 flex flex-wrap items-center gap-3">
        <LiveTicker recent={recent} reduce={reduce} />
        <div className="flex flex-wrap items-center gap-2">
          {/* Real values, falling back to the cached offer count when stats is null. */}
          <span className="chip !text-accent" title="Ofertas mineradas no total">
            <Layers size={13} /> {formatCount(stats?.totalMined ?? offers.length)}{" "}
            <span className="text-muted">Mineradas</span>
          </span>
          <span className="chip" title="Ofertas mineradas por minuto">
            <Activity size={13} /> {stats?.perMin ?? offers.length}{" "}
            <span className="text-muted">Minuto</span>
          </span>
          <span className="chip" title="Conexões ativas no Radar">
            <Users size={13} /> {stats?.connections ?? offers.length}{" "}
            <span className="text-muted">Conexões</span>
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
            className={cn("chip min-h-[44px] cursor-pointer", filters.network === "all" && "!text-text !border-primary/50")}
          >
            Todas
          </button>
          {NETWORKS.map((n) => (
            <button
              key={n.key}
              onClick={() => setFilters({ network: n.key })}
              className={cn("chip min-h-[44px] cursor-pointer", filters.network === n.key && "!text-text !border-primary/50")}
              style={{ color: filters.network === n.key ? n.color : undefined }}
            >
              {n.label}
            </button>
          ))}

          <span className="mx-2 h-4 w-px bg-border" />

          <select
            value={filters.niche}
            onChange={(e) => setFilters({ niche: e.target.value })}
            className="min-h-[44px] rounded-full border border-border bg-surface/60 px-3 py-1 text-xs text-text outline-none"
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
            className="min-h-[44px] rounded-full border border-border bg-surface/60 px-3 py-1 text-xs text-text outline-none"
            aria-label="País"
          >
            {countries.map((c) => (
              <option key={c} value={c}>
                {c === "all" ? "Todos os países" : c}
              </option>
            ))}
          </select>

          {/* Busca por termo — funciona offline (filstra o feed local). */}
          <div className="relative flex min-w-[180px] flex-1 items-center gap-2 rounded-full border border-border bg-surface/60 px-3 py-1">
            <Search size={14} className="shrink-0 text-muted" aria-hidden />
            <input
              value={query}
              onChange={(e) => search(e.target.value)}
              placeholder="Buscar ofertas, anunciantes, ângulos…"
              aria-label="Buscar ofertas"
              className="w-full bg-transparent text-xs text-text outline-none placeholder:text-muted"
            />
            {query && (
              <button
                type="button"
                onClick={() => search("")}
                aria-label="Limpar busca"
                className="shrink-0 text-muted transition-colors hover:text-text focus-visible:outline-none focus-visible:ring-2 focus-visible:ring-[var(--ring)]"
              >
                <X size={14} />
              </button>
            )}
          </div>

          <select
            value={sort}
            onChange={(e) => setSort(e.target.value as "score" | "longevity")}
            className="min-h-[44px] rounded-full border border-border bg-surface/60 px-3 py-1 text-xs text-text outline-none"
            aria-label="Ordenar por"
          >
            <option value="score">Winning score</option>
            <option value="longevity">Longevidade</option>
          </select>
        </div>
      </div>

      {isOffline && <OfflineBanner onRetry={reconnect} />}

      {showSkeletons ? (
        <div className="grid grid-cols-1 gap-4 sm:grid-cols-2 xl:grid-cols-3">
          {Array.from({ length: 6 }).map((_, i) => (
            <SkeletonCard key={i} reduce={reduce} />
          ))}
        </div>
      ) : (
        <>
          <motion.div layout className="grid grid-cols-1 gap-4 sm:grid-cols-2 xl:grid-cols-3">
            <AnimatePresence mode="popLayout">
              {results.map((o, i) => (
                <OfferCard key={o.id} offer={o} index={i} isNew={newIds.has(o.id)} />
              ))}
            </AnimatePresence>
          </motion.div>

          {results.length === 0 && (
            <div className="rounded-2xl border border-dashed border-border p-12 text-center text-muted">
              {query.trim()
                ? `Nenhum resultado para “${query.trim()}”.`
                : "Nenhuma oferta para esses filtros."}
              {" "}Ajuste rede, nicho, país ou busca para ver mais
              vencedoras.{" "}
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
        </>
      )}
    </div>
  );
}

function formatCount(n: number): string {
  if (n >= 1_000_000) return (n / 1_000_000).toFixed(1).replace(/\.0$/, "") + "M";
  if (n >= 1_000) return (n / 1_000).toFixed(1).replace(/\.0$/, "") + "k";
  return String(n);
}


