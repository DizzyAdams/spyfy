# 🤝 Guia de Contribuição — SpyFy

## Setup do ambiente

### Pré-requisitos
- Node.js 20+, pnpm 9+
- Python 3.11+, uv/poetry
- Docker + Docker Compose
- Make (opcional)

### Passos
```bash
git clone https://github.com/spyfy/spyfy.git
cd spyfy
pnpm install
cp .env.example .env
docker compose up -d          # postgres, redis, clickhouse, es, temporal
pnpm db:migrate
pnpm dev                      # sobe web + api
```

### Rodar workers Python
```bash
cd apps/workers-py
uv sync
python -m spyfy.workers
```

## Estrutura do monorepo

```
apps/     web, api, workers-node, workers-py, extension
packages/ sdk-ts, ui, config, schemas, prompts
infra/    terraform, helm, argocd
docs/     documentação (este diretório)
```

## Fluxo de trabalho

1. Crie branch a partir de `main`: `feat/discovery-filters`.
2. Commits pequenos e descritivos (Conventional Commits).
3. Abra PR com descrição + checklist + screenshots (se UI).
4. CI verde obrigatório.
5. Review de ≥ 1 (2 para áreas críticas).
6. Squash & merge.

## Conventional Commits

```
feat(discovery): adiciona filtro de longevidade
fix(cloner): corrige download de fontes
docs(readme): atualiza quick start
chore(ci): cache pnpm
```

Tipos: `feat`, `fix`, `docs`, `refactor`, `test`, `chore`, `perf`, `build`.

## Padrões de código

- **TS:** ESLint + Prettier; `strict` no tsconfig.
- **Python:** Ruff + Black; type hints obrigatórios.
- Sem `any` sem justificativa; sem código morto.
- Nomes claros; funções pequenas; SRP.

## Testes

- Adicione testes para código novo (ver [testing-strategy.md](11-quality/testing-strategy.md)).
- `pnpm test` (afetados) antes do PR.
- E2E para fluxos críticos.

## Schemas & contratos

- Tipos compartilhados vivem em `packages/schemas` (Zod).
- Mudança de contrato = versionar + atualizar consumidores + testes.

## Documentação

- Toda feature relevante atualiza os docs correspondentes.
- Decisão técnica importante → ADR (ver [adr.md](01-architecture/adr.md)).

## Feature flags

- Feature nova arriscada entra atrás de flag.
- Limpe flags obsoletas (higiene).

## Definition of Ready (DoR)

- [ ] Problema/valor claro.
- [ ] Critérios de aceite definidos.
- [ ] Dependências mapeadas.
- [ ] Design técnico (se necessário).

## Definition of Done (DoD)

- [ ] Código + testes.
- [ ] CI verde.
- [ ] Docs atualizados.
- [ ] Observabilidade (métricas/logs) adicionada.
- [ ] Review aprovado.
- [ ] Feature flag/rollout definido.

## Segurança

- Nunca commitar segredos (gitleaks roda no CI).
- Reporte vulnerabilidades em `security@spyfy.io` (não abra issue pública).

## Code review — o que buscamos

- Corretude e edge cases.
- Simplicidade e legibilidade.
- Performance (queries, N+1).
- Segurança (input validation, SSRF no cloner).
- Testes adequados.
- Aderência aos padrões.

## Comunicação

- Discussões técnicas em RFC/ADR.
- Dúvidas rápidas no canal do squad.
- Seja respeitoso e objetivo (review blameless).

## Releases

- Changesets para versionar packages/SDK.
- Release notes quinzenais.
- Deploy contínuo (staging → produção canary).
