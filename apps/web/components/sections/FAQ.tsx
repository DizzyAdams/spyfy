"use client";

import { useState } from "react";
import { motion, useReducedMotion } from "framer-motion";
import { ChevronDown } from "lucide-react";
import { EXPOCSS, revealUp } from "@/lib/motion";
import { cn } from "@/lib/utils";

const faqs = [
  {
    q: "Como funciona a longevidade das ofertas no SpyFy?",
    a: "Indexamos há quanto tempo cada anúncio está no ar usando fontes públicas (Meta Ad Library, TikTok Creative Center e Google Transparency). O score de longevidade mostra se a oferta já está validada ou se é um teste recente — assim você copia padrão, não sorte.",
  },
  {
    q: "O SpyFy é conforme a LGPD?",
    a: "Sim. Coletamos exclusivamente dados públicos de bibliotecas de anúncios e respeitamos a LGPD, o GDPR e as políticas de cada plataforma. A clonagem serve para estudo, referência e adaptação — jamais plágio de criativo protegido.",
  },
  {
    q: "Posso clonar qualquer oferta?",
    a: "Você pode clonar qualquer anúncio público indexado — landing page, VSL e funil completo. Ofertas com criativo de marca registrada ou em revisão ficam sinalizadas; recomendamos usar o clone como base e criar sua própria variação.",
  },
  {
    q: "Preciso de cartão de crédito para começar?",
    a: "Não. O plano Free é grátis e não exige cartão. Você explora ofertas vencedoras na hora; o cartão só entra se quiser liberar clonagens e redes ilimitadas no Pro.",
  },
  {
    q: "A clonagem é realmente fiel ao original?",
    a: "Sim. Cada clone passa por QA automatizado e atinge fidelidade visual acima de 95% (diff entre o original e o clone). Você exporta um ZIP pronto para subir no seu builder.",
  },
  {
    q: "Quantas redes o SpyFy cobre?",
    a: "Meta, TikTok, Google, YouTube, Native e Pinterest hoje, com expansão para 10+ redes — LinkedIn, X, Snapchat e Kwai — até 2028.",
  },
];

export function FAQ() {
  const [open, setOpen] = useState<number | null>(0);
  const reduce = useReducedMotion();

  return (
    <section id="faq" className="mx-auto max-w-3xl px-5 py-24">
      <motion.div
        variants={reduce ? undefined : revealUp}
        initial={reduce ? false : "hidden"}
        whileInView={reduce ? undefined : "show"}
        viewport={{ once: true }}
        className="mb-10 max-w-2xl"
      >
        <span className="chip mb-4 !text-primary">Antes de assinar</span>
        <h2 className="font-display text-3xl font-bold tracking-tight sm:text-4xl">
          Perguntas <span className="gradient-text">frequentes</span>
        </h2>
      </motion.div>

      <div className="space-y-3">
        {faqs.map((f, i) => {
          const isOpen = open === i;
          const btnId = `faq-btn-${i}`;
          const panelId = `faq-panel-${i}`;
          return (
            <div
              key={f.q}
              className={cn(
                "overflow-hidden rounded-xl border bg-surface/40 transition-colors duration-300",
                isOpen ? "border-primary/40" : "border-border"
              )}
            >
              <h3 className="m-0">
                <button
                  id={btnId}
                  aria-expanded={isOpen}
                  aria-controls={panelId}
                  onClick={() => setOpen(isOpen ? null : i)}
                  className="flex w-full items-center justify-between gap-4 px-5 py-4 text-left outline-none focus-visible:ring-2 focus-visible:ring-ring"
                >
                  <span className="font-display text-[15px] font-semibold text-text">
                    {f.q}
                  </span>
                  <ChevronDown
                    size={18}
                    aria-hidden
                    className={cn(
                      "shrink-0 transition-transform duration-300",
                      isOpen ? "rotate-180 text-primary" : "text-muted"
                    )}
                  />
                </button>
              </h3>
              <motion.div
                id={panelId}
                role="region"
                aria-labelledby={btnId}
                aria-hidden={!isOpen}
                initial={false}
                animate={{ height: isOpen ? "auto" : 0, opacity: isOpen ? 1 : 0 }}
                transition={{ duration: reduce ? 0 : 0.32, ease: EXPOCSS }}
                className="overflow-hidden"
              >
                <p className="px-5 pb-5 text-sm leading-relaxed text-muted">{f.a}</p>
              </motion.div>
            </div>
          );
        })}
      </div>
    </section>
  );
}
