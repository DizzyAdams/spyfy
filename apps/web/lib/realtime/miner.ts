import type { Offer, Network } from "@/lib/data";

/* Gerador de ofertas "mineradas" — usado pelo transporte SSE da Vercel
 * (Route Handler) e espelha o miner do server/realtime.js. Mantido em TS
 * para rodar dentro do bundle do Next sem dependências externas. */

export const NETWORKS: Network[] = [
  "meta", "tiktok", "google", "youtube", "native", "pinterest",
];
const FORMATS = ["video", "video", "video", "image", "carousel"] as const;
const COUNTRIES = ["BR", "BR", "BR", "US", "PT", "MX", "AR", "CO"];
const HUES = [265, 190, 330, 45, 200, 300, 155, 25];
const GRADIENTS: [string, string][] = [
  ["#6E56CF", "#22D3EE"], ["#22D3EE", "#2563EB"], ["#7C5CFF", "#2DD4FF"],
  ["#A855F7", "#22D3EE"], ["#F472B6", "#7C5CFF"], ["#34D399", "#22D3EE"],
  ["#FBBF24", "#6E56CF"], ["#FB7185", "#7C5CFF"],
];
const LP_STACKS = ["ClickFunnels", "Unbounce", "Elementor", "Kajabi", "Leadpages"];
const VSL_STACKS = ["Vimeo", "YouTube", "Wistia"];
const CHECKOUT_STACKS = ["Cartpanda", "Hotmart", "Kiwify", "Stripe"];
const TRANSCRIPT_LABELS = ["Hook", "Problema", "Solução", "Oferta", "CTA"];

const NICHE_DATA: Record<
  string,
  { advertisers: string[]; headlines: string[]; bullets: string[]; ctas: string[] }
> = {
  "Emagrecimento": {
    advertisers: ["HealthBR", "VitaCorp", "NutriFoco", "CorpoLeve"],
    headlines: [
      "Emagreça 7kg em 21 dias sem dietas malucas",
      "Queime gordura visceral enquanto você dorme",
      "O protocolo de 3 passos que reativa seu metabolismo",
      "Sumiu a barriga sem abrir mão do café da manhã",
    ],
    bullets: [
      "Protocolo de 3 passos sem academia",
      "Resultados visíveis na primeira semana",
      "Garantia de 24h ou dinheiro de volta",
    ],
    ctas: ["Quero emagrecer agora", "Começar transformação"],
  },
  "Finanças": {
    advertisers: ["AfiliadoPro", "LibertaRenda", "CashFlowBR"],
    headlines: [
      "Liberte sua renda com tráfego pago em 30 dias",
      "Saia das dívidas com o método anti-juros",
      "Fatura R$10k/mês mesmo trabalhando 2h por dia",
      "O funil que vende no piloto automático",
    ],
    bullets: [
      "Método validado por +3.000 alunos",
      "Sem precisar aparecer (faceless)",
      "Mentoria ao vivo toda semana",
    ],
    ctas: ["Quero minha liberdade", "Ver método"],
  },
  "Beleza / Nutra": {
    advertisers: ["GlowLab", "DermaPlus", "BioSkin"],
    headlines: [
      "Pele de vidro em 14 dias sem laser",
      "Cílios 2x mais longos em 3 semanas",
      "O sérum que dermatologistas não recomendam",
      "Acabe com a oleosidade em 7 dias",
    ],
    bullets: [
      "Fórmula com ácido hialurônico vegano",
      "Resultado em 14 dias ou reembolso",
      "Frete grátis hoje",
    ],
    ctas: ["Quero minha pele", "Comprar agora"],
  },
  "Relacionamento": {
    advertisers: ["Conexão+", "AmorReal", "VínculoBR"],
    headlines: [
      "Faça ele te procurar primeiro (sem mandar mensagem)",
      "O segredo das mulheres que conquistam",
      "Reacenda a chama em 72h",
      "Psicologia do desejo explicada em 1 vídeo",
    ],
    bullets: [
      "Técnicas baseadas em psicologia comportamental",
      "Acesso vitalício ao portal",
      "Bônus: roteiro de primeira mensagem",
    ],
    ctas: ["Quero aprender", "Acessar método"],
  },
  "Marketing / SaaS": {
    advertisers: ["ScaleUp", "GrowthKit", "FunilPro"],
    headlines: [
      "Pare de perder leads no checkout",
      "Automatize seu funil em uma tarde",
      "ERP que o seu contador vai amar",
      "Gere 100 leads qualificados por dia",
    ],
    bullets: [
      "Integração nativa com RD/HubSpot",
      "Onboarding em 15 minutos",
      "Suporte humano em < 1h",
    ],
    ctas: ["Ver demonstração", "Começar trial"],
  },
  "Investimentos": {
    advertisers: ["CriptoSafe", "RendaBTC", "InvesteFácil"],
    headlines: [
      "Comece a investir com R$50 hoje",
      "Proteja seu dinheiro da inflação",
      "Renda passiva em dólar sem banco",
      "O portfólio das pessoas que saíram na frente",
    ],
    bullets: ["Custódia 100% regulada", "Comece com R$50", "Liquidez diária"],
    ctas: ["Quero proteger meu dinheiro", "Começar agora"],
  },
};

