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

const RT_URL = process.env.NEXT_PUBLIC_REALTIME_URL;
const PORT = process.env.NEXT_PUBLIC_REALTIME_PORT || "4000";
const MAX_OFFERS = 240;
const MAX_BACKOFF = 15_000;
const WATCHDOG_MS = 18_000;

interface RealtimeContextValue {
  status: ConnectionStatus;
  offers: Offer[];
  stats: RealtimeStats | null;
  filters: RealtimeFilters;
  query: string;
  newIds: Set<string>;
  setFilters: (f: Partial<RealtimeFilters>) => void;
  search: (q: string) => void;
}

const RealtimeContext = createContext<RealtimeContextValue | null>(null);

export function RealtimeProvider({ children }: { children: ReactNode }) {
  const [status, setStatus] = useState<ConnectionStatus>("connecting");
  const [offers, setOffers] = useState<Offer[]>(() => OFFERS.slice(0, 60));
  const [stats, setStats] = useState<RealtimeStats | null>(null);
  const [filters, setFiltersState] = useState<RealtimeFilters>({
    network: "all",
    niche: "Todos",
    country: "all",
  });
  const [query, setQuery] = useState("");
  const [newIds, setNewIds] = useState<Set<string>>(new Set());

  const wsRef = useRef<WebSocket | null>(null);
  const filtersRef = useRef(filters);
  const queryRef = useRef(query);
  const reconnectRef = useRef<ReturnType<typeof setTimeout> | null>(null);
  const backoffRef = useRef(1000);
  const failsRef = useRef(0);
  const openedRef = useRef(false);
  const lastMsgRef = useRef<number>(Date.now());
  const watchdogRef = useRef<ReturnType<typeof setInterval> | null>(null);

  useEffect(() => {
    filtersRef.current = filters;
  }, [filters]);
  useEffect(() => {
    queryRef.current = query;
  }, [query]);

  /* ===== PROVIDER CONTINUES ===== */

  const send = useCallback((msg: ClientMessage) => {
    const ws = wsRef.current;
    if (ws && ws.readyState === WebSocket.OPEN) {
      ws.send(JSON.stringify(msg));
    }
  }, []);

  const connect = useCallback(() => {
    if (typeof window === "undefined") return;
    setStatus((s) => (s === "offline" ? "offline" : "connecting"));
    let ws: WebSocket;
    try {
      const url =
        RT_URL ||
        `${window.location.protocol === "https:" ? "wss" : "ws"}://${window.location.hostname}:${PORT}`;
      ws = new WebSocket(url);
    } catch {
      failsRef.current += 1;
      setStatus("offline");
      scheduleReconnect();
      return;
    }
    wsRef.current = ws;

    ws.onopen = () => {
      openedRef.current = true;
      failsRef.current = 0;
      backoffRef.current = 1000;
      setStatus("live");
      lastMsgRef.current = Date.now();
      send({ type: "subscribe", filters: filtersRef.current });
      if (queryRef.current) send({ type: "search", query: queryRef.current });
    };

    ws.onmessage = (ev) => {
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
      wsRef.current = null;
      if (!openedRef.current) failsRef.current += 1;
      else failsRef.current = 0;
      openedRef.current = false;
      setStatus(failsRef.current >= 6 ? "offline" : "connecting");
      scheduleReconnect();
    };

    ws.onerror = () => {
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
        return next;
      });
    },
    [send]
  );

  const search = useCallback(
    (q: string) => {
      setQuery(q);
      send({ type: "search", query: q });
    },
    [send]
  );

  return (
    <RealtimeContext.Provider
      value={{ status, offers, stats, filters, query, newIds, setFilters, search }}
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

