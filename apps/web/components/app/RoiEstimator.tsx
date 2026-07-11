"use client";

import { useState } from "react";
import { motion } from "framer-motion";
import { Calculator, TrendingUp, Gauge, Zap, Loader2 } from "lucide-react";
import { estimateOffer, isApiConfigured, type EstimateRequest, type EstimateResponse } from "@/lib/api";
import { cn } from "@/lib/utils";

function Field({
  label,
  value,
  onChange,
  step = 1,
  suffix,
}: {
  label: string;
  value: number;
  onChange: (v: number) => void;
  step?: number;
  suffix?: string;
}) {
  return (
    <label className="flex flex-col gap-1 text-xs text-muted">
      <span>{label}</span>
      <span className="flex items-center gap-1 rounded-lg border border-border bg-surface/50 px-2 py-1.5">
        <input
          type="number"
          value={value}
          min={0}
          step={step}
          onChange={(e) => onChange(Number(e.target.value) || 0)}
          className="w-full bg-transparent text-sm font-medium text-text outline-none"
        />
        {suffix && <span className="shrink-0 text-[10px] text-faint">{suffix}</span>}
      </span>
    </label>
  );
}

const SIGNAL_LABEL: Record<string, string> = {
  hot: "🔥 Hot",
  scaling: "📈 Escalando",
  warming: "🌡️ Aquecendo",
  cold: "❄️ Fria",
};

export function RoiEstimator() {
  const [days, setDays] = useState(45);
  const [variants, setVariants] = useState(4);
  const [impr, setImpr] = useState(1_000_000);
  const [engagement, setEngagement] = useState(2000);
  const [networks, setNetworks] = useState(2);
  const [countries, setCountries] = useState(2);
  const [avgTicket, setAvgTicket] = useState(47);
  const [cvr, setCvr] = useState(2);
  const [ctr, setCtr] = useState(1.2);
  const [cpm, setCpm] = useState(12);

  const [loading, setLoading] = useState(false);
  const [res, setRes] = useState<EstimateResponse | null>(null);
  const [err, setErr] = useState<string | null>(null);

  const run = async () => {
    setErr(null);
    if (!isApiConfigured()) {
      setErr("Backend não configurado (NEXT_PUBLIC_API_URL).");
      return;
    }
    setLoading(true);
    const now = new Date();
    const first = new Date(now.getTime() - days * 86_400_000);
    const body: EstimateRequest = {
      first_seen: first.toISOString(),
      last_seen: now.toISOString(),
      creative_variants: variants,
      est_impressions_low: Math.round(impr * 0.8),
      est_impressions_high: Math.round(impr * 1.2),
      engagement,
      networks,
      countries,
      avg_ticket: avgTicket || null,
      cvr: cvr || null,
      ctr: ctr || null,
      cpm: cpm || null,
    };
    const r = await estimateOffer(body);
    setLoading(false);
    if (!r) {
      setErr("Falha ao estimar (backend offline?).");
      setRes(null);
      return;
    }
    setRes(r);
  };

  return (
    <div>
      <h3 className="mb-1 flex items-center gap-2 text-sm font-semibold text-text">
        <Calculator size={16} className="text-primary" /> Estimador de ROI
      </h3>
      <p className="mb-4 text-xs text-muted">
        Simule uma oferta e veja escala, ROI e sinal — motor real do backend.
      </p>

      <div className="grid grid-cols-2 gap-2.5 sm:grid-cols-3">
        <Field label="Longevidade" value={days} onChange={setDays} suffix="d" />
        <Field label="Criativos" value={variants} onChange={setVariants} />
        <Field label="Impressões" value={impr} onChange={setImpr} step={100_000} />
        <Field label="Engajamento" value={engagement} onChange={setEngagement} step={500} />
        <Field label="Redes" value={networks} onChange={setNetworks} />
        <Field label="Países" value={countries} onChange={setCountries} />
        <Field label="Ticket médio" value={avgTicket} onChange={setAvgTicket} suffix="R$" />
        <Field label="CVR" value={cvr} onChange={setCvr} step={0.5} suffix="%" />
        <Field label="CTR" value={ctr} onChange={setCtr} step={0.1} suffix="%" />
      </div>

      <button
        type="button"
        onClick={run}
        disabled={loading}
        className="btn btn-primary mt-4 w-full justify-center !py-2.5 disabled:opacity-60"
      >
        {loading ? <Loader2 size={15} className="animate-spin" /> : <Zap size={15} />}
        {loading ? "Calculando…" : "Estimar ROI"}
      </button>

      {err && <p className="mt-3 text-xs text-[var(--warning)]">{err}</p>}

      {res && (
        <motion.div
          initial={{ opacity: 0, y: 8 }}
          animate={{ opacity: 1, y: 0 }}
          className="mt-4 space-y-3 rounded-xl border border-border bg-surface/40 p-4"
        >
          <div className="grid grid-cols-2 gap-3">
            <div>
              <p className="text-[10px] uppercase tracking-wider text-faint">Winning score</p>
              <p className="font-mono text-lg font-bold text-text tabular-nums">
                {res.winning_score.toFixed(1)}
              </p>
            </div>
            <div>
              <p className="text-[10px] uppercase tracking-wider text-faint">Sinal</p>
              <p className="text-sm font-semibold text-[var(--success)]">
                {SIGNAL_LABEL[res.scaling_signal] ?? res.scaling_signal}
              </p>
            </div>
            <div>
              <p className="text-[10px] uppercase tracking-wider text-faint">ROI</p>
              <p className="font-mono text-lg font-bold text-[var(--success)] tabular-nums">
                {res.est_roi_pct}%
              </p>
            </div>
            <div>
              <p className="text-[10px] uppercase tracking-wider text-faint">ROAS</p>
              <p className="font-mono text-lg font-bold text-text tabular-nums">
                {res.est_roas}x
              </p>
            </div>
          </div>

          <div className="grid grid-cols-2 gap-x-4 gap-y-1 border-t border-border pt-3 text-xs">
            <span className="text-muted">Impressões (est.)</span>
            <span className="text-right font-mono text-text tabular-nums">
              {res.est_impressions.toLocaleString("pt-BR")}
            </span>
            <span className="text-muted">Gasto/dia (est.)</span>
            <span className="text-right font-mono text-text tabular-nums">
              R${res.est_daily_spend.toFixed(0)}
            </span>
            <span className="text-muted">Receita/dia (est.)</span>
            <span className="text-right font-mono text-text tabular-nums">
              R${res.est_daily_revenue.toFixed(0)}
            </span>
            <span className="text-muted">Lucro/dia (est.)</span>
            <span className="text-right font-mono font-semibold text-[var(--success)] tabular-nums">
              R${res.est_daily_profit.toFixed(0)}
            </span>
            <span className="text-muted">Confiança</span>
            <span className="text-right font-mono text-text tabular-nums">
              {(res.confidence * 100).toFixed(0)}%
            </span>
          </div>

          {res.notes.length > 0 && (
            <ul className="space-y-1 border-t border-border pt-3">
              {res.notes.map((n, i) => (
                <li key={i} className="flex items-start gap-1.5 text-xs text-muted">
                  <TrendingUp size={12} className="mt-0.5 shrink-0 text-primary" aria-hidden />
                  {n}
                </li>
              ))}
            </ul>
          )}
        </motion.div>
      )}
    </div>
  );
}
