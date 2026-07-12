# Browser Miner (A2) — SpyFy

O **Browser Miner (A2)** é o agente de mineração *headless* de landing pages do SpyFy, desenhado para redes que exigem render de JS e captura de assets completos.

## Propósito

Minerar páginas-alvo extraindo **DOM, JSON de APIs internas e assets** (imagens, vídeo, CSS, fontes) via browser automatizado. SLA de processamento: **< 8s por página**.

## Stack prevista

- **Playwright** (Chromium headless) — render e interações.
- **Rotação de proxy** — geo-consistência (UA, viewport, tz, locale) por alvo.
- **Interceptação de XHR** — captura do JSON da API interna (preferível ao DOM) com fallback de extração por DOM.
- **Anti-bot** — stealth, scroll humano com jitter, troca de proxy/fingerprint em detecção de wall.

## Hook de design — degradação graciosa

Playwright, Whisper e LangChain são **intencionalmente EXCLUÍDOS** do conjunto de dependências do free-tier:

- `requirements.txt` / `requirements.docker.txt` focam no que **roda offline**.
- A2 é um *design hook*: quando essas dependências pesadas estão ausentes, ele **degrada para A1 (scout) + A3 (library)**.
- Nesse modo, a descoberta segue por API pública (A3) e rastreamento leve (A1), sem browser.

## Isolamento (sandbox)

- Execução em **sandbox isolado** (container efêmero, sem acesso à rede interna).
- Pool de browsers com semáforo; contextos descartados por job.
- Sem estado persistente entre execuções; saída via evento normalizado (`AdDiscovered`).

## Quando é ativado

SPA pesada / sem API (ex.: TikTok CC, Google Transparency) e captura de LP para clonagem. Ver [browser-mining.md](./browser-mining.md).
