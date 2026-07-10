"use client";

import Link from "next/link";
import { motion } from "framer-motion";
import { ArrowRight, Sparkles, ShieldCheck } from "lucide-react";
import { GradientMesh } from "../illustrations/GradientMesh";
import { OfferCreative } from "../OfferCreative";
import { CountUp } from "../CountUp";

export function Hero() {
  return (
    <section className="relative overflow-hidden pt-32 pb-20">
      <GradientMesh />
      <div className="grid-bg absolute inset-0" />

      <div className="relative mx-auto grid max-w-7xl items-center gap-12 px-5 lg:grid-cols-[1.1fr_0.9fr]">
        <div>
          <motion.span
            initial={{ opacity: 0, y: 10 }}
            animate={{ opacity: 1, y: 0 }}
            transition={{ duration: 0.5 }}
            className="chip mb-5 !text-primary"
          >
            <Sparkles size={13} /> Ad intelligence + offer cloning com IA
          </motion.span>

          <motion.h1
            initial={{ opacity: 0, y: 16 }}
            animate={{ opacity: 1, y: 0 }}
            transition={{ duration: 0.6, ease: [0.22, 1, 0.36, 1] }}
            className="text-balance text-4xl font-bold leading-[1.05] tracking-tight sm:text-5xl lg:text-6xl"
          >
            Encontre a oferta <span className="gradient-text">vencedora</span> e clone o funil em minutos.
          </motion.h1>

          <motion.p
            initial={{ opacity: 0, y: 16 }}
            animate={{ opacity: 1, y: 0 }}
            transition={{ duration: 0.6, delay: 0.08, ease: [0.22, 1, 0.36, 1] }}
            className="mt-5 max-w-xl text-lg text-muted"
          >
            O SpyFy indexa bilhões de anúncios, mede a <strong className="text-text">longevidade real</strong> de cada oferta
            e reconstrói funis completos (LP → VSL → checkout → upsell) com um clique — em tempo real, com IA.
          </motion.p>

          <motion.div
            initial={{ opacity: 0, y: 16 }}
            animate={{ opacity: 1, y: 0 }}
            transition={{ duration: 0.6, delay: 0.16, ease: [0.22, 1, 0.36, 1] }}
            className="mt-7 flex flex-wrap items-center gap-3"
          >
            <Link href="/#precos" className="btn btn-primary !px-6 !py-3 !text-[15px]">
              Começar grátis <ArrowRight size={16} />
            </Link>
            <Link href="/app/feed" className="btn btn-ghost !px-6 !py-3 !text-[15px]">
              Ver o app ao vivo
            </Link>
          </motion.div>

          <motion.div
            initial={{ opacity: 0 }}
            animate={{ opacity: 1 }}
            transition={{ duration: 0.8, delay: 0.3 }}
            className="mt-8 flex flex-wrap items-center gap-x-7 gap-y-3 text-sm text-muted"
          >
            <span className="inline-flex items-center gap-2">
              <ShieldCheck size={16} className="text-success" /> Ético &amp; conforme LGPD
            </span>
            <span>
              <strong className="text-text"><CountUp to={1} suffix="B+" /></strong> anúncios indexados
            </span>
            <span>
              Clone em <strong className="text-text">&lt;60s</strong>
            </span>
          </motion.div>
        </div>

        <motion.div
          initial={{ opacity: 0, scale: 0.94, y: 20 }}
          animate={{ opacity: 1, scale: 1, y: 0 }}
          transition={{ duration: 0.7, delay: 0.2, ease: [0.22, 1, 0.36, 1] }}
          className="relative"
        >
          <div className="glass-strong animate-float rounded-2xl border border-border/70 p-3 shadow-glow">
            <div className="flex items-center gap-1.5 px-2 pb-3">
              <span className="h-2.5 w-2.5 rounded-full bg-danger/70" />
              <span className="h-2.5 w-2.5 rounded-full bg-warning/70" />
              <span className="h-2.5 w-2.5 rounded-full bg-success/70" />
              <span className="ml-3 text-xs text-muted">app.spyfy.io/feed</span>
            </div>
            <OfferCreative
              hue={280}
              gradient={["#6E56CF", "#22D3EE"]}
              label="Emagreça 7kg em 21 dias sem dietas malucas"
              format="video"
              className="aspect-[16/10] w-full rounded-xl"
            />
            <div className="mt-3 flex items-center justify-between px-1 text-xs">
              <span className="chip !text-[#0EA5E9]"><TrendingUpFallback /> Escalando · 92.4</span>
              <span className="chip">63d ativa</span>
            </div>
          </div>

          <motion.div
            className="glass absolute -bottom-6 -left-6 hidden rounded-xl px-4 py-3 shadow-glow-accent sm:block"
            animate={{ y: [0, -8, 0] }}
            transition={{ duration: 5, repeat: Infinity, ease: "easeInOut" }}
          >
            <p className="text-[11px] text-muted">Funil clonado</p>
            <p className="text-sm font-semibold text-success">+95% fidelidade</p>
          </motion.div>
        </motion.div>
      </div>
    </section>
  );
}

function TrendingUpFallback() {
  return <span className="text-[#0EA5E9]">▲</span>;
}
