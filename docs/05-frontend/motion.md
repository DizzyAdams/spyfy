# 🎬 Motion & Interações (Framer Motion) — SpyFy

Padrões de animação com **Framer Motion**, dentro das regras de UX (150–300ms, easing natural, `prefers-reduced-motion`). Movimento com propósito: guiar atenção, dar feedback, comunicar estado — nunca decorar por decorar.

## Princípios

1. **Rápido:** 150–300ms para micro-interações; ≤ 500ms para transições de página.
2. **Natural:** easing `[0.22, 1, 0.36, 1]` (easeOutExpo-like) ou springs suaves.
3. **Sem jank:** animar só `transform` e `opacity` (GPU), nunca `width/top`.
4. **Acessível:** respeitar `prefers-reduced-motion` (desligar/atenuar).
5. **Sem layout shift:** reservar espaço; usar `layout` com cuidado.

## Tokens de motion

```ts
export const motionTokens = {
  fast: 0.15, base: 0.22, slow: 0.35, page: 0.5,
  ease: [0.22, 1, 0.36, 1] as const,
  spring: { type: "spring", stiffness: 300, damping: 30 },
};
```

## Reduced motion (obrigatório)

```tsx
import { useReducedMotion } from "framer-motion";

export function useAppTransition() {
  const reduce = useReducedMotion();
  return reduce
    ? { initial: false, animate: {}, transition: { duration: 0 } }
    : { transition: { duration: motionTokens.base, ease: motionTokens.ease } };
}
```

## OfferCard — entrada + hover (feed)

```tsx
import { motion } from "framer-motion";

export function OfferCard({ offer, index }) {
  return (
    <motion.article
      initial={{ opacity: 0, y: 12 }}
      animate={{ opacity: 1, y: 0 }}
      transition={{ duration: 0.22, ease: [0.22,1,0.36,1], delay: index * 0.03 }}
      whileHover={{ y: -4, transition: { duration: 0.15 } }}
      whileTap={{ scale: 0.98 }}
      className="rounded-lg bg-[--surface-dark] border border-[--border-dark]
                 focus-within:ring-2 focus-within:ring-[--ring]"
    >
      {/* ... */}
    </motion.article>
  );
}
```

- Stagger leve por índice (`delay: index * 0.03`) — sensação premium sem lentidão.
- `whileTap` dá feedback tátil; sem shift de bounds.

## Feed com stagger (lista)

```tsx
const container = { show: { transition: { staggerChildren: 0.03 } } };
const item = { hidden: { opacity: 0, y: 10 }, show: { opacity: 1, y: 0 } };

<motion.div variants={container} initial="hidden" animate="show">
  {offers.map(o => <motion.div key={o.id} variants={item}><OfferCard .../></motion.div>)}
</motion.div>
```

## Clone Timeline — progresso em tempo real

Cada etapa do clone (ver [realtime-cloning.md](../07-ai/realtime-cloning.md)) anima ao chegar via WebSocket.

```tsx
<AnimatePresence initial={false}>
  {steps.map(step => (
    <motion.li key={step.id}
      initial={{ opacity: 0, x: -8 }}
      animate={{ opacity: 1, x: 0 }}
      exit={{ opacity: 0 }}
      transition={{ duration: 0.2, ease: [0.22,1,0.36,1] }}>
      <StepDot state={step.state} />  {/* pending→running→done com spring */}
      <span>{step.label}</span>
    </motion.li>
  ))}
</AnimatePresence>
```

```tsx
// StepDot: checkmark com spring quando completa
<motion.svg animate={done ? { scale: [0.6, 1.15, 1] } : {}}
            transition={{ duration: 0.3, times: [0, 0.6, 1] }} />
```

## Modal / Drawer (Radix + Framer)

```tsx
<motion.div  // scrim: 40-60% preto p/ legibilidade
  initial={{ opacity: 0 }} animate={{ opacity: 1 }} exit={{ opacity: 0 }}
  className="fixed inset-0 bg-black/50" />
<motion.div
  initial={{ opacity: 0, scale: 0.96, y: 8 }}
  animate={{ opacity: 1, scale: 1, y: 0 }}
  exit={{ opacity: 0, scale: 0.98 }}
  transition={motionTokens.spring} />
```

## Copilot — streaming de tokens

```tsx
// texto aparece suave conforme tokens chegam (sem "pulos")
<motion.span initial={{ opacity: 0 }} animate={{ opacity: 1 }}
             transition={{ duration: 0.1 }}>{token}</motion.span>
```

## Números que sobem (métricas/ROI)

```tsx
import { animate } from "framer-motion";
useEffect(() => {
  const controls = animate(0, roiPct, {
    duration: 0.8, ease: "easeOut",
    onUpdate: v => setDisplay(v.toFixed(1)),
  });
  return () => controls.stop();
}, [roiPct]);
```

## Page transitions (Next.js App Router)

- `AnimatePresence` + `mode="wait"`; fade+slide sutil (≤ 300ms).
- Preferir **View Transitions API** onde suportado (mais performático).

## Performance de motion

- Só `transform`/`opacity`.
- `will-change` com parcimônia.
- `layout` animations medidas (evitar em listas grandes).
- Desligar animações caras sob `prefers-reduced-motion`.

## Checklist de motion

- [ ] 150–300ms nas micro-interações.
- [ ] Easing natural / spring suave.
- [ ] `prefers-reduced-motion` respeitado.
- [ ] Sem animar layout properties (só transform/opacity).
- [ ] Feedback de tap/hover sem shift.
- [ ] Sem CLS causado por animação.
