"use client";

import { useEffect, useRef, useState } from "react";
import Link from "next/link";
import { motion, AnimatePresence, useReducedMotion } from "framer-motion";
import {
  ArrowLeft, Copy, Bookmark, BookmarkCheck, Bell, Play, Check, Loader2, Download, ExternalLink, ListChecks,
} from "lucide-react";
import { Offer, NETWORKS } from "@/lib/data";
import { scoreBand, formatNumber, cn } from "@/lib/utils";
import { OfferCreative } from "../OfferCreative";
import { FunnelDiagram } from "../illustrations/FunnelDiagram";

const cloneSteps = ["Fetch da LP", "Download de assets", "Detecção de funil", "Fingerprint de stack", "Extração de copy", "Empacotando ZIP"];

export function OfferDetail({ offer }: { offer: Offer }) {
  const band = scoreBand(offer.winningScore);
  const net = NETWORKS.find((n) => n.key === offer.network);
  const reduce = useReducedMotion();
  const [saved, setSaved] = useState<Set<string>>(new Set());
  const [justSaved, setJustSaved] = useState(false);
  const saveTimeout = useRef<ReturnType<typeof setTimeout> | undefined>(undefined);

  useEffect(() => {
    try {
      const raw = localStorage.getItem("spyfy_saved");
      if (raw) setSaved(new Set(JSON.parse(raw)));
    } catch { /* corrupt storage */ }
  }, []);

  useEffect(() => {
    clearTimeout(saveTimeout.current);
    saveTimeout.current = setTimeout(() => {
      localStorage.setItem("spyfy_saved", JSON.stringify([...saved]));
    }, 300);
    return () => clearTimeout(saveTimeout.current);
  }, [saved]);

  const toggleSave = () => {
    const wasSaved = saved.has(offer.id);
    setSaved((prev) => {
      const next = new Set(prev);
      if (next.has(offer.id)) next.delete(offer.id);
      else next.add(offer.id);
      return next;
    });
    if (!wasSaved) {
      setJustSaved(true);
      setTimeout(() => setJustSaved(false), 1500);
    }
  };

  const [step, setStep] = useState(-1);
  const timer = useRef<ReturnType<typeof setInterval> | undefined>(undefined);

  const startClone = () => {
    if (step >= 0 && step < 6) return;
    setStep(0);
    if (reduce) { setStep(6); return; }
    clearInterval(timer.current);
    timer.current = setInterval(() => {
      setStep((s) => {
        if (s >= 5) { clearInterval(timer.current); return 6; }
        return s + 1;
      });
    }, 700);
  };

  useEffect(() => () => clearInterval(timer.current), []);
  const done = step === 6;

  return (
    <div className="mx-auto max-w-6xl">
      <Link href="/app/feed" className="mb-5 inline-flex items-center gap-1.5 text-sm text-muted transition-colors hover:text-text">
        <ArrowLeft size={16} /> Voltar ao feed
      </Link>

      <div className="grid gap-6 lg:grid-cols-[1.4fr_1fr]">
        <div className="space-y-5">
          <div className="overflow-hidden rounded-2xl border border-border">
            <OfferCreative hue={offer.thumbnailHue} gradient={offer.gradient} label={offer.headline} format={offer.format} image={offer.image} videoUrl={offer.videoUrl} className="aspect-[16/9] w-full" />
          </div>

          <div className="flex flex-wrap items-center gap-2">
            <span className="chip" style={{ color: net?.color }}>
              <span className="h-1.5 w-1.5 rounded-full" style={{ background: net?.color }} /> {net?.label}
            </span>
            <span className="chip">{offer.niche}</span>
            <span className="chip">{offer.country}</span>
            <span className="chip" style={{ color: band.color }}>{band.label} · {offer.winningScore.toFixed(1)}</span>
            <span className="chip">{offer.longevityDays}d ativa</span>
            <span className="chip">{formatNumber(offer.estImpressions)} impr.</span>
          </div>

          <h1 className="text-2xl font-bold leading-tight tracking-tight">{offer.headline}</h1>
          <p className="text-sm text-muted">por {offer.advertiser}</p>

          <ul className="space-y-2">
            {offer.bullets.map((b) => (
              <li key={b} className="flex items-start gap-2 text-sm">
                <Check size={16} className="mt-0.5 shrink-0 text-success" />
                <span className="text-muted">{b}</span>
              </li>
            ))}
          </ul>

          <div className="rounded-2xl border border-border bg-surface/50 p-5">
            <div className="flex items-center justify-between">
              <div>
                <p className="text-sm font-semibold text-text">Offer Cloner</p>
                <p className="text-xs text-muted">Reconstrução do funil em tempo real</p>
              </div>
              <button onClick={startClone} disabled={step >= 0 && step < 6} className="btn btn-primary !py-2 !text-[13px]">
                {done ? <Download size={14} /> : <Copy size={14} />}
                {done ? "Exportar ZIP" : step >= 0 ? "Clonando…" : "Clonar agora"}
              </button>
            </div>

            <ol className="mt-4 space-y-1.5">
              {cloneSteps.map((label, i) => {
                const state = step < 0 ? "idle" : step === i ? "running" : step > i ? "done" : "pending";
                return (
                  <li key={label} className="flex items-center gap-3 text-sm">
                    <span className={cn("grid h-5 w-5 place-items-center rounded-full border text-[10px]", state === "done" && "border-success bg-success/20 text-success", state === "running" && "border-primary bg-primary/20 text-primary", (state === "pending" || state === "idle") && "border-border text-muted/50")}>
                      {state === "done" ? <Check size={12} /> : state === "running" ? <Loader2 size={12} className="animate-spin" /> : i + 1}
                    </span>
                    <span className={cn(state === "idle" || state === "pending" ? "text-muted/60" : "text-text")}>{label}</span>
                    {state === "running" && (
                      <span className="ml-auto h-1 w-16 overflow-hidden rounded-full bg-bg">
                        <span className="block h-full w-1/2 animate-[shimmer_1.2s_infinite] bg-primary" />
                      </span>
                    )}
                  </li>
                );
              })}
            </ol>

            <AnimatePresence>
              {done && (
                <motion.div initial={{ opacity: 0, y: 6 }} animate={{ opacity: 1, y: 0 }} className="mt-4 flex items-center justify-between rounded-xl border border-success/30 bg-success/10 px-4 py-3 text-sm">
                  <span className="font-medium text-success">Clone completo · 95.2% fidelidade</span>
                  <ExternalLink size={15} className="text-success" />
                </motion.div>
              )}
            </AnimatePresence>
          </div>

          <div className="flex gap-2">
            <div className="relative flex-1">
              <button onClick={toggleSave} className="btn btn-ghost w-full">
                <motion.span
                  key={saved.has(offer.id) ? "saved" : "unsaved"}
                  initial={{ scale: 0.8 }}
                  animate={{ scale: 1 }}
                  transition={{ type: "spring", stiffness: 400, damping: 15 }}
                  className="inline-flex items-center gap-1.5"
                >
                  {saved.has(offer.id) ? <BookmarkCheck size={15} className="text-[var(--accent)]" /> : <Bookmark size={15} />}
                  {saved.has(offer.id) ? "Salvo" : "Salvar"}
                </motion.span>
              </button>
              <AnimatePresence>
                {justSaved && (
                  <motion.span
                    initial={{ opacity: 0, y: 6, scale: 0.9 }}
                    animate={{ opacity: 1, y: 0, scale: 1 }}
                    exit={{ opacity: 0, y: -4 }}
                    transition={{ duration: 0.2 }}
                    className="absolute -bottom-5 left-1/2 -translate-x-1/2 whitespace-nowrap rounded-full bg-primary/20 px-2 py-0.5 text-[10px] text-primary"
                  >
                    Salvo!
                  </motion.span>
                )}
              </AnimatePresence>
            </div>
            <button className="btn btn-ghost flex-1"><Bell size={15} /> Alerta</button>
          </div>
        </div>

        <div className="space-y-5">
          <div className="rounded-2xl border border-border bg-surface/50 p-5">
            <h3 className="mb-4 flex items-center gap-2 text-sm font-semibold text-text">
              <ListChecks size={16} className="text-primary" /> Funil reconstruído
            </h3>
            <FunnelDiagram steps={offer.funnel} />
          </div>

          <div className="rounded-2xl border border-border bg-surface/50 p-5">
            <h3 className="mb-3 text-sm font-semibold text-text">Stack detectada</h3>
            <div className="flex flex-wrap gap-2">
              {Array.from(new Set(offer.funnel.map((f) => f.stack).filter(Boolean) as string[])).map((s) => (
                <span key={s} className="chip !text-accent">{s}</span>
              ))}
              <span className="chip !text-warning">Pixel FB</span>
              <span className="chip !text-warning">Pixel TikTok</span>
            </div>
          </div>

          {offer.transcript.length > 0 && (
            <div className="rounded-2xl border border-border bg-surface/50 p-5">
              <h3 className="mb-3 flex items-center gap-2 text-sm font-semibold text-text">
                <Play size={15} className="text-accent" /> Transcrição da VSL
              </h3>
              <ul className="space-y-3">
                {offer.transcript.map((t, i) => (
                  <motion.li
                    key={i}
                    initial={{ opacity: 0, x: -8 }}
                    whileInView={{ opacity: 1, x: 0 }}
                    viewport={{ once: true }}
                    transition={{ duration: 0.3, delay: i * 0.05 }}
                    className="flex gap-3 text-sm"
                  >
                    <span className="shrink-0 font-mono text-xs text-muted">{t.t}</span>
                    <span>
                      <span className="font-semibold text-primary">{t.label}: </span>
                      <span className="text-muted">{t.text}</span>
                    </span>
                  </motion.li>
                ))}
              </ul>
            </div>
          )}
        </div>
      </div>
    </div>
  );
}
