"use client";

import Link from "next/link";
import { motion } from "framer-motion";
import { Check } from "lucide-react";
import { PRICING } from "@/lib/data";
import { staggerContainer, fadeUp } from "@/lib/motion";

export function Pricing() {
  return (
    <section id="precos" className="mx-auto max-w-7xl px-5 py-24">
      <motion.div
        initial={{ opacity: 0, y: 16 }}
        whileInView={{ opacity: 1, y: 0 }}
        viewport={{ once: true }}
        transition={{ duration: 0.6 }}
        className="mb-12 text-center"
      >
        <span className="chip mb-4 !text-accent">Planos</span>
        <h2 className="text-3xl font-bold tracking-tight sm:text-4xl">
          Comece de graça. <span className="gradient-text">Escale quando quiser.</span>
        </h2>
      </motion.div>

      <motion.div
        variants={staggerContainer}
        initial="hidden"
        whileInView="show"
        viewport={{ once: true, margin: "-60px" }}
        className="grid grid-cols-1 gap-5 md:grid-cols-3"
      >
        {PRICING.map((p) => (
          <motion.div
            key={p.name}
            variants={fadeUp}
            className={`relative flex flex-col rounded-2xl border p-6 ${
              p.highlight
                ? "border-primary bg-primary/10 shadow-glow"
                : "border-border bg-surface/50"
            }`}
          >
            {p.highlight && (
              <span className="absolute -top-3 left-1/2 -translate-x-1/2 chip !bg-primary !text-white">
                Mais popular
              </span>
            )}
            <h3 className="text-lg font-semibold">{p.name}</h3>
            <p className="mt-1 text-sm text-muted">{p.description}</p>
            <div className="mt-5 flex items-end gap-1">
              <span className="text-4xl font-bold tracking-tight">{p.price}</span>
              <span className="pb-1 text-sm text-muted">{p.period}</span>
            </div>
            <ul className="mt-6 flex-1 space-y-2.5 text-sm">
              {p.features.map((f) => (
                <li key={f} className="flex items-center gap-2 text-muted">
                  <Check size={15} className="text-success" />
                  {f}
                </li>
              ))}
            </ul>
            <Link
              href="/app/feed"
              className={`mt-7 ${p.highlight ? "btn btn-primary" : "btn btn-ghost"} w-full`}
            >
              {p.cta}
            </Link>
          </motion.div>
        ))}
      </motion.div>
    </section>
  );
}
