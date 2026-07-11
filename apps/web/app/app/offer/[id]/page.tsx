import { notFound } from "next/navigation";
import { getOffer, type Offer } from "@/lib/data";
import { OfferDetail } from "@/components/app/OfferDetail";

// A rota é dinâmica: busca o detalhe na API (ofertas reais das
// Ad Libraries) a cada request, então NÃO pode ser estática.
export const dynamic = "force-dynamic";

// Tenta o mock local; se não achar (oferta vinda da API /v1/offers),
// busca o detalhe real no backend (ID determinístico ofr_{net}_{key}_{i}).
async function loadOffer(id: string): Promise<Offer | null> {
  const local = getOffer(id);
  if (local) return local;
  const base = process.env.NEXT_PUBLIC_API_URL?.replace(/\/$/, "");
  if (!base) return null;
  try {
    const r = await fetch(`${base}/v1/offers/${encodeURIComponent(id)}`, {
      cache: "no-store",
    });
    if (!r.ok) return null;
    return (await r.json()) as Offer;
  } catch {
    return null;
  }
}

export default async function OfferPage({ params }: { params: Promise<{ id: string }> }) {
  const { id } = await params;
  const offer = await loadOffer(id);
  if (!offer) notFound();
  return <OfferDetail offer={offer} />;
}
