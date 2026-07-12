# A12 — Guard / QA (qualidade e fidelidade)

Agente da squad de mining que faz a **validação de qualidade/fidelidade** do
pipeline antes de liberar alertas/clones. É a porta de Human-in-the-Loop.

## Responsabilidades
- Medir a **completude** do pipeline (etapas obrigatórias executadas).
- Calcular a **confiança** final e decidir se precisa de revisão humana.
- Emitir flags de QA (ex.: pipeline incompleto).

## Mapeamento de código
- **`apps/workers-py/spyfy/agents/orchestrator.py`** — nó `guard`
  (`_make_guard`):
  - `REQUIRED_STEPS = {"scout", "enricher", "copy", "roi", "dedup"}`.
  - `completeness = |REQUIRED_STEPS ∩ done_steps| / |REQUIRED_STEPS|`.
  - `confidence = 0.6 * completeness + 0.4 * prior` (onde `prior` é a
    confiança acumulada dos nós anteriores).
  - `needs_human = confidence < 0.6` → escala para revisão humana.
  - `flags = ["pipeline_incompleto"]` quando `completeness < 1.0`.

## Saída (no estado do grafo)
- `confidence` (float), `needs_human` (bool), `stack.qa_flags` (list).

## SLA / propriedades
- `< 4s`.
- Garante que só ofertas com pipeline completo e confiança adequada seguem
  para o A13 (Alert/Notify) ou para exportação.
