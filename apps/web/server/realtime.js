/**
 * SpyFy Realtime Radar — WebSocket server (zero dependencies, Node built-ins only).
 *
 * Implements a minimal but correct RFC6455 server (handshake + frame
 * encode/decode + ping/pong + close) on top of `http`, plus a live "miner"
 * that simulates scraping ad offers in real time and streams them to clients.
 *
 * In production this process would be fed by the Python scrapers
 * (apps/workers-py) via a queue; here we ship a self-contained generator so
 * the real-time UX is fully demonstrable and testable end-to-end.
 *
 * Env:
 *   REALTIME_PORT      (default 4000)
 *   REALTIME_INTERVAL  base ms between mined offers (default 1600)
 */

"use strict";

const http = require("http");
const crypto = require("crypto");

const PORT = Number(process.env.REALTIME_PORT || 4000);
const BASE_INTERVAL = Number(process.env.REALTIME_INTERVAL || 1600);
const TOKEN = process.env.REALTIME_TOKEN || "";
const SIMULATE = (process.env.REALTIME_SIMULATE || "true").toLowerCase() !== "false";
const WS_GUID = "258EAFA5-E914-47DA-95CA-C5AB0DC85B11";

/* ------------------------------------------------------------------ */
/* WebSocket framing (server -> client is never masked)               */
/* ------------------------------------------------------------------ */

function encodeFrame(data, opcode = 0x1) {
  const payload = Buffer.isBuffer(data) ? data : Buffer.from(String(data), "utf8");
  const len = payload.length;
  let header;
  if (len < 126) {
    header = Buffer.alloc(2);
    header[1] = len;
  } else if (len < 65536) {
    header = Buffer.alloc(4);
    header[1] = 126;
    header.writeUInt16BE(len, 2);
  } else {
    header = Buffer.alloc(10);
    header[1] = 127;
    header.writeBigUInt64BE(BigInt(len), 2);
  }
  header[0] = 0x80 | (opcode & 0x0f); // FIN + opcode
  return Buffer.concat([header, payload]);
}

function makeReceiver(socket, onMessage, onClose) {
  let buf = Buffer.alloc(0);

  socket.on("data", (chunk) => {
    buf = Buffer.concat([buf, chunk]);
    while (true) {
      if (buf.length < 2) return;
      const opcode = buf[0] & 0x0f;
      const masked = (buf[1] & 0x80) === 0x80;
      let len = buf[1] & 0x7f;
      let offset = 2;
      if (len === 126) {
        if (buf.length < offset + 2) return;
        len = buf.readUInt16BE(offset);
        offset += 2;
      } else if (len === 127) {
        if (buf.length < offset + 8) return;
        len = Number(buf.readBigUInt64BE(offset));
        offset += 8;
      }
      const maskLen = masked ? 4 : 0;
      if (buf.length < offset + maskLen + len) return;

      let payload = buf.slice(offset + maskLen, offset + maskLen + len);
      if (masked) {
        const mask = buf.slice(offset, offset + 4);
        const out = Buffer.alloc(len);
        for (let i = 0; i < len; i++) out[i] = payload[i] ^ mask[i & 3];
        payload = out;
      }
      buf = buf.slice(offset + maskLen + len);

      if (opcode === 0x8) {
        try { socket.write(encodeFrame(Buffer.alloc(0), 0x8)); } catch (_) {}
        socket.end();
        return;
      } else if (opcode === 0x9) {
        try { socket.write(encodeFrame(payload, 0xa)); } catch (_) {}
        continue;
      } else if (opcode === 0x1 || opcode === 0x2) {
        try { onMessage(payload.toString("utf8")); } catch (_) {}
        continue;
      }
      continue;
    }
  });

  socket.on("close", onClose);
  socket.on("error", () => {
    try { socket.destroy(); } catch (_) {}
  });
}

/* ===== MINER SECTION BELOW ===== */

