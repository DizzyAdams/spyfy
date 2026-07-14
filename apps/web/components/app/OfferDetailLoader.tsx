"use client";

import { useEffect, useState } from "react";
import Link from "next/link";
import { Loader2, ArrowLeft } from "lucide-react";
import type { Offer } from "@/lib/data";
import { OfferDetail } from "./OfferDetail";

// Busca o detalhe da oferta NO BROWSER do usuário (IP residencial).
// Motivo: quick-tunnels trycloudflare aplicam challenge anti-abuse aos
// IPs de datacenter da Vercel de forma intermitente, quebrando o SSR fetch.
// O cliente não sofre esse bloqueio, então a oferta carrega 100%.
export function OfferDetailLoader({
  id,
  initial,
}: {
  id: string;
  initial: Offer | null;
}) {
  const [offer, setOffer] = useState<Offer | null>(initial);
  const [state, setState] = useState<"loading" | "ok" | "error">(
    initial ? "ok" : "loading",
  );

  useEffect(() => {
    if (initial) return;
    let alive = true;
    const base = process.env.NEXT_PUBLIC_API_URL?.replace(/\/$/, "");
    if (!base) {
      setState("error");
      return;
    }
    const url = `${base}/v1/offers/${encodeURIComponent(id)}`;
    (async () => {
      for (let attempt = 0; attempt < 4 && alive; attempt++) {
        try {
          const r = await fetch(url, { cache: "no-store" });
          if (r.ok) {
            const data = (await r.json()) as Offer;
            if (alive) {
              setOffer(data);
              setState("ok");
            }
            return;
          }
        } catch {
          /* retry */
        }
        await new Promise((res) => setTimeout(res, 500));
      }
      if (alive) setState("error");
    })();
    return () => {
      alive = false;
    };
  }, [id, initial]);

  if (state === "ok" && offer) return <OfferDetail offer={offer} />;

  if (state === "error") {
    return (
      <div className="mx-auto flex min-h-[60vh] max-w-2xl flex-col items-center justify-center gap-4 px-6 text-center">
        <p className="text-lg font-semibold text-white">Oferta não encontrada</p>
        <p className="text-sm text-white/50">
          Não foi possível carregar esta oferta. Tente novamente em instantes.
        </p>
        <Link
          href="/app/feed"
          className="inline-flex items-center gap-2 rounded-lg border border-white/10 px-4 py-2 text-sm text-white/80 transition hover:bg-white/5"
        >
          <ArrowLeft className="h-4 w-4" /> Voltar ao feed
        </Link>
      </div>
    );
  }

  return (
    <div className="mx-auto flex min-h-[60vh] max-w-2xl flex-col items-center justify-center gap-3 px-6 text-center">
      <Loader2 className="h-6 w-6 animate-spin text-white/60" />
      <p className="text-sm text-white/50">Carregando oferta…</p>
    </div>
  );
}
