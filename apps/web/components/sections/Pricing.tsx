"use client";

import Link from "next/link";
import { useRef, type MouseEvent as ReactMouseEvent, type ReactNode } from "react";
import {
  motion,
  useMotionValue,
  useReducedMotion,
  useSpring,
} from "framer-motion";
import { ArrowRight, Check } from "lucide-react";
import { cn } from "@/lib/utils";
import { magnetic, revealUp, staggerContainer, cardHover } from "@/lib/motion";

type Tier = {
  name: string;
  price: string;
  period: string;
  description: string;
  features: string[];
  highlight: boolean;
  cta: string;
  href: string;
};

const TIERS: Tier[] = [
  {
    name: "Grátis",
    price: "R$0",
    period: "/mês",
    description: "Para começar a espionar ofertas vencedoras hoje.",
    features: ["20 buscas por dia", "1 clonagem por mês", "Rede Meta", "Score de vencedora"],
    highlight: false,
    cta: "Comece grátis",
    href: "/app/feed",
  },
  {
    name: "Pro",
    price: "R$129",
    period: "/mês",
    description: "Para media buyers e afiliados que escalam de verdade.",
    features: ["Busca ilimitada", "100 clonagens por mês", "Todas as redes", "API (10k req)", "Alertas em tempo real"],
    highlight: true,
    cta: "Assinar Pro",
    href: "/app/feed",
  },
  {
    name: "Scale",
    price: "R$349",
    period: "/mês",
    description: "Para agências e equipes de performance.",
    features: ["Tudo do Pro", "500 clonagens por mês", "Workspaces + white-label", "API (100k req)", "Suporte prioritário"],
    highlight: false,
    cta: "Falar com vendas",
    href: "/app/feed",
  },
];

function Magnetic({ children, className }: { children: ReactNode; className?: string }) {
  const reduce = useReducedMotion();
  const ref = useRef<HTMLSpanElement>(null);
  const x = useMotionValue(0);
  const y = useMotionValue(0);
  const sx = useSpring(x, { stiffness: 320, damping: 22, mass: 0.5 });
  const sy = useSpring(y, { stiffness: 320, damping: 22, mass: 0.5 });

  function handleMove(e: ReactMouseEvent) {
    if (reduce || !ref.current) return;
    const r = ref.current.getBoundingClientRect();
    x.set((e.clientX - (r.left + r.width / 2)) * 0.35);
    y.set((e.clientY - (r.top + r.height / 2)) * 0.35);
  }
  function reset() {
    x.set(0);
    y.set(0);
  }

  return (
    <motion.span
      ref={ref}
      onMouseMove={handleMove}
      onMouseLeave={reset}
      style={{ x: sx, y: sy }}
      initial="rest"
      whileHover={reduce ? undefined : "hover"}
      variants={magnetic}
      className={cn("group inline-flex", className)}
    >
      {children}
    </motion.span>
  );
}

export function Pricing() {
  const reduce = useReducedMotion();
  return (
    <section id="precos" className="mx-auto max-w-7xl px-5 py-24 sm:py-28">
      <motion.div
        initial={reduce ? false : "hidden"}
        whileInView={reduce ? undefined : "show"}
        viewport={{ once: true, margin: "-80px" }}
        variants={reduce ? undefined : revealUp}
        className="mb-12 max-w-2xl"
      >
        <span className="chip mb-4 !text-accent">Planos</span>
        <h2 className="font-display text-3xl font-semibold tracking-tight sm:text-4xl md:text-[2.75rem]">
          Comece de graça.{" "}
          <span className="gradient-text">Escale quando quiser.</span>
        </h2>
        <p className="mt-4 max-w-xl text-muted">
          Sem cartão. Cancele quando quiser. O radar começa ligado.
        </p>
      </motion.div>

      <motion.div
        variants={reduce ? undefined : staggerContainer}
        initial={reduce ? false : "hidden"}
        whileInView={reduce ? undefined : "show"}
        viewport={{ once: true, margin: "-60px" }}
        className="grid grid-cols-1 gap-5 md:grid-cols-3"
      >
        {TIERS.map((t) => (
          <motion.div
            key={t.name}
            variants={reduce ? undefined : revealUp}
            className="relative"
          >
            <motion.div
              variants={reduce ? undefined : cardHover}
              initial="rest"
              animate="rest"
              whileHover={reduce ? undefined : "hover"}
              className={cn(
                "bento group relative flex h-full flex-col rounded-2xl p-6 sm:p-7",
                t.highlight
                  ? "border-primary bg-primary/[0.06] shadow-glow"
                  : "border-border bg-surface/40",
              )}
            >
            {t.highlight && (
              <>
                <span
                  aria-hidden
                  className="pointer-events-none absolute inset-x-10 top-0 h-px bg-gradient-to-r from-transparent via-primary/70 to-transparent"
                />
                <span className="absolute -top-3 left-1/2 -translate-x-1/2 chip border-primary/50 bg-primary/15 !text-text">
                  <span aria-hidden className="h-1.5 w-1.5 rounded-full bg-lime shadow-glow-lime" />
                  Mais popular
                </span>
              </>
            )}

            <div className="flex items-center justify-between gap-3">
              <h3 className="font-display text-lg font-semibold tracking-tight text-text">
                {t.name}
              </h3>
              {t.highlight && (
                <span className="inline-flex items-center gap-1.5 text-[11px] font-medium uppercase tracking-wide text-lime">
                  <span className="relative flex h-1.5 w-1.5">
                    <span className="absolute inline-flex h-full w-full animate-ping rounded-full bg-lime opacity-75" />
                    <span className="relative inline-flex h-1.5 w-1.5 rounded-full bg-lime" />
                  </span>
                  Sinal quente
                </span>
              )}
            </div>

            <p className="mt-2 text-sm leading-relaxed text-muted">{t.description}</p>

            <div className="mt-5 flex items-end gap-1.5">
              <span className="font-mono text-4xl font-semibold tracking-tight text-text">
                {t.price}
              </span>
              <span className="pb-1 text-sm text-muted">{t.period}</span>
            </div>

            <ul className="mt-6 flex-1 space-y-3 text-sm">
              {t.features.map((f) => (
                <li key={f} className="flex items-start gap-2.5 text-muted">
                  <Check
                    size={16}
                    strokeWidth={2.5}
                    className="mt-0.5 shrink-0 text-success"
                  />
                  <span>{f}</span>
                </li>
              ))}
            </ul>

            <Magnetic className="mt-7 w-full">
              <Link
                href={t.href}
                className={cn(
                  "btn w-full",
                  t.highlight ? "btn-primary" : "btn-ghost",
                )}
              >
                {t.cta}
                {t.highlight && (
                  <ArrowRight
                    size={16}
                    className="transition-transform duration-200 group-hover:translate-x-0.5"
                  />
                )}
              </Link>
            </Magnetic>
          </motion.div>
          </motion.div>
        ))}
      </motion.div>
    </section>
  );
}
