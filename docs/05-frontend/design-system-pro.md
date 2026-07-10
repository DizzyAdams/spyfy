# 🎨 Design System Pro — SpyFy

Design system de nível produto, seguindo prioridades de UX (acessibilidade → interação → performance → estilo). Dark-first, denso e rápido — feito para media buyers que passam horas escaneando ofertas.

## Princípios (ordem de prioridade)

1. **Acessibilidade (CRÍTICO):** contraste ≥ 4.5:1 (texto), foco visível sempre, aria-labels, cor nunca é o único indicador.
2. **Interação (CRÍTICO):** alvos ≥ 44×44px, feedback em toda ação, micro-interações 150–300ms.
3. **Performance (ALTO):** WebP/AVIF, lazy load, reservar espaço (CLS < 0.1).
4. **Estilo (ALTO):** consistência, ícones SVG (nunca emoji), tokens semânticos.

## Estilo escolhido

**Dark Minimalism + Bento Grid** com toques de **glassmorphism** em overlays. Racional: produto data-dense (dashboards/feeds) pede clareza, hierarquia forte e baixa fadiga visual.

## Tokens semânticos (light + dark)

```css
:root {
  /* superfícies */
  --bg: #FFFFFF;         --bg-dark: #0B0D12;
  --surface: #F6F7F9;    --surface-dark: #151922;
  --surface-2: #EEF0F3;  --surface-2-dark: #1B2130;
  /* texto (contraste AA) */
  --text: #0B0D12;       --text-dark: #E6E8EC;      /* >=4.5:1 */
  --muted: #5B6472;      --muted-dark: #9AA4B2;     /* >=3:1  */
  /* marca */
  --primary: #6E56CF;    --primary-hover: #7C66D9;
  --accent: #22D3EE;
  /* semânticos */
  --success: #16A34A;    --warning: #D97706;
  --danger: #DC2626;     --info: #2563EB;
  /* bordas/estados */
  --border: #E3E6EA;     --border-dark: #263042;
  --ring: #6E56CF;                                   /* foco visível */
}
```

- **Nunca** hardcode hex por tela — use tokens.
- Testar AMBOS os temas antes de entregar.
- Scrim de modal: 40–60% preto para legibilidade do foreground.

## Paleta por nicho (badges de score)

| Faixa score | Cor | Significado |
|-------------|-----|-------------|
| 80–100 | `--success` | 🔥 vencedora (hot) |
| 60–79 | `#0EA5E9` | escalando |
| 40–59 | `--warning` | aquecendo |
| 0–39 | `--muted` | fria |

Sempre acompanhar cor de **ícone + label** (cor não é único indicador).

## Tipografia (font pairing)

- **Display/UI:** `Inter` (variable) — legibilidade em densidade alta.
- **Mono/dados:** `JetBrains Mono` — métricas, IDs, código.
- Escala (rem): 0.75 / 0.875 / 1 / 1.125 / 1.25 / 1.5 / 2 / 3.
- Line-height: 1.5 corpo, 1.2 títulos. Measure ≤ 75ch.

## Espaçamento (ritmo 4/8px)

`4 · 8 · 12 · 16 · 24 · 32 · 48 · 64`. Hierarquia vertical: 16 (dentro), 24 (entre grupos), 48 (entre seções).

## Elevação & raio

- Raio: 8px (cards/inputs), 12px (modais), full (pills).
- Sombras suaves (dark usa borda + leve glow em vez de sombra pesada).

## Estados de interação (obrigatórios)

| Estado | Regra |
|--------|-------|
| hover | mudança sutil (150ms), nunca só hover em mobile |
| active/pressed | feedback imediato (opacidade/scale), sem shift de layout |
| focus | ring visível 2px `--ring` (nunca remover) |
| disabled | claro e não interativo |
| loading | skeleton/spinner, reservar espaço |

## Grid & responsividade

- Mobile-first; breakpoints: 640 / 768 / 1024 / 1280 / 1536.
- Feed: bento grid responsivo (1 col mobile → 4 col desktop).
- Gutters adaptam por breakpoint; respeitar safe-areas.

## Ícones

- Família única: **Lucide** (SVG). Sem emoji como ícone.
- Tamanho base 20px; alvo clicável 44px.

## Gráficos (Analytics)

- Recharts/visx; paleta categórica acessível (checar daltonismo).
- Sempre eixo rotulado + tooltip + estado vazio.
- Tipos: linha (tendência), barra (ranking), área (volume), heatmap (longevidade).

## Componentes-base (shadcn/ui + Radix)

Button, Input, Select, Dialog, Drawer, Tooltip, Tabs, Toast, DropdownMenu, Command (⌘K), Skeleton, Badge, Table — todos acessíveis por Radix. Ver [components.md](components.md).

## Checklist pré-entrega (UI)

- [ ] Contraste AA (texto 4.5:1 / secundário 3:1) nos 2 temas.
- [ ] Foco visível em todos os interativos.
- [ ] Alvos ≥ 44px + espaçamento ≥ 8px.
- [ ] Micro-interações 150–300ms com easing natural.
- [ ] Ícones SVG (Lucide), sem emoji.
- [ ] Estados: hover/active/focus/disabled/loading/empty/error.
- [ ] CLS < 0.1 (espaço reservado, imagens com dimensões).
- [ ] `prefers-reduced-motion` respeitado.
- [ ] Testado mobile/desktop, light/dark.