const NETWORKS = ["meta", "tiktok", "google", "youtube", "native", "pinterest"];
const FORMATS = ["video", "video", "video", "image", "carousel"];
const COUNTRIES = ["BR", "BR", "BR", "US", "PT", "MX", "AR", "CO"];
const HUES = [265, 190, 330, 45, 200, 300, 155, 25];
const GRADIENTS = [
  ["#6E56CF", "#22D3EE"], ["#22D3EE", "#2563EB"], ["#7C5CFF", "#2DD4FF"],
  ["#A855F7", "#22D3EE"], ["#F472B6", "#7C5CFF"], ["#34D399", "#22D3EE"],
  ["#FBBF24", "#6E56CF"], ["#FB7185", "#7C5CFF"],
];
const LP_STACKS = ["ClickFunnels", "Unbounce", "Elementor", "Kajabi", "Leadpages"];
const VSL_STACKS = ["Vimeo", "YouTube", "Wistia"];
const CHECKOUT_STACKS = ["Cartpanda", "Hotmart", "Kiwify", "Stripe"];
const TRANSCRIPT_LABELS = ["Hook", "Problema", "Solução", "Oferta", "CTA"];

const NICHE_DATA = {
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
    bullets: [
      "Custódia 100% regulada",
      "Comece com R$50",
      "Liquidez diária",
    ],
    ctas: ["Quero proteger meu dinheiro", "Começar agora"],
  },
};

/* ===== MINER GEN BELOW ===== */

const NICHE_KEYS = Object.keys(NICHE_DATA);
const pick = (arr) => arr[Math.floor(Math.random() * arr.length)];
const randInt = (min, max) => Math.floor(Math.random() * (max - min + 1)) + min;

