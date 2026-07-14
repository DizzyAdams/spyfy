"use client";

import { useState, useMemo } from "react";
import { motion, AnimatePresence } from "framer-motion";
import {
  Bell,
  BellOff,
  TrendingUp,
  TrendingDown,
  Search,
  Zap,
  BarChart3,
  Activity,
  AlertTriangle,
  CheckCheck,
  Sparkles,
  Clock,
  Tag,
} from "lucide-react";
import { cn } from "@/lib/utils";
import { EXPOCSS, staggerContainer, fadeUp } from "@/lib/motion";

/* ── Mock alert data ── */

type AlertType = "offer" | "system" | "roi";

interface Alert {
  id: string;
  type: AlertType;
  icon: typeof Bell;
  title: string;
  description: string;
  timestamp: Date;
  read: boolean;
}

const now = Date.now();
const HOUR = 3600_000;
const DAY = 86_400_000;

const MOCK_ALERTS: Alert[] = [
  {
    id: "a1",
    type: "offer",
    icon: TrendingUp,
    title: "🔥 Hot offer detected",
    description:
      '"Emagreça 7kg em 21 dias" just crossed 80 winning score on Meta.',
    timestamp: new Date(now - HOUR * 2),
    read: false,
  },
  {
    id: "a2",
    type: "offer",
    icon: Search,
    title: "New competitor offer found",
    description:
      "HealthBR launched a new variant on TikTok with a different VSL angle.",
    timestamp: new Date(now - HOUR * 5),
    read: false,
  },
  {
    id: "a3",
    type: "roi",
    icon: TrendingDown,
    title: "ROI drop — LeadFlow campaign",
    description:
      '"O mini-site que gera leads" ROI dropped from 210% to 165% in 24h.',
    timestamp: new Date(now - HOUR * 8),
    read: false,
  },
  {
    id: "a4",
    type: "system",
    icon: Zap,
    title: "Radar back online",
    description:
      "Real-time feed reconnected after 3 minutes of downtime. All caches synced.",
    timestamp: new Date(now - DAY * 0.5),
    read: false,
  },
  {
    id: "a5",
    type: "offer",
    icon: Sparkles,
    title: "Scaling signal — skincare offer",
    description:
      '"Pele de vidro" entered scaling phase on Meta with impressions +40% in 7 days.',
    timestamp: new Date(now - DAY * 1),
    read: true,
  },
  {
    id: "a6",
    type: "roi",
    icon: BarChart3,
    title: "Weekly ROI report ready",
    description:
      "Your top 5 saved offers averaged 187% ROI this week. 2 offers underperforming.",
    timestamp: new Date(now - DAY * 1.5),
    read: true,
  },
  {
    id: "a7",
    type: "system",
    icon: Activity,
    title: "New network available",
    description:
      "Pinterest Ad Library integration is now live. You can now discover pin ads.",
    timestamp: new Date(now - DAY * 2),
    read: true,
  },
  {
    id: "a8",
    type: "offer",
    icon: Tag,
    title: "Price drop — clone credits",
    description:
      "Pro Plan clone credits refreshed. You have 87 clonagens remaining this month.",
    timestamp: new Date(now - DAY * 3),
    read: true,
  },
];

/* ── Helpers ── */

function timeAgo(d: Date): string {
  const diff = now - d.getTime();
  if (diff < HOUR) return `${Math.round(diff / 60000)}m ago`;
  if (diff < DAY) return `${Math.round(diff / HOUR)}h ago`;
  if (diff < DAY * 7) return `${Math.round(diff / DAY)}d ago`;
  return d.toLocaleDateString("en-US", { month: "short", day: "numeric" });
}

type FilterKey = "all" | "offer" | "system" | "roi";
const filters: { key: FilterKey; label: string }[] = [
  { key: "all", label: "All" },
  { key: "offer", label: "Offers" },
  { key: "system", label: "System" },
  { key: "roi", label: "ROI" },
];

const typeIcons: Record<AlertType, typeof Bell> = {
  offer: TrendingUp,
  system: Zap,
  roi: BarChart3,
};

function groupAlerts(alerts: Alert[]): { label: string; items: Alert[] }[] {
  const groups: { label: string; threshold: number }[] = [
    { label: "Today", threshold: DAY },
    { label: "This Week", threshold: DAY * 7 },
    { label: "Earlier", threshold: Infinity },
  ];

  const now = Date.now();
  const buckets = groups.map(() => [] as Alert[]);

  for (const a of alerts) {
    const age = now - a.timestamp.getTime();
    const idx = groups.findIndex((g) => age < g.threshold);
    if (idx >= 0) buckets[idx].push(a);
    else buckets[buckets.length - 1].push(a);
  }

  return groups
    .map((g, i) => ({ label: g.label, items: buckets[i] }))
    .filter((g) => g.items.length > 0);
}

/* ── Component ── */

