# 🤖 Modelos de ML — SpyFy

## Visão geral

O SpyFy combina **LLMs de terceiros** (OpenAI/Anthropic) com **modelos próprios/leves** (classificadores, embeddings self-hosted) para equilibrar qualidade e custo.

## Modelos e uso

| Modelo | Tipo | Uso | Hosting |
|--------|------|-----|---------|
| Claude Sonnet/Opus | LLM | Estrutura de funil, análise longa | API |
| GPT-4o / mini | LLM | Extração, classificação, resumo | API |
| Whisper | ASR | Transcrição de VSL | Self-host / API |
| text-embedding-3 | Embedding | Busca semântica | API |
| bge-large | Embedding | Fallback self-host | GPU |
| Niche Classifier | Classificação | Nicho/vertical | Self-host |
| Angle Detector | Classificação | Ângulo persuasivo | Self-host |
| Scaling Predictor | Regressão/série temporal | Prever "escalando" | Self-host |

## Classificador de nicho

- **Baseline:** LLM zero-shot.
- **Produção:** modelo fine-tuned (DistilBERT multilíngue) treinado com dados rotulados.
- Retreino periódico com feedback humano.
- Métricas: F1 macro > 0.90.

## Detector de ângulo

- Embeddings + clustering (HDBSCAN) para descobrir ângulos.
- Classificador supervisionado para ângulos conhecidos.

## Scaling Predictor

- Features: longevidade, nº criativos, derivada de atividade, nicho.
- Modelo: gradient boosting (XGBoost/LightGBM).
- Target: probabilidade de estar "escalando" nos próximos 7d.
- Validação temporal (sem leakage).

## Embeddings & busca semântica

- Pipeline: copy + transcrição → embedding → pgvector (HNSW).
- Usado em: busca semântica, "ofertas similares", dedup.

## Pipeline de treino (MLOps)

```
Dados rotulados (feedback + curadoria)
   ▼
Feature store / dataset versionado
   ▼
Treino (offline, GPU) → avaliação (holdout temporal)
   ▼
Registro de modelo (MLflow) → aprovação
   ▼
Deploy (serving) → monitoramento de drift
```

## Serving

- Modelos leves: servidos via FastAPI + ONNX Runtime.
- Embeddings self-host: batch em GPU.
- LLMs: via API com fallback e cache.

## Avaliação & monitoramento

- Evals offline (datasets rotulados).
- Monitoramento de drift (distribuição de features/saídas).
- A/B de modelos (ex.: ranking).
- Alertas de degradação.

## Dados & rotulagem

- Ferramenta de rotulagem interna.
- Active learning: priorizar amostras de baixa confiança.
- Governança: versionamento de datasets.

## Custo

- Roteamento de modelo por complexidade.
- Cache agressivo de embeddings/classificações.
- Self-host para volume alto e previsível.

## Ética & viés

- Auditoria de viés em classificadores.
- Transparência: estimativas rotuladas como tal.
- Sem uso de PII de usuários finais.
- Ver [compliance.md](../09-security/compliance.md).

## Roadmap de ML

- Fine-tune de LLM próprio para extração de copy (reduzir custo).
- Modelo multimodal (analisar criativo de vídeo diretamente).
- Previsão de CPA/performance (long-term).
