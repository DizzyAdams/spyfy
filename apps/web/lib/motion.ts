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
