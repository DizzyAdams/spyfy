"use client";

import Link from "next/link";
import { useRef, type ReactNode, type MouseEvent as ReactMouseEvent } from "react";
import {
  motion,
  useScroll,
  useTransform,
  useReducedMotion,
  useMotionValue,
  useSpring,
  type Variants,
} from "framer-motion";
import { ArrowRight, Sparkles, ShieldCheck, TrendingUp } from "lucide-react";
import { GradientMesh } from "../illustrations/GradientMesh";
import { OfferCreative } from "../OfferCreative";
import { CountUp } from "../CountUp";
import { cn } from "@/lib/utils";
import { staggerContainer, revealUp, revealMask, signalSweep } from "@/lib/motion";

export function Hero() {
  const reduce = useReducedMotion();
  const { scrollY } = useScroll();

  // Cheap parallax — translateY only, tied to scroll. Disabled on reduced-motion.
  const yMesh = useTransform(scrollY, [0, 520], [0, reduce ? 0 : 96]);
  const yGrid = useTransform(scrollY, [0, 520], [0, reduce ? 0 : -48]);

  // Reduced-motion aware reveal orchestration.
  const init: false | "hidden" = reduce ? false : "hidden";
  const anim: "show" | undefined = reduce ? undefined : "show";
  const v = (variant: Variants): Variants | undefined =>
    reduce ? undefined : variant;

  return (
    <section className="relative overflow-hidden pb-24 pt-32 sm:pt-36">
      {/* Living background — layered + parallax */}
      <motion.div aria-hidden className="absolute inset-0 -z-10" style={{ y: yMesh }}>
        <GradientMesh />
      </motion.div>
      <motion.div
        aria-hidden
        className="pointer-events-none absolute inset-0 -z-10 opacity-40"
        style={{ y: yGrid }}
      >
        <div className="grid-bg absolute inset-0" />
      </motion.div>

      <div className="relative mx-auto grid max-w-7xl items-center gap-12 px-5 lg:grid-cols-[1.1fr_0.9fr] lg:gap-10">
        {/* LEFT — narrative */}
        <motion.div
          initial={init}
          animate={anim}
          variants={v(staggerContainer)}
          className="max-w-xl"
        >
          <motion.span variants={v(revealUp)} className="chip mb-6 !text-primary">
            <Sparkles size={13} /> Ad intelligence + offer cloning com IA
          </motion.span>

          <div className="block overflow-hidden">
            <motion.h1
              variants={v(revealMask)}
              className="font-display text-[clamp(2.6rem,6vw,5rem)] font-semibold leading-[1.04] tracking-[-0.02em] text-balance"
            >
              Encontre a oferta{" "}
              <span className="gradient-text">vencedora</span> e reconstrua o funil
              inteiro em minutos.
            </motion.h1>
          </div>

          <motion.p
            variants={v(revealUp)}
            className="mt-6 max-w-xl text-lg leading-relaxed text-muted"
          >
            O SpyFy indexa bilhões de anúncios, mede a{" "}
            <strong className="font-semibold text-text">longevidade real</strong> de
            cada oferta e reconstrói funis completos (LP → VSL → checkout → upsell)
            com um clique — em tempo real, com IA.
          </motion.p>

          <motion.div
            variants={v(revealUp)}
            className="mt-8 flex flex-wrap items-center gap-3"
          >
            <MagneticLink
              href="/#precos"
              className="btn btn-primary !px-6 !py-3 !text-[15px]"
            >
              Começar grátis <ArrowRight size={16} />
            </MagneticLink>
            <Link
              href="/app/feed"
              className="btn btn-ghost !px-6 !py-3 !text-[15px]"
            >
              Ver o app ao vivo
            </Link>
          </motion.div>

          <motion.div
            variants={v(revealUp)}
            className="mt-5 flex items-center gap-2 text-xs text-muted"
          >
            <ShieldCheck size={14} className="text-success" /> Ético &amp; conforme
            LGPD
          </motion.div>

          <motion.dl
            variants={v(revealUp)}
            className="mt-10 grid grid-cols-3 gap-4 border-t border-border/60 pt-6"
          >
            <Stat label="anúncios indexados">
              <CountUp to={1} suffix="B+" />
            </Stat>
            <Stat label="clone completo">
              <CountUp to={60} prefix="<" suffix="s" />
            </Stat>
            <Stat label="fidelidade do funil">
              <CountUp to={95} suffix="%" />
            </Stat>
          </motion.dl>
        </motion.div>

        <motion.div
          initial={init}
          animate={anim}
          variants={v(revealUp)}
          className="relative"
        >
          {/* Recon reticle — orbiting targeting ring around the live creative */}
          {!reduce && (
            <motion.svg
              aria-hidden
              viewBox="0 0 400 320"
              preserveAspectRatio="none"
              className="pointer-events-none absolute -inset-5 -z-0 h-[calc(100%+2.5rem)] w-[calc(100%+2.5rem)] text-primary/35"
              style={{ transformBox: "view-box", transformOrigin: "200px 160px" }}
              animate={{ rotate: 360 }}
              transition={{ duration: 26, ease: "linear", repeat: Infinity }}
            >
              <circle
                cx="200"
                cy="160"
                r="150"
                fill="none"
                stroke="currentColor"
                strokeWidth="1"
                strokeDasharray="2 9"
                opacity="0.7"
              />
              <circle
                cx="200"
                cy="160"
                r="150"
                fill="none"
                stroke="var(--cyan)"
                strokeWidth="1.5"
                strokeDasharray="40 904"
                opacity="0.6"
              />
            </motion.svg>
          )}

          <div className="glass-strong animate-float rounded-3xl border border-border/70 p-3 shadow-glow">
            <div className="flex items-center gap-1.5 px-2 pb-3">
              <span className="h-2.5 w-2.5 rounded-full bg-danger/70" />
              <span className="h-2.5 w-2.5 rounded-full bg-warning/70" />
              <span className="h-2.5 w-2.5 rounded-full bg-success/70" />
              <span className="ml-3 text-xs text-muted">app.spyfy.io/feed</span>
            </div>
            <OfferCreative
              hue={280}
              gradient={["#7C5CFF", "#2DD4FF"]}
              label="Emagreça 7kg em 21 dias sem dietas malucas"
              format="video"
              className="aspect-[16/10] w-full rounded-xl"
            />
            <div className="mt-3 flex items-center justify-between px-1 text-xs">
              <span className="chip !text-accent">
                <TrendingUp size={12} /> Escalando · 92.4
              </span>
              <span className="chip">63d ativa</span>
            </div>
          </div>

          {/* Hot-signal chip — lime reserved for the winning signal */}
          <motion.div
            className="glass absolute -bottom-6 -left-6 hidden rounded-xl px-4 py-3 shadow-glow-lime sm:block"
            animate={reduce ? undefined : { y: [0, -8, 0] }}
            transition={
              reduce
                ? undefined
                : { duration: 5, repeat: Infinity, ease: "easeInOut" }
            }
          >
            <p className="text-[11px] text-muted">Funil clonado</p>
            <p className="text-sm font-semibold text-lime">+95% fidelidade</p>
          </motion.div>
        </motion.div>
      </div>

      {/* Signal sweep divider — expands scaleX 0->1 on view (DEEP SIGNAL) */}
      <div className="relative mx-auto mt-16 max-w-7xl px-5">
        <motion.div
          aria-hidden
          className="signal-line"
          initial={reduce ? false : "hidden"}
          whileInView={reduce ? undefined : "show"}
          viewport={{ once: true, margin: "-80px" }}
          variants={signalSweep}
        >
          {!reduce && (
            <span
              className="absolute inset-y-0 left-0 w-[42%] animate-sweep bg-[linear-gradient(90deg,transparent,var(--violet-soft),var(--cyan),transparent)]"
              style={{ filter: "blur(0.4px)" }}
            />
          )}
        </motion.div>
      </div>
    </section>
  );
}

