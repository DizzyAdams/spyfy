"use client";

import { motion } from "framer-motion";
import { Search, Copy, FileText, Bot, BarChart3, Bell, Library, ShieldCheck } from "lucide-react";
import { staggerContainer, fadeUp } from "@/lib/motion";

const features = [
  {
    icon: Search,
    title: "Discovery inteligente",
    desc: "Busca híbrida (BM25 + kNN semântico) sobre bilhões de anúncios. Filtros combináveis e ranking por winning score.",
    span: "lg:col-span-2",
    accent: "#6E56CF",
  },
  {
    icon: Copy,
    title: "Offer Cloner",
    desc: "Reconstrói LP + funil inteiro (checkout, upsell, downsell) em < 60s, com fidelidade > 95%.",
    span: "",
    accent: "#22D3EE",
  },
  {
    icon: FileText,
    title: "Transcrição de VSL",
    desc: "Whisper + LLM transcrevem e resumem vídeos longos, com marcação de estrutura (hook, problema, solução, CTA).",
    span: "",
    accent: "#EC4899",
  },
  {
    icon: Bot,
    title: "Sub-agents de IA",
    desc: "Agentes LangGraph raspam, classificam e reconstroem ofertas 24/7 — sem você levantar um dedo.",
    span: "lg:col-span-2",
    accent: "#16A34A",
  },
  {
    icon: BarChart3,
    title: "Analytics de mercado",
    desc: "Trend radar, saturation index e competitor watch em dashboards OLAP em tempo quase real.",
    span: "",
    accent: "#F97316",
  },
  {
    icon: Bell,
    title: "Alertas em tempo real",
    desc: "Saiba no instante em que um concorrente entra em escala. Slack, e-mail, webhook ou app.",
    span: "",
    accent: "#2563EB",
  },
  {
    icon: Library,
    title: "Swipe file colaborativo",
    desc: "Coleções compartilhadas, tags e histórico imutável. Nada se perde quando o anúncio sai do ar.",
    span: "",
    accent: "#A855F7",
  },
  {
    icon: ShieldCheck,
    title: "Garantia 24h de fidelidade",
    desc: "QA agent valida cada clone antes de liberar. Você exporta um ZIP pronto pra hospedar.",
    span: "lg:col-span-2",
    accent: "#22D3EE",
  },
];

export function Features() {
  return (
    <section id="recursos" className="relative mx-auto max-w-7xl px-5 py-24">
      <motion.div
        initial={{ opacity: 0, y: 16 }}
        whileInView={{ opacity: 1, y: 0 }}
        viewport={{ once: true }}
        transition={{ duration: 0.6, ease: [0.22, 1, 0.36, 1] }}
        className="mb-12 max-w-2xl"
      >
        <span className="chip mb-4 !text-primary">Recursos</span>
        <h2 className="text-3xl font-bold tracking-tight sm:text-4xl">
          Tudo que você precisa pra <span className="gradient-text">vencer no tráfego</span>
        </h2>
        <p className="mt-3 text-muted">
          Não é só “ver anúncio”. É encontrar a oferta certa, entender o funil e ter o clone na mão — num só lugar.
        </p>
      </motion.div>

      <motion.div
        variants={staggerContainer}
        initial="hidden"
        whileInView="show"
        viewport={{ once: true, margin: "-60px" }}
        className="grid grid-cols-1 gap-4 sm:grid-cols-2 lg:grid-cols-4"
      >
        {features.map((f) => (
          <motion.div
            key={f.title}
            variants={fadeUp}
            className={`bento group p-5 ${f.span}`}
          >
            <div
              className="mb-4 grid h-11 w-11 place-items-center rounded-xl"
              style={{ background: `${f.accent}1f`, color: f.accent }}
            >
              <f.icon size={22} />
            </div>
            <h3 className="text-base font-semibold text-text">{f.title}</h3>
            <p className="mt-2 text-sm leading-relaxed text-muted">{f.desc}</p>
          </motion.div>
        ))}
      </motion.div>
    </section>
  );
}