export function AlertsView() {
  const [alerts, setAlerts] = useState<Alert[]>(MOCK_ALERTS);
  const [filter, setFilter] = useState<FilterKey>("all");

  const unreadCount = useMemo(
    () => alerts.filter((a) => !a.read).length,
    [alerts],
  );

  const filtered = useMemo(() => {
    if (filter === "all") return alerts;
    return alerts.filter((a) => a.type === filter);
  }, [alerts, filter]);

  const grouped = useMemo(() => groupAlerts(filtered), [filtered]);

  const markAllRead = () =>
    setAlerts((prev) => prev.map((a) => ({ ...a, read: true })));

  const markOneRead = (id: string) =>
    setAlerts((prev) =>
      prev.map((a) => (a.id === id ? { ...a, read: true } : a)),
    );

  return (
    <div>
      {/* Header */}
      <div className="mb-6 flex flex-wrap items-center justify-between gap-3">
        <div>
          <h1 className="text-2xl font-bold tracking-tight">Alerts</h1>
          <p className="mt-1 text-sm text-muted">
            {unreadCount > 0
              ? `${unreadCount} unread notification${unreadCount !== 1 ? "s" : ""}`
              : "All caught up"}
          </p>
        </div>
        {unreadCount > 0 && (
          <motion.button
            type="button"
            onClick={markAllRead}
            initial={{ opacity: 0, scale: 0.95 }}
            animate={{ opacity: 1, scale: 1 }}
            className="btn btn-ghost !inline-flex !gap-2 !py-2 !text-[13px] focus-visible:ring-2 focus-visible:ring-[var(--ring)] focus-visible:ring-offset-2 focus-visible:ring-offset-[var(--bg)]"
          >
            <CheckCheck size={16} />
            Mark all read
          </motion.button>
        )}
      </div>

      {/* Filter tabs */}
      <div className="mb-6 flex gap-1 rounded-xl border border-border bg-surface/50 p-1">
        {filters.map((f) => {
          const isActive = filter === f.key;
          return (
            <button
              key={f.key}
              onClick={() => setFilter(f.key)}
              className={cn(
                "relative flex flex-1 items-center justify-center rounded-lg px-3 py-2 text-sm font-medium transition-colors",
                isActive ? "text-text" : "text-muted hover:text-text",
              )}
            >
              {isActive && (
                <motion.span
                  layoutId="alert-filter-active"
                  className="absolute inset-0 rounded-lg bg-primary/15 ring-1 ring-primary/30"
                  transition={{ duration: 0.3, ease: EXPOCSS }}
                />
              )}
              <span className="relative z-10">{f.label}</span>
            </button>
          );
        })}
      </div>

      {/* Alert groups */}
      <motion.div
        variants={staggerContainer}
        initial="hidden"
        animate="show"
        className="space-y-8"
      >
        <AnimatePresence mode="popLayout">
          {grouped.length > 0 ? (
            grouped.map((group) => (
              <motion.div key={group.label} variants={fadeUp}>
                <h3 className="mb-3 flex items-center gap-2 text-xs font-semibold uppercase tracking-widest text-muted">
                  <span className="h-px flex-1 bg-border" />
                  {group.label}
                  <span className="h-px flex-1 bg-border" />
                </h3>
                <div className="space-y-1.5">
                  {group.items.map((alert) => (
                    <motion.button
                      key={alert.id}
                      layout
                      initial={{ opacity: 0, x: -8 }}
                      animate={{ opacity: 1, x: 0 }}
                      exit={{ opacity: 0, height: 0, marginBottom: 0 }}
                      transition={{ duration: 0.3, ease: EXPOCSS }}
                      onClick={() => markOneRead(alert.id)}
                      className={cn(
                        "group relative flex w-full items-start gap-4 rounded-xl border px-4 py-3.5 text-left transition-all hover:border-primary/30",
                        alert.read
                          ? "border-border bg-surface/30"
                          : "border-primary/20 bg-primary/5",
                      )}
                    >
                      {/* Unread dot */}
                      {!alert.read && (
                        <motion.span
                          layoutId={`dot-${alert.id}`}
                          className="absolute right-3 top-3 h-2 w-2 rounded-full bg-accent"
                        />
                      )}

                      {/* Icon */}
                      <span
                        className={cn(
                          "grid h-10 w-10 shrink-0 place-items-center rounded-xl border",
                          alert.read
                            ? "border-border bg-surface text-muted"
                            : "border-primary/20 bg-primary/10 text-accent",
                        )}
                      >
                        <alert.icon size={18} />
                      </span>

                      {/* Content */}
                      <div className="min-w-0 flex-1">
                        <p
                          className={cn(
                            "text-sm font-medium",
                            alert.read ? "text-text" : "text-text",
                          )}
                        >
                          {alert.title}
                        </p>
                        <p className="mt-0.5 text-sm text-muted line-clamp-2">
                          {alert.description}
                        </p>
                        <p className="mt-1.5 flex items-center gap-1 font-mono text-[11px] tabular-nums text-muted">
                          <Clock size={11} />
                          {timeAgo(alert.timestamp)}
                        </p>
                      </div>

                      {/* Type badge */}
                      <span className="hidden shrink-0 self-start rounded-full border border-border bg-surface/60 px-2 py-0.5 text-[11px] font-medium text-muted sm:inline-flex items-center gap-1">
                        {alert.type === "offer" && <TrendingUp size={11} />}
                        {alert.type === "system" && <Zap size={11} />}
                        {alert.type === "roi" && <BarChart3 size={11} />}
                        {alert.type.charAt(0).toUpperCase() +
                          alert.type.slice(1)}
                      </span>
                    </motion.button>
                  ))}
                </div>
              </motion.div>
            ))
          ) : (
            <motion.div
              variants={fadeUp}
              className="flex flex-col items-center gap-4 rounded-2xl border border-dashed border-border px-6 py-16 text-center"
            >
              <span className="grid h-14 w-14 place-items-center rounded-2xl border border-border bg-surface text-muted">
                <BellOff size={26} aria-hidden />
              </span>
              <div>
                <p className="font-display text-base font-semibold text-text">
                  No alerts
                </p>
                <p className="mt-1 text-sm text-muted">
                  {filter === "all"
                    ? "You're all caught up. New alerts will appear here."
                    : `No ${filter} alerts to show. Try another filter.`}
                </p>
              </div>
            </motion.div>
          )}
        </AnimatePresence>
      </motion.div>
    </div>
  );
}
