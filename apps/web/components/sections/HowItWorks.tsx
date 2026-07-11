"use client";

import { motion } from "framer-motion";
import { Search, Activity, Copy, Rocket } from "lucide-react";
import { staggerContainer, revealUp } from "@/lib/motion";

const steps = [
  {
    icon: Search,
    title: "Busque",
    desc: "Aponte o radar pra qualquer nicho, concorrente ou criativo. A SpyFy varre bilhões de anúncios em segundos.",
  },
  {
    icon: Activity,
    title: "Analise",
    desc: "A IA classifica winning score, longevidade e saturação. Você enxerga só o que vale copiar.",
  },
  {
    icon: Copy,
    title: "Clone",
    desc: "Reconstrói landing, checkout e upsell com fidelidade acima de 95%. Exporta o bundle pronto pra hospedar.",
  },
  {
    icon: Rocket,
    title: "Escalone",
    desc: "Jogue o clone no ar, ligue os pixels e escale. Os agentes seguem o mercado 24/7, sem pausa.",
  },
];

export function HowItWorks() {
  return (
    <section
      id="como-funciona"
      className="relative border-y border-border/60 bg-surface/30 py-24 sm:py-28"
    >
      <div className="mx-auto max-w-5xl px-5">
        <motion.div
          initial="hidden"
          whileInView="show"
          viewport={{ once: true, margin: "-80px" }}
          variants={revealUp}
          className="mb-14 max-w-2xl"
        >
          <span className="chip mb-4 !text-accent">Como funciona</span>
          <h2 className="font-display text-3xl font-semibold tracking-tight sm:text-4xl md:text-[2.75rem]">
            Do ruído ao clone em <span className="gradient-text">quatro comandos</span>
          </h2>
          <p className="mt-4 text-muted">
            Busque o sinal, deixe a IA analisar, clone o funil e escale. O resto roda sozinho.
          </p>
        </motion.div>

        <motion.ol
          variants={staggerContainer}
          initial="hidden"
          whileInView="show"
          viewport={{ once: true, margin: "-60px" }}
          className="relative"
        >
          {steps.map((s, i) => {
            const last = i === steps.length - 1;
            return (
              <motion.li
                key={s.title}
                variants={revealUp}
                className="group relative grid grid-cols-[auto_1fr] gap-5 pb-10 last:pb-0 sm:gap-7"
              >
                {!last && (
                  <span
                    aria-hidden
                    className="absolute left-7 top-0 bottom-0 z-0 w-px bg-gradient-to-b from-primary/60 via-accent/30 to-transparent"
                  />
                )}
                <div className="relative z-10 flex items-center justify-center">
                  <div className="bento grid h-14 w-14 place-items-center rounded-2xl border border-border-strong bg-surface-2 text-primary transition-colors duration-300 group-hover:border-primary/50 group-hover:text-accent">
                    <s.icon size={22} strokeWidth={1.75} />
                  </div>
                </div>
                <div className="relative z-10 pb-1">
                  <div className="flex items-baseline gap-3">
                    <span className="font-mono text-xl font-semibold tracking-tight text-faint">
                      {String(i + 1).padStart(2, "0")}
                    </span>
                    <h3 className="font-display text-xl font-semibold tracking-tight text-text sm:text-2xl">
                      {s.title}
                    </h3>
                  </div>
                  <p className="mt-2 max-w-xl text-sm leading-relaxed text-muted sm:text-base">
                    {s.desc}
                  </p>
                </div>
              </motion.li>
            );
          })}
        </motion.ol>
      </div>
    </section>
  );
}
