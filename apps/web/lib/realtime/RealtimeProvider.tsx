"use client";

import {
  createContext,
  useContext,
  useEffect,
  useRef,
  useState,
  useCallback,
  type ReactNode,
} from "react";
import type { Offer } from "@/lib/data";
import { OFFERS } from "@/lib/data";
import type {
  ClientMessage,
  ConnectionStatus,
  RealtimeFilters,
  RealtimeStats,
  ServerMessage,
} from "./types";

// Allow connection status to represent polling fallback
type ExtendedConnectionStatus = ConnectionStatus | "polling";

const RT_URL = process.env.NEXT_PUBLIC_REALTIME_URL;
const API_URL = process.env.NEXT_PUBLIC_API_URL || "https://workers-py.vercel.app";
const PORT = process.env.NEXT_PUBLIC_REALTIME_PORT || "4000";
const MAX_OFFERS = 240;
const MAX_BACKOFF = 15_000;
const WATCHDOG_MS = 18_000;

interface RealtimeContextValue {
  status: ExtendedConnectionStatus;
  offers: Offer[];
  stats: RealtimeStats | null;
  filters: RealtimeFilters;
  query: string;
  newIds: Set<string>;
  setFilters: (f: Partial<RealtimeFilters>) => void;
  search: (q: string) => void;
  loadedOnce: boolean;
  retry: () => void;
}

const RealtimeContext = createContext<RealtimeContextValue | null>(null);