function buildTranscript(vslSeconds) {
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

function buildFunnel(vslSeconds) {
  const steps = [
    { type: "lp", label: "Landing Page", stack: pick(LP_STACKS) },
    { type: "vsl", label: `VSL ${Math.round(vslSeconds / 60)}min`, stack: pick(VSL_STACKS) },
    { type: "checkout", label: "Checkout", stack: pick(CHECKOUT_STACKS) },
    { type: "upsell", label: "Upsell 1", stack: pick(CHECKOUT_STACKS) },
    { type: "ty", label: "Thank You", stack: pick(CHECKOUT_STACKS) },
  ];
  if (!vslSeconds) steps.splice(1, 1); // drop VSL when absent
  return steps;
}

function generateOffer() {
  const niche = pick(NICHE_KEYS);
  const d = NICHE_DATA[niche];
  const hasVsl = Math.random() > 0.25;
  const vslSeconds = hasVsl ? randInt(300, 900) : 0;
  const network = pick(NETWORKS);
  return {
    id: `live_${Date.now().toString(36)}_${Math.random().toString(36).slice(2, 7)}`,
    headline: pick(d.headlines),
    advertiser: pick(d.advertisers),
    network,
    format: pick(FORMATS),
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

/* ===== CLIENTS SECTION BELOW ===== */

const clients = new Set();

/* ------------------------------------------------------------------ */
/* Ingestão de ofertas reais (scraper/workers)                        */
/* Normaliza qualquer payload para o shape do Offer do app web.        */
/* ------------------------------------------------------------------ */

function num(v, d) {
  const n = Number(v);
  return Number.isFinite(n) ? n : d;
}

const VALID_NETWORKS = new Set(NETWORKS);

function normalizeOffer(raw) {
  const o = raw && typeof raw === "object" ? raw : {};
  return {
    id:
      typeof o.id === "string" && o.id
        ? o.id
        : `ext_${Date.now().toString(36)}_${Math.random().toString(36).slice(2, 7)}`,
    headline: String(o.headline || o.title || "Oferta sem título"),
    advertiser: String(o.advertiser || o.advertiser_name || "Anunciante"),
    network: VALID_NETWORKS.has(o.network) ? o.network : "meta",
    format: ["video", "image", "carousel"].includes(o.format) ? o.format : "video",
    niche: String(o.niche || "Geral"),
    longevityDays: Math.max(0, Math.round(num(o.longevityDays ?? o.longevity_days, 1))),
    winningScore: Math.min(
      100,
      Math.max(0, Math.round(num(o.winningScore ?? o.winning_score ?? o.score, 0) * 10) / 10)
    ),
    estImpressions: Math.max(0, Math.round(num(o.estImpressions ?? o.est_impressions, 0))),
    country: String(o.country || "BR"),
    thumbnailHue: Math.round(num(o.thumbnailHue, pick(HUES))),
    gradient:
      Array.isArray(o.gradient) && o.gradient.length >= 2
        ? [String(o.gradient[0]), String(o.gradient[1])]
        : pick(GRADIENTS),
    bullets: Array.isArray(o.bullets) ? o.bullets.map(String) : [],
    cta: String(o.cta || "Ver oferta"),
    funnel:
      Array.isArray(o.funnel) && o.funnel.length
        ? o.funnel.map((f) => ({
            type: String(f.type || "lp"),
            label: String(f.label || "Etapa"),
            stack: f.stack ? String(f.stack) : undefined,
          }))
        : [{ type: "lp", label: "Landing Page" }],
    vslSeconds: Math.max(0, Math.round(num(o.vslSeconds ?? o.vsl_seconds, 0))),
    transcript: Array.isArray(o.transcript) ? o.transcript : [],
  };
}

function ingestOffer(raw) {
  const offer = normalizeOffer(raw);
  stats.totalMined += 1;
  rateWindow.push(Date.now());
  emitOffer(offer);
  broadcastStats();
  return offer;
}

const stats = { totalMined: 0, startedAt: Date.now() };
const rateWindow = [];

function currentStats() {
  const now = Date.now();
  while (rateWindow.length && now - rateWindow[0] > 60_000) rateWindow.shift();
  return {
    totalMined: stats.totalMined,
    perMin: rateWindow.length,
    connections: clients.size,
    uptimeSec: Math.floor((now - stats.startedAt) / 1000),
  };
}

function passesFilter(o, c) {
  const f = c.filters;
  if (f.network && f.network !== "all" && o.network !== f.network) return false;
  if (f.niche && f.niche !== "Todos" && o.niche !== f.niche) return false;
  if (f.country && f.country !== "all" && o.country !== f.country) return false;
  if (c.query) {
    const q = c.query.toLowerCase();
    const hay = `${o.headline} ${o.advertiser} ${o.niche} ${o.cta}`.toLowerCase();
    if (!hay.includes(q)) return false;
  }
  return true;
}

function send(client, obj) {
  if (client.socket.writable) {
    try { client.socket.write(encodeFrame(JSON.stringify(obj))); } catch (_) {}
  }
}

function emitOffer(offer) {
  for (const c of clients) {
    if (c.socket.writable && passesFilter(offer, c)) {
      send(c, { type: "offer.new", offer, stats: currentStats() });
    }
  }
}

function broadcastStats() {
  const s = currentStats();
  for (const c of clients) send(c, { type: "stats", stats: s });
}

/* ------------------------------------------------------------------ */
/* Miner loop                                                          */
/* ------------------------------------------------------------------ */

function scheduleNext() {
  const jitter = randInt(-500, 1100);
  const delay = Math.max(450, BASE_INTERVAL + jitter);
  setTimeout(() => {
    const offer = generateOffer();
    stats.totalMined += 1;
    rateWindow.push(Date.now());
    emitOffer(offer);
    scheduleNext();
  }, delay);
}

/* ------------------------------------------------------------------ */
/* HTTP + WebSocket server                                             */
/* ------------------------------------------------------------------ */

const server = http.createServer((req, res) => {
  if (req.url === "/health") {
    res.writeHead(200, { "Content-Type": "application/json" });
    res.end(JSON.stringify({ ok: true, ...currentStats() }));
    return;
  }

  const isIngest =
    req.method === "POST" &&
    (req.url === "/v1/radar/ingest" || req.url.startsWith("/v1/radar/ingest?"));
  if (isIngest) {
    if (TOKEN) {
      const auth = req.headers["authorization"] || "";
      const ok =
        auth === `Bearer ${TOKEN}` || (req.url && req.url.includes(`token=${TOKEN}`));
      if (!ok) {
        res.writeHead(401, { "Content-Type": "application/json" });
        res.end(JSON.stringify({ ok: false, error: "unauthorized" }));
        return;
      }
    }
    let data = "";
    let aborted = false;
    req.on("data", (c) => {
      data += c;
      if (data.length > 1_000_000) {
        aborted = true;
        req.destroy();
      }
    });
    req.on("end", () => {
      if (aborted) return;
      let body;
      try {
        body = JSON.parse(data || "{}");
      } catch {
        res.writeHead(400, { "Content-Type": "application/json" });
        res.end(JSON.stringify({ ok: false, error: "invalid json" }));
        return;
      }
      const raws = body.offers
        ? body.offers
        : body.offer
        ? [body.offer]
        : body.type === "offer.new" && body.offer
        ? [body.offer]
        : [body];
      const ingested = raws.map(ingestOffer);
      res.writeHead(200, { "Content-Type": "application/json" });
      res.end(
        JSON.stringify({ ok: true, ingested: ingested.length, stats: currentStats() })
      );
    });
    return;
  }

  res.writeHead(426, { "Content-Type": "text/plain" });
  res.end("Upgrade Required");
});

server.on("upgrade", (req, socket) => {
  const key = req.headers["sec-websocket-key"];
  if (!key) {
    socket.destroy();
    return;
  }
  const accept = crypto.createHash("sha1").update(key + WS_GUID).digest("base64");
  socket.write(
    "HTTP/1.1 101 Switching Protocols\r\n" +
      "Upgrade: websocket\r\n" +
      "Connection: Upgrade\r\n" +
      `Sec-WebSocket-Accept: ${accept}\r\n\r\n`
  );
  socket.setNoDelay(true);

  const client = {
    socket,
    alive: true,
    filters: { network: "all", niche: "Todos", country: "all" },
    query: "",
  };
  clients.add(client);

  socket.on("pong", () => {
    client.alive = true;
  });

  makeReceiver(
    socket,
    (raw) => {
      let msg;
      try { msg = JSON.parse(raw); } catch (_) { return; }
      if (msg && msg.type === "subscribe" && msg.filters) {
        client.filters = {
          network: msg.filters.network || "all",
          niche: msg.filters.niche || "Todos",
          country: msg.filters.country || "all",
        };
      } else if (msg && msg.type === "search") {
        client.query = typeof msg.query === "string" ? msg.query : "";
      }
    },
    () => clients.delete(client)
  );

  // Heartbeat
  const hb = setInterval(() => {
    if (!client.alive) {
      try { socket.destroy(); } catch (_) {}
      clearInterval(hb);
      return;
    }
    client.alive = false;
    if (socket.writable) {
      try { socket.write(encodeFrame(Buffer.alloc(0), 0x9)); } catch (_) {}
    }
  }, 25_000);
  socket.on("close", () => clearInterval(hb));

  // Greet + immediately show live activity
  send(client, { type: "hello", stats: currentStats() });
  const first = generateOffer();
  if (passesFilter(first, client)) emitOffer(first);
});

server.listen(PORT, () => {
  console.log(`[spyfy-realtime] Radar WebSocket ouvindo em ws://localhost:${PORT}`);
  console.log(`[spyfy-realtime] healthcheck: http://localhost:${PORT}/health`);
  if (SIMULATE) {
    console.log("[spyfy-realtime] simulador LIGADO — gerando ofertas de demonstração");
    scheduleNext();
  } else {
    console.log(
      "[spyfy-realtime] simulador DESLIGADO (REALTIME_SIMULATE=false) — aguardando ofertas reais via /v1/radar/ingest"
    );
  }
  setInterval(broadcastStats, 5000);
});



