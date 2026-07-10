# ⚡ Real-Time Cloning Engine — SpyFy

Engine que **clona ofertas em tempo real**, transmitindo cada etapa (fetch → assets → funil → copy → pronto) para a UI enquanto acontece. Construída sobre os agents LangGraph (ver [langgraph-agents.md](langgraph-agents.md)).

## Objetivo

- Do clique "Clonar" ao bundle pronto, com **feedback ao vivo** (< 60s).
- Nada de "aguarde..." opaco: o usuário vê o funil sendo descoberto passo a passo.

## Visão geral

```
[Usuário] clica Clonar
    │  POST /v1/clones (SSE/WS upgrade)
    ▼
[API BFF] cria thread LangGraph (thread_id = clone-<id>)
    │
    ▼
[LangGraph runtime] astream(stream_mode=["updates","custom"])
    ├── lp_fetched
    ├── assets_saved (n)
    ├── stack_detected {cartpanda, fb_pixel}
    ├── funnel_mapped (5 steps)
    ├── copy_extracted
    ├── qa {fidelity: 0.97}
    └── clone_ready {url}
    │
    ▼
[Event Gateway] → WebSocket/SSE → [Frontend timeline ao vivo]
```

## Transporte em tempo real

### Opção A — Server-Sent Events (SSE)
```python
from fastapi.responses import StreamingResponse

@router.post("/v1/clones/{offer_id}/stream")
async def stream_clone(offer_id: str):
    async def gen():
        config = {"configurable": {"thread_id": f"clone-{offer_id}"}}
        async for chunk in graph.astream(
            init_state(offer_id), config, stream_mode="updates"
        ):
            for node, update in chunk.items():
                for ev in update.get("events", []):
                    yield f"event: {ev['type']}\ndata: {json.dumps(ev)}\n\n"
        yield "event: done\ndata: {}\n\n"
    return StreamingResponse(gen(), media_type="text/event-stream")
```

### Opção B — WebSocket (bidirecional; permite cancelar/aprovar)
```python
@app.websocket("/ws/clones/{offer_id}")
async def ws_clone(ws: WebSocket, offer_id: str):
    await ws.accept()
    config = {"configurable": {"thread_id": f"clone-{offer_id}"}}
    async for chunk in graph.astream(init_state(offer_id), config,
                                     stream_mode=["updates", "custom"]):
        await ws.send_json(serialize(chunk))
```

**Recomendação:** WebSocket (permite human-in-the-loop e cancelamento).

## Frontend (timeline ao vivo)

```tsx
const es = new EventSource(`/v1/clones/${offerId}/stream`);
es.addEventListener("lp_fetched",    () => addStep("Landing page capturada"));
es.addEventListener("assets_saved",  e => addStep(`${data(e).n} assets salvos`));
es.addEventListener("stack_detected",e => setStack(data(e).stack));
es.addEventListener("funnel_mapped", e => setFunnel(data(e).steps));
es.addEventListener("clone_ready",   e => setDownload(data(e).url));
es.addEventListener("done", () => es.close());

## Mapeamento de funil (funnel walker)

```
Do LP:
  1. Encontrar CTAs/botões de compra (heurística + IA).
  2. Seguir cada CTA em browser isolado.
  3. Detectar checkout (domínio/stack conhecidos).
  4. Após "compra simulada" (sem pagar) detectar upsell/downsell.
  5. Registrar TY page.
  6. Cada step vira funnel_step + snapshot.
```
- Executa em **sandbox isolada** (segurança — ver [security.md](../09-security/security.md)).
- Nunca completa pagamento; só mapeia a estrutura pública.

## Infra do runtime em tempo real

```
┌──────────────┐   WS/SSE   ┌───────────────┐
│  Frontend    │◀──────────▶│  Realtime GW  │  (FastAPI, sticky sessions)
└──────────────┘            └──────┬────────┘
                                   │ pub/sub (Redis)
                            ┌──────▼────────┐
                            │ LangGraph      │  (workers Python, GPU p/ ASR)
                            │ runtime + ckpt │
                            └──────┬────────┘
                            ┌──────▼────────┐
                            │ Browser pool  │  (Playwright, sandbox)
                            │ + R2 assets   │
                            └───────────────┘
```

- **Sticky sessions** ou pub/sub Redis para rotear eventos ao socket certo com múltiplos gateways.
- **Checkpointer Postgres** → se o worker cair, outro retoma o thread e continua o stream.
- **Browser pool** reutilizável; sandbox por clone.

## Resiliência

- Falha em etapa → retry no nó (LangGraph) sem reiniciar tudo.
- Worker morre → checkpoint permite retomar; cliente reconecta ao mesmo `thread_id`.
- Timeout global por clone (ex.: 180s) → degrada para "parcial" com o que já capturou.

## Cancelamento & aprovação (HIL)

```python
# cliente envia {"cmd":"cancel"} pelo WS
await graph.aupdate_state(config, {"cancelled": True})
# nós checam state["cancelled"] e encerram cedo

# aprovação humana (baixa confiança) — retoma após update
await graph.aupdate_state(config, {"needs_human": False})
await graph.ainvoke(None, config)
```

## Performance & custo

- Assets baixados em paralelo (`asyncio.gather`).
- Enrichment/transcrição só sob demanda e cacheados.
- Modelo barato (Haiku) para roteamento; modelo forte só para extração/estrutura.
- Meta: p95 de clonagem < 60s; custo IA por clone < $0.10.

## Métricas do engine

- Tempo por etapa (histograma).
- Clone success rate, fidelidade média.
- Taxa de reconexão de socket.
- Custo por clone.

## Segurança (crítico)

- Fetch de LPs externas em sandbox **sem acesso à VPC**.
- HTML sanitizado antes do preview.
- Allowlist/denylist de domínios; proteção SSRF.
- Ver [security.md](../09-security/security.md) e [compliance.md](../09-security/compliance.md).

```

UI mostra um **stepper animado**: cada etapa concluindo ao vivo, thumbnails dos assets aparecendo, badges de stack.

## Pipeline de clonagem (etapas)

| # | Etapa | Nó LangGraph | Evento | Tempo típico |
|---|-------|--------------|--------|--------------|
| 1 | Render LP | `fetch_lp` | `lp_fetched` | 3–8s |
| 2 | Baixar assets | `grab_assets` | `assets_saved` | 5–15s |
| 3 | Fingerprint | `fingerprint` | `stack_detected` | <1s |
| 4 | Mapear funil | `map_funnel` | `funnel_mapped` | 10–25s |
| 5 | Extrair copy | `extract_copy` | `copy_extracted` | 2–5s |
| 6 | Empacotar | `package` | `clone_ready` | 2–5s |
| 7 | QA visual | `qa_check` | `qa` | 2–4s |
