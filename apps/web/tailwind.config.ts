import type { Config } from "tailwindcss";

const config: Config = {
  darkMode: "class",
  content: [
    "./app/**/*.{ts,tsx}",
    "./components/**/*.{ts,tsx}",
    "./lib/**/*.{ts,tsx}",
  ],
  theme: {
    extend: {
      colors: {
        // Canvas
        bg: "#06070B",
        surface: "#0E1016",
        "surface-2": "#14161F",
        "surface-3": "#1B1E2A",
        // Text
        text: "#EAECF2",
        muted: "#8A90A2",
        faint: "#5A6072",
        // Signal / brand (signature duotone = violet -> cyan)
        primary: "#7C5CFF",
        "primary-hover": "#8B6DFF",
        "violet-soft": "#A78BFA",
        accent: "#2DD4FF",
        lime: "#C6F24E",
        // Semantic
        success: "#34D399",
        warning: "#FBBF24",
        danger: "#FB7185",
        info: "#60A5FA",
        // Borders / focus
        border: "#20232F",
        "border-strong": "#2C3040",
        ring: "#7C5CFF",
      },
      fontFamily: {
        sans: ["var(--font-sans)", "Inter", "system-ui", "sans-serif"],
        mono: ["var(--font-mono)", "JetBrains Mono", "ui-monospace", "monospace"],
        display: ["var(--font-display)", "Space Grotesk", "system-ui", "sans-serif"],
      },
      borderRadius: {
        lg: "8px",
        xl: "12px",
        "2xl": "16px",
        "3xl": "24px",
      },
      boxShadow: {
        glow: "0 0 0 1px rgba(124,92,255,0.30), 0 10px 50px -12px rgba(124,92,255,0.55)",
        "glow-accent": "0 0 0 1px rgba(45,212,255,0.22), 0 10px 50px -12px rgba(45,212,255,0.40)",
        "glow-cyan": "0 0 0 1px rgba(45,212,255,0.22), 0 10px 50px -12px rgba(45,212,255,0.45)",
        "glow-lime": "0 0 0 1px rgba(198,242,78,0.22), 0 10px 50px -12px rgba(198,242,78,0.40)",
      },
      keyframes: {
        "fade-up": {
          "0%": { opacity: "0", transform: "translateY(12px)" },
          "100%": { opacity: "1", transform: "translateY(0)" },
        },
        shimmer: {
          "100%": { transform: "translateX(100%)" },
        },
        plasma: {
          "0%": {
            transform: "translate3d(0,0,0) scale(1)",
            filter: "hue-rotate(0deg)",
          },
          "50%": {
            transform: "translate3d(2%,-2%,0) scale(1.06)",
            filter: "hue-rotate(28deg)",
          },
          "100%": {
            transform: "translate3d(0,0,0) scale(1)",
            filter: "hue-rotate(0deg)",
          },
        },
        sweep: {
          "0%": { transform: "translateX(-100%)" },
          "100%": { transform: "translateX(100%)" },
        },
        "pulse-ring": {
          "0%": { transform: "scale(0.8)", opacity: "0.7" },
          "100%": { transform: "scale(2.2)", opacity: "0" },
        },
        float: {
          "0%,100%": { transform: "translateY(-10px)" },
          "50%": { transform: "translateY(10px)" },
        },
      },
      animation: {
        "fade-up": "fade-up 0.5s ease-out both",
        "pulse-ring": "pulse-ring 1.8s ease-out infinite",
        plasma: "plasma 18s ease-in-out infinite",
        sweep: "sweep 3.5s ease-in-out infinite",
        float: "float 6s ease-in-out infinite",
      },
    },
  },
  plugins: [],
};

export default config;
