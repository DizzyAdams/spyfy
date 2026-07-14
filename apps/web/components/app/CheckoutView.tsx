"use client";

import { useState } from "react";
import { motion } from "framer-motion";
import {
  CreditCard,
  QrCode,
  Wallet,
  Bitcoin,
  Check,
  ChevronRight,
  Loader2,
  ArrowLeft,
  Copy,
  ExternalLink,
} from "lucide-react";
import { cn } from "@/lib/utils";
import { fadeUp, staggerContainer } from "@/lib/motion";

/* ─── Tipos ───────────────────────────────────────────────────── */

interface PaymentMethod {
  key: string;
  label: string;
  description: string;
  icon: string;
  enabled: boolean;
  fee_pct: number;
}

interface PaymentResult {
  payment_id: string;
  gateway: string;
  status: string;
  amount_brl: number;
  qr_code: string;
  qr_code_base64: string;
  checkout_url: string;
  wallet_address: string;
  crypto_amount: number;
  crypto_currency: string;
  expires_in: number;
}

/* ─── Dados dos gateways ──────────────────────────────────────── */

const GATEWAYS: PaymentMethod[] = [
  { key: "mercadopago", label: "Mercado Pago", description: "Cartão de crédito, boleto, PIX", icon: "credit-card", enabled: true, fee_pct: 4.99 },
  { key: "pix", label: "PIX", description: "QR code dinâmico — menor taxa", icon: "qr-code", enabled: true, fee_pct: 0.99 },
  { key: "usdt", label: "USDT (TRC-20)", description: "Stablecoin — dólar digital sem volatilidade", icon: "wallet", enabled: true, fee_pct: 1.0 },
  { key: "bitcoin", label: "Bitcoin", description: "BTC — aceito globalmente, sem chargeback", icon: "bitcoin", enabled: true, fee_pct: 1.0 },
];

const GATEWAY_ICONS: Record<string, typeof CreditCard> = {
  "credit-card": CreditCard,
  "qr-code": QrCode,
  wallet: Wallet,
  bitcoin: Bitcoin,
};

/* ─── Planos locais (fallback: API não disponível) ────────────── */

const PLANS = [
  { name: "Pro", price: 129, period: "/mês", description: "Para media buyers e afiliados que escalam." },
  { name: "Agency", price: 349, period: "/mês", description: "Para agências e equipes de performance." },
];

/* ─── Componentes UI ─────────────────────────────────────────── */

function Hairline() {
  return <div className="h-px bg-gradient-to-r from-transparent via-border/60 to-transparent" />;
}

/* ─── CheckoutView ───────────────────────────────────────────── */

