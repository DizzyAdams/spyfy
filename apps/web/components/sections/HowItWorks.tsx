"use client";

import { motion } from "framer-motion";
import { Globe, Download, GitBranch, Fingerprint, Sparkles, Package } from "lucide-react";
import { FunnelDiagram } from "../illustrations/FunnelDiagram";

const steps = [
  { icon: Globe, label: "Fetch da LP", desc: "Render completo com Playwright headless." },
  { icon: Download, label: "Assets", desc: "Baixa imagens, CSS, JS e fontes; reescreve URLs." },
  { icon: GitBranch, label: "Detecta o funil", desc: "Segue CTAs e mapeia upsell/downsell pós-checkout." },
  { icon: Fingerprint, label: "Fingerprint de stack", desc: "Identifica checkout, pixels e builder com confiança." },
  { icon: Sparkles, label: "Extrai a copy", desc: "LLM segmenta seções e classifica elementos persuasivos." },
  { icon: Package, label: "Empacota", desc: "Gera bundle estático + manifest e notifica o usuário." },
];

export function HowItWorks() {
  return (
    <section id="como-funciona" className="relative border-y border-border/60 bg-surface/30 py-24">
      <div className="mx-auto grid max-w-7xl items-center gap-14 px-5 lg:grid-cols-2">
        <div>
          <motion.div
            initial={{ opacity: 0, y: 16 }}
            whileInView={{ opacity: 1, y: 0 }}
            viewport={{ once: true }}
            transition={{ duration: 0.6 }}
            className="mb-10 max-w-xl"
          >
            <span className="chip mb-4 !text-accent">Offer Cloner</span>
            <h2 className="text-3xl font-bold tracking-tight sm:text-4xl">
              Engenharia reversa em <span className="gradient-text">tempo real</span>
            </h2>
            <p className="mt-3 text-muted">
              Cada etapa do clone chega via WebSocket e anima na tela. Você vê o funil sendo reconstruído, passo a passo.
            </p>
          </motion.div>

          <ol className="space-y-3">
            {steps.map((s, i) => (
              <motion.li
                key={s.label}
                initial={{ opacity: 0, x: -12 }}
                whileInView={{ opacity: 1, x: 0 }}
                viewport={{ once: true }}
                transition={{ duration: 0.4, delay: i * 0.08, ease: [0.22, 1, 0.36, 1] }}
                className="flex items-start gap-4 rounded-xl border border-border bg-surface/60 p-4"
              >
                <span className="grid h-9 w-9 shrink-0 place-items-center rounded-lg bg-primary/15 text-primary">
                  <s.icon size={18} />
                </span>
                <div>
                  <p className="text-sm font-semibold text-text">
                    <span className="mr-2 text-muted">0{i + 1}</span>
                    {s.label}
                  </p>
                  <p className="text-sm text-muted">{s.desc}</p>
                </div>
              </motion.li>
            ))}
          </ol>
        </div>

        <motion.div
          initial={{ opacity: 0, y: 20 }}
          whileInView={{ opacity: 1, y: 0 }}
          viewport={{ once: true }}
          transition={{ duration: 0.7, ease: [0.22, 1, 0.36, 1] }}
          className="glass-strong rounded-2xl border border-border/70 p-6 shadow-glow"
        >
          <p className="mb-4 text-sm font-semibold text-muted">Funil reconstruído · ofr_123</p>
          <FunnelDiagram
            steps={[
              { label: "Landing Page", stack: "ClickFunnels" },
              { label: "VSL 14min", stack: "Vimeo" },
              { label: "Checkout", stack: "Cartpanda" },
              { label: "Upsell 1", stack: "Cartpanda" },
              { label: "Thank You", stack: "Kiwify" },
            ]}
          />
          <div className="mt-6 flex items-center justify-between rounded-xl border border-border bg-bg/50 px-4 py-3 text-xs">
            <span className="text-muted">Fidelidade do clone</span>
            <span className="font-semibold text-success">95.2%</span>
          </div>
        </motion.div>
      </div>
    </section>
  );
}
