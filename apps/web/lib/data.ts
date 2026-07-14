export type Network = "meta" | "tiktok" | "google" | "youtube" | "native" | "pinterest";
export type Format = "video" | "image" | "carousel";

export interface Offer {
  id: string;
  headline: string;
  advertiser: string;
  network: Network;
  format: Format;
  niche: string;
  longevityDays: number;
  winningScore: number;
  estImpressions: number;
  country: string;
  thumbnailHue: number;
  gradient: [string, string];
  image?: string; // URL of the actual ad creative (photo/video poster)
  thumb?: string; // thumbnail URL
  videoUrl?: string; // direct mp4/webm of the creative video (plays inline)
  bullets: string[];
  cta: string;
  /** DESTINO REAL da oferta (landing page / snapshot do anúncio). O card e o
   *  detalhe abrem este link em nova aba. Vem do backend; nunca vazio após
   *  o enriquecimento (offers_service garante fallback a partir de snapshotUrl). */
  link?: string;
  funnel: { type: string; label: string; stack?: string }[];
  vslSeconds: number;
  transcript: { t: string; label: string; text: string }[];
  /** Derivado (opcional) — índice de escala 0–100; o cliente recalcula via scaleIndex(). */
  scaleIndex?: number;
  /** Derivado (opcional) — gasto diário estimado em BRL; o cliente recalcula via spendBand(). */
  spendPerDay?: number;
  // --- Campos vindos do backend (/v1/offers) — enriquecimento real ---
  /** Sinal de escala calculado no backend (roi._scaling_signal). */
  scalingSignal?: string;
  /** ROI % estimado (backend). */
  estRoiPct?: number;
  /** ROAS estimado (backend). */
  estRoas?: number;
  /** Probabilidade de vencer (radar.win_probability, 0–1). */
  winProb?: number;
  /** Lucro diário estimado (BRL, backend). */
  estDailyProfit?: number;
  /** Gasto diário estimado (BRL, backend, mais preciso que spendPerDay). */
  estDailySpend?: number;
  /** Receita diária estimada (BRL, backend). */
  estDailyRevenue?: number;
  /** Confiança da estimativa (0–1). */
  confidence?: number;
  /** Origem ("library" quando minerado das Ad Libraries). */
  source?: string;
}

export const NETWORKS: { key: Network; label: string; color: string }[] = [
  { key: "meta", label: "Meta", color: "#1877F2" },
  { key: "tiktok", label: "TikTok", color: "#FE2C55" },
  { key: "google", label: "Google", color: "#EA4335" },
  { key: "youtube", label: "YouTube", color: "#FF0000" },
  { key: "native", label: "Native", color: "#A855F7" },
  { key: "pinterest", label: "Pinterest", color: "#E60023" },
];

