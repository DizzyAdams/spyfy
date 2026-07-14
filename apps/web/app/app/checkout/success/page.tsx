"use client";

import { motion } from "framer-motion";
import { Check, ArrowLeft } from "lucide-react";
import { fadeUp, staggerContainer } from "@/lib/motion";

export default function CheckoutSuccessPage() {
  return (
    <motion.div
      initial="hidden"
      animate="show"
      variants={staggerContainer}
      className="mx-auto flex max-w-lg flex-col items-center justify-center gap-6 py-16 text-center"
    >
      <motion.span
        variants={fadeUp}
        className="inline-flex h-20 w-20 items-center justify-center rounded-full bg-success/10 text-success"
      >
        <Check size={40} />
      </motion.span>

      <motion.div variants={fadeUp} className="space-y-2">
        <h1 className="text-2xl font-bold text-text">Pagamento aprovado!</h1>
        <p className="text-sm text-muted">
          Sua assinatura foi ativada. Você já pode acessar todos os recursos do seu plano.
        </p>
      </motion.div>

      <motion.div variants={fadeUp}>
        <a
          href="/app/feed"
          className="inline-flex items-center gap-2 rounded-xl bg-primary px-6 py-3 text-sm font-semibold text-white shadow-lg shadow-primary/25 transition-all hover:brightness-110"
        >
          <ArrowLeft size={16} /> Ir para o feed
        </a>
      </motion.div>
    </motion.div>
  );
}
