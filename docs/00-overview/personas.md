# 👥 Personas & Casos de Uso — SpyFy

## Persona 1 — "Bruno, o Media Buyer"

- **Idade:** 28 · **Contexto:** roda R$ 150k/mês em Meta Ads para e-commerce.
- **Objetivos:** achar criativos ganhadores rápido, reduzir CPA, escalar sem cansar audiência.
- **Frustrações:** perde horas na Meta Ad Library; não sabe qual criativo escalou de verdade.
- **Como usa o SpyFy:** feed diário de criativos ativos há > 21 dias no seu nicho; salva em coleção "para testar".
- **Feature killer:** score de longevidade + alerta de novos criativos do concorrente.

## Persona 2 — "Carla, a Copywriter"

- **Idade:** 33 · **Contexto:** freelancer, escreve VSLs e páginas de vendas.
- **Objetivos:** biblioteca de ângulos, headlines e big ideas que já converteram.
- **Frustrações:** referências espalhadas; VSLs longas demais para assistir.
- **Como usa o SpyFy:** busca por nicho → lê transcrições resumidas de VSLs → extrai ganchos.
- **Feature killer:** transcrição + resumo de VSL com marcação de estrutura (hook, problema, solução, oferta, CTA).

## Persona 3 — "Diego, o Afiliado"

- **Idade:** 25 · **Contexto:** afiliado de infoprodutos e nutra.
- **Objetivos:** clonar funil validado, subir rápido, testar barato.
- **Frustrações:** reconstruir LP no braço; perde detalhes de pixel/upsell.
- **Como usa o SpyFy:** encontra oferta escalando → clona LP + funil → exporta → adapta.
- **Feature killer:** cloner de funil completo + detecção de stack/checkout.

## Persona 4 — "Agência PerforMax"

- **Contexto:** 12 pessoas, 30 clientes, precisa provar ROI.
- **Objetivos:** relatórios de concorrência, benchmarks de nicho, swipe file de time.
- **Como usa:** coleções compartilhadas, relatórios white-label, API para dashboards internos.
- **Feature killer:** workspace multiusuário + API + export white-label.

## Persona 5 — "Marina, a Infoprodutora"

- **Contexto:** lança cursos, quer validar antes de investir.
- **Objetivos:** medir saturação do nicho, ver o que concorrentes oferecem.
- **Feature killer:** análise de saturação + tendências históricas.

---

## Matriz de casos de uso

| ID | Caso de uso | Persona | Módulo | Prioridade |
|----|-------------|---------|--------|------------|
| UC-01 | Descobrir criativos escalando no nicho | Bruno | Discovery | P0 |
| UC-02 | Alerta de novo criativo do concorrente | Bruno | Alerts | P0 |
| UC-03 | Transcrever e resumir VSL | Carla | AI | P1 |
| UC-04 | Clonar landing page fiel | Diego | Cloner | P0 |
| UC-05 | Mapear funil completo (upsells) | Diego | Cloner | P1 |
| UC-06 | Detectar stack/checkout da oferta | Diego | Cloner | P1 |
| UC-07 | Coleções compartilhadas de time | Agência | Library | P1 |
| UC-08 | Relatório white-label de concorrência | Agência | Analytics | P2 |
| UC-09 | Medir saturação de nicho | Marina | Analytics | P2 |
| UC-10 | Exportar dados via API | Agência | API | P1 |

## User Stories (exemplos)

```
Como media buyer,
quero filtrar anúncios por "ativos há mais de 30 dias",
para focar apenas em ofertas comprovadamente vencedoras.
```

```
Como afiliado,
quero clonar a landing page e o funil de uma oferta,
para lançar minha própria versão sem reconstruir do zero.
```

```
Como copywriter,
quero ler a transcrição resumida de uma VSL,
para extrair o ângulo sem assistir 45 minutos de vídeo.
```

```
Como gestor de agência,
quero um workspace com coleções compartilhadas,
para que todo o time acesse o mesmo swipe file.
```

## Jobs To Be Done (JTBD)

- Quando estou planejando uma nova campanha, **quero saber quais ofertas já estão escalando** para não desperdiçar budget testando o que não funciona.
- Quando um concorrente lança algo novo, **quero ser avisado imediatamente** para reagir rápido.
- Quando encontro uma oferta boa, **quero replicá-la em minutos** para chegar ao mercado antes da saturação.
