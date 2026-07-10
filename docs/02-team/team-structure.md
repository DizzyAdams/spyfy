# 🧑‍🤝‍🧑 Estrutura do Time — SpyFy

## Filosofia

Times **pequenos, autônomos e cross-functional**, organizados por domínio de produto (squads), com uma camada de plataforma que dá alavancagem a todos.

```
                     ┌───────────────────┐
                     │   CTO / VP Eng     │
                     └─────────┬─────────┘
        ┌──────────────┬───────┴───────┬───────────────┐
        ▼              ▼               ▼               ▼
 ┌────────────┐ ┌────────────┐ ┌────────────┐ ┌──────────────┐
 │ Squad      │ │ Squad      │ │ Squad      │ │ Platform &   │
 │ Discovery  │ │ Cloner     │ │ Intelligence│ │ Data/AI      │
 └────────────┘ └────────────┘ └────────────┘ └──────────────┘
```

## Squads

### Squad Discovery
- **Missão:** busca, ranking e feed de ofertas.
- **Membros:** 1 Tech Lead, 2 Backend Sr, 1 Frontend Sr, 1 Data Eng, 1 PM, 1 Designer (compartilhado).
- **KPIs:** latência de busca < 300ms, freshness > 90%, TTFI.

### Squad Cloner
- **Missão:** engenharia reversa e clonagem de funis/LPs.
- **Membros:** 1 Tech Lead, 2 Backend Sr (scraping), 1 Frontend Sr, 1 QA Sr.
- **KPIs:** clone success rate > 95%, tempo de clonagem < 60s.

### Squad Intelligence
- **Missão:** analytics, tendências, alertas, relatórios.
- **Membros:** 1 Tech Lead, 1 Data Eng Sr, 1 Backend Sr, 1 Frontend Sr, 1 Analytics.
- **KPIs:** precisão de alertas, adoção de relatórios.

### Platform & Data/AI
- **Missão:** infra, pipeline de dados, IA/ML, DX, observabilidade.
- **Membros:** 1 Staff Eng, 1 DevOps/SRE Sr, 1 ML Eng Sr, 1 Data Platform Sr, 1 Security Eng.
- **KPIs:** uptime 99.9%, custo por 1k anúncios, DORA metrics.

## Papéis transversais

| Papel | Responsabilidade |
|-------|------------------|
| **CTO** | Visão técnica, arquitetura macro, hiring. |
| **Staff Engineer** | Decisões cross-squad, ADRs, mentoria. |
| **EM (Eng Manager)** | Pessoas, delivery, saúde do time. |
| **PM** | Priorização, discovery, roadmap. |
| **Design Lead** | Design system, UX research. |
| **QA Lead** | Estratégia de testes, qualidade. |
| **SRE** | Confiabilidade, on-call, incidentes. |
| **Security Eng** | AppSec, compliance, pentest. |

## Modelo de trabalho

- **Cadência:** sprints de 2 semanas + discovery contínuo.
- **Cerimônias:** planning, daily assíncrona, review, retro.
- **RFC/ADR:** toda decisão técnica relevante documentada.
- **Trunk-based** + feature flags.
- **DoR/DoD** claros (Definition of Ready/Done).

## RACI (exemplo — feature nova)

| Atividade | PM | TechLead | Eng | Design | QA | SRE |
|-----------|----|----------|-----|--------|----|-----|
| Descoberta | R | C | C | C | I | I |
| Design técnico | C | R | C | I | I | C |
| Implementação | I | A | R | I | C | I |
| Testes | I | A | C | I | R | I |
| Deploy | I | A | R | I | C | C |
| Monitoramento | I | C | C | I | I | R |

R=Responsible, A=Accountable, C=Consulted, I=Informed.

## Organização de sub-agents de IA

Além dos humanos, cada squad é amplificada por **sub-agents de IA** especializados (ver [sub-agents.md](sub-agents.md)) que executam tarefas repetitivas 24/7: scraping, classificação, transcrição, clonagem, QA de dados.

## Onboarding

1. Semana 1: setup local, ler docs `00`–`02`, primeiro PR (good-first-issue).
2. Semana 2: pairing com buddy, primeiro job de squad.
3. Semana 3–4: ownership de uma feature pequena end-to-end.
