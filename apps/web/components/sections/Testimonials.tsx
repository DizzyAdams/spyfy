"use client";

import { motion, useReducedMotion } from "framer-motion";
import { Quote } from "lucide-react";
import { staggerContainer, revealUp } from "@/lib/motion";

type Testimonial = {
  quote: string;
  name: string;
  role: string;
  initials: string;
};

const TESTIMONIALS: Testimonial[] = [
  {
    quote:
      "Bati o filtro de longevidade + score e a oferta vencedora apareceu em 4 minutos. Parei de testar cego e fui direto na variação que já escalava.",
    name: "Bruno Marques",
    role: "Media Buyer · R$180k/mês em escala",
    initials: "BM",
  },
  {
    quote:
      "Clonar o funil inteiro — LP, VSL e checkout — em menos de um minuto e baixar o ZIP pronto? Acabou a tarde inteira montando estrutura no Canva.",
    name: "Camila Reis",
    role: "Afiliada de infoprodutos",
    initials: "CR",
  },
  {
    quote:
      "Minha equipe roda 14 contas. O SpyFy virou nosso briefing automático: a gente espiona o funil do concorrente, clona e entrega pro cliente no mesmo dia.",
    name: "Rafael Tavares",
    role: "Agência de performance · 14 contas",
    initials: "RT",
  },
];

export function Testimonials() {
  const reduce = useReducedMotion();

  return (
    <section className="mx-auto max-w-7xl px-5 py-24">
      <motion.div
        variants={reduce ? undefined : revealUp}
        initial={reduce ? false : "hidden"}
        whileInView={reduce ? undefined : "show"}
        viewport={{ once: true }}
        className="mb-12 max-w-2xl"
      >
        <span className="chip mb-4 !text-primary">Prova real</span>
        <h2 className="font-display text-3xl font-bold tracking-tight sm:text-4xl">
          Quem escala não <span className="gradient-text">advinha</span> — espiona.
        </h2>
      </motion.div>

      <motion.div
        variants={reduce ? undefined : staggerContainer}
        initial={reduce ? false : "hidden"}
        whileInView={reduce ? undefined : "show"}
        viewport={{ once: true }}
        className="grid grid-cols-1 gap-5 md:grid-cols-3"
      >
        {TESTIMONIALS.map((t, i) => (
          <motion.figure
            key={t.name}
            variants={reduce ? undefined : revealUp}
            className="bento group relative flex flex-col gap-5 border border-border p-6 transition-colors duration-300 hover:border-primary/40"
          >
            <div
              aria-hidden
              className="absolute inset-x-6 top-0 h-px bg-gradient-to-r from-transparent via-primary/60 to-transparent transition-opacity duration-300 group-hover:via-primary"
            />
            <div className="flex items-start justify-between">
              <Quote size={20} className="text-primary" aria-hidden />
              <span className="font-mono text-xs text-faint">0{i + 1}</span>
            </div>
            <blockquote className="text-[15px] leading-relaxed text-text">
              “{t.quote}”
            </blockquote>
            <figcaption className="mt-auto flex items-center gap-3 border-t border-border pt-4">
              <div className="relative grid h-11 w-11 shrink-0 place-items-center rounded-full bg-gradient-to-tr from-primary to-accent p-[1.5px]">
                <div className="grid h-full w-full place-items-center rounded-full bg-surface-2 font-mono text-sm font-semibold text-text">
                  {t.initials}
                </div>
              </div>
              <div>
                <p className="text-sm font-semibold text-text">{t.name}</p>
                <p className="text-xs text-muted">{t.role}</p>
              </div>
            </figcaption>
          </motion.figure>
        ))}
      </motion.div>
    </section>
  );
}
