# SpyFy Realtime Radar — Busca de ofertas ao vivo (scraper + WebSocket)

Feature essencial para minerar anúncios em tempo real: um servidor WebSocket
(zero dependências, Node built-ins) faz o papel do "Radar" que descobre ofertas
a cada ~1–2,6s e as envia para o app web, que renderiza o feed ao vivo com
destaque das ofertas novas, badge "AO VIVO", ticker e métricas do Radar.

## Como rodar

```bash
# opção A — tudo de uma vez (WS + Next dev), cross-platform:
cd apps/web
npm run dev:all

# opção B — dois terminais:
npm run realtime   # sobe o Radar WebSocket em ws://localhost:4000
npm run dev        # sobe o Next em http://localhost:3000
```

Abra `http://localhost:3000/app/feed`. O badge no topo e no feed mostra
**AO VIVO** assim que o socket conecta; novas ofertas entram no grid com o
selo **Nova** e um anel de destaque que some sozinho.

### Variáveis de ambiente

| Var | Default | Descrição |
|-----|---------|-----------|
| `REALTIME_PORT` | `4000` | Porta do servidor WS. |
| `NEXT_PUBLIC_REALTIME_PORT` | `4000` | Porta usada pelo cliente quando `NEXT_PUBLIC_REALTIME_URL` não está setado. |
| `NEXT_PUBLIC_REALTIME_URL` | — | **URL completa** do WS que o navegador usa (ex.: `wss://radar.exemplo.com`). Sobrepõe host+porta. Essencial em produção. |
| `REALTIME_INTERVAL` | `1600` | Intervalo base (ms) entre ofertas mineradas (modo simulador). |
| `REALTIME_TOKEN` | — | Se definido, exige `Authorization: Bearer <token>` no `/v1/radar/ingest`. |
| `REALTIME_SIMULATE` | `true` | `false` desliga o gerador interno — só entra o que o scraper mandar. |

Healthcheck: `http://localhost:4000/health` (JSON com `totalMined`, `perMin`, `connections`, `uptimeSec`).

## Arquitetura

```
┌──────────────┐   ws://host:4000   ┌──────────────────────────┐
│  Web (Next)  │ ◀──── offer.new ───│  server/realtime.js       │
│  FeedView    │ ──── subscribe ───▶│  • RFC6455 WS (sem deps)  │
│  (browser)   │ ──── search ─────▶│  • Miner (gerador pt-BR)  │
└──────────────┘                    └──────────────────────────┘
   RealtimeProvider                        heartbeat 25s
   • 1 socket por aba                      stats broadcast 5s
   • reconnect exponencial (1s→15s)
   • watchdog 18s (fecha socket morto)
   • fallback offline (mostra seed OFFERS)
```

### Servidor (`apps/web/server/realtime.js`)
- Handshake + frame encode/decode + ping/pong + close implementados à mão
  sobre `http`/`crypto` (RFC6455). Sem `npm install` de nada.
- **Miner**: gera ofertas `_realistas_` (pt-BR) com rede, nicho, país, score,
  impressões, funil, VSL/transcripta — varia por nicho. Em produção este
  processo seria alimentado pelos scrapers Python (`apps/workers-py`) via fila;
  aqui há um gerador embutido para a feature ser 100% demonstrável.
- Por cliente: filtro de `network`/`niche`/`country` e busca textual. Envia
  `hello` → oferta imediata → stream `offer.new` + `stats` a cada 5s.

### Ingestão de ofertas reais (scraper → Radar)
O servidor também aceita ofertas reais (do scraper Python ou qualquer produtor)
via HTTP, e as retransmite ao vivo para todos os clientes WS conectados:

```bash
curl -X POST http://localhost:4000/v1/radar/ingest \
  -H 'Content-Type: application/json' \
  -d '{"offer":{"headline":"Oferta real","advertiser":"Adv","network":"meta","niche":"Finanças","winningScore":91}}'
```

