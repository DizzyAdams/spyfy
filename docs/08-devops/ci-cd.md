# 🔄 CI/CD — SpyFy

## Ferramentas

- **GitHub Actions** (CI + gatilhos de deploy).
- **Turborepo** (build/test com cache remoto).
- **ArgoCD** (CD via GitOps).
- **Changesets** (versionamento de packages).

## Fluxo Git

- **Trunk-based** com PRs curtos.
- Branch protegida `main`; deploy contínuo para staging.
- Feature flags para desacoplar deploy de release.

## Pipeline de CI (PR)

```
on: pull_request
jobs:
  install (pnpm, cache)
  lint      → ESLint/Prettier, Ruff/Black
  typecheck → tsc
  test      → Vitest/Pytest (afetados via turbo)
  build     → apps/packages afetados
  e2e       → Playwright (smoke)
  security  → Snyk/Trivy/gitleaks
  evals     → evals de IA (se prompts mudaram)
```

- Só builda/testa **projetos afetados** (turbo affected).
- Preview environment por PR (namespace K8s efêmero).

## Pipeline de CD

```
merge em main
   ▼
build imagens (Docker) → push registry (com SHA)
   ▼
atualizar manifests (Helm values) → commit no repo infra
   ▼
ArgoCD detecta → sync para staging
   ▼
smoke tests em staging
   ▼
promoção manual/auto → production (rolling/canary)
```

## Estratégias de deploy

- **Rolling** para serviços stateless.
- **Canary** (5% → 25% → 100%) para mudanças de risco.
- **Blue/Green** para migrações grandes.
- Migrations DB via job com expand/contract.

## Qualidade obrigatória (gates)

- Cobertura mínima (ex.: 70% em pacotes core).
- Zero vulnerabilidades críticas.
- E2E críticos verdes.
- Evals de IA acima do baseline.

## Versionamento

- SemVer para packages/SDK (Changesets).
- Imagens taggeadas por SHA + semver.

## Rollback

- ArgoCD rollback para revisão anterior.
- Feature flags para desligar feature sem redeploy.
- Migrations reversíveis.

## Secrets no CI

- Via GitHub OIDC → assume role AWS (sem chaves estáticas).
- Segredos de runtime no Vault (não no CI).

## Métricas DORA

- Deploy frequency (meta: diário).
- Lead time for changes (< 1 dia).
- Change failure rate (< 15%).
- MTTR (< 1h).

## Ambientes

| Env | Trigger | Aprovação |
|-----|---------|-----------|
| preview | PR | automática |
| staging | merge main | automática |
| production | tag/manual | 1 reviewer |
