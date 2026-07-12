# A7 — Funnel Walker (Mapeador de Funil)

Agente do esquadrão de 14 miners do SpyFy. Percorre os links de uma
landing page e os converte em etapas de funil estruturadas.

## Responsabilidade
Mapear os `links` extraídos de uma LP em passos de funil ordenados,
identificando cada destino pelo padrão da URL.

## Mapeamento de código
Implementado em `detect_funnel()`, em
`apps/workers-py/spyfy/clone.py`. Recebe a lista de links (`href`)
coletada pelo `_PageExtractor` e classifica cada um conforme
palavras-chave presentes na URL.

## Regras de classificação (keyword → etapa)
| Palavra-chave na URL        | Etapa        |
|-----------------------------|--------------|
| `checkout`, `pagamento`     | Checkout     |
| `obrigado`, `thank`         | Thank You    |
| `upsell`                    | Upsell       |
| `vsl`, `video`              | VSL          |
| `lead`, `inscricao`         | Lead         |

Cada etapa é emitida uma única vez (deduplicada por rótulo `label`).

## Garantias obrigatórias
- **Landing Page** sempre existe como 1º passo (inserida se ausente).
- **Checkout** sempre existe (inserido com URL vazia se não detectado).
- Ordem final: `Landing Page` → ... → `Checkout` → demais etapas.

## SLA
Processamento **< 25s** em modo headless (apenas stdlib + `httpx`,
sem navegador). O `detect_funnel()` é puramente local e determinístico.