- Aceita `{ "offer": {...} }`, `{ "offers": [...] }` ou `{ "type":"offer.new", "offer": {...} }`.
- `REALTIME_TOKEN` (opcional): se definido, exige `Authorization: Bearer <token>` (ou `?token=`).
- `REALTIME_SIMULATE=false`: desliga o gerador interno — só entra o que o scraper mandar.
- O payload é **normalizado** (`normalizeOffer`) para o shape do `Offer` do app,
  preenchendo campos faltantes (gradient, funnel, etc.) para não quebrar a UI.

Produtor Python (stdlib, sem deps) em `apps/workers-py/spyfy/realtime_producer.py`:

```bash
cd apps/workers-py
python -m spyfy.realtime_producer --sample 5
python -m spyfy.realtime_producer --file ofertas.json --url http://localhost:4000
python -m spyfy.realtime_producer --token <REALTIME_TOKEN> --radar q1   # usa spyfy.radar
```

A função `radar_offer_to_payload()` converte um `RadarOffer` no payload do app web.

### Cliente (`apps/web/lib/realtime/*`)
- `RealtimeProvider.tsx`: abre **um** `WebSocket` por aba, reconecta com
  backoff exponencial + jitter, tem watchdog, faz dedupe por `id`, marca
  `newIds` e expõe `status/offers/stats/filters/query` + `setFilters/search`.
- `FeedView.tsx`: consome o provider, mostra `LiveBadge`, stats (mineradas/min,
  indexadas, radar online), ticker ao vivo e destaque das ofertas novas.
- `AppShell.tsx`: a busca global envia `search` para o Radar (debounce 250ms).
- `OfferCard`: prop `isNew` → selo "Nova" + ring (respeita reduced-motion).

## UX / Validação

- ✅ Badge "AO VIVO" com pulso (desliga em `prefers-reduced-motion`).
- ✅ Novas ofertas entram no topo com selo "Nova" e anel de destaque.
- ✅ Filtros (rede/nicho/país/ordenação) e busca globais funcionam em tempo real.
- ✅ Reconexão automática + estado "Offline" gracioso (mostra seed estático).
- ✅ Build limpo (`next build`) e tipos validados.

### Deploy

**Local (Docker Compose)** — o `docker-compose.yml` já sobe `web` + `api` + `realtime`:
```bash
docker compose up -d --build
# web:      http://localhost:3000/app/feed
# realtime: ws://localhost:4000  (mapeado no host; web aponta NEXT_PUBLIC_REALTIME_URL=ws://localhost:4000)
# health:   http://localhost:4000/health
```
O `realtime` tem healthcheck no `/health`. Para produção real (sem simulador):
`REALTIME_SIMULATE=false REALTIME_TOKEN=seu-token docker compose up -d realtime`.

**Vercel (web) + Radar externo**
WebSockets não rodam em funções serverless da Vercel. O build da web continua
green; o cliente detecta a ausência do socket e cai para **Offline** exibindo o
seed estático. Para o Radar ao vivo, rode `server/realtime.js` num processo
long-running (VM, container, Railway, Render, Fly.io…) e defina na Vercel:
```
NEXT_PUBLIC_REALTIME_URL=wss://seu-radar.exemplo.com
```
O `RealtimeProvider` usará essa URL completa (sobrepõe host+porta). Proteja o
ingest com `REALTIME_TOKEN` e exponha apenas a porta 4000 (ou atrás de TLS).

**Scraper → Radar**
Em produção, rode `apps/workers-py` e empurre ofertas reais:
```bash
cd apps/workers-py
# minerador contínuo (ponte scraper -> Radar)
python -m spyfy.scraper_bridge --niche keto --network meta --interval 3 --token <REALTIME_TOKEN>
# ou lote avulso
python -m spyfy.realtime_producer --file ofertas.json --token <REALTIME_TOKEN>
```
Troque o corpo de `spyfy.scraper_bridge.mine()` pela chamada real ao
Meta/TikTok/Google Ad Library quando os miners A2/A3 estiverem prontos — o
transporte e o loop não mudam.
