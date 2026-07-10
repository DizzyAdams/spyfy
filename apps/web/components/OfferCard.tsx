"use client";

import Link from "next/link";
import { motion } from "framer-motion";
import { Bookmark, Copy, Flame, TrendingUp, Thermometer, Snowflake, Trophy } from "lucide-react";
import { Offer, NETWORKS } from "@/lib/data";
import { scoreBand, formatNumber, cn } from "@/lib/utils";
import { OfferCreative } from "./OfferCreative";

const bandIcon = {
  hot: Flame,
  scaling: TrendingUp,
  warming: Thermometer,
  cold: Snowflake,
};

export function OfferCard({ offer, index = 0 }: { offer: Offer; index?: number }) {
  const band = scoreBand(offer.winningScore);
  const Icon = bandIcon[band.key];
  const net = NETWORKS.find((n) => n.key === offer.network);

  return (
    <motion.article
      initial={{ opacity: 0, y: 14 }}
      whileInView={{ opacity: 1, y: 0 }}
      viewport={{ once: true, margin: "-40px" }}
      transition={{ duration: 0.4, delay: Math.min(index * 0.05, 0.3), ease: [0.22, 1, 0.36, 1] }}
      whileHover={{ y: -4 }}
      className="group bento flex flex-col overflow-hidden"
    >
      <Link href={`/app/offer/${offer.id}`} className="block focus:outline-none" aria-label={offer.headline}>
        <OfferCreative
          hue={offer.thumbnailHue}
          gradient={offer.gradient}
          label={offer.headline}
          format={offer.format}
          className="aspect-[5/3] w-full"
        />
      </Link>

      <div className="flex flex-1 flex-col gap-3 p-4">
        <div className="flex items-center justify-between text-xs">
          <span className="chip" style={{ color: net?.color }}>
            <span className="h-1.5 w-1.5 rounded-full" style={{ background: net?.color }} />
            {net?.label}
          </span>
          <span className="chip" title="Dias ativo">
            <Trophy size={12} /> {offer.longevityDays}d ativa
          </span>
        </div>

        <Link href={`/app/offer/${offer.id}`} className="line-clamp-2 text-[15px] font-semibold leading-snug text-text transition-colors group-hover:text-white">
          {offer.headline}
        </Link>

        <div className="mt-auto flex items-center justify-between">
          <span
            className="inline-flex items-center gap-1.5 rounded-full px-2.5 py-1 text-xs font-semibold"
            style={{ color: band.color, background: `color-mix(in srgb, ${band.color} 16%, transparent)` }}
          >
            <Icon size={13} /> {band.label} · {offer.winningScore.toFixed(1)}
          </span>
          <span className="text-xs text-muted">{formatNumber(offer.estImpressions)} impr.</span>
        </div>

        <div className="flex gap-2 pt-1">
          <Link href={`/app/offer/${offer.id}`} className="btn btn-primary flex-1 !py-2 !text-[13px]">
            <Copy size={14} /> Clonar
          </Link>
          <button className="btn btn-ghost !px-3 !py-2" aria-label="Salvar">
            <Bookmark size={14} />
          </button>
        </div>
      </div>
    </motion.article>
  );
}
