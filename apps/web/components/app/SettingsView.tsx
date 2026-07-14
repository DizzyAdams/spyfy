"use client";

import { useState, useEffect } from "react";
import { motion } from "framer-motion";
import {
  User,
  Bell,
  Key,
  Settings,
  CreditCard,
  Sun,
  ChevronRight,
  Copy,
  Eye,
  EyeOff,
  Check,
  Shield,
} from "lucide-react";
import { cn } from "@/lib/utils";
import { fadeUp, EXPOCSS } from "@/lib/motion";

/* ─── Primitives ─── */

function Section({
  title,
  description,
  children,
  index = 0,
}: {
  title: string;
  description?: string;
  children: React.ReactNode;
  index?: number;
}) {
  return (
    <motion.div
      variants={fadeUp}
      initial="hidden"
      animate="show"
      transition={{ delay: index * 0.06 }}
    >
      <div className="mb-4">
        <h2 className="text-base font-semibold text-text">{title}</h2>
        {description && (
          <p className="mt-0.5 text-sm text-muted">{description}</p>
        )}
      </div>
      <div className="rounded-xl border border-border bg-surface/40">
        {children}
      </div>
    </motion.div>
  );
}

function Hairline() {
  return <div className="h-px bg-gradient-to-r from-transparent via-border/60 to-transparent" />;
}

function RowIcon({ icon: Icon }: { icon: typeof User }) {
  return (
    <span className="grid h-9 w-9 shrink-0 place-items-center rounded-lg border border-border bg-surface text-muted">
      <Icon size={16} />
    </span>
  );
}

/* ─── Checkbox-style toggle (border-color based active/inactive) ─── */

function CheckToggle({
  enabled,
  onChange,
  label,
}: {
  enabled: boolean;
  onChange: (v: boolean) => void;
  label: string;
}) {
  return (
    <button
      type="button"
      role="switch"
      aria-checked={enabled}
      onClick={() => onChange(!enabled)}
      className={cn(
        "flex items-center gap-2 rounded-lg border px-3 py-2 text-xs font-medium transition-all duration-200 focus-visible:ring-2 focus-visible:ring-[var(--ring)] focus-visible:ring-offset-2 focus-visible:ring-offset-[var(--bg)]",
        enabled
          ? "border-violet/40 bg-violet/8 text-violet-soft"
          : "border-border bg-transparent text-muted hover:border-border-strong hover:text-text",
      )}
    >
      <span
        className={cn(
          "grid h-4 w-4 shrink-0 place-items-center rounded border transition-colors duration-200",
          enabled
            ? "border-violet bg-violet text-white"
            : "border-border-strong bg-transparent",
        )}
      >
        {enabled && <Check size={10} strokeWidth={3} />}
      </span>
      {label}
    </button>
  );
}

/* ─── Component ─── */

