# 🧪 Estratégia de Testes — SpyFy

## Pirâmide de testes

```
        ▲  E2E (poucos, críticos) — Playwright
       ███
      █████ Integração (APIs, DB, filas)
     ███████
    █████████ Unit (muitos, rápidos) — Vitest/Pytest
```

## Tipos de teste

| Tipo | Ferramenta | Escopo |
|------|-----------|--------|
| Unit | Vitest (TS), Pytest (Py) | funções, componentes puros |
| Integração | Vitest + Testcontainers, Pytest | serviço + DB/fila reais |
| Contrato | Pact / schema Zod | contratos entre serviços |
| E2E | Playwright | fluxos de usuário críticos |
| Carga | k6 | performance/limites |
| Segurança | ZAP, Snyk, Trivy | SAST/DAST/deps |
| Evals IA | dataset rotulado | qualidade de agents/modelos |
| Visual | Storybook/Chromatic | regressão visual UI |

## Cobertura-alvo

- Core packages (schemas, sdk, ranking): > 85%.
- Serviços: > 70%.
- UI: fluxos críticos cobertos por E2E.

## Fluxos E2E críticos

1. Signup → busca → salvar oferta.
2. Busca → clonar → download do bundle.
3. Criar alerta → recebê-lo.
4. Upgrade de plano (billing sandbox).

## Testes de integração (exemplo)

```ts
describe("offers.search", () => {
  it("filtra por longevidade", async () => {
    await seed(adsFixture);
    const res = await api.search({ minDays: 30 });
    expect(res.results.every(o => o.longevityDays >= 30)).toBe(true);
  });
});
```

## Testes de scraping/cloner

- Fixtures de HTML salvos (não bater na rede real no CI).
- Testes de extrator por rede (snapshot de DOM).
- Cloner: validar manifest e presença de assets no bundle.

## QA de dados

- Validação de schema na ingestão.
- Testes de dedup e idempotência.
- Detecção de anomalia (amostras sintéticas).

## Evals de IA

- Rodam no CI quando prompts/modelos mudam.
- Bloqueiam merge se abaixo do baseline.
- Métricas: accuracy/F1 (classificação), fidelidade (extração).

## Testes de carga (k6)

```js
export const options = { vus: 200, duration: "5m" };
export default function () {
  http.get(`${BASE}/v1/offers/search?q=keto`);
}
```
- Metas: p95 < 300ms sob carga alvo; sem erros > 1%.

## Dados de teste

- Factories/fixtures determinísticas.
- Testcontainers para Postgres/Redis/ES em integração.
- Ambiente sandbox de billing (Stripe test mode).

## CI

- Testes afetados via `turbo` (monorepo).
- Paralelização; flaky tests quarentenados e corrigidos.
- Relatório de cobertura no PR.

## Definition of Done (testes)

- [ ] Unit para lógica nova.
- [ ] Integração para novos endpoints.
- [ ] E2E se fluxo crítico afetado.
- [ ] Evals se IA afetada.
- [ ] Cobertura não regride.

## Qualidade contínua

- Mutation testing (amostral) em pacotes core.
- Monitoramento de flakiness.
- Defect escape rate acompanhado como métrica de qualidade.