export const OFFERS: Offer[] = [
  {
    id: "ofr_123",
    headline: "Emagreça 7kg em 21 dias sem dietas malucas",
    advertiser: "HealthBR",
    network: "meta",
    format: "video",
    niche: "Emagrecimento",
    longevityDays: 63,
    winningScore: 92.4,
    estImpressions: 4_200_000,
    country: "BR",
    thumbnailHue: 280,
    gradient: ["#6E56CF", "#22D3EE"],
    image: "https://images.unsplash.com/photo-1511884642898-4c92249e20b6?w=800&q=80",
    thumb: "https://images.unsplash.com/photo-1511884642898-4c92249e20b6?w=800&q=80",
    videoUrl: "/videos/fitness.mp4",
    bullets: [
      "Protocolo de 3 passos sem academia",
      "Resultados visíveis na primeira semana",
      "Garantia de 24h ou dinheiro de volta",
    ],
    cta: "Quero emagrecer agora",
    funnel: [
      { type: "lp", label: "Landing Page", stack: "ClickFunnels" },
      { type: "vsl", label: "VSL 14min", stack: "Vimeo" },
      { type: "checkout", label: "Checkout", stack: "Cartpanda" },
      { type: "upsell", label: "Upsell 1", stack: "Cartpanda" },
      { type: "ty", label: "Thank You", stack: "Kiwify" },
    ],
    vslSeconds: 842,
    transcript: [
      { t: "00:00", label: "Hook", text: "Você já tentou de tudo e nada funcionou de verdade?" },
      { t: "01:12", label: "Problema", text: "A indústria da dieta lucra com seu fracasso." },
      { t: "03:40", label: "Solução", text: "O protocolo de 3 passos que reativa seu metabolismo." },
      { t: "09:05", label: "Oferta", text: "Acesso completo por menos que um cafezinho por dia." },
      { t: "13:20", label: "CTA", text: "Clique e garanta sua vaga com garantia de 24h." },
    ],
  },
  {
    id: "ofr_204",
    headline: "Liberte sua renda com tráfego pago em 30 dias",
    advertiser: "AfiliadoPro",
    network: "tiktok",
    format: "video",
    niche: "Finanças",
    longevityDays: 41,
    winningScore: 81.7,
    estImpressions: 2_800_000,
    country: "BR",
    thumbnailHue: 190,
    gradient: ["#22D3EE", "#2563EB"],
    image: "https://images.unsplash.com/photo-1460925895917-afdab827c52f?w=800&q=80",
    thumb: "https://images.unsplash.com/photo-1460925895917-afdab827c52f?w=800&q=80",
    videoUrl: "/videos/finance.mp4",
    bullets: [
      "Método validado por +3.000 alunos",
      "Sem precisar aparecer (faceless)",
      "Mentoria ao vivo toda semana",
    ],
    cta: "Quero minha liberdade",
    funnel: [
      { type: "lp", label: "Landing Page", stack: "Elementor" },
      { type: "vsl", label: "VSL 9min", stack: "YouTube" },
      { type: "checkout", label: "Checkout", stack: "Hotmart" },
      { type: "upsell", label: "Mentoria", stack: "Hotmart" },
      { type: "ty", label: "Thank You", stack: "Hotmart" },
    ],
    vslSeconds: 540,
    transcript: [
      { t: "00:00", label: "Hook", text: "Trabalhar 8h por dia não é liberdade." },
      { t: "00:48", label: "Problema", text: "O emprego não te dá escala." },
      { t: "04:10", label: "Solução", text: "Tráfego pago faceless com IA." },
      { t: "07:30", label: "Oferta", text: "Turma limitada com mentoria." },
      { t: "08:40", label: "CTA", text: "Garanta sua vaga agora." },
    ],
  },
  {
    id: "ofr_318",
    headline: "Pele de vidro: o ritual de 3 minutos que virou febre",
    advertiser: "GlowSkin",
    network: "meta",
    format: "carousel",
    niche: "Beleza / Nutra",
    longevityDays: 88,
    winningScore: 88.1,
    estImpressions: 6_100_000,
    country: "BR",
    thumbnailHue: 330,
    gradient: ["#EC4899", "#6E56CF"],
    image: "https://images.unsplash.com/photo-1542204165-65bf26472b9b?w=800&q=80",
    thumb: "https://images.unsplash.com/photo-1542204165-65bf26472b9b?w=800&q=80",
    bullets: ["Fórmula com niacinamida + vitamina C", "Resultado em 14 dias", "Frete grátis hoje"],
    cta: "Comprar com frete grátis",
    funnel: [
      { type: "lp", label: "Landing Page", stack: "Shopify" },
      { type: "checkout", label: "Checkout", stack: "Shopify" },
      { type: "upsell", label: "Bundle", stack: "Shopify" },
      { type: "ty", label: "Thank You", stack: "Shopify" },
    ],
    vslSeconds: 0,
    transcript: [],
  },
];

OFFERS.push(
  {
    id: "ofr_441",
    headline: "Recupere seu ex em 7 dias com psicologia comportamental",
    advertiser: "AmorPleno",
    network: "youtube",
    format: "video",
    niche: "Relacionamento",
    longevityDays: 27,
    winningScore: 74.3,
    estImpressions: 1_900_000,
    country: "PT",
    thumbnailHue: 12,
    gradient: ["#F97316", "#EC4899"],
    image: "https://images.unsplash.com/photo-1522338242992-e1a54906a8da?w=800&q=80",
    thumb: "https://images.unsplash.com/photo-1522338242992-e1a54906a8da?w=800&q=80",
    videoUrl: "/videos/sample1.mp4",
    bullets: ["Gatilhos mentais comprovados", "Sem implorar ou humilhar", "Plano passo a passo"],
    cta: "Quero meu amor de volta",
    funnel: [
      { type: "lp", label: "Landing Page", stack: "ClickFunnels" },
      { type: "vsl", label: "VSL 21min", stack: "Vimeo" },
      { type: "checkout", label: "Checkout", stack: "Kiwify" },
      { type: "ty", label: "Thank You", stack: "Kiwify" },
    ],
    vslSeconds: 1260,
    transcript: [],
  },
  {
    id: "ofr_512",
    headline: "O mini-site que gera leads no piloto automático",
    advertiser: "LeadFlow",
    network: "google",
    format: "image",
    niche: "Marketing / SaaS",
    longevityDays: 54,
    winningScore: 79.6,
    estImpressions: 1_200_000,
    country: "US",
    thumbnailHue: 150,
    gradient: ["#16A34A", "#22D3EE"],
    image: "https://images.unsplash.com/photo-1551434678-e076c223a692?w=800&q=80",
    thumb: "https://images.unsplash.com/photo-1551434678-e076c223a692?w=800&q=80",
    bullets: ["Templates prontos de alta conversão", "Integração com CRM nativa", "Setup em 5 minutos"],
    cta: "Criar meu funil",
    funnel: [
      { type: "lp", label: "Landing Page", stack: "Webflow" },
      { type: "checkout", label: "Checkout", stack: "Stripe" },
      { type: "ty", label: "Thank You", stack: "Stripe" },
    ],
    vslSeconds: 0,
    transcript: [],
  },
  {
    id: "ofr_607",
    headline: "Dólar alto? Proteja sua reserva com ouro digital",
    advertiser: "ReservaForte",
    network: "native",
    format: "image",
    niche: "Investimentos",
    longevityDays: 35,
    winningScore: 68.9,
    estImpressions: 980_000,
    country: "BR",
    thumbnailHue: 45,
    gradient: ["#D97706", "#6E56CF"],
    image: "https://images.unsplash.com/photo-1551288049-bebda4e38f71?w=800&q=80",
    thumb: "https://images.unsplash.com/photo-1551288049-bebda4e38f71?w=800&q=80",
    bullets: ["Custódia 100% regulada", "Comece com R$ 50", "Liquidez diária"],
    cta: "Quero proteger meu dinheiro",
    funnel: [
      { type: "lp", label: "Landing Page", stack: "Unbounce" },
      { type: "checkout", label: "Checkout", stack: "Stripe" },
      { type: "ty", label: "Thank You", stack: "Stripe" },
    ],
    vslSeconds: 0,
    transcript: [],
  }
);

