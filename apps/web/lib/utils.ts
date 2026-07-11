export function cn(...classes: Array<string | false | null | undefined>): string {
  return classes.filter(Boolean).join(" ");
}

// Format a winning score band with label + semantic color (never color-only — see design-system).
// `tone` lets the UI pair the color with a textual/icon signal (e.g. positive/good/warn/muted)
// so state is perceivable WITHOUT relying on color alone.
export type ScoreBand = {
  label: string;
  color: string;
  key: "hot" | "scaling" | "warming" | "cold";
  tone: "positive" | "good" | "warn" | "muted";
};

export function scoreBand(score: number): ScoreBand {
  if (score >= 80)
    return { label: "Vencedora", color: "var(--success)", key: "hot", tone: "positive" };
  if (score >= 60)
    return { label: "Escalando", color: "#0EA5E9", key: "scaling", tone: "good" };
  if (score >= 40)
    return { label: "Aquecendo", color: "var(--warning)", key: "warming", tone: "warn" };
  return { label: "Fria", color: "var(--muted)", key: "cold", tone: "muted" };
}

export function formatNumber(n: number): string {
  if (n >= 1_000_000) return (n / 1_000_000).toFixed(1).replace(/\.0$/, "") + "M";
  if (n >= 1_000) return (n / 1_000).toFixed(1).replace(/\.0$/, "") + "k";
  return String(n);
}

// Índice de Escala (0–100): mede o "tamanho + qualidade + consistência" de uma oferta.
// Combina três fatores normalizados para 0–1 e ponderados:
//   • winningScore / 100                                 (peso ~0.5) — força da oferta
//   • log10(estImpressions + 1) / log10(10_000_000 + 1)  (peso ~0.3) — volume (log-escala, teto ~10M impr.)
//   • min(longevityDays, 92) / 92                        (peso ~0.2) — consistência / longevidade
// Resultado = 100 * (0.5*score + 0.3*impr + 0.2*longev), arredondado a 1 casa decimal.
export function scaleIndex(o: {
  winningScore: number;
  estImpressions: number;
  longevityDays: number;
}): number {
  const scorePart = o.winningScore / 100;
  const impPart = Math.log10(o.estImpressions + 1) / Math.log10(10_000_000 + 1);
  const longevityPart = Math.min(o.longevityDays, 92) / 92;
  const idx = 100 * (0.5 * scorePart + 0.3 * impPart + 0.2 * longevityPart);
  return Math.round(idx * 10) / 10;
}

// Estimativa de gasto diário (BRL) a partir de impressões e longevidade.
// Assume CPM (custo por mil impressões) de R$9:
//   daily = round( (estImpressions / 1000) * 9 / max(longevityDays, 1) )
// Faixas de escala de investimento:
//   daily < 2000            → "Teste"
//   2000 ≤ daily ≤ 15000    → "Escalando"
//   daily > 15000           → "Saturado"
export function spendBand(
  estImpressions: number,
  longevityDays = 1
): { daily: number; label: string } {
  const daily = Math.round(
    ((estImpressions / 1000) * 9) / Math.max(longevityDays, 1)
  );
  const label = daily < 2000 ? "Teste" : daily <= 15000 ? "Escalando" : "Saturado";
  return { daily, label };
}
