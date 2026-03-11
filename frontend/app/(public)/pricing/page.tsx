import Link from "next/link";
import { ArrowRight, Check, Sparkles } from "lucide-react";

import { PricingCard } from "@/components/pricing-card";
import { PricingPlanAction } from "@/components/pricing-plan-action";
import { SectionHeading } from "@/components/section-heading";
import { SignupCta } from "@/components/signup-cta";
import { pricingComparison, pricingFaqs, pricingTiers } from "@/lib/public-site";
import { createMetadata } from "@/lib/metadata";

export const metadata = createMetadata({
  title: "Pricing",
  description:
    "Compare Scivly pricing tiers for solo researchers, shared team workspaces, and enterprise deployments.",
  path: "/pricing",
  ogImage: "/pricing/opengraph-image",
});

export default function PricingPage() {
  return (
    <main>
      <section className="px-4 pb-16 pt-12 sm:px-6 lg:px-8 lg:pb-24 lg:pt-20">
        <div className="mx-auto max-w-7xl">
          <div className="grid gap-8 lg:grid-cols-[0.88fr_1.12fr] lg:items-end">
            <div>
              <SectionHeading
                eyebrow="Pricing"
                title="Simple pricing for teams that need paper monitoring to become an actual system."
                body="Start with a free workspace, upgrade when shared delivery matters, and move to enterprise controls when the platform becomes part of how your organization runs."
              />
            </div>

            <div className="card rounded-[32px] p-6 sm:p-8">
              <div className="flex items-center gap-3">
                <div className="flex h-11 w-11 items-center justify-center rounded-2xl bg-[var(--primary-subtle)] text-[var(--primary-dark)]">
                  <Sparkles className="h-5 w-5" />
                </div>
                <div>
                  <p className="text-sm font-semibold uppercase tracking-[0.22em] text-[var(--primary)]">
                    Recommended
                  </p>
                  <p className="mt-1 text-lg font-medium text-[var(--foreground)]">
                    Pro is the default starting point for most labs and product teams.
                  </p>
                </div>
              </div>

              <div className="mt-6 grid gap-4 sm:grid-cols-2">
                {[
                  "Self-serve Stripe Checkout and billing portal",
                  "Higher daily paper and token ceilings",
                  "Usage-aware workspace operations",
                  "A clean path to enterprise controls later",
                ].map((item) => (
                  <div key={item} className="flex gap-3 rounded-2xl border border-[var(--border)] bg-[var(--surface-hover)] px-4 py-3">
                    <span className="mt-0.5 flex h-6 w-6 shrink-0 items-center justify-center rounded-full bg-[var(--primary-subtle)] text-[var(--primary-dark)]">
                      <Check className="h-3.5 w-3.5" />
                    </span>
                    <span className="text-sm leading-6 text-[var(--foreground)]">{item}</span>
                  </div>
                ))}
              </div>
            </div>
          </div>

          <div className="mt-12 grid gap-5 xl:grid-cols-3">
            {pricingTiers.map((tier) => (
              <PricingCard
                key={tier.name}
                tier={tier}
                action={
                  <PricingPlanAction
                    plan={tier.billingPlan}
                    href={tier.ctaHref}
                    label={tier.ctaLabel}
                    featured={Boolean(tier.featured)}
                  />
                }
              />
            ))}
          </div>
        </div>
      </section>

      <section id="compare" className="border-y border-[var(--border)] bg-[var(--surface)]/75 px-4 py-16 sm:px-6 lg:px-8 lg:py-24">
        <div className="mx-auto max-w-7xl">
          <div className="flex flex-col gap-4 lg:flex-row lg:items-end lg:justify-between">
            <SectionHeading
              eyebrow="Compare Plans"
              title="The tiers are intentionally narrow so you can tell when the workspace is ready to level up."
              body="Pricing follows product maturity: validation, shared execution, then governance and integration support."
            />

            <Link href="/signup" className="inline-flex items-center gap-2 text-sm font-semibold text-[var(--primary-dark)]">
              Choose a plan
              <ArrowRight className="h-4 w-4" />
            </Link>
          </div>

          <div className="mt-10 overflow-x-auto">
            <div className="min-w-[760px] rounded-[32px] border border-[var(--border)] bg-[var(--surface)] shadow-[var(--shadow-sm)]">
              <div className="grid grid-cols-[1.15fr_repeat(3,minmax(0,1fr))] border-b border-[var(--border)]">
                <div className="px-5 py-4 text-sm font-semibold uppercase tracking-[0.18em] text-[var(--foreground-subtle)]">
                  Capability
                </div>
                {pricingTiers.map((tier) => (
                  <div
                    key={tier.name}
                    className={`px-5 py-4 text-sm font-semibold ${
                      tier.featured ? "bg-[var(--primary-subtle)] text-[var(--primary-dark)]" : "text-[var(--foreground)]"
                    }`}
                  >
                    {tier.name}
                  </div>
                ))}
              </div>

              {pricingComparison.map((row, rowIndex) => (
                <div
                  key={row.label}
                  className={`grid grid-cols-[1.15fr_repeat(3,minmax(0,1fr))] ${
                    rowIndex < pricingComparison.length - 1 ? "border-b border-[var(--border)]" : ""
                  }`}
                >
                  <div className="px-5 py-4 text-sm font-medium text-[var(--foreground)]">{row.label}</div>
                  {row.values.map((value, valueIndex) => (
                    <div
                      key={`${row.label}-${value}`}
                      className={`px-5 py-4 text-sm leading-6 ${
                        valueIndex === 1 ? "bg-[var(--primary-subtle)]/45 text-[var(--foreground)]" : "text-[var(--foreground-muted)]"
                      }`}
                    >
                      {value}
                    </div>
                  ))}
                </div>
              ))}
            </div>
          </div>
        </div>
      </section>

      <section className="px-4 py-16 sm:px-6 lg:px-8 lg:py-24">
        <div className="mx-auto max-w-7xl">
          <SectionHeading
            eyebrow="FAQ"
            title="Questions teams usually ask before they commit paper monitoring to a system."
            body="The answers are intentionally direct because the product is still in its early feature pipeline phase."
            align="center"
          />

          <div className="mt-12 grid gap-5 lg:grid-cols-2">
            {pricingFaqs.map((item) => (
              <div key={item.question} className="card rounded-[32px] p-6 sm:p-7">
                <h2 className="font-[family:var(--font-display)] text-3xl font-semibold tracking-tight text-[var(--foreground)]">
                  {item.question}
                </h2>
                <p className="mt-4 text-base leading-7 text-[var(--foreground-muted)]">{item.answer}</p>
              </div>
            ))}
          </div>
        </div>
      </section>

      <SignupCta
        title="Pick the workspace shape that fits your current research cadence."
        body="Free keeps the barrier low. Pro is the default self-serve setup. Enterprise closes the loop on governance, integrations, and support."
      />
    </main>
  );
}
