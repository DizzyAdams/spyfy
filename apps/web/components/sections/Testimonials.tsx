"use client";

import { motion } from "framer-motion";
import { Quote } from "lucide-react";
import { TESTIMONIALS } from "@/lib/data";
import { staggerContainer, fadeUp } from "@/lib/motion";

export function Testimonials() {
  return (
    <section className="mx-auto max-w-7xl px-5 py-24">
      <motion.div
        initial={{ opacity: 0, y: 16 }}
        whileInView={{ opacity: 1, y: 0 }}
        viewport={{ once: true }}
        transition={{ duration: 0.6 }}
        className="mb-12 max-w-2xl"
      >
        <span className="chip mb-4 !text-primary">Quem usa, aprova</span>
        <h2 className="text-3xl font-bold tracking-tight sm:text-4xl">
          A ferramenta que <span className="gradient-text">media buyers</span> sonhavam
        </h2>
      </motion.div>

      <motion.div
        variants={staggerContainer}
        initial="hidden"
        whileInView="show"
        viewport={{ once: true }}
        className="grid grid-cols-1 gap-5 md:grid-cols-3"
      >
        {TESTIMONIALS.map((t) => (
          <motion.figure key={t.name} variants={fadeUp} className="bento p-6">
            <Quote size={22} style={{ color: `hsl(${t.hue} 80% 65%)` }} />
            <blockquote className="mt-3 text-[15px] leading-relaxed text-text">“{t.quote}”</blockquote>
            <figcaption className="mt-5 border-t border-border/70 pt-4">
              <p className="text-sm font-semibold text-text">{t.name}</p>
              <p className="text-xs text-muted">{t.role}</p>
            </figcaption>
          </motion.figure>
        ))}
      </motion.div>
    </section>
  );
}
