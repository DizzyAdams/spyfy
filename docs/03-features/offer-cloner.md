# 🧬 Offer Cloner — SpyFy

## Objetivo

Fazer **engenharia reversa e clonagem fiel** de uma oferta: landing page, funil completo, criativos, copy e stack técnica — em menos de 60 segundos.

## O que é clonado

| Componente | Detalhe |
|-----------|---------|
| Landing Page | HTML, CSS, JS, imagens, fontes, favicon. |
| Funil | LP → VSL → checkout → upsell → downsell → TY. |
| Copy | Headlines, subheads, bullets, CTAs, garantias, FAQ. |
| Criativos | Imagens/vídeos do anúncio. |
| Stack | Plataforma de checkout, pixels, ferramentas de LP. |
| Estrutura | Seções, ordem, provas sociais, timers. |

## Pipeline de clonagem (Temporal workflow)

```
CloneRequested
   │
   ▼
[1] Fetch LP (Playwright headless, render completo)
   │
   ▼
[2] Baixar assets (imagens, CSS, JS, fontes) → reescrever URLs
   │
   ▼
[3] Detectar funil:
     - Seguir CTAs / botões de compra
     - Identificar checkout (domínio/stack)
     - Detectar upsell/downsell pós-checkout (heurística + IA)
   │
   ▼
[4] Fingerprint de stack:
     - Pixels (FB, TikTok, GA)
     - Checkout (Cartpanda, Kiwify, Hotmart...)
     - Builder (ClickFunnels, Elementor...)
   │
   ▼
[5] Extração de copy/estrutura (LLM):
     - Segmentar seções
     - Classificar elementos persuasivos
   │
   ▼
[6] Empacotar:
     - Bundle HTML estático + manifest.json do funil
     - ZIP no Object Storage
   │
   ▼
CloneCompleted → notificar usuário
```

## Detecção de stack (fingerprinting)

```
Sinais analisados:
- <script src> conhecidos (checkout, pixel, builder)
- meta tags e comentários
- padrões de DOM/classes
- domínios de checkout no fluxo
- cookies setados
```

Exemplo de saída:
```json
{
  "checkout": "cartpanda",
  "builder": "clickfunnels",
  "pixels": ["facebook", "tiktok", "google_analytics"],
  "confidence": 0.92
}
```

## Manifest de funil (exemplo)

```json
{
  "offer_id": "ofr_123",
  "steps": [
    { "order": 1, "type": "lp",       "url": "https://.../lp",       "snapshot": "r2://.../lp.html" },
    { "order": 2, "type": "checkout", "url": "https://.../checkout", "stack": "cartpanda" },
    { "order": 3, "type": "upsell",   "url": "https://.../up1" },
    { "order": 4, "type": "ty",       "url": "https://.../obrigado" }
  ],
  "clone_bundle": "r2://clones/cl_789/bundle.zip"
}
```

## Fidelidade & QA

- **Diff visual:** screenshot original vs clone → similaridade > 95%.
- **Checklist:** assets carregam, fontes corretas, layout responsivo.
- QA Agent valida antes de liberar (ver [sub-agents.md](../02-team/sub-agents.md)).

## Exportação

| Formato | Uso |
|---------|-----|
| ZIP (HTML estático) | Hospedar em qualquer lugar. |
| Editor visual | Ajustar no SpyFy antes de exportar. |
| GrapesJS / JSON | Importar em builders. |

## Guardrails legais/éticos

- Clonagem é para **estudo, referência e adaptação** — não plágio direto.
- Aviso no produto sobre direitos autorais e marcas.
- Não clonamos áreas logadas/pagas nem conteúdo protegido por login.
- Ver [compliance.md](../09-security/compliance.md).

## Créditos

- Cada clonagem consome 1 crédito (por plano).
- Reclonagens do mesmo funil em 24h não recobram.

## Métricas

- Clone success rate (> 95%).
- Tempo médio de clonagem (< 60s).
- Fidelidade visual média.
- Uso do editor pós-clone.

## Edge cases

- LP com JS pesado/SPA → render completo + espera de network idle.
- Cloaking (LP diferente por origem) → usar user-agent/geo do anúncio.
- Checkout externo bloqueado → registrar só metadados do step.