export function CheckoutView() {
  const [selectedPlan, setSelectedPlan] = useState<string>("Pro");
  const [selectedGateway, setSelectedGateway] = useState<string>("mercadopago");
  const [loading, setLoading] = useState(false);
  const [result, setResult] = useState<PaymentResult | null>(null);
  const [error, setError] = useState("");
  const [copied, setCopied] = useState(false);

  const plan = PLANS.find((p) => p.name === selectedPlan) || PLANS[0];
  const gateway = GATEWAYS.find((g) => g.key === selectedGateway) || GATEWAYS[0];
  const Icon = GATEWAY_ICONS[gateway.icon] || CreditCard;

  async function handleSubmit() {
    setLoading(true);
    setError("");
    setResult(null);

    try {
      const body = {
        amount_brl: plan.price,
        gateway: selectedGateway,
        email: "user@spyfy.io",    // TODO: user real email
        user_id: "user_001",       // TODO: user real ID
        description: `SpyFy ${plan.name}`,
      };

      const res = await fetch(
        `${process.env.NEXT_PUBLIC_API_URL || "http://localhost:8000"}/v1/payments/create`,
        { method: "POST", headers: { "Content-Type": "application/json" }, body: JSON.stringify(body) },
      );

      if (!res.ok) {
        const errData = await res.json().catch(() => ({ detail: `HTTP ${res.status}` }));
        throw new Error(errData.detail || `Erro ${res.status}`);
      }

      const data: PaymentResult = await res.json();
      setResult(data);
    } catch (e) {
      setError(e instanceof Error ? e.message : "Erro ao processar pagamento");
    } finally {
      setLoading(false);
    }
  }

  function handleCopy(text: string) {
    navigator.clipboard.writeText(text);
    setCopied(true);
    setTimeout(() => setCopied(false), 2000);
  }

  /* ── Tela de resultado ─────────────────────────────────────── */

  if (result) {
    return (
      <motion.div initial="hidden" animate="show" variants={staggerContainer} className="mx-auto max-w-lg space-y-6 py-8">
        {/* Header */}
        <motion.div variants={fadeUp} className="text-center">
          <span className="inline-flex h-14 w-14 items-center justify-center rounded-2xl bg-success/10 text-success">
            <Check size={28} />
          </span>
          <h1 className="mt-4 text-xl font-semibold text-text">Pagamento criado!</h1>
          <p className="mt-1 text-sm text-muted">Siga as instruções abaixo para concluir.</p>
        </motion.div>

        {/* Detalhes */}
        <motion.div variants={fadeUp} className="rounded-xl border border-border bg-surface/40 p-5 space-y-3">
          <div className="flex items-center justify-between">
            <span className="text-sm text-muted">Valor</span>
            <span className="font-semibold text-text">
              R$ {result.amount_brl.toFixed(2)}
            </span>
          </div>
          <Hairline />
          <div className="flex items-center justify-between">
            <span className="text-sm text-muted">Gateway</span>
            <span className="text-sm font-medium text-text capitalize">{result.gateway}</span>
          </div>
          <Hairline />
          <div className="flex items-center justify-between">
            <span className="text-sm text-muted">Status</span>
            <span className="text-sm font-medium text-warning capitalize">{result.status}</span>
          </div>
          <Hairline />
          <div className="flex items-center justify-between">
            <span className="text-sm text-muted">ID</span>
            <span className="text-xs font-mono text-muted">{result.payment_id}</span>
          </div>
        </motion.div>

        {/* Ação específica do gateway */}
        <motion.div variants={fadeUp} className="space-y-3">
          {result.checkout_url && (
            <a
              href={result.checkout_url}
              target="_blank"
              rel="noopener noreferrer"
              className="flex w-full items-center justify-center gap-2 rounded-xl bg-primary px-5 py-3 text-sm font-semibold text-white shadow-lg shadow-primary/25 transition-all hover:brightness-110"
            >
              Ir para pagamento <ExternalLink size={16} />
            </a>
          )}

          {result.qr_code && (
            <div className="rounded-xl border border-border bg-surface/40 p-5 text-center space-y-3">
              {result.qr_code_base64 && (
                <img
                  src={`data:image/png;base64,${result.qr_code_base64}`}
                  alt="QR Code PIX"
                  className="mx-auto h-48 w-48 rounded-lg"
                />
              )}
              <div className="space-y-2">
                <p className="text-xs text-muted">Código copia e cola</p>
                <button
                  onClick={() => handleCopy(result.qr_code)}
                  className="inline-flex items-center gap-1.5 rounded-lg border border-border bg-surface px-4 py-2 text-xs font-mono text-text transition-colors hover:bg-surface/60"
                >
                  {result.qr_code.slice(0, 40)}...
                  {copied ? <Check size={14} className="text-success" /> : <Copy size={14} />}
                </button>
              </div>
            </div>
          )}

          {result.wallet_address && (
            <div className="rounded-xl border border-border bg-surface/40 p-5 space-y-3">
              <div className="text-center">
                <p className="text-sm font-medium text-text">Envie {result.crypto_currency}</p>
                <p className="text-xs text-muted">Rede: {result.crypto_currency === "USDT" ? "TRC-20" : "BTC"}</p>
              </div>
              <div className="flex items-center gap-2 rounded-lg border border-border bg-surface p-3">
                <code className="flex-1 truncate text-xs font-mono text-text">{result.wallet_address}</code>
                <button
                  onClick={() => handleCopy(result.wallet_address)}
                  className="shrink-0 rounded-md p-1.5 text-muted transition-colors hover:bg-surface/60"
                >
                  {copied ? <Check size={14} className="text-success" /> : <Copy size={14} />}
                </button>
              </div>
              {result.crypto_amount > 0 && (
                <div className="text-center text-sm text-muted">
                  Equivalente: <span className="font-semibold text-text">{result.crypto_amount} {result.crypto_currency}</span>
                </div>
              )}
            </div>
          )}
        </motion.div>

        <motion.div variants={fadeUp} className="text-center">
          <button
            onClick={() => { setResult(null); setSelectedGateway("mercadopago"); }}
            className="inline-flex items-center gap-1.5 text-sm text-muted transition-colors hover:text-text"
          >
            <ArrowLeft size={16} /> Novo pagamento
          </button>
        </motion.div>
      </motion.div>
    );
  }

  /* ── Tela de seleção ───────────────────────────────────────── */

  return (
    <motion.div initial="hidden" animate="show" variants={staggerContainer} className="mx-auto max-w-lg space-y-6 py-8">
      {/* Header */}
      <motion.div variants={fadeUp}>
        <h1 className="text-xl font-semibold text-text">Checkout</h1>
        <p className="mt-1 text-sm text-muted">Escolha seu plano e forma de pagamento.</p>
      </motion.div>

      {/* Seleção de plano */}
      <motion.div variants={fadeUp} className="space-y-3">
        <h2 className="text-xs font-semibold uppercase tracking-wider text-muted">Plano</h2>
        <div className="grid grid-cols-2 gap-3">
          {PLANS.map((p) => (
            <button
              key={p.name}
              onClick={() => setSelectedPlan(p.name)}
              className={cn(
                "rounded-xl border p-4 text-left transition-all",
                selectedPlan === p.name
                  ? "border-primary bg-primary/5 shadow-sm"
                  : "border-border bg-surface/30 hover:border-border/80",
              )}
            >
              <span className="text-sm font-semibold text-text">{p.name}</span>
              <div className="mt-1">
                <span className="text-lg font-bold text-text">R${p.price}</span>
                <span className="text-xs text-muted">{p.period}</span>
              </div>
              <p className="mt-1 text-xs text-muted line-clamp-2">{p.description}</p>
            </button>
          ))}
        </div>
      </motion.div>

      {/* Seleção de gateway */}
      <motion.div variants={fadeUp} className="space-y-3">
        <h2 className="text-xs font-semibold uppercase tracking-wider text-muted">Forma de pagamento</h2>
        <div className="space-y-2">
          {GATEWAYS.map((g) => {
            const GI = GATEWAY_ICONS[g.icon] || CreditCard;
            return (
              <button
                key={g.key}
                disabled={!g.enabled}
                onClick={() => setSelectedGateway(g.key)}
                className={cn(
                  "flex w-full items-center gap-4 rounded-xl border p-4 text-left transition-all",
                  selectedGateway === g.key
                    ? "border-primary bg-primary/5 shadow-sm"
                    : "border-border bg-surface/30 hover:border-border/80",
                  !g.enabled && "cursor-not-allowed opacity-40",
                )}
              >
                <span className="grid h-10 w-10 shrink-0 place-items-center rounded-lg border border-border bg-surface text-muted">
                  <GI size={18} />
                </span>
                <div className="flex-1 min-w-0">
                  <span className="block text-sm font-medium text-text">{g.label}</span>
                  <span className="block text-xs text-muted truncate">{g.description}</span>
                </div>
                <span className="text-xs text-muted">{g.fee_pct}%</span>
                {selectedGateway === g.key && <Check size={16} className="text-primary shrink-0" />}
              </button>
            );
          })}
        </div>
      </motion.div>

      {/* Resumo + submit */}
      <motion.div variants={fadeUp} className="rounded-xl border border-border bg-surface/40 p-5 space-y-3">
        <div className="flex items-center justify-between">
          <span className="text-sm text-muted">{plan.name}</span>
          <span className="font-semibold text-text">R$ {plan.price.toFixed(2)}</span>
        </div>
        <div className="flex items-center justify-between">
          <span className="text-sm text-muted">Taxa ({gateway.fee_pct}%)</span>
          <span className="text-sm text-muted">R$ {(plan.price * gateway.fee_pct / 100).toFixed(2)}</span>
        </div>
        <Hairline />
        <div className="flex items-center justify-between">
          <span className="text-sm font-semibold text-text">Total</span>
          <span className="text-lg font-bold text-text">
            R$ {(plan.price * (1 + gateway.fee_pct / 100)).toFixed(2)}
          </span>
        </div>
      </motion.div>

      {error && (
        <motion.div variants={fadeUp} className="rounded-xl border border-error/30 bg-error/5 p-4 text-sm text-error">
          {error}
        </motion.div>
      )}

      <motion.div variants={fadeUp}>
        <button
          onClick={handleSubmit}
          disabled={loading}
          className="flex w-full items-center justify-center gap-2 rounded-xl bg-primary px-5 py-3 text-sm font-semibold text-white shadow-lg shadow-primary/25 transition-all hover:brightness-110 disabled:opacity-50"
        >
          {loading ? (
            <><Loader2 size={16} className="animate-spin" /> Processando...</>
          ) : (
            <><ChevronRight size={16} /> Pagar R$ {plan.price.toFixed(2)}</>
          )}
        </button>
      </motion.div>

      <motion.p variants={fadeUp} className="text-center text-xs text-muted">
        Pagamento processado com segurança. Seus dados não são armazenados.
      </motion.p>
    </motion.div>
  );
}
