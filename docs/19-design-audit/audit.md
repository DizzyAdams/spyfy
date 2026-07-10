# 🔍 Auditoria de Design CTO — SpyFy

> **Autor:** Lead de UX/UI (CTO de Produto) · **Data:** 10/07/2026
> **Escopo:** Avaliação de nível CTO da experiência de produto SpyFy com base na documentação existente
> (`docs/00-overview`, `docs/05-frontend`, `docs/12-market`, `docs/16-notifications`, `docs/17-engagement`, `docs/18-proxies-crm-cart`).
> **Entregáveis da pasta:** `audit.md` (este), `improvements.md`, `design-system.md`, `ux-principles.md`.

---

## 1. Resumo executivo

O SpyFy é, em essência, um **produto de inteligência de alta densidade de dados** para media buyers, afiliados e agências. A base documentada é forte: design system *dark-first* definido, componentes de domínio nomeados (`OfferCard`, `FunnelMap`, `VslTranscript`), princípios de UX claros e uma arquitetura de **9 loops de retenção/comercial** que é um diferencial real frente a AdSpy/BigSpy/Minea.

No entanto, a documentação de design apresenta **sinais típicos de maturidade "alpha"**: duas fontes de verdade conflitantes para tokens de cor, regras de acessibilidade declaradas mas não verificáveis na prática, contradições de direção *mobile-first vs desktop-first*, e uso de emoji em tabelas que violam a própria regra "nunca emoji". O produto também **não torna visível na UI** os seus maiores trunfos comerciais: a **Garantia 24h** e os **5 loops de retenção** (personalização, gamificação, radar, digest, health score).

**Veredito CTO:** a fundação está correta e é defensável. A lacuna não é de conceito, é de **execução e consistência**. Antes de escalar aquisição, o design precisa (a) consolidar uma única fonte de verdade de tokens acessíveis, (b) expor os diferenciais como superfícies de UI reais, e (c) fechar o *gap* entre o que os loops entregam (backend) e o que o usuário *vê e sente* (frontend).

| Dimensão | Nota (1–5) | Comentário |
|---|:---:|---|
| Fundação de design system | 4 | Tokens e componentes bem pensados, mas duplicados/contraditórios. |
| Acessibilidade (WCAG 2.1 AA) | 2 | Regras declaradas; contraste e estados não validados. |
| Hierarquia visual | 3 | Bento grid coerente; score de oferta depende de cor. |
| Consistência | 2 | Conflitos de token, emoji e direção de layout. |
| Conversão (funil/clarity) | 2 | Aha moment e garantia 24h sub-superficializados. |
| Diferenciação vs concorrência | 4 | Fortíssima no papel; precisa virar UI percebida. |
| Retenção (loops → UX) | 2 | 9 loops no backend; quase nenhum mapeado em UI. |

---

## 2. Metodologia

A auditoria avalia 7 lentes, alinhadas ao mandato CTO:

1. **Heurísticas de Usabilidade de Nielsen (10)** — framework clássico de avaliação de interface.
2. **Hierarquia visual** — quanto esforço cognitivo para o *primeiro insight*.
3. **Consistência** — uma fonte de verdade para tokens, padrões e tom.
4. **Acessibilidade WCAG 2.1 AA** — contraste, foco, estados, daltonismo, *reduced motion*.
5. **Tom de voz** — coerência da comunicação em produto e notificações.
6. **Conversão** — clareza do funil, redução de atrito no *aha moment* e na compra.
7. **Diferenciais vs AdSpy / BigSpy / Minea** — onde o design vira vantagem competitiva.

Cada achado tem severidade: 🔴 *crítico* (bloqueia lançamento/GTM), 🟠 *alto* (prejudica retenção/conversão), 🟡 *médio* (consistência/qualidade), 🟢 *baixo* (polimento).

---

## 3. Heurísticas de Nielsen

### H1 — Visibilidade do status do sistema 🟠
- **Ponto forte:** `Clone Timeline` em tempo real (WebSocket), skeletons e progresso em etapas documentados (`motion.md`, `components.md`) dão feedback de estado.
- **Gap:** o *backend* já emite eventos ricos (`offer.scaling`, `clone.completed`, `roi.milestone` — `notifications/overview.md`), mas **não há especificação de como o app Web reflete "oferta escalando AGORA" em tempo real na home**. O usuário não vê o sistema "vivo".
- **Ação:** criar um indicador `live` (pulso animado, respeitando *reduced motion*) na home e no feed quando o Radar detecta novidade.

### H2 — Correspondência sistema ↔ mundo real 🟢
- Termos da indústria já usados corretamente (longevidade, winning score, funil, upsell). Boa calibração com o jargão de media buying.

### H3 — Controle e liberdade do usuário 🟡
- **Gap:** fluxos de clonagem e de *page builder por email* (`cart-garantia.md`) não documentam **cancelamento/descarte visível** nem confirmação de ação destrutiva. Clonar consome crédito (pago) — exige confirmação e rota de undo.
- **Ação:** todo gasto de crédito (`onClone`) precisa de modal de confirmação + `<undo>` por 5s.

### H4 — Consistência e padrões 🔴
- **Crítico:** dois documentos definem paletas diferentes:
  - `ui-ux.md`: `--success #22C55E`, `--warning #F59E0B`, `--danger #EF4444`
  - `design-system-pro.md`: `--success #16A34A`, `--warning #D97706`, `--danger #DC2626`
