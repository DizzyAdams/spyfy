"use client";

import { useState, useEffect, useMemo } from "react";
import { motion, AnimatePresence } from "framer-motion";
import {
  Bookmark,
  BookmarkCheck,
  Clock,
  Archive,
  BookOpen,
  Trash2,
  ArrowRight,
} from "lucide-react";
import { OFFERS, type Offer } from "@/lib/data";
import { OfferCard } from "../OfferCard";
import { cn } from "@/lib/utils";
import { EXPOCSS, staggerContainer, fadeUp } from "@/lib/motion";

type Tab = "saved" | "recent" | "archived";

const tabs: { key: Tab; label: string; icon: typeof Bookmark }[] = [
  { key: "saved", label: "Saved", icon: BookmarkCheck },
  { key: "recent", label: "Recent", icon: Clock },
  { key: "archived", label: "Archived", icon: Archive },
];

function EmptyState({
  icon: Icon,
  title,
  description,
  action,
}: {
  icon: typeof Bookmark;
  title: string;
  description: string;
  action?: { label: string; onClick: () => void };
}) {
  return (
    <motion.div
      variants={fadeUp}
      initial="hidden"
      animate="show"
      className="col-span-full flex flex-col items-center gap-4 rounded-2xl border border-dashed border-border px-6 py-16 text-center"
    >
      <span className="grid h-14 w-14 place-items-center rounded-2xl border border-border bg-surface text-muted">
        <Icon size={26} aria-hidden />
      </span>
      <div>
        <p className="font-display text-base font-semibold text-text">{title}</p>
        <p className="mt-1 text-sm text-muted">{description}</p>
      </div>
      {action && (
        <button
          type="button"
          onClick={action.onClick}
          className="btn btn-primary mt-2 !inline-flex !gap-2 focus-visible:ring-2 focus-visible:ring-[var(--ring)] focus-visible:ring-offset-2 focus-visible:ring-offset-[var(--bg)]"
        >
          {action.label}
          <ArrowRight size={15} />
        </button>
      )}
    </motion.div>
  );
}

