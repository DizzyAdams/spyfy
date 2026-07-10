# 🛒 SpyFy Marketplace — Economia de Ofertas

Um marketplace de dois lados onde **criadores** publicam ativos de inteligência e **compradores** os adquirem: funis clonáveis, swipe files curados, packs de criativos, templates de LP, briefs e playbooks.

## Por que existe

- Media buyers experientes têm swipe files valiosos → monetizam.
- Iniciantes querem atalhos validados → compram.
- SpyFy captura take rate e cria efeito de rede (liquidez de dois lados).

## O que se vende

| Ativo | Descrição | Faixa de preço |
|-------|-----------|----------------|
| **Funil clonável** | Bundle de funil pronto (LP+upsell+TY). | $19–$199 |
| **Swipe pack** | Coleção curada de ofertas vencedoras por nicho. | $9–$99 |
| **Creative pack** | Criativos/templates editáveis. | $9–$79 |
| **Playbook** | Guia + ofertas + estrutura de campanha. | $29–$299 |
| **Alert preset** | Conjunto de alertas configurados por expert. | $5–$49 |
| **Copilot routine** | Rotina autônoma pronta (ver copilot). | $5–$49 |

## Fluxo do criador

```
1. Criador seleciona ofertas/coleções → "Publicar no Marketplace".
2. SpyFy valida (QA + compliance) e gera preview.
3. Define preço, licença e descrição.
4. Publicado → aparece na loja (busca + categorias).
5. Vendas caem na carteira; payout via Stripe Connect.
```

## Fluxo do comprador

```
1. Navega/busca por nicho, rede, rating.
2. Preview (sem revelar tudo) + reviews.
3. Compra (créditos ou cartão).
4. Ativo entra na sua Library / clona direto.
```

## Economia

- **Take rate:** 15% (padrão), 10% para top creators.
- **Payout:** Stripe Connect, semanal.
- **Créditos:** compra interna acelera transações.
- **Assinatura de creator:** verificação + destaque.

## Curadoria & qualidade

- QA Agent valida fidelidade e completude antes de publicar.
- Compliance Agent verifica direitos autorais/marcas (ver [compliance.md](../09-security/compliance.md)).
- Rating e reviews da comunidade.
- "Verified Winner" badge para ofertas com longevidade comprovada.

## Anti-abuso

- Detecção de duplicatas (embeddings) — não revender clone alheio.
- Watermark/licença por comprador.
- Denúncia + takedown.
- Split de royalties se um ativo deriva de outro.

## Descoberta

- Loja com categorias (nicho, rede, tipo).
- Ranking por vendas, rating, freshness.
- Recomendação personalizada (o Copilot sugere).
- Coleções em destaque curadas pela equipe.

## Licenciamento

| Licença | Uso |
|---------|-----|
| **Single-use** | 1 comprador, uso próprio. |
| **Multi-seat** | Time/agência. |
| **Exclusive** | Comprador único remove do mercado (premium). |

## Modelo de dados (resumo)

```sql
listings (id, creator_id, type, title, price, license, status, rating)
purchases (id, listing_id, buyer_id, price, created_at)
payouts (id, creator_id, amount, status, period)
reviews (id, listing_id, buyer_id, stars, text)
royalties (id, listing_id, parent_listing_id, pct)
```

## API do Marketplace

```
GET  /v1/marketplace/listings?niche=keto&sort=sales
POST /v1/marketplace/listings           # publicar
POST /v1/marketplace/listings/{id}/buy  # comprar
GET  /v1/marketplace/creators/{id}
```

## Métricas

- GMV (volume transacionado).
- Take rate efetivo.
- Liquidez (tempo até primeira venda de um listing).
- Retenção de criadores.
- % de compras que viram campanhas ativas.

## Por que é fora do comum

Transforma o SpyFy de ferramenta em **economia**. Cada usuário pode ser criador; cada oferta vencedora vira ativo negociável. É o "Gumroad + Envato do performance marketing".