export const PRICING = [
  {
    name: "Free",
    price: "R$0",
    priceValue: 0,
    period: "/mês",
    description: "Comece a explorar ofertas vencedoras.",
    features: ["20 buscas/dia", "1 clonagem/mês", "Rede Meta", "Score de vencedora"],
    highlight: false,
    cta: "Começar grátis",
    checkoutUrl: "/app/feed",
  },
  {
    name: "Pro",
    price: "R$129",
    priceValue: 129,
    period: "/mês",
    description: "Para media buyers e afiliados que escalam.",
    features: [
      "Busca ilimitada",
      "100 clonagens/mês",
      "Todas as redes",
      "API (10k req)",
      "Alertas em tempo real",
    ],
    highlight: true,
    cta: "Assinar Pro",
    checkoutUrl: "/app/checkout?plan=pro",
  },
  {
    name: "Agency",
    price: "R$349",
    priceValue: 349,
    period: "/mês",
    description: "Para agências e equipes de performance.",
    features: [
      "Tudo do Pro",
      "500 clonagens/mês",
      "Workspaces + white-label",
      "API (100k req)",
      "Suporte prioritário",
    ],
    highlight: false,
    cta: "Falar com vendas",
    checkoutUrl: "/app/checkout?plan=agency",
  },
];

export interface Competitor {
  name: string;
  multi: boolean | string;
  longevity: boolean | string;
  vsl: boolean;
  cloneLP: boolean;
  cloneFunnel: boolean;
  agents: boolean;
  realtime: boolean;
  isUs?: boolean;
}

export const COMPETITORS: Competitor[] = [
  { name: "AdSpy", multi: false, longevity: "parcial", vsl: false, cloneLP: false, cloneFunnel: false, agents: false, realtime: false },
  { name: "BigSpy", multi: true, longevity: "parcial", vsl: false, cloneLP: false, cloneFunnel: false, agents: false, realtime: false },
  { name: "Minea", multi: "parcial", longevity: "parcial", vsl: false, cloneLP: false, cloneFunnel: false, agents: false, realtime: false },
  { name: "Anstrex", multi: "native", longevity: false, vsl: false, cloneLP: true, cloneFunnel: false, agents: false, realtime: false },
  { name: "Foreplay", multi: true, longevity: false, vsl: false, cloneLP: false, cloneFunnel: false, agents: false, realtime: false },
  { name: "SpyFy", multi: true, longevity: true, vsl: true, cloneLP: true, cloneFunnel: true, agents: true, realtime: true, isUs: true },
];

export const TESTIMONIALS = [
  { name: "Bruno M.", role: "Media Buyer · R$150k/mês", quote: "O score de longevidade mudou meu processo. Paro de testar oferta morta e vou direto no que escala.", hue: 280 },
  { name: "Carla S.", role: "Copywriter freelancer", quote: "Transcrição de VSL com marcação de estrutura me economiza 3 horas por brief. É ridículo de útil.", hue: 190 },
  { name: "Diego R.", role: "Afiliado de infoprodutos", quote: "Clonar o funil inteiro em menos de um minuto e exportar o ZIP? Isso destruiu o trabalho manual.", hue: 330 },
];

export const STATS = [
  { value: "1B+", label: "anúncios indexados" },
  { value: "10+", label: "redes cobertas" },
  { value: "<60s", label: "para clonar um funil" },
  { value: "95%", label: "fidelidade do clone" },
];

export function getOffer(id: string): Offer | undefined {
  return OFFERS.find((o) => o.id === id);
}
