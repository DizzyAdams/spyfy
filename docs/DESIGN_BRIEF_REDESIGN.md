# SpyFy Redesign — Design Brief "DEEP SIGNAL"

**Mandate:** Elevate SpyFy's web UI to "Silicon Valley / a startup Elon Musk would
invest in" level — surreal, precise, expensive-looking. **Zero AI-slop:** no generic
centered hero + 3 equal cards, no flat purple→blue 45° gradient buttons, no emoji
icons, no lorem, no box-shadow "floating" cards.

**Concept:** SpyFy surfaces *signal from noise* (ad intelligence). The aesthetic is a
**near-future reconnaissance console**: calm, exact, dark — but with a *living,
surreal core* (a volumetric plasma/aurora field with grain). Precision-instrument
energy (Vercel/Linear/Raycast craft) + otherworldly atmosphere.

## 1. Palette (exact — use TOKENS, never raw hex in components)
Canvas (near-black, faint blue-violet cast):
- `--bg:#06070B` · `--surface:#0E1016` · `--surface-2:#14161F` · `--surface-3:#1B1E2A`
Text:
- `--text:#EAECF2` · `--muted:#8A90A2` · `--faint:#5A6072`
Signal / brand (signature duotone = `violet→cyan`):
- `--violet:#7C5CFF` · `--violet-soft:#A78BFA` · `--cyan:#2DD4FF`
- `--lime:#C6F24E`  ← RARE "hot winner" accent, used sparingly only for winning signals
Semantic:
- `--success:#34D399` · `--warning:#FBBF24` · `--danger:#FB7185` · `--info:#60A5FA`
Borders / focus:
- `--border:#20232F` · `--border-strong:#2C3040` · `--ring:#7C5CFF`

Tailwind already maps these as `bg`,`surface`,`surface-2`,`text`,`muted`,`primary`
(violet),`accent`(cyan),`border`,`ring`. **Add** `surface-3`, `violet-soft`, `lime`,
`faint`, and the semantic colors as Tailwind colors too.

## 2. Typography
- **Display/UI:** `Space Grotesk` (Google Fonts) — geometric, confident, slightly
  surreal. Apply via `--font-display` + a `.font-display` utility + `font-display`
  Tailwind class. Hero `clamp(2.6rem,6vw,5rem)`, tracking tight (-0.02em).
- **Body:** `Inter` (keep), tightened; body 15–16px, line-height 1.6.
- **Mono/data:** `JetBrains Mono` (keep) for metrics, IDs, scores.

## 6. Shared contracts — PRESERVE exactly (don't break imports)
- `GradientMesh` — default export, renders full-bleed bg. Keep signature.
- `OfferCreative` — props: `{ hue?, gradient?, label, format?, className? }`. Keep.
- `CountUp` — props: `{ to, suffix?, prefix?, duration? }`. Keep.
- `Logo` — default export, props `{ className?, variant? }`. Keep.
- `Navbar`, `Footer` — keep export names; Navbar stays `"use client"`.
- Allowed imports only: `@/lib/motion`, `@/lib/utils` (`cn`), `framer-motion`,
  `lucide-react`, `next/link`, `next/image`. Do NOT introduce new deps.

## 7. Agent slices (14 roles, disjoint files — touch ONLY your files)
1. **Tokens & primitives:** rewrite `tailwind.config.ts` + `app/globals.css`
   (all tokens above, new utilities: `.glass`, `.surface`, `.grain`, `.signal-line`,
   `.font-display`, refined `.bento`, `.btn` with magnetic+layered glow, `.chip`).
2. **Motion system:** `lib/motion.ts` (add `revealUp`, `magnetic`, `sweep`,
   `EXPOCSS`) + ensure `lib/utils.ts` exports `cn`.
3. **Brand mark:** `components/illustrations/Logo.tsx` — signature, geometric,
   looks like a recon/signal glyph; light/dark aware.
4. **Atmosphere:** `components/illustrations/GradientMesh.tsx` — volumetric plasma
   + grain + vignette + faint grid (per §4).
5. **Data viz:** `components/illustrations/RadarChart.tsx`, `FunnelDiagram.tsx` —
   premium, on-brand, animated on view.
6. **Navigation:** `components/Navbar.tsx` — sticky, blur, magnetic CTA, elegant.
7. **Hero:** `components/sections/Hero.tsx` — cinematic centerpiece, signal sweep,
   parallax bg, count-up stats, the OfferCreative showcase.
8. **Feature story:** `components/sections/Features.tsx`, `HowItWorks.tsx` —
   asymmetric bento, editorial, not 3-up.
9. **Social proof:** `components/sections/Testimonials.tsx`, `FAQ.tsx`,
   `Comparison.tsx` — bold, confident, animated reveals.
10. **Pricing & CTA:** `components/sections/Pricing.tsx` + the final CTA block in
    `app/page.tsx` — high-contrast, one clear primary action.
11. **Offer surface:** `components/OfferCard.tsx`, `OfferCreative.tsx`,
    `CountUp.tsx` — elevate cards/creatives to product-grade.
12. **Product app:** `components/AppShell.tsx`, `components/app/*`, `app/app/*`
    (analytics/feed/offer) — apply tokens, density, motion; keep routes working.
13. **Chrome & layout:** `components/Footer.tsx`, `app/layout.tsx` (fonts/metadata),
    `app/template.tsx` (page transition), `app/app/layout.tsx` if present.
14. **Integration/QA:** after others — ensure imports resolve, run `next build`,
    fix cross-references, verify no console errors, commit.

## 8. Quality bar
- Builds clean (`next build`). Respects a11y (focus rings, contrast, reduced-motion).
- Cohesive: every screen uses the same tokens, type, motion. Surreal but usable.
- Commit with a clear message; do NOT commit secrets/`.env*`.

- Update `app/layout.tsx` to load Space Grotesk and wire `--font-display`.

## 3. Motion language (framer-motion — `lib/motion.ts`)
- Signature easing: `EXPOCSS = [0.16,1,0.3,1]`.
- Reveal: masked/translateY fade, `staggerChildren:0.07`.
- **Magnetic** buttons/cards (translate toward cursor on hover, spring back).
- **Signal sweep:** a 1px accent line that sweeps across hero + section dividers.
- **Count-up** stats. **Parallax** on the background tied to scroll.
- ALWAYS respect `prefers-reduced-motion`.

## 4. Atmosphere (the "surreal" — centerpiece)
`GradientMesh` becomes a **volumetric plasma/aurora** field: layered radial
gradients (violet→cyan) drifting slowly + a fine **grain/noise** overlay + vignette
+ a faint reactive grid. Must feel alive, not a static gradient. Keep it
`pointer-events-none` and GPU-cheap (transform/opacity only).

## 5. Anti-slop rules (HARD)
- NO emoji as icons — Lucide only.
- NO raw hex in components — tokens/utilities only.
- NO lorem — keep real SpyFy pt-BR copy, elevate the voice (confident, specific).
- NO heavy drop shadows as the main elevation — use 1px borders + subtle glow +
  surface elevation for depth.
- NO generic 3-up feature row as the only pattern — use asymmetric bento, editorial
  layouts, big type.
