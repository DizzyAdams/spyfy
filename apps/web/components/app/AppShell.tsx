"use client";

import { useState, useRef } from "react";
import Link from "next/link";
import { usePathname } from "next/navigation";
import { motion, useReducedMotion } from "framer-motion";
import {
  LayoutGrid,
  BarChart3,
  Library,
  Bell,
  Settings,
  Search,
  Command,
} from "lucide-react";
import Logo from "../illustrations/Logo";
import { LiveBadge } from "./LiveBadge";
import { useRealtime } from "@/lib/realtime/RealtimeProvider";
import { cn } from "@/lib/utils";
import { fadeIn, revealUp, magnetic, EXPOCSS } from "@/lib/motion";

const MotionLink = motion.create(Link);

const nav = [
  { href: "/app/feed", label: "Feed", icon: LayoutGrid },
  { href: "/app/analytics", label: "Analytics", icon: BarChart3 },
  { href: "/app/library", label: "Library", icon: Library },
  { href: "/app/alerts", label: "Alerts", icon: Bell },
  { href: "/app/settings", label: "Settings", icon: Settings },
];

export function AppShell({ children }: { children: React.ReactNode }) {
  const pathname = usePathname();
  const reduce = useReducedMotion();
  const { status, search } = useRealtime();
  const [q, setQ] = useState("");
  const debounceRef = useRef<ReturnType<typeof setTimeout> | undefined>(undefined);

  const onSearch = (v: string) => {
    setQ(v);
    if (debounceRef.current) clearTimeout(debounceRef.current);
    debounceRef.current = setTimeout(() => search(v), 250);
  };

  return (
    <div className="flex min-h-screen">
      {/* Sidebar */}
      <motion.aside
        variants={revealUp}
        initial={reduce ? false : "hidden"}
        animate={reduce ? undefined : "show"}
        className="sticky top-0 hidden h-screen w-60 shrink-0 flex-col border-r border-border bg-surface/40 p-4 lg:flex"
      >
        <div className="px-2 py-2">
          <Link href="/">
            <motion.div
              variants={fadeIn}
              initial={reduce ? false : "hidden"}
              animate={reduce ? undefined : "show"}
            >
              <Logo />
            </motion.div>
          </Link>
        </div>

        <nav className="mt-6 flex flex-1 flex-col gap-1">
          {nav.map((n) => {
            const isActive = pathname.startsWith(n.href);
            return (
              <MotionLink
                key={n.label}
                href={n.href}
                initial="rest"
                animate="rest"
                whileHover={reduce ? undefined : "hover"}
                className={cn(
                  "relative flex items-center gap-3 rounded-lg px-3 py-2.5 text-sm transition-colors",
                  isActive ? "text-text" : "text-muted hover:text-text"
                )}
              >
                {isActive && (
                  <motion.span
                    layoutId="nav-active"
                    className="absolute inset-0 -z-10 rounded-lg bg-primary/15 ring-1 ring-primary/30"
                    transition={{ duration: 0.3, ease: [0.22, 1, 0.36, 1] }}
                  />
                )}
                <motion.span variants={magnetic} className="inline-flex">
                  <n.icon size={18} />
                </motion.span>
                {n.label}
              </MotionLink>
            );
          })}
        </nav>

        <motion.div
          variants={revealUp}
          initial={reduce ? false : "hidden"}
          animate={reduce ? undefined : "show"}
          transition={{ duration: 0.6, ease: EXPOCSS, delay: 0.3 }}
          className="rounded-xl border border-border bg-surface-2 p-3 text-xs"
        >
          <p className="font-semibold text-text">Plano Pro</p>
          <p className="mt-1 text-muted">87 clonagens restantes</p>
          <div className="mt-2 h-1.5 overflow-hidden rounded-full bg-bg">
            <div className="h-full w-[70%] rounded-full bg-primary" />
          </div>
        </motion.div>
      </motion.aside>

      {/* Content */}
      <div className="flex min-w-0 flex-1 flex-col">
        {/* Topbar */}
        <header className="sticky top-0 z-40 flex h-16 items-center gap-4 border-b border-border bg-bg/80 px-5 backdrop-blur">
          <div className="flex flex-1 items-center gap-2 rounded-lg border border-border bg-surface/60 px-3 py-2 text-sm text-muted">
            <Search size={16} />
            <input
              value={q}
              onChange={(e) => onSearch(e.target.value)}
              placeholder="Buscar ofertas, anunciantes, ângulos…"
              className="w-full bg-transparent text-text outline-none placeholder:text-muted"
              aria-label="Busca global"
            />
            <span className="hidden items-center gap-1 rounded border border-border px-1.5 py-0.5 text-[11px] sm:flex">
              <Command size={11} /> K
            </span>
          </div>
          <LiveBadge status={status} className="hidden sm:inline-flex" />
          <button className="relative grid h-9 w-9 place-items-center rounded-lg border border-border bg-surface/60 text-muted hover:text-text" aria-label="Notificações">
            <Bell size={17} />
            <span className="absolute right-2 top-2 h-2 w-2 rounded-full bg-accent" />
            {!reduce && (
              <motion.span
                aria-hidden
                className="pointer-events-none absolute right-2 top-2 h-2 w-2 rounded-full bg-accent"
                animate={{ scale: [1, 2.4], opacity: [0.6, 0] }}
                transition={{ duration: 2, repeat: Infinity, ease: "easeOut" }}
              />
            )}
          </button>
          <div className="grid h-9 w-9 place-items-center rounded-full bg-gradient-to-br from-primary to-accent text-sm font-bold text-white">
            F
          </div>
        </header>

        <main className="flex-1 px-5 py-6">{children}</main>
      </div>
    </div>
  );
}
