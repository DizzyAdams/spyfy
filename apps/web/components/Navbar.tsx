"use client";

import { useEffect, useRef, useState } from "react";
import type { MouseEvent as ReactMouseEvent } from "react";
import Link from "next/link";
import { AnimatePresence, motion, useMotionValue, useReducedMotion, useSpring } from "framer-motion";
import { ArrowRight, Menu, X } from "lucide-react";
import { magnetic, EXPOCSS } from "@/lib/motion";
import { cn } from "@/lib/utils";
import Logo from "./illustrations/Logo";

const links = [
  { href: "/#recursos", label: "Funcionalidades" },
  { href: "/#precos", label: "Preços" },
  { href: "/#biblioteca", label: "Biblioteca" },
  { href: "/#analytics", label: "Analytics" },
];

/**
 * Magnetic wrapper — translates its child toward the cursor (console-instrument
 * feel) and applies the `magnetic` hover variant from lib/motion. No-ops under
 * prefers-reduced-motion.
 */
function Magnetic({ children }: { children: React.ReactNode }) {
  const reduce = useReducedMotion();
  const ref = useRef<HTMLSpanElement>(null);
  const x = useMotionValue(0);
  const y = useMotionValue(0);
  const sx = useSpring(x, { stiffness: 320, damping: 22, mass: 0.5 });
  const sy = useSpring(y, { stiffness: 320, damping: 22, mass: 0.5 });

  function handleMove(e: ReactMouseEvent) {
    if (reduce || !ref.current) return;
    const r = ref.current.getBoundingClientRect();
    x.set((e.clientX - (r.left + r.width / 2)) * 0.35);
    y.set((e.clientY - (r.top + r.height / 2)) * 0.35);
  }
  function reset() {
    x.set(0);
    y.set(0);
  }

  return (
    <motion.span
      ref={ref}
      onMouseMove={handleMove}
      onMouseLeave={reset}
      style={{ x: sx, y: sy }}
      initial="rest"
      whileHover={reduce ? undefined : "hover"}
      variants={magnetic}
      className="group inline-flex"
    >
      {children}
    </motion.span>
  );
}