export function SettingsView() {
  const [name] = useState("Fernando");
  const [email] = useState("fernando@spyfy.io");

  // Notification preferences — persisted to localStorage
  const [emailNotif, setEmailNotif] = useState(true);
  const [pushNotif, setPushNotif] = useState(true);
  const [inAppNotif, setInAppNotif] = useState(true);

  useEffect(() => {
    const stored = localStorage.getItem("spyfy_settings_notifications");
    if (stored) {
      try {
        const parsed = JSON.parse(stored);
        if (typeof parsed.emailNotif === "boolean") setEmailNotif(parsed.emailNotif);
        if (typeof parsed.pushNotif === "boolean") setPushNotif(parsed.pushNotif);
        if (typeof parsed.inAppNotif === "boolean") setInAppNotif(parsed.inAppNotif);
      } catch {
        /* ignore corrupt data */
      }
    }
  }, []);

  useEffect(() => {
    localStorage.setItem(
      "spyfy_settings_notifications",
      JSON.stringify({ emailNotif, pushNotif, inAppNotif }),
    );
  }, [emailNotif, pushNotif, inAppNotif]);

  // API Key visibility & copy
  const [apiKeyVisible, setApiKeyVisible] = useState(false);
  const [copied, setCopied] = useState(false);

  useEffect(() => {
    const stored = localStorage.getItem("spyfy_settings_apiKeyVisible");
    if (stored === "true") setApiKeyVisible(true);
  }, []);

  useEffect(() => {
    localStorage.setItem("spyfy_settings_apiKeyVisible", String(apiKeyVisible));
  }, [apiKeyVisible]);

  const maskedKey = "sk-••••••••••••••••••8f3a";
  const fullKey = "sk_live_SpyFy_3fKd8w2jR9mXnQpLvB4cH6tY8f3a";

  const copyKey = async () => {
    try {
      await navigator.clipboard.writeText(fullKey);
      setCopied(true);
      setTimeout(() => setCopied(false), 2000);
    } catch {
      /* fallback */
    }
  };

  const usagePct = 70;
  const clonesRemaining = 87;
  const clonesTotal = 100;

  return (
    <div className="mx-auto max-w-2xl">
      {/* Header */}
      <div className="mb-8">
        <div className="flex items-center gap-3">
          <span className="grid h-10 w-10 place-items-center rounded-xl border border-border bg-surface text-muted">
            <Settings size={18} />
          </span>
          <div>
            <h1 className="text-2xl font-bold tracking-tight text-text">
              Settings
            </h1>
            <p className="mt-0.5 text-sm text-muted">
              Manage your account, notifications, and API keys
            </p>
          </div>
        </div>
      </div>

      <div className="space-y-8">
        {/* ── Profile ── */}
        <Section title="Profile" description="Your account information" index={0}>
          <div className="flex items-center gap-4 px-5 py-5">
            {/* Avatar placeholder */}
            <div className="flex h-14 w-14 shrink-0 items-center justify-center rounded-full border border-border-strong bg-gradient-to-b from-surface-2 to-surface font-display text-lg font-bold text-text shadow-sm">
              {name.charAt(0).toUpperCase()}
            </div>
            <div>
              <p className="text-sm font-semibold text-text">{name}</p>
              <p className="text-xs text-muted">{email}</p>
            </div>
          </div>
        </Section>

        <Hairline />

        {/* ── Notifications ── */}
        <Section
          title="Notification Preferences"
          description="Choose how you receive alerts"
          index={1}
        >
          <div className="flex flex-wrap gap-2 px-5 py-4">
            <CheckToggle
              enabled={emailNotif}
              onChange={setEmailNotif}
              label="Email"
            />
            <CheckToggle
              enabled={pushNotif}
              onChange={setPushNotif}
              label="Push"
            />
            <CheckToggle
              enabled={inAppNotif}
              onChange={setInAppNotif}
              label="In-app"
            />
          </div>
          <div className="border-t border-border px-5 py-3">
            <p className="flex items-center gap-2 text-xs text-muted">
              <Bell size={12} />
              {[emailNotif, pushNotif, inAppNotif].filter(Boolean).length === 3
                ? "All notifications enabled"
                : [emailNotif, pushNotif, inAppNotif].filter(Boolean).length === 0
                  ? "All notifications disabled"
                  : `${[emailNotif, pushNotif, inAppNotif].filter(Boolean).length} of 3 notification channels active`}
            </p>
          </div>
        </Section>

        <Hairline />

        {/* ── API Keys ── */}
        <Section title="API Keys" description="Access the SpyFy API" index={2}>
          <div className="flex items-center justify-between gap-4 px-5 py-4">
            <div className="flex items-center gap-3 min-w-0">
              <RowIcon icon={Key} />
              <div className="min-w-0">
                <p className="text-sm font-medium text-text">Secret key</p>
                <p className="truncate text-xs text-muted">
                  {apiKeyVisible ? fullKey : maskedKey}
                </p>
              </div>
            </div>
            <div className="flex shrink-0 items-center gap-1.5">
              <button
                type="button"
                onClick={() => setApiKeyVisible(!apiKeyVisible)}
                aria-label={apiKeyVisible ? "Hide key" : "Show key"}
                className="grid h-8 w-8 place-items-center rounded-lg border border-border text-muted transition-colors hover:border-border-strong hover:text-text focus-visible:ring-2 focus-visible:ring-[var(--ring)]"
              >
                {apiKeyVisible ? <EyeOff size={15} /> : <Eye size={15} />}
              </button>
              <button
                type="button"
                onClick={copyKey}
                aria-label="Copy key"
                className="grid h-8 w-8 place-items-center rounded-lg border border-border text-muted transition-colors hover:border-border-strong hover:text-text focus-visible:ring-2 focus-visible:ring-[var(--ring)]"
              >
                {copied ? (
                  <Check size={15} className="text-[var(--success)]" />
                ) : (
                  <Copy size={15} />
                )}
              </button>
            </div>
          </div>
        </Section>

        <Hairline />

        {/* ── Plan ── */}
        <Section
          title="Plan & Billing"
          description="Your current subscription"
          index={3}
        >
          <div className="px-5 py-4">
            {/* Plan header */}
            <div className="mb-4 flex items-center justify-between gap-3">
              <div className="flex items-center gap-3">
                <span className="grid h-10 w-10 place-items-center rounded-xl border border-border bg-gradient-to-br from-violet/20 to-cyan/10 text-violet-soft">
                  <CreditCard size={17} />
                </span>
                <div>
                  <div className="flex items-center gap-2">
                    <p className="text-sm font-semibold text-text">Pro Plan</p>
                    <span className="rounded-full border border-violet/30 bg-violet/8 px-2 py-0.5 text-[10px] font-semibold uppercase tracking-wider text-violet-soft">
                      Active
                    </span>
                  </div>
                  <p className="text-xs text-muted">$49 / month</p>
                </div>
              </div>
              <button
                type="button"
                className="btn btn-primary !px-4 !py-2 !text-xs"
              >
                Upgrade
                <ChevronRight size={13} />
              </button>
            </div>

            {/* Usage bar */}
            <div>
              <div className="mb-1.5 flex items-center justify-between text-xs">
                <span className="text-muted">Monthly clone credits</span>
                <span className="font-mono tabular-nums text-text">
                  {clonesRemaining} / {clonesTotal} remaining
                </span>
              </div>
              <div className="h-2 overflow-hidden rounded-full bg-border/50">
                <motion.div
                  className="h-full rounded-full bg-gradient-to-r from-violet to-cyan"
                  initial={{ width: 0 }}
                  animate={{ width: `${usagePct}%` }}
                  transition={{ duration: 0.8, ease: EXPOCSS }}
                />
              </div>
              <div className="mt-2 flex items-center justify-between text-xs">
                <span className="text-muted">
                  <span className="font-semibold text-[var(--success)]">
                    {clonesRemaining}
                  </span>{" "}
                  clones remaining this billing period
                </span>
                <span className="text-muted">{usagePct}% used</span>
              </div>
            </div>
          </div>
        </Section>

        <Hairline />

        {/* ── Theme ── */}
        <Section
          title="Appearance"
          description="Customize your interface"
          index={4}
        >
          <div className="flex items-center justify-between gap-4 px-5 py-4">
            <div className="flex items-center gap-3">
              <span className="grid h-9 w-9 shrink-0 place-items-center rounded-lg border border-border bg-surface text-muted">
                <Sun size={16} />
              </span>
              <div>
                <p className="text-sm font-medium text-text">Theme</p>
                <p className="text-xs text-muted">Dark mode is always on</p>
              </div>
            </div>
            <div className="flex items-center gap-2">
              <span className="rounded-md bg-primary/12 px-2.5 py-1 text-xs font-medium text-primary">
                Dark
              </span>
              <div className="relative h-6 w-10 shrink-0 rounded-full bg-primary opacity-40">
                <span className="absolute left-0.5 top-0.5 h-5 w-5 rounded-full bg-white translate-x-4" />
              </div>
            </div>
          </div>
        </Section>

        {/* ── Footer ── */}
        <div className="flex items-center justify-between rounded-xl border border-border/50 bg-surface/20 px-5 py-3">
          <div className="flex items-center gap-2 text-xs text-muted">
            <Shield size={13} />
            Your data is encrypted at rest and in transit
          </div>
          <span className="text-xs text-muted">SpyFy v1.0.0</span>
        </div>
      </div>
    </div>
  );
}
