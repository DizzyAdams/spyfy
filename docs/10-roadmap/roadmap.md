# 🗺️ Roadmap & Milestones — SpyFy

## Estratégia de fases

```
Fase 0: Fundação  →  Fase 1: MVP  →  Fase 2: Escala  →  Fase 3: Plataforma
```

## Fase 0 — Fundação (Mês 0–1)

**Objetivo:** base técnica e primeiro scraping.

- [ ] Monorepo (Turborepo) + CI/CD básico.
- [ ] Infra base (Terraform: VPC, EKS, RDS, Redis, R2).
- [ ] Schema inicial (Postgres) + migrations.
- [ ] Scraper MVP para Meta Ad Library.
- [ ] Pipeline de ingestão + dedup.
- [ ] Auth (Clerk) + workspaces.

**Marco:** primeiros anúncios ingeridos e pesquisáveis internamente.

## Fase 1 — MVP (Mês 2–3)

**Objetivo:** produto usável para early adopters (Meta).

- [ ] Discovery UI (feed + filtros + busca).
- [ ] Enrichment (nicho, idioma, embeddings).
- [ ] Winning score + ranking.
- [ ] Ad Library (coleções, salvar).
- [ ] Cloner v1 (LP estática + assets).
- [ ] Billing (Stripe) + planos Free/Pro.
- [ ] Observabilidade básica.

**Marco:** beta fechado com 50 usuários; primeira clonagem bem-sucedida.

## Fase 2 — Escala (Mês 4–6)

**Objetivo:** multi-rede, IA avançada, confiabilidade.

- [ ] TikTok + Google Ads Transparency.
- [ ] Transcrição de VSL (Whisper) + resumos.
- [ ] Cloner v2 (funil completo, upsells, stack detection).
- [ ] Sub-agents orquestrados (LangGraph).
- [ ] Analytics (dashboards, tendências, alertas).
- [ ] Extensão Chrome.
- [ ] SLOs + on-call + DR.
- [ ] API pública + SDK.

**Marco:** lançamento público; 1.000 usuários pagantes.

## Fase 3 — Plataforma (Mês 7–12)

**Objetivo:** liderança de mercado e expansão.

- [ ] Mais redes (Pinterest, LinkedIn, X, native).
- [ ] Editor visual de clones.
- [ ] Relatórios white-label (agências).
- [ ] Modelos próprios (extração, scaling predictor).
- [ ] Integrações (Slack, Zapier, webhooks).
- [ ] Mobile app.
- [ ] SOC 2 Type II.

**Marco:** 10.000 usuários; ARR significativo.

## Backlog / Futuro

- Análise multimodal de criativos de vídeo.
- Previsão de performance/CPA.
- Marketplace de ofertas/templates.
- Colaboração em tempo real.
- Alertas via WhatsApp.

## Dependências entre fases

```
Scraper (F0) → Enrichment (F1) → Analytics (F2)
Cloner v1 (F1) → Cloner v2 (F2) → Editor (F3)
Auth/Billing (F1) → API/SDK (F2) → White-label (F3)
```

## Riscos & mitigação

| Risco | Impacto | Mitigação |
|-------|---------|-----------|
| Bloqueio de scraping | Alto | Multi-fonte, proxies, API pública. |
| Custo de IA | Médio | Roteamento de modelo, cache, self-host. |
| Legal (cloner) | Alto | Compliance, avisos, takedown. |
| Concorrência | Médio | Velocidade + UX + IA superior. |
| Escala de dados | Médio | ClickHouse, sharding, arquitetura event-driven. |

## Cadência de release

- Deploy contínuo (staging diário).
- Release notes quinzenais.
- Changelog público.
