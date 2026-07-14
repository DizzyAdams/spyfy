import { getOffer, type Offer } from "@/lib/data";
import { OfferDetailLoader } from "@/components/app/OfferDetailLoader";

// Rota dinâmica: detalhe vem das Ad Libraries reais a cada request.
export const dynamic = "force-dynamic";

// Backend estável (Vercel Python) — fallback quando a env não está injetada.
const FALLBACK_API = "https://spyfyv1prod.vercel.app";

// Tenta o mock local e, se não achar, tenta o backend no SSR (rápido quando
// o túnel responde). Se falhar, entrega null e o cliente busca no browser
// (IP residencial, sem challenge do quick-tunnel).
async function loadOffer(id: string): Promise<Offer | null> {
  const local = getOffer(id);
  if (local) return local;
  const base = (process.env.NEXT_PUBLIC_API_URL || FALLBACK_API).replace(/\/$/, "");
  try {
    const ctrl = new AbortController();
    const t = setTimeout(() => ctrl.abort(), 4000);
    const r = await fetch(`${base}/v1/offers/${encodeURIComponent(id)}`, {
      cache: "no-store",
      signal: ctrl.signal,
    });
    clearTimeout(t);
    if (r.ok) return (await r.json()) as Offer;
  } catch {
    /* fallback para fetch no cliente */
  }
  return null;
}

export default async function OfferPage({
  params,
}: {
  params: Promise<{ id: string }>;
}) {
  const { id } = await params;
  const offer = await loadOffer(id);
  return <OfferDetailLoader id={id} initial={offer} />;
}
