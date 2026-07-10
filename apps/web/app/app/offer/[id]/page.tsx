import { notFound } from "next/navigation";
import { getOffer } from "@/lib/data";
import { OfferDetail } from "@/components/app/OfferDetail";

export default async function OfferPage({ params }: { params: Promise<{ id: string }> }) {
  const { id } = await params;
  const offer = getOffer(id);
  if (!offer) notFound();
  return <OfferDetail offer={offer} />;
}

export async function generateStaticParams() {
  const { OFFERS } = await import("@/lib/data");
  return OFFERS.map((o) => ({ id: o.id }));
}
