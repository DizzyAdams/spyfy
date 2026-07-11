"use client";

import Link from "next/link";
import { motion, useReducedMotion } from "framer-motion";
import {
  Bookmark,
  Copy,
  Flame,
  TrendingUp,
  Thermometer,
  Snowflake,
  CalendarDays,
  Gauge,
} from "lucide-react";
import { Offer, NETWORKS } from "@/lib/data";
import { scoreBand, formatNumber, scaleIndex, spendBand, cn } from "@/lib/utils";
import { cardHover, EXPOCSS, magnetic, fadeIn } from "@/lib/motion";
import { OfferCreative } from "./OfferCreative";

const MotionLink = motion.create(Link);

const bandIcon = {
  hot: Flame,
  scaling: TrendingUp,
  warming: Thermometer,
  cold: Snowflake,
};

export function OfferCard({
  offer,
  index = 0,
  isNew = false,
}: {
  offer: Offer;
  index?: number;
  isNew?: boolean;
}) {
  const reduce = useReducedMotion();
  const band = scoreBand(offer.winningScore);
  const Icon = bandIcon[band.key];
  const net = NETWORKS.find((n) => n.key === offer.network);
  const href = `/app/offer/${offer.id}`;
  // Índice de escala + faixa de gasto diário — derivados 100% no cliente.
  const scale = scaleIndex(offer);
  const spend = spendBand(offer.estImpressions, offer.longevityDays);

  // Entrance reveal + magnetic-style lift (honors reduced-motion).
  const cardVariants = {
    hidden: reduce ? { opacity: 0 } : { opacity: 0, y: 14 },
    show: {
      opacity: 1,
      y: 0,
      transition: { duration: 0.5, ease: EXPOCSS, delay: Math.min(index * 0.05, 0.3) },
    },
    hover: reduce ? {} : cardHover.hover,
  };

  return (
    <motion.article
      variants={cardVariants}
      initial="hidden"
      whileInView="show"
      viewport={{ once: true, margin: "-40px" }}
      whileHover={reduce ? undefined : "hover"}
      className="group relative flex h-full flex-col rounded-2xl"
    >
      <div className={cn(
          "surface bento relative flex flex-1 flex-col overflow-hidden rounded-2xl border border-border transition-[border-color,box-shadow] duration-500 group-hover:border-ring group-hover:shadow-[0_24px_60px_-30px_var(--violet)] motion-reduce:transition-none",
          isNew && "ring-1 ring-accent/60"
        )}>
        {/* Signal-line sweep on hover (surreal accent, top edge) */}
        <span
          aria-hidden
          className="pointer-events-none absolute inset-x-0 top-0 z-10 h-px bg-gradient-to-r from-transparent via-[var(--violet)] to-transparent opacity-0 transition-opacity duration-500 group-hover:opacity-60 motion-reduce:transition-none"
        />

        {isNew && (
          <motion.span
            variants={fadeIn}
            initial={reduce ? false : "hidden"}
            animate="show"
            className="absolute left-3 top-12 z-20 inline-flex items-center gap-1 rounded-full border border-accent/50 bg-accent/15 px-2 py-0.5 text-[10px] font-bold uppercase tracking-wider text-accent backdrop-blur-md"
          >
            Nova
          </motion.span>
        )}

        {/* Creative / thumbnail with gradient placeholder */}
        <div className="relative">
          <Link
            href={href}
            aria-label={offer.headline}
            className="block rounded-t-2xl focus:outline-none focus-visible:ring-2 focus-visible:ring-[var(--ring)] focus-visible:ring-offset-2 focus-visible:ring-offset-[var(--bg)]"
          >
            <OfferCreative
              hue={offer.thumbnailHue}
              gradient={offer.gradient}
              label={offer.headline}
              format={offer.format}
              image={offer.image}
              className="aspect-[5/3] w-full"
            />
          </Link>

          {/* Longevity badge — score on the brand palette, color + icon + label */}
          <span
            title={`Score de longevidade ${offer.winningScore.toFixed(1)} — ${band.label}`}
            className="absolute right-3 top-3 inline-flex items-center gap-1.5 rounded-full border border-white/10 bg-black/45 px-2.5 py-1 text-[11px] font-semibold backdrop-blur-md"
            style={{ color: band.color }}
          >
            <Icon size={12} aria-hidden />
            {band.label}
            <span className="font-mono tabular-nums">{offer.winningScore.toFixed(1)}</span>
          </span>
        </div>

        {/* Body */}
        <div className="flex flex-1 flex-col gap-3 p-4">
          <div className="flex flex-wrap items-center gap-2">
            <span className="chip" style={{ color: net?.color }}>
              <span className="h-1.5 w-1.5 rounded-full" style={{ background: net?.color }} />
              {net?.label}
            </span>
            <span className="chip">{offer.niche}</span>
          </div>

          <Link
            href={href}
            className="line-clamp-2 font-display text-[15px] font-semibold leading-snug tracking-tight text-text transition-colors duration-300 group-hover:text-white motion-reduce:transition-none"
          >
            {offer.headline}
          </Link>

          {/* Scale score (mono) + longevity days */}
          <div className="mt-auto flex flex-col gap-2">
            <div className="flex items-end justify-between gap-3">
              <div className="flex flex-col gap-0.5">
                <span className="flex items-center gap-1 font-mono text-lg font-semibold leading-none text-text tabular-nums">
                  <Gauge size={13} className="text-[var(--violet-soft)]" aria-hidden />
                  {formatNumber(offer.estImpressions)}
                </span>
                <span className="text-[10px] font-medium uppercase tracking-[0.14em] text-faint">
                  impressões · escala
                </span>
              </div>
              <div className="flex items-center gap-1.5 text-xs text-muted">
                <CalendarDays size={13} className="text-[var(--muted)]" aria-hidden />
                <span className="font-mono tabular-nums text-text">{offer.longevityDays}d</span>
                ativa
              </div>
            </div>

            {/* Índice de Escala (chip violet-soft) + estimativa de gasto diário */}
            <div className="flex items-center justify-between gap-3">
              <motion.span
                className="chip"
                style={{
                  color: "var(--violet-soft)",
                  borderColor: "rgba(167, 139, 250, 0.35)",
                  background: "rgba(167, 139, 250, 0.12)",
                }}
                initial={reduce ? false : { opacity: 0, x: -8 }}
                animate={{ opacity: 1, x: 0 }}
                transition={{ duration: 0.5, ease: EXPOCSS, delay: 0.15 }}
              >
                <Gauge size={12} aria-hidden />
                Escala {scale}
              </motion.span>
              <span className="font-mono text-[11px] text-faint tabular-nums">
                ~R${formatNumber(spend.daily)}/dia · {spend.label}
              </span>
            </div>
          </div>

          {/* Quick actions */}
          <div className="flex items-center gap-2 pt-1">
            <MotionLink
              href={href}
              variants={magnetic}
              initial="rest"
              animate="rest"
              whileHover={reduce ? undefined : "hover"}
              className="btn btn-primary flex-1 !justify-center !py-2 !text-[13px] focus-visible:ring-2 focus-visible:ring-[var(--ring)] focus-visible:ring-offset-2 focus-visible:ring-offset-[var(--bg)]"
            >
              <Copy size={14} aria-hidden />
              Clonar
            </MotionLink>
            <button
              type="button"
              aria-label="Salvar oferta"
              className="btn btn-ghost !px-3 !py-2 focus-visible:ring-2 focus-visible:ring-[var(--ring)] focus-visible:ring-offset-2 focus-visible:ring-offset-[var(--bg)]"
            >
              <Bookmark size={14} aria-hidden />
            </button>
          </div>
        </div>
      </div>
    </motion.article>
  );
}

export default OfferCard;