/* MINER FUNCS BELOW */

const NICHE_KEYS = Object.keys(NICHE_DATA);
const pick = <T,>(arr: T[]): T => arr[Math.floor(Math.random() * arr.length)];
const randInt = (min: number, max: number) =>
  Math.floor(Math.random() * (max - min + 1)) + min;

function buildTranscript(vslSeconds: number) {
  if (!vslSeconds) return [];
  const lines = [
    "Você já tentou de tudo e nada funcionou de verdade?",
    "A indústria lucra com o seu fracasso.",
    "O método validado por quem já chegou lá.",
    "Acesso completo por menos que um cafezinho por dia.",
    "Clique e garanta sua vaga com garantia total.",
  ];
  const step = Math.max(40, Math.floor(vslSeconds / lines.length));
  return lines.map((text, i) => {
    const total = i * step;
    const mm = String(Math.floor(total / 60)).padStart(2, "0");
    const ss = String(total % 60).padStart(2, "0");
    return { t: `${mm}:${ss}`, label: TRANSCRIPT_LABELS[i], text };
  });
}

function buildFunnel(vslSeconds: number) {
  const steps = [
    { type: "lp", label: "Landing Page", stack: pick(LP_STACKS) },
    { type: "vsl", label: `VSL ${Math.round(vslSeconds / 60)}min`, stack: pick(VSL_STACKS) },
    { type: "checkout", label: "Checkout", stack: pick(CHECKOUT_STACKS) },
    { type: "upsell", label: "Upsell 1", stack: pick(CHECKOUT_STACKS) },
    { type: "ty", label: "Thank You", stack: pick(CHECKOUT_STACKS) },
  ];
  if (!vslSeconds) steps.splice(1, 1);
  return steps;
}

export function generateOffer(): Offer {
  const niche = pick(NICHE_KEYS);
  const d = NICHE_DATA[niche];
  const hasVsl = Math.random() > 0.25;
  const vslSeconds = hasVsl ? randInt(300, 900) : 0;
  return {
    id: `live_${Date.now().toString(36)}_${Math.random().toString(36).slice(2, 7)}`,
    headline: pick(d.headlines),
    advertiser: pick(d.advertisers),
    network: pick(NETWORKS),
    format: pick(FORMATS as unknown as string[]) as Offer["format"],
    niche,
    longevityDays: randInt(1, 92),
    winningScore: Math.round((randInt(350, 975) / 10) * 10) / 10,
    estImpressions: randInt(2, 92) * 100_000,
    country: pick(COUNTRIES),
    thumbnailHue: pick(HUES),
    gradient: pick(GRADIENTS),
    bullets: d.bullets,
    cta: pick(d.ctas),
    funnel: buildFunnel(vslSeconds),
    vslSeconds,
    transcript: buildTranscript(vslSeconds),
  };
}

export interface MinerFilters {
  network: Network | "all";
  niche: string;
  country: string;
  query: string;
}

export function passesFilter(o: Offer, f: MinerFilters): boolean {
  if (f.network !== "all" && o.network !== f.network) return false;
  if (f.niche !== "Todos" && o.niche !== f.niche) return false;
  if (f.country !== "all" && o.country !== f.country) return false;
  if (f.query) {
    const q = f.query.toLowerCase();
    const hay = `${o.headline} ${o.advertiser} ${o.niche} ${o.cta}`.toLowerCase();
    if (!hay.includes(q)) return false;
  }
  return true;
}