export function Navbar() {
  const reduce = useReducedMotion();
  const [scrolled, setScrolled] = useState(false);
  const [open, setOpen] = useState(false);

  const toggleRef = useRef<HTMLButtonElement>(null);
  const sheetRef = useRef<HTMLDivElement>(null);

  // Strengthen the hairline once the user leaves the hero.
  useEffect(() => {
    const onScroll = () => setScrolled(window.scrollY > 16);
    onScroll();
    window.addEventListener("scroll", onScroll, { passive: true });
    return () => window.removeEventListener("scroll", onScroll);
  }, []);

  // Mobile sheet: Escape to close, lite focus trap, scroll lock, focus return.
  useEffect(() => {
    if (!open) return;

    const focusables = () =>
      Array.from(
        sheetRef.current?.querySelectorAll<HTMLElement>(
          'a[href], button:not([disabled]), [tabindex]:not([tabindex="-1"])',
        ) ?? [],
      );

    const onKey = (e: KeyboardEvent) => {
      if (e.key === "Escape") {
        e.preventDefault();
        setOpen(false);
        toggleRef.current?.focus();
        return;
      }
      if (e.key === "Tab") {
        const items = focusables();
        if (items.length === 0) return;
        const first = items[0];
        const last = items[items.length - 1];
        const active = document.activeElement as HTMLElement | null;
        if (e.shiftKey && (active === first || !sheetRef.current?.contains(active))) {
          e.preventDefault();
          last.focus();
        } else if (!e.shiftKey && active === last) {
          e.preventDefault();
          first.focus();
        }
      }
    };

    document.addEventListener("keydown", onKey);
    const prevOverflow = document.body.style.overflow;
    document.body.style.overflow = "hidden";
    focusables()[0]?.focus();

    return () => {
      document.removeEventListener("keydown", onKey);
      document.body.style.overflow = prevOverflow;
    };
  }, [open]);

  return (
    <motion.header
      initial={reduce ? { opacity: 0 } : { y: -24, opacity: 0 }}
      animate={{ y: 0, opacity: 1 }}
      transition={{ duration: reduce ? 0.001 : 0.5, ease: EXPOCSS }}
      className={cn(
        "fixed inset-x-0 top-0 z-50 backdrop-blur-xl transition-colors duration-300",
        "glass border-x-0 border-t-0 border-b",
        scrolled ? "border-border/80" : "border-border/20",
      )}
    >
      <nav className="mx-auto flex h-16 max-w-7xl items-center justify-between px-5">
        {/* Brand */}
        <Link href="/" aria-label="SpyFy — início" className="rounded-lg text-xl">
          <Logo />
        </Link>

        {/* Center links (desktop) */}
        <div className="hidden flex-1 items-center justify-center gap-1 md:flex">
          {links.map((l) => (
            <NavLink key={l.href} href={l.href} label={l.label} reduce={!!reduce} />
          ))}
        </div>

        {/* Right actions (desktop) */}
        <div className="hidden items-center gap-2 md:flex">
          <Link href="/app/feed" className="btn btn-ghost text-sm">
            Entrar
          </Link>
          <Magnetic>
            <Link href="/#precos" className="btn btn-primary text-sm shadow-glow">
              Começar grátis
              <ArrowRight
                size={16}
                className="transition-transform duration-200 group-hover:translate-x-0.5"
              />
            </Link>
          </Magnetic>
        </div>

        {/* Mobile toggle */}
        <button
          ref={toggleRef}
          type="button"
          aria-label={open ? "Fechar menu" : "Abrir menu"}
          aria-expanded={open}
          aria-controls="mobile-nav"
          onClick={() => setOpen((v) => !v)}
          className="btn btn-ghost h-10 w-10 p-0 md:hidden"
        >
          {open ? <X size={18} /> : <Menu size={18} />}
        </button>
      </nav>

      {/* Mobile sheet */}
      <AnimatePresence>
        {open && (
          <motion.div
            key="mobile-nav-sheet"
            id="mobile-nav"
            role="navigation"
            aria-label="Navegação mobile"
            initial={{ height: 0, opacity: 0 }}
            animate={{ height: "auto", opacity: 1 }}
            exit={{ height: 0, opacity: 0 }}
            transition={{ duration: reduce ? 0.001 : 0.34, ease: EXPOCSS }}
            className="overflow-hidden border-t border-border/60 glass"
          >
            <div ref={sheetRef} className="mx-auto max-w-7xl px-5 py-4">
              <div className="flex flex-col">
                {links.map((l) => (
                  <Link
                    key={l.href}
                    href={l.href}
                    onClick={() => setOpen(false)}
                    className="rounded-lg px-3 py-3 text-sm font-medium text-muted transition-colors hover:text-text"
                  >
                    {l.label}
                  </Link>
                ))}
              </div>
              <div className="mt-3 flex flex-col gap-2 border-t border-border/60 pt-4">
                <Link
                  href="/app/feed"
                  onClick={() => setOpen(false)}
                  className="btn btn-ghost w-full"
                >
                  Entrar
                </Link>
                <Link
                  href="/#precos"
                  onClick={() => setOpen(false)}
                  className="btn btn-primary w-full shadow-glow"
                >
                  Começar grátis
                  <ArrowRight size={16} />
                </Link>
              </div>
            </div>
          </motion.div>
        )}
      </AnimatePresence>
    </motion.header>
  );
}

function NavLink({
  href,
  label,
  reduce,
}: {
  href: string;
  label: string;
  reduce: boolean;
}) {
  const [active, setActive] = useState(false);

  return (
    <Link
      href={href}
      onMouseEnter={() => setActive(true)}
      onMouseLeave={() => setActive(false)}
      onFocus={() => setActive(true)}
      onBlur={() => setActive(false)}
      className="group relative rounded-lg px-3 py-2 text-sm font-medium text-muted transition-colors duration-200 hover:text-text"
    >
      {label}
      <motion.span
        aria-hidden
        className="absolute inset-x-3 -bottom-px h-px origin-center bg-gradient-to-r from-primary to-accent"
        initial={false}
        animate={{ scaleX: active ? 1 : 0, opacity: active ? 1 : 0 }}
        transition={{ duration: reduce ? 0.001 : 0.28, ease: EXPOCSS }}
      />
    </Link>
  );
}
