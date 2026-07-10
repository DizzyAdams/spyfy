# 🔎 Offer Discovery Engine — SpyFy

## Objetivo

Permitir que o usuário encontre, em segundos, as ofertas/anúncios mais relevantes e **comprovadamente vencedores** para seu nicho, com filtros ricos e ranking inteligente.

## Capacidades

- Busca full-text (headline, copy, anunciante).
- Busca semântica (por ângulo/tema, via embeddings).
- Filtros combináveis.
- Ranking por `winning_score`.
- Feed infinito com preview de criativo.
- Salvar em coleções + criar alertas.

## Filtros disponíveis

| Filtro | Valores |
|--------|---------|
| Rede | Meta, TikTok, Google, YouTube, Native, Pinterest |
| Nicho | Emagrecimento, Finanças, Relacionamento, Nutra, E-com, Cripto... |
| País | BR, US, PT, ES, LATAM... |
| Idioma | pt, en, es... |
| Formato | Imagem, Vídeo, Carrossel |
| Longevidade | 0–7d, 7–30d, 30–90d, 90d+ |
| Status | Ativo, Pausado |
| Checkout/Stack | Cartpanda, Kiwify, Hotmart, ClickFunnels, Shopify... |
| Volume estimado | faixas |
| Ordenar por | Winning score, mais recente, longevidade, nº de criativos |

## Ranking — Winning Score

```
score = W_LONG * norm(longevity_days)
      + W_VOL  * norm(log(est_impressions+1))
      + W_VAR  * norm(creative_variants)
      + W_ENG  * norm(engagement)
      + recency_boost
```
- Sinais normalizados por nicho (z-score) para comparar maçãs com maçãs.
- Pesos ajustáveis por experimento (A/B de relevância).

## Busca híbrida

```
1. Query do usuário → parse (texto + filtros).
2. BM25 no Elasticsearch (full-text) → top 500.
3. kNN no pgvector (semântica) → top 500.
4. Fusão (Reciprocal Rank Fusion).
5. Re-rank por winning_score + boosts de filtro.
6. Paginação (cursor-based).
```

## API (exemplo)

```http
GET /v1/offers/search?q=keto&network=meta&country=BR&min_days=30&sort=score
Authorization: Bearer <token>
```

Resposta:
```json
{
  "results": [
    {
      "offer_id": "ofr_123",
      "headline": "Emagreça 7kg em 21 dias sem dieta",
      "network": "meta",
      "niche": "weight_loss",
      "longevity_days": 63,
      "winning_score": 87.4,
      "creative": { "type": "video", "thumbnail": "https://..." },
      "advertiser": { "name": "HealthBR", "page_url": "https://..." }
    }
  ],
  "next_cursor": "eyJvZmZzZXQiOjI1fQ=="
}
```

## Busca semântica (exemplo)

```
q = "anúncios que prometem resultado rápido sem esforço"
→ embedding → kNN → retorna ofertas com ângulo de "resultado rápido"
  mesmo sem essas palavras exatas na copy.
```

## UX do feed

- Cards com: thumbnail, headline, badge de longevidade, score, rede.
- Hover → preview do criativo (vídeo autoplay mudo).
- Ações rápidas: salvar, clonar, criar alerta, ver detalhes.
- Filtros persistentes (URL sharable).

## Performance

- Cache de queries populares (Redis, TTL curto).
- Índices otimizados + shards por nicho.
- Meta: p95 < 300ms.

## Métricas

- CTR nos resultados.
- Save rate / clone rate por busca.
- Zero-result rate (minimizar).
- NDCG (relevância).

## Edge cases

- Nicho sem dados suficientes → sugerir nichos relacionados.
- Query ambígua → mostrar facetas para refinar.
- Anúncio removido → mostrar snapshot histórico com badge "inativo".
