# A10 — Dedup / Graph (memória de longo prazo / RAG)

Agente da squad de mining responsável por **deduplicação** de ofertas e pela
**memória de longo prazo** (grafo RAG) que alimenta busca semântica e detecção
de ofertas similares.

## Responsabilidades
- Evitar re-processar/alertar a mesma oferta (idempotência).
- Indexar ofertas em memória vetorial para RAG (`query` por similaridade).
- Expor a memória via API para o frontend e para o pipeline autônomo.

## Mapeamento de código
- **`apps/workers-py/spyfy/agents/memory.py`** — núcleo da memória:
  - `OfferMemory` — store de ofertas com embeddings.
  - `HashEmbedding` — embedding **determinístico offline** (hash do conteúdo),
    não precisa de modelo/LLM (roda 100% no free tier).
  - `ModelEmbedding` — embedding via `chromadb` quando instalado (mais rico);
    degrada para `HashEmbedding` se ausente.
  - `add_offers(offers)` — indexa e devolve nº de novos.
  - `find_similar(o)` — ofertas próximas (cosseno próprio).
  - `query(text, n)` / `count()` — RAG e tamanho do índice.
- **`apps/workers-py/spyfy/agents/orchestrator.py`** — nó `dedup`
  (`_make_dedup`): ao fim do pipeline, chama `memory.add_offers` e
  `memory.find_similar` para cada oferta.

## Exposição via API
- `POST /v1/agents/rag/query` — `{ "text": "...", "n": 3 }` → hits por similaridade.
- `GET  /v1/agents/rag/count` — nº de ofertas indexadas.

## SLA / propriedades
- **Idempotente**: re-indexar a mesma oferta não duplica.
- Offline-safe: embeddings determinísticos, sem GPU/LLM.
