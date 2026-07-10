export function cn(...classes: Array<string | false | null | undefined>): string {
  return classes.filter(Boolean).join(" ");
}

// Format a winning score band with label + semantic color (never color-only — see design-system).
export type ScoreBand = { label: string; color: string; key: "hot" | "scaling" | "warming" | "cold" };

export function scoreBand(score: number): ScoreBand {
  if (score >= 80) return { label: "Vencedora", color: "var(--success)", key: "hot" };
  if (score >= 60) return { label: "Escalando", color: "#0EA5E9", key: "scaling" };
  if (score >= 40) return { label: "Aquecendo", color: "var(--warning)", key: "warming" };
  return { label: "Fria", color: "var(--muted)", key: "cold" };
}

export function formatNumber(n: number): string {
  if (n >= 1_000_000) return (n / 1_000_000).toFixed(1).replace(/\.0$/, "") + "M";
  if (n >= 1_000) return (n / 1_000).toFixed(1).replace(/\.0$/, "") + "k";
  return String(n);
}
