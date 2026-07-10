# 🎨 UI/UX & Design System — SpyFy

## Princípios de design

1. **Velocidade percebida** — skeletons, otimistic UI, prefetch.
2. **Densidade útil** — muitos dados sem poluição (o usuário quer escanear ofertas).
3. **Ação em 1 clique** — salvar/clonar/alertar sempre à mão.
4. **Escuro por padrão** — media buyers trabalham por horas; dark mode primeiro.
5. **Consistência** — design system compartilhado (`packages/ui`).

## Design tokens

```
Cores (dark):
  --bg:        #0B0D12
  --surface:   #151922
  --primary:   #6E56CF   (roxo SpyFy)
  --accent:    #22D3EE
  --success:   #22C55E
  --warning:   #F59E0B
  --danger:    #EF4444
  --text:      #E6E8EC
  --muted:     #9AA4B2

Tipografia:
  --font-sans: "Inter", system-ui
  --font-mono: "JetBrains Mono"

Espaçamento: escala 4px (4,8,12,16,24,32,48)
Raio: 8px (cards), 12px (modais)
```

## Layout principal

```
┌──────────────────────────────────────────────┐
│  Topbar: logo · busca global · workspace · you │
├────────┬─────────────────────────────────────┤
│ Sidebar│   Conteúdo                            │
│ - Feed │   ┌─── Filtros ───┐  ┌── Feed grid ──┐│
│ - Libr.│   │ rede/nicho/... │  │ cards ofertas ││
│ - Alert│   └────────────────┘  └───────────────┘│
│ - Analy│                                        │
└────────┴─────────────────────────────────────┘
```

## Telas principais

### Discovery Feed
- Barra de filtros sticky.
- Grid de cards (thumbnail, headline, badge longevidade, score).
- Infinite scroll + cursor.
- Hover → preview de vídeo mudo.

### Offer Detail
- Criativo grande + variantes.
- Copy extraída (headline, bullets, CTA).
- Transcrição da VSL (colapsável, com timestamps).
- Stack detectado + funil.
- Ações: salvar, clonar, alerta.

### Cloner
- Botão "Clonar" → progresso em etapas (fetch → assets → funil → pronto).
- Preview do clone + diff visual.
- Export (ZIP/editor).

### Library
- Coleções, tags, drag-and-drop.
- Painel de detalhes lateral.

### Analytics
- Dashboards com gráficos (Recharts/visx).
- Filtros de período e nicho.

## Estados

- Loading: skeletons por componente.
- Empty: ilustração + CTA ("faça sua primeira busca").
- Error: mensagem clara + retry.
- Offline: banner + cache.

## Acessibilidade (a11y)

- WCAG 2.1 AA.
- Navegação por teclado, foco visível.
- Contraste mínimo respeitado.
- ARIA em componentes interativos.
- Testes com axe.

## Performance frontend

- Next.js App Router (RSC onde possível).
- Code splitting por rota.
- Imagens otimizadas (next/image).
- Prefetch de rotas prováveis.
- Meta Core Web Vitals: LCP < 2.5s, INP < 200ms, CLS < 0.1.

## i18n

- pt-BR (default), en, es.
- next-intl; strings externalizadas.

## Motion

- Framer Motion; transições sutis (150–250ms).
- Respeitar `prefers-reduced-motion`.

## Responsividade

- Desktop-first (ferramenta de trabalho), mas responsivo até tablet.
- Mobile: feed + alertas (app dedicado no roadmap).
