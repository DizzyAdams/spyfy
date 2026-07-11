"use client";

import { motion, useReducedMotion } from "framer-motion";
import { Image as ImageIcon, Play, Video } from "lucide-react";
import { cn } from "@/lib/utils";
import { EXPOCSS } from "@/lib/motion";

// Premium "ad creative" preview surface — a faux, beautiful ad thumbnail.
type OfferCreativeProps = {
  hue?: number;
  gradient?: string[];
  label: string;
  format?: string;
  image?: string; // optional real creative (photo/video poster)
  className?: string;
};

// Derive a violet→cyan-ish duotone from a hue when no explicit gradient is passed.
function deriveGradient(hue?: number): [string, string] {
  const h = ((((hue ?? 265) % 360) + 360) % 360);
  return [`hsl(${h} 84% 64%)`, `hsl(${(h + 44) % 360} 92% 56%)`];
}

export function OfferCreative({
  hue,
  gradient,
  label,
  format,
  image,
  className = "",
}: OfferCreativeProps) {
  const reduce = useReducedMotion();
  const [g0, g1] =
    gradient && gradient.length >= 2 ? [gradient[0], gradient[1]] : deriveGradient(hue);
  const isVideo = Boolean(format && /video/i.test(format));
  const Icon = isVideo ? Video : ImageIcon;
  const hasImage = Boolean(image && image.trim().length > 0);

  return (
    <div
      className={cn(
        "group relative isolate flex overflow-hidden rounded-xl border border-border bg-surface",
        className,
      )}
    >
      {/* Gradient field — kept as the background fallback */}
      <div
        aria-hidden
        className="absolute inset-0 -z-10"
        style={{ backgroundImage: `linear-gradient(135deg, ${g0}, ${g1})` }}
      />
      {/* Real creative (photo/video poster) — sits above the gradient,
          below the chip/play/scrim. Gradient remains as graceful fallback. */}
      {hasImage && (
        <img
          src={image}
          alt={label}
          loading="lazy"
          decoding="async"
          className="pointer-events-none absolute inset-0 -z-10 h-full w-full object-cover"
        />
      )}
      {/* Volumetric depth — soft top highlight + vignette toward canvas */}
      <div
        aria-hidden
        className="absolute inset-0 -z-10"
        style={{
          background:
            "radial-gradient(120% 90% at 78% 10%, rgba(255,255,255,0.22), transparent 42%), radial-gradient(130% 120% at 12% 108%, var(--bg), transparent 58%)",
        }}
      />
      {/* Fine grain for a filmic, non-flat surface */}
      <div aria-hidden className="grain" />

      {/* Subtle animated sheen — transform/opacity only, GPU-cheap */}
      {!reduce && (
        <motion.div
          aria-hidden
          className="pointer-events-none absolute -inset-y-1/2 -left-1/3 z-[5] w-1/2 skew-x-12"
          style={{
            background:
              "linear-gradient(90deg, transparent, rgba(255,255,255,0.16), transparent)",
          }}
          initial={{ x: "-60%" }}
          animate={{ x: "340%" }}
          transition={{ duration: 3.4, repeat: Infinity, repeatDelay: 2.4, ease: EXPOCSS }}
        />
      )}

      {/* Format badge — Lucide icon + pt-BR label (icon is decorative; label is the signal) */}
      <span
        className="chip absolute left-3 top-3 z-20 !border-white/15 !bg-black/35 !text-white/90 backdrop-blur-md"
        aria-label={`Formato: ${isVideo ? "Vídeo" : "Imagem"}`}
      >
        <Icon size={12} className="text-accent" aria-hidden />
        <span className="capitalize">{isVideo ? "Vídeo" : "Imagem"}</span>
      </span>

      {/* Center play affordance for video — decorative only (poster is already described) */}
      {isVideo && (
        <div aria-hidden className="pointer-events-none absolute inset-0 z-10 grid place-items-center">
          <div className="grid h-12 w-12 place-items-center rounded-full border border-white/25 bg-black/30 text-white ring-1 ring-white/15 backdrop-blur-md transition-transform duration-300 group-hover:scale-110 group-hover:bg-primary/40 motion-reduce:transition-none">
            <Play size={18} className="ml-0.5 fill-current" />
          </div>
        </div>
      )}

      {/* Bottom scrim + refined headline treatment */}
      <div className="absolute inset-x-0 bottom-0 z-20 bg-gradient-to-t from-black/75 via-black/25 to-transparent px-3 pb-3 pt-10">
        <p className="font-display text-[15px] font-semibold leading-snug tracking-tight text-white">
          {label}
        </p>
        {isVideo && (
          <div className="mt-2.5 flex items-center gap-1.5" aria-hidden>
            <span className="h-1 flex-1 overflow-hidden rounded-full bg-white/20">
              <span className="block h-full w-[38%] rounded-full bg-accent" />
            </span>
          </div>
        )}
      </div>
    </div>
  );
}
