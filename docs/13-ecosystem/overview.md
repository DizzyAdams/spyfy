# 🌐 SpyFy Ecosystem — Visão do Ecossistema

O SpyFy não é um produto — é uma **plataforma-ecossistema**. Assim como Shopify criou uma economia ao redor de lojas, o SpyFy cria uma **economia ao redor de inteligência de ofertas**.

## Mapa do ecossistema

```
                        ┌───────────────────────────┐
                        │        SpyFy Core          │
                        │ Discovery · Cloner · Intel │
                        └─────────────┬─────────────┘
        ┌──────────────┬─────────────┼─────────────┬──────────────┐
        ▼              ▼             ▼             ▼              ▼
 ┌────────────┐ ┌────────────┐ ┌──────────┐ ┌────────────┐ ┌────────────┐
 │ Marketplace│ │ AI Copilot │ │ Plugins  │ │ Community  │ │ SpyFy Cloud│
 │ ofertas/   │ │ conversac. │ │ & Apps   │ │ & Creators │ │ (API/infra)│
 │ templates  │ │ (LangGraph)│ │ Platform │ │ economy    │ │            │
 └────────────┘ └────────────┘ └──────────┘ └────────────┘ └────────────┘
        │              │             │             │              │
        └──────────────┴──── SpyFy Graph (dados + eventos) ──────┘
```

## Camadas do ecossistema

### 1. SpyFy Core
O motor central: descoberta, clonagem, inteligência. Documentado em `03`–`07`.

### 2. SpyFy Marketplace
Economia de ofertas/templates: usuários e criadores publicam funis clonáveis, swipe files curados, packs de criativos. Comissão sobre transações. Ver [marketplace.md](marketplace.md).

### 3. SpyFy Copilot
Agente conversacional (LangGraph) que opera **toda** a plataforma por linguagem natural: "encontre ofertas de keto escalando no BR e clone as 3 melhores". Ver [copilot.md](copilot.md).

### 4. Plugins & Apps Platform
SDK para terceiros construírem apps sobre o SpyFy Graph: conectores (Meta Ads, Google Ads), automações, dashboards. App Store interna. Ver [plugins-platform.md](plugins-platform.md).

### 5. Community & Creator Economy
Programa de afiliados, criadores de conteúdo, "SpyFy Experts", leaderboards, desafios. Loops virais embutidos. Ver [community.md](community.md).

### 6. SpyFy Cloud
API pública, webhooks, infra multi-tenant, white-label para agências.

## SpyFy Graph — o ativo central

O **SpyFy Graph** é o grafo de conhecimento que conecta:

```
Anúncios ── Ofertas ── Funis ── Anunciantes ── Nichos ── Ângulos
   │           │          │          │            │         │
Criativos  Snapshots  Steps    Timeline    Tendências  Embeddings
```

- Toda camada do ecossistema lê/escreve no Graph.
- Efeito de rede: mais uso → mais dados → melhores insights → mais valor.
- API GraphQL expõe o Graph a plugins e parceiros.

## Efeitos de rede & moats

| Moat | Como se forma |
|------|---------------|
| **Dados** | Bilhões de anúncios + histórico imutável (ninguém replica o backfill). |
| **Marketplace** | Criadores + compradores → liquidez de dois lados. |
| **Copilot** | Quanto mais uso, melhores prompts/evals → agente mais esperto. |
| **Plugins** | Ecossistema de apps prende agências. |
| **Comunidade** | Experts e conteúdo geram aquisição orgânica. |

## Flywheel

```
Mais usuários → mais ofertas descobertas/clonadas
      ▲                        │
      │                        ▼
Aquisição orgânica ◀── mais dados no Graph
(comunidade/marketplace)      │
      ▲                        ▼
      └──── melhores insights (IA) ◀── Copilot/Analytics
```

## Modelo econômico do ecossistema

- **SaaS** (assinaturas) — base.
- **Marketplace take rate** (10–20% sobre vendas de templates/ofertas).
- **Créditos de clonagem** (consumo).
- **API/Enterprise** (uso + SLA).
- **Revenue share** com plugins pagos (App Store).
- **Programa de afiliados** (CAC eficiente).

## Princípios do ecossistema

1. **API-first & aberto** — tudo acessível programaticamente.
2. **Criadores ganham** — economia de soma positiva.
3. **Composabilidade** — plugins encaixam como Lego.
4. **Ético por design** — dados públicos, respeito a ToS/direitos.
5. **Tempo real** — o ecossistema pulsa ao vivo (streaming em toda parte).

## Documentos do ecossistema

- [marketplace.md](marketplace.md)
- [copilot.md](copilot.md)
- [plugins-platform.md](plugins-platform.md)
- [community.md](community.md)
- [monorepo-scaffold.md](monorepo-scaffold.md)
