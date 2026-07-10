"use client";

import { useState } from "react";
import { motion, AnimatePresence } from "framer-motion";
import { ChevronDown } from "lucide-react";

const faqs = [
  { q: "O SpyFy é legal e ético?", a: "Sim. Usamos apenas fontes públicas (Meta Ad Library, TikTok Creative Center, Google Transparency) e respeitamos ToS, LGPD/GDPR e direitos autorais. A clonagem é para estudo, referência e adaptação — não plágio." },
  { q: "Quantas redes vocês cobrem?", a: "Meta, TikTok, Google, YouTube, Native e Pinterest, com expansão para 10+ redes até 2028 (LinkedIn, X, Snapchat, Kwai...)." },
  { q: "A clonagem é realmente fiel?", a: "Sim. Cada clone passa por QA automatizado e atinge fidelidade visual > 95% (diff screenshot original vs clone). Você exporta um ZIP pronto." },
  { q: "Preciso saber programar?", a: "Não. A interface é point-and-click: busque, filtre, clique em “Clonar” e receba o funil reconstruído. A API é opcional para agências." },
  { q: "Como funciona a garantia de 24h?", a: "Se a oferta não estiver escalando como o esperado dentro de 24h do lançamento, devolvemos seu investimento — sem burocracia." },
];

export function FAQ() {
  const [open, setOpen] = useState<number | null>(0);
  return (
    <section id="faq" className="mx-auto max-w-3xl px-5 py-24">
      <motion.h2
        initial={{ opacity: 0, y: 16 }}
        whileInView={{ opacity: 1, y: 0 }}
        viewport={{ once: true }}
        transition={{ duration: 0.6 }}
        className="mb-10 text-center text-3xl font-bold tracking-tight sm:text-4xl"
      >
        Perguntas <span className="gradient-text">frequentes</span>
      </motion.h2>

      <div className="space-y-3">
        {faqs.map((f, i) => {
          const isOpen = open === i;
          return (
            <div key={f.q} className="overflow-hidden rounded-xl border border-border bg-surface/50">
              <button
                onClick={() => setOpen(isOpen ? null : i)}
                className="flex w-full items-center justify-between gap-4 px-5 py-4 text-left"
                aria-expanded={isOpen}
              >
                <span className="text-[15px] font-medium text-text">{f.q}</span>
                <ChevronDown
                  size={18}
                  className={`shrink-0 text-muted transition-transform duration-300 ${isOpen ? "rotate-180" : ""}`}
                />
              </button>
              <AnimatePresence initial={false}>
                {isOpen && (
                  <motion.div
                    initial={{ height: 0, opacity: 0 }}
                    animate={{ height: "auto", opacity: 1 }}
                    exit={{ height: 0, opacity: 0 }}
                    transition={{ duration: 0.3, ease: [0.22, 1, 0.36, 1] }}
                  >
                    <p className="px-5 pb-5 text-sm leading-relaxed text-muted">{f.a}</p>
                  </motion.div>
                )}
              </AnimatePresence>
            </div>
          );
        })}
      </div>
    </section>
  );
}