- **Ação:** eleger `design-system.md` (nesta pasta) como **única fonte de verdade** e atualizar `ui-ux.md`.

### H5 — Prevenção de erros 🟠
- Filtros sincronizados com URL e chips removíveis (`components.md`) ajudam. Mas **sem preview de custo antes de clicar "Clonar"**, o usuário pode gastar crédito por engano (especialmente no Free/Starter com limites baixos).

### H6 — Reconhecimento > recordação 🟢
- Command palette ⌘K, filtros ativos visíveis e deep links (`spyfy://offer/{id}`) reduzem carga de memória. Bom.

### H7 — Flexibilidade e eficiência de uso 🟡
- Atalhos por persona (Loop 1) e ⌘K cobrem usuários avançados. **Gap:** não há "modo denso/compacto" para quem passa horas escaneando (contrário ao próprio princípio de densidade útil).

### H8 — Estética e design minimalista 🟢
- *Dark Minimalism + Bento Grid* é a escolha certa para data-density. Coerente com a missão.

### H9 — Recuperação de erros 🟠
- Notificações de `clone.failed` (HIGH) existem no backend, mas **não há padrão de UI de erro documentado** (mensagem + retry + próximo passo). `ui-ux.md` cita "mensagem clara + retry" de forma genérica.

### H10 — Ajuda e documentação 🟡
- Storybook e docs de componentes existem. **Gap:** sem *empty states* orientados por persona nem *tooltips* de primeira viagem para o aha (primeira clonagem).

---

## 4. Hierarquia visual

- **Estrutura OK:** Topbar (busca global) + Sidebar (Feed/Library/Alerts/Analytics) + conteúdo em bento grid é hierarquia clara.
- **Problema de sinalização:** o *winning score* (0–100) e a faixa de "vencedora/escalando/aquecendo/fria" são comunicados **primariamente por cor** (`design-system-pro.md`). Isso (a) falha em WCAG se a cor for o único canal e (b) força o usuário a "decorar" o mapa de cores.
- **Recomendação:** todo score deve vir acompanhado de **ícone + label textual** (ex.: 🔥→"Hot 91" vira `■ Hot · 91`). Ver `design-system.md` (tokens de score) e `improvements.md` (P0-A11Y-2).


---

## 5. Consistência (achados concretos)

| # | Inconsistência | Onde | Impacto |
|---|---|---|---|
| C1 🔴 | Paletas de cor divergentes | `ui-ux.md` vs `design-system-pro.md` | Dois "verdades" quebram tema e revisão. |
| C2 🔴 | Uso de emoji em tabela de badge de score | `design-system-pro.md` (🔥) | Viola a própria regra "ícones SVG, nunca emoji". |
| C3 🟠 | Direção de layout conflitante | `design-system-pro.md` diz *mobile-first*; `ui-ux.md` diz *desktop-first*. | Ambiguidade para quem implementa responsividade. |
| C4 🟡 | Cor hardcoded fora de token | `design-system-pro.md` usa `#0EA5E9` para "escalando" | Quebra o sistema semântico e o tema claro. |
| C5 🟡 | `--muted` reaproveitado como status "fria" | `design-system-pro.md` | Cor de texto secundário usada como semântica de estado. |

**Regra CTO:** `docs/19-design-audit/design-system.md` é a fonte de verdade; `05-frontend/*` deve referenciá-lo e remover duplicações.

---

## 6. Acessibilidade — WCAG 2.1 AA

- **Contraste (AA):** `design-system-pro.md` afirma `--text-dark #E6E8EC` e `--muted-dark #9AA4B2` sobre `--surface-dark #151922`. O texto principal passa; o `--muted` (3:1) só é válido para texto *grande/secundário* — **não deve carregar informação crítica** (ex.: não usar `--muted` sozinho para "oferta fria").
- **Foco:** regra de `ring` 2px existe, mas nenhum componente documenta foco *visível em tema claro* também.
- **Estados:** hover/active/focus/disabled/loading/empty/error listados, porém sem matriz de implementação por componente.
- **Daltonismo:** paleta de score (verde/azul/âmbar/cinza) — o verde e o cinza podem colapsar para protanopia; exige ícone+label (ver H4/H8 acima).
- **Reduced motion:** bem coberto em `motion.md` (hook `useReducedMotion`). Manter.
- **Alvos:** ≥44×44px definido — **validar** nos chips de filtro e ícones da sidebar (frequentemente < 44px no ícone puro).
- **Ponto cego:** não há evidência de teste com **axe/Lighthouse** automatizado no pipeline (`11-quality/testing-strategy.md` deve incluir a11y gate).

---

## 7. Tom de voz

O produto fala como uma ferramenta técnica (correto para a persona), mas há **assimetria**:
- Backend tem tom de *copilot* ("Level up!", "🥇 Você é dos primeiros", `loops.md`), mas a UI de produto não tem voz definida.
- Notificações (`channels.md`) pedem "1 CTA principal", título ≤ 50 chars, mas **não há guia de tom de voz** (formal? incentivador? em pt-BR ou en?).
- **Recomendação:** definir 1 guia de tom (ver `ux-principles.md`) afirmando: *direto, orientado a ganho, sem jargão vazio; celebra ação (gamificação) mas nunca promete resultado ilegal/enganoso* (alinhado ao princípio "Ético e legal").

