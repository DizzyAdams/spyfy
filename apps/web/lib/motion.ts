// Motion tokens — aligned with docs/05-frontend/motion.md
export const motionTokens = {
  fast: 0.15,
  base: 0.22,
  slow: 0.35,
  page: 0.5,
  ease: [0.22, 1, 0.36, 1] as const,
  spring: { type: "spring" as const, stiffness: 300, damping: 30 },
};

// Container + item variants for staggered feeds
export const staggerContainer = {
  hidden: {},
  show: {
    transition: { staggerChildren: 0.06, delayChildren: 0.05 },
  },
};

export const fadeUp = {
  hidden: { opacity: 0, y: 16 },
  show: { opacity: 1, y: 0, transition: { duration: 0.5, ease: motionTokens.ease } },
};

export const fadeIn = {
  hidden: { opacity: 0 },
  show: { opacity: 1, transition: { duration: 0.6, ease: motionTokens.ease } },
};

// Page transition (App Router template)
export const pageVariants = {
  initial: { opacity: 0, y: 8 },
  animate: { opacity: 1, y: 0, transition: { duration: motionTokens.page, ease: motionTokens.ease } },
  exit: { opacity: 0, y: -8, transition: { duration: 0.2, ease: motionTokens.ease } },
};

// Signature easing — DEEP SIGNAL (docs/DESIGN_BRIEF_REDESIGN.md §3)
export const EXPOCSS = [0.16, 1, 0.3, 1] as const;

// Clean translateY reveal for content blocks
export const revealUp = {
  hidden: { opacity: 0, y: 18 },
  show: { opacity: 1, y: 0, transition: { duration: 0.6, ease: EXPOCSS } },
};

// Masked headline reveal — pair with an overflow-hidden parent for clip effect
export const revealMask = {
  hidden: { opacity: 0, y: "0.4em" },
  show: { opacity: 1, y: 0, transition: { duration: 0.7, ease: EXPOCSS } },
};

// Magnetic buttons/cards — subtle scale on hover, springs back to rest
export const magnetic = {
  rest: {},
  hover: { scale: 1.03, transition: { type: "spring", stiffness: 400, damping: 25 } },
};

// Signal sweep — a 1px accent line that expands across hero + section dividers
export const signalSweep = {
  hidden: { scaleX: 0, opacity: 0 },
  show: { scaleX: 1, opacity: 1, transition: { duration: 0.8, ease: EXPOCSS } },
};

// Card hover lift — subtle spring elevation (depth via surface, not heavy shadow)
export const cardHover = {
  rest: {},
  hover: { y: -6, transition: { type: "spring", stiffness: 300, damping: 24 } },
};

