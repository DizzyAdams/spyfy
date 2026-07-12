# A5 — Transcriber

O agente **A5 (Transcriber)** converte VSLs (Video Sales Letters) em texto e produz um resumo estruturado via LLM, alimentando as etapas seguintes de mineração.

## Objetivo

Transformar áudio/vídeo de VSLs em transcrição textual e, a partir dela, gerar um resumo estruturado (tópicos, promessas, gatilhos, oferta).

## Pipeline

1. **VSL → texto** — transcrição de áudio via **Whisper**.
2. **Texto → resumo estruturado** — sumarização e extração via **LLM**.
3. **Handoff** — o texto e o resumo alimentam a **extração de copy/ângulos** (agentes de análise de mensagem).

## Design offline-first

- O **Whisper está intencionalmente FORA das dependências do free-tier**. O projeto segue um design *offline-first*, sem embutir modelos pesados de transcrição por padrão.
- O A5 é um **hook documentado no pipeline**: fica pronto para ser ativado quando um **LLM/Whisper for injetado** (via configuração ou provedor externo).
- Sem esse provedor injetado, o A5 permanece inerte e não bloqueia o restante da squad.

## SLA

- **Alvo: RTF < 0.5** (Real-Time Factor) — a transcrição deve levar menos da metade da duração do vídeo.

## Saída / Consumidores

- Transcrição bruta + resumo estruturado.
- Consumido pela **extração de copy e ângulos**, que analisa a mensagem de venda a partir do texto produzido.
