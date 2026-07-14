"use client";

import { motion } from "framer-motion";
import { XCircle, ArrowLeft, RefreshCw } from "lucide-react";
import { fadeUp, staggerContainer } from "@/lib/motion";

export default function CheckoutCancelPage() {
  return (
    <motion.div
      initial="hidden"
      animate="show"
      variants={staggerContainer}
      className="mx-auto flex max-w-lg flex-col items-center justify-center gap-6 py-16 text-center"
    >
      <motion.span
        variants={fadeUp}
        className="inline-flex h-20 w-20 items-center justify-center rounded-full bg-error/10 text-error"
      >
        <XCircle size={40} />
      </motion.span>

      <motion.div variants={fadeUp} className="space-y-2">
        <h1 className="text-2xl font-bold text-text">Pagamento não concluído</h1>
        <p className="text-sm text-muted">
          O pagamento foi cancelado ou não pôde ser processado. Nenhum valor foi cobrado.
        </p>
      </motion.div>

      <motion.div variants={fadeUp} className="flex gap-3">
        <a
          href="/app/checkout"
          className="inline-flex items-center gap-2 rounded-xl bg-primary px-6 py-3 text-sm font-semibold text-white shadow-lg shadow-primary/25 transition-all hover:brightness-110"
        >
          <RefreshCw size={16} /> Tentar novamente
        </a>
        <a
          href="/app/feed"
          className="inline-flex items-center gap-2 rounded-xl border border-border bg-surface/40 px-6 py-3 text-sm font-medium text-text transition-all hover:bg-surface/60"
        >
          <ArrowLeft size={16} /> Voltar
        </a>
      </motion.div>
    </motion.div>
  );
}
