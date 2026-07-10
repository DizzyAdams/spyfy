# ✨ Enrichment & Normalização — SpyFy

## Objetivo

Transformar anúncios brutos em **dados ricos e pesquisáveis**: nicho, idioma, país, ângulo, stack, embeddings e transcrições.

## Etapas de enrichment

```
Ad bruto
  ├─ 1. Idioma (detecção)
  ├─ 2. Nicho/vertical (classificação)
  ├─ 3. Ângulo/tema (LLM + clustering)
  ├─ 4. Formato (imagem/vídeo/carrossel)
  ├─ 5. Stack/checkout (fingerprint da LP)
  ├─ 6. Transcrição de VSL (Whisper)
  ├─ 7. Extração de copy (headline/CTA/bullets)
  └─ 8. Embedding (busca semântica)
→ Offer enriquecida
```

## 1. Detecção de idioma
- `fastText` / lingua; fallback LLM.

## 2. Classificação de nicho
- Classificador fine-tuned (labels: weight_loss, finance, nutra, ecom, crypto, relationships...).
- Confiança baixa → LLM zero-shot → fila de revisão humana.

## 3. Ângulo/tema
- LLM extrai ângulo ("resultado rápido", "sem esforço", "medo/urgência").
- Clustering de embeddings agrupa ângulos emergentes (Trend Radar).

## 4. Formato
- Derivado do tipo de criativo.

## 5. Fingerprint de stack
- Analisa LP: scripts, pixels, checkout, builder.
- Ver [offer-cloner.md](../03-features/offer-cloner.md).

## 6. Transcrição de VSL
- Whisper transcreve; LLM estrutura (hook/problema/solução/oferta/CTA) e resume.
- Salva transcrição + resumo + timestamps.

## 7. Extração de copy
- LLM extrai headline, subheads, bullets, CTA, garantia, provas.
- Normaliza em campos estruturados.

## 8. Embeddings
- `text-embedding-3` (ou bge) sobre copy + transcrição.
- Armazenado em `offers.embedding` (pgvector).
- Usado em busca semântica e "ofertas similares".

## Orquestração
- Cada etapa é um worker/agent (ver [sub-agents.md](../02-team/sub-agents.md)).
- Pipeline com DAG; etapas paralelas onde possível.
- Retries + idempotência por etapa.

## Custo & performance
- Etapas caras (LLM, Whisper) só quando necessário e cacheadas.
- Dedup: não reprocessar oferta inalterada.
- Batch de embeddings.

## Qualidade
- Evals periódicos de classificação (amostra rotulada).
- Métricas: precisão de nicho, cobertura de transcrição, latência.
- Human-in-the-loop para baixa confiança.

## Saída
- Postgres: campos enriquecidos + embedding.
- Elasticsearch: documento indexado.
- ClickHouse: métricas agregadas.

## Métricas de sucesso
- % de ofertas com nicho classificado (> 98%).
- Precisão de nicho (> 90%).
- Cobertura de transcrição de VSLs (> 95%).
- Custo médio de enrichment por oferta.
