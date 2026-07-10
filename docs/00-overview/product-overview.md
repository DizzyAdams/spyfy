# 📦 Visão de Produto — SpyFy

## Resumo executivo

O SpyFy é uma **plataforma SaaS + biblioteca (SDK)** de inteligência de anúncios. Entrega três produtos integrados sobre uma base de dados unificada de ofertas:

1. **Discovery** — motor de busca e descoberta de ofertas ativas.
2. **Cloner** — engenharia reversa e clonagem de funis/LPs/criativos.
3. **Intelligence** — analytics, tendências e alertas.

## Arquitetura de produto (camadas)

```
┌─────────────────────────────────────────────────────┐
│                    SpyFy Cloud (SaaS)                 │
│  Web App · Extensão Chrome · Mobile (futuro)          │
├─────────────────────────────────────────────────────┤
│                     SpyFy API                         │
│  REST · GraphQL · tRPC · Webhooks                     │
├─────────────────────────────────────────────────────┤
│                  SpyFy SDK / Libs                     │
│  @spyfy/sdk (TS) · spyfy-py (Python) · CLI            │
├─────────────────────────────────────────────────────┤
│           Core Engine (Discovery/Cloner/AI)           │
├─────────────────────────────────────────────────────┤
│      Data Lake (anúncios, ofertas, snapshots)         │
└─────────────────────────────────────────────────────┘
```

## Módulos

### 1. Offer Discovery
- Busca full-text e semântica sobre milhões de anúncios.
- Filtros: rede, nicho, país, idioma, formato (imagem/vídeo/carrossel), longevidade, plataforma de checkout, tecnologia de LP.
- Ordenação por "score de vencedora" (longevidade × volume estimado × engajamento).
- Ver [offer-discovery.md](../03-features/offer-discovery.md).

### 2. Offer Cloner
- Captura fiel da landing page (HTML/CSS/JS, assets, fontes).
- Mapeamento de funil (LP → VSL → checkout → upsell → downsell → TY page).
- Extração de copy, headlines, CTAs, provas sociais, garantias.
- Detecção de stack (Cartpanda, Kiwify, Hotmart, ClickFunnels, pixels).
- Export para HTML estático, editor visual ou ZIP.
- Ver [offer-cloner.md](../03-features/offer-cloner.md).

### 3. Intelligence & Alerts
- Dashboards de tendências por nicho.
- Detecção de "novas ofertas escalando".
- Alertas por e-mail/Slack/webhook quando uma oferta entra em escala.
- Relatórios de concorrentes.
- Ver [analytics.md](../03-features/analytics.md).

## Planos & Pricing

| Plano | Preço (USD/mês) | Ofertas/dia | Clonagens/mês | Redes | API |
|-------|-----------------|-------------|----------------|-------|-----|
| **Free** | $0 | 20 buscas | 1 | Meta | ❌ |
| **Starter** | $49 | 500 buscas | 15 | Meta, TikTok | ❌ |
| **Pro** | $129 | Ilimitado | 100 | Todas | ✅ (10k req) |
| **Agency** | $349 | Ilimitado | 500 | Todas | ✅ (100k req) |
| **Enterprise** | Custom | Ilimitado | Custom | Todas + custom | ✅ (SLA) |

Créditos extras de clonagem: pacotes de 50 por $19.

## Fluxo de usuário principal (happy path)

1. Usuário loga e escolhe nicho "Emagrecimento — BR".
2. Discovery retorna 240 ofertas ativas ordenadas por longevidade.
3. Usuário filtra: vídeo + ativo há > 30 dias.
4. Clica numa oferta → vê criativo, LP, transcrição da VSL, stack.
5. Clica em "Clonar" → SpyFy reconstrói a LP e mapeia o funil.
6. Exporta ZIP ou envia para editor.
7. Salva a oferta numa coleção e cria alerta de "novos criativos deste anunciante".

## Superfícies de produto

- **Web App** (principal) — Next.js.
- **Extensão Chrome** — salvar anúncios enquanto navega no Facebook/TikTok.
- **CLI** — `spyfy search "keto" --network meta --min-days 30`.
- **API/SDK** — integração com stacks internas de agências.
- **Mobile** (roadmap Q4) — feed de ofertas + alertas push.

## KPIs de produto

- Activation: % que salva ≥ 1 oferta em 24h.
- Aha moment: primeira clonagem bem-sucedida.
- Expansion: upgrade Free → Pro em 14 dias.
- Ver métricas completas em [okrs.md](../10-roadmap/okrs.md).
