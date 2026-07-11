"use client";

import { motion, useReducedMotion } from "framer-motion";
import { Radar, Copy, Bot, Crosshair, Activity, BellRing } from "lucide-react";
import { cn } from "@/lib/utils";
import { staggerContainer, revealUp, cardHover } from "@/lib/motion";

type Feature = {
  icon: typeof Radar;
  title: string;
  desc: string;
  span: string;
  accent: "primary" | "accent";
  big?: boolean;
};

const features: Feature[] = [
  {
    icon: Radar,
    title: "Descoberta",
    desc: "Varredura híbrida — BM25 + kNN semântico — sobre bilhões de criativos. Filtre por vertical, formato e país e ranqueie por winning score.",
    span: "lg:col-span-4 lg:row-span-2",
    accent: "primary",
    big: true,
  },
  {
    icon: Copy,
    title: "Clone de funil",
    desc: "Reconstrói landing, checkout, upsell e downsell em menos de 60s, com fidelidade acima de 95%.",
    span: "lg:col-span-2",
    accent: "accent",
  },
  {
    icon: Bot,
    title: "IA agentic",
    desc: "Agentes LangGraph raspam, classificam e reconstroem ofertas 24/7 — sem você tocar em nada.",
    span: "lg:col-span-2",
    accent: "primary",
  },
  {
    icon: Crosshair,
    title: "Radar de nichos",
    desc: "Trend radar, saturation index e competitor watch em tempo quase real. Veja onde o sinal está nascendo.",
    span: "lg:col-span-2",
    accent: "accent",
  },
  {
    icon: Activity,
    title: "Longevidade real",
    desc: "Saiu do ar ou ainda escala? Acompanhe o ciclo de vida de cada oferta e copie só o que está vivo.",
    span: "lg:col-span-2",
    accent: "primary",
  },
  {
    icon: BellRing,
    title: "Alertas",
    desc: "Saiba no instante em que um concorrente entra em escala. Slack, e-mail, webhook ou push no app.",
    span: "lg:col-span-2",
    accent: "accent",
  },
];

export function Features() {
  const reduce = useReducedMotion();

  return (
    <section id="recursos" className="relative mx-auto max-w-7xl px-5 py-24 sm:py-28">
      <motion.div
        initial={reduce ? false : "hidden"}
        whileInView={reduce ? undefined : "show"}
        viewport={{ once: true, margin: "-80px" }}
        variants={reduce ? undefined : revealUp}
        className="mb-12 max-w-2xl"
      >
        <span className="chip mb-4 !text-primary">Recursos</span>
        <h2 className="font-display text-3xl font-semibold tracking-tight sm:text-4xl md:text-[2.75rem]">
          O console de reconhecimento que separa o{" "}
          <span className="gradient-text">sinal do ruído</span>
        </h2>
        <p className="mt-4 text-muted">
          Não é só ver anúncio. É encontrar a oferta viva, entender o funil e ter o clone na mão — num só lugar.
        </p>
      </motion.div>

      <motion.div
        variants={reduce ? undefined : staggerContainer}
        initial={reduce ? false : "hidden"}
        whileInView={reduce ? undefined : "show"}
        viewport={{ once: true, margin: "-80px" }}
        className="grid grid-cols-1 gap-4 sm:grid-cols-2 lg:grid-cols-6 lg:auto-rows-[minmax(11rem,auto)]"
      >
        {features.map((f) => (
          <motion.div
            key={f.title}
            variants={reduce ? undefined : revealUp}
            className={cn("min-w-0", f.span)}
          >
            <motion.div
              variants={reduce ? undefined : cardHover}
              initial="rest"
              animate="rest"
              whileHover={reduce ? undefined : "hover"}
              className="bento group relative flex h-full flex-col overflow-hidden rounded-2xl p-6 transition-colors duration-300 hover:border-primary/40"
            >
              <span
                aria-hidden
                className={cn(
                  "pointer-events-none absolute -top-16 left-1/2 h-40 w-40 -translate-x-1/2 rounded-full bg-primary/20 opacity-0 blur-3xl transition-opacity duration-500 group-hover:opacity-100",
                  f.accent === "accent" && "bg-accent/20",
                )}
              />
              <div
                className={cn(
                  "relative z-10 mb-5 grid h-11 w-11 place-items-center rounded-xl border border-border-strong bg-surface-2",
                  f.accent === "primary" ? "text-primary" : "text-accent",
                )}
              >
                <f.icon size={22} strokeWidth={1.75} />
              </div>
              <h3 className="relative z-10 font-display text-lg font-semibold tracking-tight text-text">
                {f.title}
              </h3>
              <p className="relative z-10 mt-2 text-sm leading-relaxed text-muted">
                {f.desc}
              </p>

              {f.big && (
                <div className="relative z-10 mt-auto flex flex-wrap items-center gap-3 pt-7">
                  <span className="chip !text-primary">BM25 + kNN</span>
                  <span className="font-mono text-xs text-faint">2.4B creatives indexados</span>
                </div>
              )}
            </motion.div>
          </motion.div>
        ))}
      </motion.div>
    </section>
  );
}