export function LibraryView() {
  const [activeTab, setActiveTab] = useState<Tab>("saved");
  const [savedIds, setSavedIds] = useState<Set<string>>(new Set());
  const [archivedIds, setArchivedIds] = useState<Set<string>>(new Set());

  // Load saved & archived IDs from localStorage on mount
  useEffect(() => {
    try {
      const raw = localStorage.getItem("spyfy_saved");
      if (raw) setSavedIds(new Set(JSON.parse(raw)));
      const rawArch = localStorage.getItem("spyfy_archived");
      if (rawArch) setArchivedIds(new Set(JSON.parse(rawArch)));
    } catch {
      /* corrupt storage — ignore */
    }
  }, []);

  // Persist to localStorage whenever the sets change
  const persistSaved = (ids: Set<string>) => {
    setSavedIds(ids);
    localStorage.setItem("spyfy_saved", JSON.stringify([...ids]));
  };
  const persistArchived = (ids: Set<string>) => {
    setArchivedIds(ids);
    localStorage.setItem("spyfy_archived", JSON.stringify([...ids]));
  };

  // Remove from saved (move to archived)
  const archiveOffer = (id: string) => {
    const next = new Set(savedIds);
    next.delete(id);
    const nextArch = new Set(archivedIds);
    nextArch.add(id);
    persistSaved(next);
    persistArchived(nextArch);
  };

  // Permanently remove from archived
  const deleteArchived = (id: string) => {
    const next = new Set(archivedIds);
    next.delete(id);
    persistArchived(next);
  };

  // Restore from archived back to saved
  const restoreOffer = (id: string) => {
    const next = new Set(savedIds);
    next.add(id);
    const nextArch = new Set(archivedIds);
    nextArch.delete(id);
    persistSaved(next);
    persistArchived(nextArch);
  };

  // Derive the offer objects from the ID sets
  const savedOffers = useMemo(
    () => OFFERS.filter((o) => savedIds.has(o.id)),
    [savedIds],
  );
  const recentOffers = useMemo(
    () =>
      [...OFFERS]
        .sort((a, b) => b.longevityDays - a.longevityDays)
        .slice(0, 6),
    [],
  );
  const archivedOffers = useMemo(
    () => OFFERS.filter((o) => archivedIds.has(o.id)),
    [archivedIds],
  );

  // Determine which list to show
  const activeList =
    activeTab === "saved"
      ? savedOffers
      : activeTab === "recent"
        ? recentOffers
        : archivedOffers;

  return (
    <div>
      <div className="mb-6">
        <h1 className="text-2xl font-bold tracking-tight">Library</h1>
        <p className="mt-1 text-sm text-muted">
          Your curated collection of winning offers
        </p>
      </div>

      {/* Tabs */}
      <div className="mb-6 flex gap-1 rounded-xl border border-border bg-surface/50 p-1">
        {tabs.map((t) => {
          const isActive = activeTab === t.key;
          const count =
            t.key === "saved"
              ? savedOffers.length
              : t.key === "recent"
                ? recentOffers.length
                : archivedOffers.length;
          return (
            <button
              key={t.key}
              onClick={() => setActiveTab(t.key)}
              className={cn(
                "relative flex flex-1 items-center justify-center gap-2 rounded-lg px-3 py-2 text-sm font-medium transition-colors",
                isActive
                  ? "text-text"
                  : "text-muted hover:text-text",
              )}
            >
              {isActive && (
                <motion.span
                  layoutId="lib-tab-active"
                  className="absolute inset-0 rounded-lg bg-primary/15 ring-1 ring-primary/30"
                  transition={{ duration: 0.3, ease: EXPOCSS }}
                />
              )}
              <span className="relative z-10 inline-flex items-center gap-2">
                <t.icon size={16} />
                {t.label}
                <span className="font-mono text-xs tabular-nums text-muted">
                  {count}
                </span>
              </span>
            </button>
          );
        })}
      </div>

      {/* Content */}
      <motion.div
        variants={staggerContainer}
        initial="hidden"
        animate="show"
        className="grid grid-cols-1 gap-4 sm:grid-cols-2 xl:grid-cols-3"
      >
        <AnimatePresence mode="popLayout">
          {activeList.length > 0 ? (
            activeList.map((offer, i) => (
              <motion.div
                key={offer.id}
                variants={fadeUp}
                layout
                exit={{ opacity: 0, scale: 0.95 }}
                className="relative"
              >
                <OfferCard offer={offer} index={i} />

                {/* Tab-specific actions overlay */}
                <div className="pointer-events-none absolute inset-0 z-10 p-3">
                  <div className="pointer-events-auto flex justify-end gap-1.5">
                    {activeTab === "saved" && (
                      <button
                        type="button"
                        onClick={() => archiveOffer(offer.id)}
                        aria-label="Archive offer"
                        className="grid h-8 w-8 place-items-center rounded-lg border border-border bg-surface/80 text-muted opacity-0 backdrop-blur transition-opacity hover:text-text group-hover:opacity-100 focus-visible:opacity-100 focus-visible:ring-2 focus-visible:ring-[var(--ring)]"
                      >
                        <Archive size={14} />
                      </button>
                    )}
                    {activeTab === "archived" && (
                      <>
                        <button
                          type="button"
                          onClick={() => restoreOffer(offer.id)}
                          aria-label="Restore offer"
                          className="grid h-8 w-8 place-items-center rounded-lg border border-border bg-surface/80 text-muted opacity-0 backdrop-blur transition-opacity hover:text-[var(--success)] focus-visible:opacity-100 focus-visible:ring-2 focus-visible:ring-[var(--ring)]"
                        >
                          <BookmarkCheck size={14} />
                        </button>
                        <button
                          type="button"
                          onClick={() => deleteArchived(offer.id)}
                          aria-label="Delete permanently"
                          className="grid h-8 w-8 place-items-center rounded-lg border border-border bg-surface/80 text-muted opacity-0 backdrop-blur transition-opacity hover:text-[var(--danger)] focus-visible:opacity-100 focus-visible:ring-2 focus-visible:ring-[var(--ring)]"
                        >
                          <Trash2 size={14} />
                        </button>
                      </>
                    )}
                  </div>
                </div>
              </motion.div>
            ))
          ) : (
            <EmptyState
              icon={
                activeTab === "saved"
                  ? BookmarkCheck
                  : activeTab === "recent"
                    ? Clock
                    : Archive
              }
              title={
                activeTab === "saved"
                  ? "No saved offers yet"
                  : activeTab === "recent"
                    ? "No recent offers"
                    : "No archived offers"
              }
              description={
                activeTab === "saved"
                  ? "Save winning offers from the Discovery Feed to build your library."
                  : activeTab === "recent"
                    ? "Recently viewed offers will appear here."
                    : "Archived offers will show up here after you archive them."
              }
              action={
                activeTab === "saved"
                  ? {
                      label: "Browse Feed",
                      onClick: () =>
                        (window.location.href = "/app/feed"),
                    }
                  : undefined
              }
            />
          )}
        </AnimatePresence>
      </motion.div>
    </div>
  );
}