function Stat({ label, children }: { label: string; children: ReactNode }) {
  return (
    <div className="flex flex-col gap-1">
      <dd className="font-mono text-2xl font-semibold text-text sm:text-3xl">
        {children}
      </dd>
      <dt className="text-xs leading-tight text-muted">{label}</dt>
    </div>
  );
}

function MagneticLink({
  href,
  children,
  className,
}: {
  href: string;
  children: ReactNode;
  className?: string;
}) {
  const reduce = useReducedMotion();
  const ref = useRef<HTMLAnchorElement>(null);
  const mx = useMotionValue(0);
  const my = useMotionValue(0);
  const x = useSpring(mx, { stiffness: 220, damping: 18, mass: 0.4 });
  const y = useSpring(my, { stiffness: 220, damping: 18, mass: 0.4 });

  function handleMove(e: ReactMouseEvent<HTMLAnchorElement>) {
    if (reduce || !ref.current) return;
    const rect = ref.current.getBoundingClientRect();
    mx.set((e.clientX - (rect.left + rect.width / 2)) * 0.28);
    my.set((e.clientY - (rect.top + rect.height / 2)) * 0.28);
  }

  function handleLeave() {
    mx.set(0);
    my.set(0);
  }

  return (
    <motion.span style={{ x, y }} className="inline-flex">
      <Link
        ref={ref}
        href={href}
        onMouseMove={handleMove}
        onMouseLeave={handleLeave}
        className={cn(className)}
      >
        {children}
      </Link>
    </motion.span>
  );
}