export function RealtimeProvider({ children }: { children: ReactNode }) {
  const [status, setStatus] = useState<ExtendedConnectionStatus>(
    RT_URL ? "connecting" : "polling"
  );
  const [offers, setOffers] = useState<Offer[]>(() => OFFERS.slice(0, 60));
  const [stats, setStats] = useState<RealtimeStats | null>(null);
  const [filters, setFiltersState] = useState<RealtimeFilters>({
    network: "all",
    niche: "Todos",
    country: "all",
  });
  const [query, setQuery] = useState("");
  const [newIds, setNewIds] = useState<Set<string>>(new Set());

  // Tracks whether the realtime layer has confirmed a live feed or given up.
  // The UI uses it to choose between a first-load skeleton and real content.
  // NOTE: the provider seeds cached offers at mount, so we key this off the
  // connection status (first `live` or `offline`) rather than `offers.length`,
  // which is already > 0 from the cache on the very first render.
  const [loadedOnce, setLoadedOnce] = useState(false);
  const loadedOnceRef = useRef(false);

  const wsRef = useRef<WebSocket | null>(null);
  const filtersRef = useRef(filters);
  const queryRef = useRef(query);
  const reconnectRef = useRef<ReturnType<typeof setTimeout> | null>(null);
  const backoffRef = useRef(1000);
  const failsRef = useRef(0);
  const openedRef = useRef(false);
  const lastMsgRef = useRef<number>(Date.now());
  const watchdogRef = useRef<ReturnType<typeof setInterval> | null>(null);
  const pollingRef = useRef<ReturnType<typeof setInterval> | null>(null);

  // Helper to fetch from REST API
  const fetchFromRest = useCallback(async () => {
    try {
      const { network, niche, country } = filtersRef.current;
      const params = new URLSearchParams();
      if (network && network !== "all") params.append("network", network);
      if (niche && niche !== "Todos") params.append("niche", niche);
      if (country && country !== "all") params.append("country", country);
      params.append("limit", "24");

      const res = await fetch(`${API_URL}/v1/offers?${params.toString()}`);
      if (res.ok) {
        const data = await res.json();
        if (data.offers && Array.isArray(data.offers)) {
          setOffers((prev) => {
            const newOffers = data.offers.filter((o: any) => !prev.some(p => p.id === o.id));
            if (newOffers.length > 0) {
              setNewIds(new Set(newOffers.map((o: any) => o.id)));
              setTimeout(() => setNewIds(new Set()), 2600);
            }
            // Marge and dedup
            const all = [...data.offers, ...prev];
            const unique = Array.from(new Map(all.map((o) => [o.id, o])).values());
            return unique.slice(0, MAX_OFFERS);
          });
          setLoadedOnce(true);
          loadedOnceRef.current = true;
        }
      }

      // Also fetch stats
      const statsRes = await fetch(`${API_URL}/v1/metrics?${params.toString()}`);
      if (statsRes.ok) {
        const statsData = await statsRes.json();
        setStats({
          totalMined: statsData.total ?? statsData.total_offers ?? 0,
          perMin: typeof statsData.per_min === "number" ? statsData.per_min : 0,
          connections: 1,
          uptimeSec: typeof statsData.uptime_sec === "number" ? statsData.uptime_sec : 0,
        });
      }

      // REST respondeu com dados reais → tratamos como feed "ao vivo"
      // (nunca mais ficamos presos em "Conectando").
      setStatus((s) => (s === "connecting" || s === "polling" ? "live" : s));
    } catch (err) {
      console.warn("[RealtimeProvider] Polling falhou:", err);
      setStatus((s) => (s === "connecting" ? "polling" : s));
    }
  }, []);

  useEffect(() => {
    filtersRef.current = filters;
  }, [filters]);
  useEffect(() => {
    queryRef.current = query;
  }, [query]);

  // First-load flag: stays false through the initial connecting phase so the
  // feed can show skeletons, then latches true once the socket confirms a live
  // feed or the layer gives up (offline). Falls back after 3s so cached offers
  // appear even without a WebSocket server — never gets stuck showing skeletons.
  useEffect(() => {
    if (loadedOnceRef.current) return;
    if (status === "live" || status === "offline") {
      loadedOnceRef.current = true;
      setLoadedOnce(true);
    }
  }, [status]);

  // Fallback timer: after 3s of connecting, show cached offers anyway.
  useEffect(() => {
    if (loadedOnceRef.current) return;
    const t = setTimeout(() => {
      if (!loadedOnceRef.current) {
        loadedOnceRef.current = true;
        setLoadedOnce(true);
      }
    }, 3000);
    return () => clearTimeout(t);
  }, []);

  /* ===== PROVIDER CONTINUES ===== */

  const send = useCallback((msg: ClientMessage) => {
    const ws = wsRef.current;
    if (ws && ws.readyState === WebSocket.OPEN) {
      ws.send(JSON.stringify(msg));
    }
  }, []);

  const connect = useCallback(() => {
    if (typeof window === "undefined") return;
    // Sem servidor WebSocket configurado (NEXT_PUBLIC_REALTIME_URL): não
    // ficamos travados em "Conectando". Vamos direto pro fallback REST,
    // que marca o feed como "live" assim que os dados chegarem.
    if (!RT_URL) {
      setStatus("polling");
      if (!pollingRef.current) {
        fetchFromRest(); // initial fetch
        pollingRef.current = setInterval(fetchFromRest, 10000); // poll every 10s
      }
      return;
    }
    setStatus((s) => (s === "offline" ? "offline" : "connecting"));
    if (failsRef.current >= 3) {
      // Switch to REST polling fallback
      setStatus("polling");
      if (!pollingRef.current) {
        fetchFromRest(); // initial fetch
        pollingRef.current = setInterval(fetchFromRest, 10000); // poll every 10s
      }
      return;
    }

    let ws: WebSocket;
    try {
      const url =
        RT_URL ||
        `${window.location.protocol === "https:" ? "wss" : "ws"}://${window.location.hostname}:${PORT}`;
      ws = new WebSocket(url);
    } catch {
      failsRef.current += 1;
      scheduleReconnect();
      return;
    }
    wsRef.current = ws;

    ws.onopen = () => {
      if (wsRef.current !== ws) return;
      openedRef.current = true;
      failsRef.current = 0;
      backoffRef.current = 1000;
      setStatus("live");
      lastMsgRef.current = Date.now();
      send({ type: "subscribe", filters: filtersRef.current });
      if (queryRef.current) send({ type: "search", query: queryRef.current });
    };

    ws.onmessage = (ev) => {
      if (wsRef.current !== ws) return;
      lastMsgRef.current = Date.now();
      let msg: ServerMessage;
      try {
        msg = JSON.parse(ev.data as string);
      } catch {
        return;
      }
      if (msg.type === "hello" || msg.type === "stats") {
        setStats(msg.stats);
      } else if (msg.type === "offer.new") {
        const offer = msg.offer;
        setOffers((prev) => {
          const deduped = prev.filter((o) => o.id !== offer.id);
          return [offer, ...deduped].slice(0, MAX_OFFERS);
        });
        setNewIds((prev) => {
          const n = new Set(prev);
          n.add(offer.id);
          return n;
        });
        // Auto-clear the "new" highlight after the entrance settles.
        setTimeout(() => {
          setNewIds((prev) => {
            if (!prev.has(offer.id)) return prev;
            const n = new Set(prev);
            n.delete(offer.id);
            return n;
          });
        }, 2600);
        setStats(msg.stats);
      }
    };

    ws.onclose = () => {
      if (wsRef.current !== ws) return;
      wsRef.current = null;
      if (!openedRef.current) failsRef.current += 1;
      else failsRef.current = 0;
      openedRef.current = false;
      
      if (failsRef.current >= 3) {
        setStatus("polling");
        if (!pollingRef.current) {
          fetchFromRest();
          pollingRef.current = setInterval(fetchFromRest, 10000);
        }
      } else {
        setStatus("connecting");
        scheduleReconnect();
      }
    };

    ws.onerror = () => {
      if (wsRef.current !== ws) return;
      try {
        ws.close();
      } catch {
        /* noop */
      }
    };
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, [send]);

  const scheduleReconnect = useCallback(() => {
    if (reconnectRef.current) return;
    const delay = Math.min(backoffRef.current, MAX_BACKOFF) + Math.random() * 400;
    backoffRef.current = Math.min(backoffRef.current * 2, MAX_BACKOFF);
    reconnectRef.current = setTimeout(() => {
      reconnectRef.current = null;
      connect();
    }, delay);
  }, [connect]);

  useEffect(() => {
    connect();
    watchdogRef.current = setInterval(() => {
      const ws = wsRef.current;
      if (ws && ws.readyState === WebSocket.OPEN) {
        if (Date.now() - lastMsgRef.current > WATCHDOG_MS) {
          try {
            ws.close();
          } catch {
            /* noop */
          }
        }
      }
    }, 6000);
    return () => {
      if (reconnectRef.current) {
        clearTimeout(reconnectRef.current);
        reconnectRef.current = null;
      }
      if (watchdogRef.current) {
        clearInterval(watchdogRef.current);
        watchdogRef.current = null;
      }
      if (pollingRef.current) {
        clearInterval(pollingRef.current);
        pollingRef.current = null;
      }
      if (wsRef.current) {
        try {
          wsRef.current.close();
        } catch {
          /* noop */
        }
        wsRef.current = null;
      }
    };
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, [connect]);

  const setFilters = useCallback(
    (f: Partial<RealtimeFilters>) => {
      setFiltersState((prev) => {
        const next = { ...prev, ...f };
        send({ type: "subscribe", filters: next });
        if (pollingRef.current) {
          // Immediately fetch new filter data if polling
          filtersRef.current = next;
          fetchFromRest();
        }
        return next;
      });
    },
    [send, fetchFromRest]
  );

  const search = useCallback(
    (q: string) => {
      setQuery(q);
      send({ type: "search", query: q });
    },
    [send]
  );

  const retry = useCallback(() => {
    backoffRef.current = 1000;
    failsRef.current = 0;
    openedRef.current = false;
    if (reconnectRef.current) {
      clearTimeout(reconnectRef.current);
      reconnectRef.current = null;
    }
    if (pollingRef.current) {
      clearInterval(pollingRef.current);
      pollingRef.current = null;
    }
    if (wsRef.current) {
      try {
        wsRef.current.close();
      } catch {
        /* noop */
      }
      wsRef.current = null;
    }
    setStatus("connecting");
    connect();
  }, [connect]);

  return (
    <RealtimeContext.Provider
      value={{ status, offers, stats, filters, query, newIds, setFilters, search, loadedOnce, retry }}
    >
      {children}
    </RealtimeContext.Provider>
  );
}

export function useRealtime() {
  const ctx = useContext(RealtimeContext);
  if (!ctx) {
    throw new Error("useRealtime deve ser usado dentro de <RealtimeProvider>");
  }
  return ctx;
}

