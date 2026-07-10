"use client";

import Link from "next/link";
import { usePathname } from "next/navigation";
import { motion } from "framer-motion";
import {
  LayoutGrid,
  BarChart3,
  Library,
  Bell,
  Settings,
  Search,
  Command,
} from "lucide-react";
import { Logo } from "../illustrations/Logo";
import { cn } from "@/lib/utils";

const nav = [
  { href: "/app/feed", label: "Feed", icon: LayoutGrid },
  { href: "/app/analytics", label: "Analytics", icon: BarChart3 },
  { href: "/app/feed", label: "Library", icon: Library },
  { href: "/app/feed", label: "Alerts", icon: Bell },
  { href: "/app/feed", label: "Settings", icon: Settings },
];

export function AppShell({ children }: { children: React.ReactNode }) {
  const pathname = usePathname();

  return (
    <div className="flex min-h-screen">
      {/* Sidebar */}
      <aside className="sticky top-0 hidden h-screen w-60 shrink-0 flex-col border-r border-border bg-surface/40 p-4 lg:flex">
        <div className="px-2 py-2">
          <Link href="/">
            <Logo />
          </Link>
        </div>

        <nav className="mt-6 flex flex-1 flex-col gap-1">
          {nav.map((n) => {
            const isActive = n.href === "/app/feed" ? pathname.startsWith("/app/feed") : pathname.startsWith(n.href);
            return (
              <Link
                key={n.label}
                href={n.href}
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
                <n.icon size={18} />
                {n.label}
              </Link>
            );
          })}
        </nav>

        <div className="rounded-xl border border-border bg-surface-2 p-3 text-xs">
          <p className="font-semibold text-text">Plano Pro</p>
          <p className="mt-1 text-muted">87 clonagens restantes</p>
          <div className="mt-2 h-1.5 overflow-hidden rounded-full bg-bg">
            <div className="h-full w-[70%] rounded-full bg-primary" />
          </div>
        </div>
      </aside>

      {/* Content */}
      <div className="flex min-w-0 flex-1 flex-col">
        {/* Topbar */}
        <header className="sticky top-0 z-40 flex h-16 items-center gap-4 border-b border-border bg-bg/80 px-5 backdrop-blur">
          <div className="flex flex-1 items-center gap-2 rounded-lg border border-border bg-surface/60 px-3 py-2 text-sm text-muted">
            <Search size={16} />
            <input
              placeholder="Buscar ofertas, anunciantes, ângulos…"
              className="w-full bg-transparent text-text outline-none placeholder:text-muted"
              aria-label="Busca global"
            />
            <span className="hidden items-center gap-1 rounded border border-border px-1.5 py-0.5 text-[11px] sm:flex">
              <Command size={11} /> K
            </span>
          </div>
          <button className="relative grid h-9 w-9 place-items-center rounded-lg border border-border bg-surface/60 text-muted hover:text-text" aria-label="Notificações">
            <Bell size={17} />
            <span className="absolute right-2 top-2 h-2 w-2 rounded-full bg-accent" />
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
