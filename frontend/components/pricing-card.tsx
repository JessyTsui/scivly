import type { ReactNode } from "react";
import Link from "next/link";
import { Check } from "lucide-react";

import type { PricingTier } from "@/lib/public-site";

export function PricingCard({
  tier,
  compact = false,
  action,
}: {
  tier: PricingTier;
  compact?: boolean;
  action?: ReactNode;
}) {
  return (
    <div
      className={`card relative flex h-full flex-col overflow-hidden rounded-[32px] p-6 sm:p-8 ${
        tier.featured ? "border-[var(--primary)]/25 shadow-[var(--shadow-lg)]" : ""
      }`}
    >
      {tier.featured ? (
        <div className="absolute inset-x-0 top-0 h-1 bg-gradient-to-r from-[var(--primary)] via-[var(--primary-light)] to-[var(--accent)]" />
      ) : null}

      <div className="flex items-start justify-between gap-4">
        <div>
          <p className="text-sm font-semibold uppercase tracking-[0.22em] text-[var(--primary)]">
            {tier.name}
          </p>
          <p className="mt-3 font-[family:var(--font-display)] text-4xl font-semibold tracking-tight text-[var(--foreground)]">
            {tier.price}
          </p>
          <p className="mt-2 text-sm text-[var(--foreground-subtle)]">{tier.cadence}</p>
        </div>
        <span
          className={`rounded-full px-3 py-1 text-xs font-semibold ${
            tier.featured
              ? "bg-[var(--primary-subtle)] text-[var(--primary-dark)]"
              : "bg-[var(--surface-elevated)] text-[var(--foreground-muted)]"
          }`}
        >
          {tier.highlight}
        </span>
      </div>

      <p className="mt-6 text-base leading-7 text-[var(--foreground-muted)]">{tier.summary}</p>

      <div className="mt-6 h-px w-full bg-[var(--border)]" />

      <ul className="mt-6 space-y-3">
        {tier.features.slice(0, compact ? 3 : tier.features.length).map((feature) => (
          <li key={feature} className="flex gap-3 text-sm leading-6 text-[var(--foreground)]">
            <span className="mt-0.5 flex h-6 w-6 shrink-0 items-center justify-center rounded-full bg-[var(--primary-subtle)] text-[var(--primary-dark)]">
              <Check className="h-3.5 w-3.5" />
            </span>
            <span>{feature}</span>
          </li>
        ))}
      </ul>

      <div className="mt-8">
        {action ?? (
          <Link href={tier.ctaHref} className={tier.featured ? "btn-primary" : "btn-secondary"}>
            {tier.ctaLabel}
          </Link>
        )}
      </div>
    </div>
  );
}
