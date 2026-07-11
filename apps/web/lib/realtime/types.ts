import type { Offer, Network } from "@/lib/data";

export type ConnectionStatus = "connecting" | "live" | "offline";

export interface RealtimeFilters {
  network: Network | "all";
  niche: string; // "Todos" or a niche name
  country: string; // "all" or ISO code (BR, US, PT, …)
}

export interface RealtimeStats {
  totalMined: number;
  perMin: number;
  connections: number;
  uptimeSec: number;
}

export type ClientMessage =
  | { type: "subscribe"; filters: RealtimeFilters }
  | { type: "search"; query: string };

export type ServerMessage =
  | { type: "hello"; stats: RealtimeStats }
  | { type: "offer.new"; offer: Offer; stats: RealtimeStats }
  | { type: "stats"; stats: RealtimeStats };
