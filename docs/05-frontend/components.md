# 🧩 Componentes — SpyFy Design System

Biblioteca de componentes em `packages/ui`, baseada em **shadcn/ui + Radix + Tailwind**.

## Estrutura

```
packages/ui/
├── src/
│   ├── primitives/   # Button, Input, Dialog, Tooltip...
│   ├── data/         # Table, Card, Badge, Stat...
│   ├── feedback/     # Skeleton, Toast, EmptyState...
│   ├── layout/       # Sidebar, Topbar, Grid...
│   └── domain/       # OfferCard, FunnelMap, CreativePreview...
└── package.json
```

## Componentes de domínio

### OfferCard
```tsx
<OfferCard
  headline="Emagreça 7kg em 21 dias"
  thumbnail={url}
  network="meta"
  longevityDays={63}
  winningScore={87.4}
  onSave={...}
  onClone={...}
/>
```
- Badge de longevidade colorido (verde > 30d).
- Hover: autoplay do vídeo mudo.
- Ações rápidas no rodapé.

### CreativePreview
- Player de vídeo/imagem/carrossel.
- Controles mínimos, mudo por padrão.
- Suporte a variantes (galeria).

### FunnelMap
- Visualização do funil (LP → checkout → upsell → TY).
- Cada step clicável → snapshot.
- Badge de stack por step.

### VslTranscript
- Transcrição com timestamps.
- Marcação de estrutura (hook/problema/solução/oferta/CTA).
- Botão "resumir".

### StackBadges
- Chips de checkout/builder/pixels detectados.

### FiltersBar
- Filtros combináveis, sincronizados com URL.
- Chips removíveis de filtros ativos.

### CollectionPicker
- Modal para salvar oferta em coleções.
- Criar coleção inline.

### AlertBuilder
- Form para criar alertas (tipo, query, canal).

## Primitivos (shadcn/ui)

Button, Input, Select, Checkbox, Switch, Dialog, Drawer, Tooltip, Popover, Tabs, Toast, DropdownMenu, Command (⌘K), Skeleton, Badge, Avatar, Table.

## Command Palette (⌘K)

- Busca global de ofertas, navegação, ações rápidas.
- Ações: "clonar última oferta", "criar alerta", "ir para library".

## Padrões

- Componentes **controlados** e acessíveis (Radix).
- Variantes via `cva` (class-variance-authority).
- Sem lógica de dados dentro do UI package (só apresentação).
- Storybook para documentação visual.

## Extensão Chrome (MV3)

- Content script injeta botão "Salvar no SpyFy" no FB/TikTok.
- Popup: coleções recentes, busca rápida.
- Background service worker para auth.

## Editor visual de clones

- Baseado em GrapesJS (ou tldraw p/ layout).
- Edita HTML exportado do cloner.
- Preview responsivo + export.

## Testes de componentes

- Vitest + Testing Library (unit).
- Playwright (E2E de fluxos críticos).
- Storybook interaction tests.
- Visual regression (Chromatic, opcional).

## Convenções

- Nomeados em PascalCase.
- Props tipadas com TS + defaults.
- `data-testid` em elementos-chave.
- Tokens do design system (sem cores hardcoded).
