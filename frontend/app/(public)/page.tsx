import Link from "next/link";
import {
  ArrowRight,
  BrainCircuit,
  ChevronRight,
  Globe2,
  Send,
} from "lucide-react";

import { PricingCard } from "@/components/pricing-card";
import { SectionHeading } from "@/components/section-heading";
import { SignupCta } from "@/components/signup-cta";
import { audienceCards, heroStats, pipelineChapters, pricingTiers, problemCards } from "@/lib/public-site";
import { createMetadata } from "@/lib/metadata";

export const metadata = createMetadata({
  title: "Research Intelligence for Fast-Moving Teams",
  description:
    "Track papers, translate signal, and route research insight through digests, workspaces, and developer surfaces with Scivly.",
  path: "/",
});

const liveQueue = [
  { state: "syncing", title: "New multimodal agents paper landed", detail: "Matched by workspace topic rules", icon: Globe2 },
  { state: "matched", title: "Digest candidate scored 0.94", detail: "Queued for translation and figure extraction", icon: BrainCircuit },
  { state: "delivered", title: "Morning brief sent to the team", detail: "Workspace feed, digest, and admin log all updated", icon: Send },
];

export default function LandingPage() {
  return (
    <main>
      <section className="px-4 pb-20 pt-12 sm:px-6 lg:px-8 lg:pb-24 lg:pt-20">
        <div className="mx-auto grid max-w-7xl gap-12 lg:grid-cols-[1.03fr_0.97fr] lg:items-start">
          <div className="animate-in">
            <div className="inline-flex items-center gap-2 rounded-full border border-[var(--border)] bg-[var(--surface)]/88 px-4 py-2 text-sm font-medium text-[var(--foreground-muted)] shadow-[var(--shadow-sm)] backdrop-blur">
              <span className="h-2.5 w-2.5 rounded-full bg-[var(--accent)]" />
              Open-source multi-tenant paper intelligence
            </div>

            <h1 className="mt-7 max-w-4xl font-[family:var(--font-display)] text-5xl font-semibold tracking-[-0.06em] text-[var(--foreground)] sm:text-6xl lg:text-[6.25rem] lg:leading-[0.92]">
              The paper intelligence layer for teams that cannot miss the next paper.
            </h1>

            <p className="mt-6 max-w-2xl text-lg leading-8 text-[var(--foreground-muted)] sm:text-xl">
              Scivly monitors research sources, scores relevance, translates the signal, and keeps
              every digest, question, and delivery step attached to source evidence.
            </p>

            <div className="mt-8 flex flex-col gap-3 sm:flex-row">
              <Link href="/signup" className="btn-primary justify-center text-base">
                Start free workspace
                <ArrowRight className="h-4 w-4" />
              </Link>
              <Link href="/pricing" className="btn-secondary justify-center text-base">
                Explore pricing
              </Link>
            </div>

            <div className="mt-12 grid gap-5 sm:grid-cols-3">
              {heroStats.map((stat) => (
                <div key={stat.label} className="border-l border-[var(--border-strong)] pl-4">
                  <p className="font-[family:var(--font-display)] text-3xl font-semibold tracking-tight text-[var(--foreground)]">
                    {stat.value}
                  </p>
                  <p className="mt-2 text-sm leading-6 text-[var(--foreground-muted)]">{stat.label}</p>
                </div>
              ))}
            </div>
          </div>

          <div className="animate-in-delay-1 lg:pt-5">
            <div className="card relative overflow-hidden rounded-[36px] p-6 sm:p-8">
              <div className="absolute inset-x-0 top-0 h-40 bg-[radial-gradient(circle_at_top,rgba(14,165,233,0.18),transparent_70%)]" />
              <div className="relative">
                <div className="flex items-center justify-between gap-3">
                  <div>
                    <p className="text-sm font-semibold uppercase tracking-[0.22em] text-[var(--primary)]">
                      Live pipeline
                    </p>
                    <h2 className="mt-3 font-[family:var(--font-display)] text-3xl font-semibold tracking-tight">
                      Story-led product surface
                    </h2>
                  </div>
                  <div className="rounded-full bg-[var(--surface-elevated)] px-3 py-1 text-xs font-semibold uppercase tracking-[0.18em] text-[var(--foreground-subtle)]">
                    public
                  </div>
                </div>

                <div className="mt-8 space-y-4">
                  {liveQueue.map((item) => {
                    const Icon = item.icon;

                    return (
                      <div key={item.title} className="flex gap-4 rounded-[28px] border border-[var(--border)] bg-[var(--surface)]/92 p-4 shadow-[var(--shadow-sm)]">
                        <div className="flex h-12 w-12 shrink-0 items-center justify-center rounded-2xl bg-[var(--primary-subtle)] text-[var(--primary-dark)]">
                          <Icon className="h-5 w-5" />
                        </div>
                        <div className="min-w-0">
                          <p className="text-xs font-semibold uppercase tracking-[0.2em] text-[var(--foreground-subtle)]">
                            {item.state}
                          </p>
                          <p className="mt-2 text-base font-medium text-[var(--foreground)]">
                            {item.title}
                          </p>
                          <p className="mt-1 text-sm leading-6 text-[var(--foreground-muted)]">
                            {item.detail}
                          </p>
                        </div>
                      </div>
                    );
                  })}
                </div>

                <div className="mt-8 grid gap-4 sm:grid-cols-2">
                  <div className="rounded-[28px] bg-[var(--surface-dark)] p-5 text-white shadow-[var(--shadow-lg)]">
                    <p className="text-xs font-semibold uppercase tracking-[0.22em] text-sky-200">
                      Why it matters
                    </p>
                    <p className="mt-3 font-[family:var(--font-display)] text-2xl font-semibold tracking-tight">
                      Digests, questions, and operator actions all read from one graph.
                    </p>
                  </div>

                  <div className="rounded-[28px] border border-dashed border-[var(--border-strong)] bg-[var(--surface-elevated)]/75 p-5">
                    <p className="text-xs font-semibold uppercase tracking-[0.22em] text-[var(--foreground-subtle)]">
                      Product boundary
                    </p>
                    <p className="mt-3 text-sm leading-7 text-[var(--foreground-muted)]">
                      Public pages explain the system clearly. Workspace and operator surfaces keep
                      the execution trace visible after signup.
                    </p>
                  </div>
                </div>
              </div>
            </div>
          </div>
        </div>
      </section>

      <section id="story" className="border-y border-[var(--border)] bg-[var(--surface)]/72 px-4 py-20 sm:px-6 lg:px-8 lg:py-24">
        <div className="mx-auto max-w-7xl">
          <SectionHeading
            eyebrow="The Problem"
            title="Research teams do not need more tabs, more alerts, or more unstructured PDFs."
            body="Scivly is designed to turn a volatile paper stream into a monitored, explainable, and shareable operating loop."
            align="center"
          />

          <div className="mt-14 grid gap-5 lg:grid-cols-3">
            {problemCards.map((card) => {
              const Icon = card.icon;

              return (
                <div key={card.title} className="card card-hover rounded-[32px] p-6 sm:p-7">
                  <div className="flex items-center justify-between">
                    <div className="flex h-12 w-12 items-center justify-center rounded-2xl bg-[var(--primary-subtle)] text-[var(--primary-dark)]">
                      <Icon className="h-5 w-5" />
                    </div>
                    <span className="text-xs font-semibold uppercase tracking-[0.22em] text-[var(--foreground-subtle)]">
                      {card.eyebrow}
                    </span>
                  </div>
                  <h2 className="mt-6 font-[family:var(--font-display)] text-3xl font-semibold tracking-tight text-[var(--foreground)]">
                    {card.title}
                  </h2>
                  <p className="mt-4 text-base leading-7 text-[var(--foreground-muted)]">
                    {card.description}
                  </p>
                </div>
              );
            })}
          </div>
        </div>
      </section>

      <section className="px-4 py-20 sm:px-6 lg:px-8 lg:py-24">
        <div className="mx-auto max-w-7xl">
          <SectionHeading
            eyebrow="Four Chapters"
            title="Scroll through the workflow the same way the platform processes research."
            body="The public site mirrors the system design: intake, triage, enrichment, and delivery are explicit product surfaces, not implementation accidents."
          />

          <div className="mt-14 grid gap-5 xl:grid-cols-2">
            {pipelineChapters.map((chapter) => (
              <div key={chapter.phase} className="card rounded-[32px] p-6 sm:p-7">
                <div className="flex items-center justify-between gap-3">
                  <span className="text-xs font-semibold uppercase tracking-[0.24em] text-[var(--primary)]">
                    {chapter.phase}
                  </span>
                  <ChevronRight className="h-4 w-4 text-[var(--foreground-subtle)]" />
                </div>
                <h2 className="mt-4 font-[family:var(--font-display)] text-3xl font-semibold tracking-tight text-[var(--foreground)]">
                  {chapter.title}
                </h2>
                <p className="mt-4 text-base leading-7 text-[var(--foreground-muted)]">
                  {chapter.description}
                </p>

                <ul className="mt-6 grid gap-3 sm:grid-cols-3">
                  {chapter.bullets.map((bullet) => (
                    <li
                      key={bullet}
                      className="rounded-2xl border border-[var(--border)] bg-[var(--surface-hover)] px-4 py-3 text-sm font-medium text-[var(--foreground)]"
                    >
                      {bullet}
                    </li>
                  ))}
                </ul>
              </div>
            ))}
          </div>
        </div>
      </section>

      <section className="border-y border-[var(--border)] bg-[var(--surface-dark)] px-4 py-20 sm:px-6 lg:px-8 lg:py-24">
        <div className="mx-auto grid max-w-7xl gap-10 xl:grid-cols-[0.92fr_1.08fr]">
          <SectionHeading
            eyebrow="Who It Is For"
            title="Built for the teams that treat literature review like an operating discipline."
            body="Scivly fits founders, labs, and developer-facing teams that need more than a search box and less than a pile of scripts."
            light
          />

          <div className="grid gap-5 md:grid-cols-3">
            {audienceCards.map((card) => {
              const Icon = card.icon;

              return (
                <div key={card.title} className="card-dark rounded-[32px] p-6">
                  <div className="flex h-12 w-12 items-center justify-center rounded-2xl bg-white/10 text-sky-200">
                    <Icon className="h-5 w-5" />
                  </div>
                  <h2 className="mt-6 font-[family:var(--font-display)] text-2xl font-semibold tracking-tight text-white">
                    {card.title}
                  </h2>
                  <p className="mt-4 text-sm leading-7 text-slate-300">{card.description}</p>
                </div>
              );
            })}
          </div>
        </div>
      </section>

      <section className="px-4 py-20 sm:px-6 lg:px-8 lg:py-24">
        <div className="mx-auto max-w-7xl">
          <div className="flex flex-col gap-5 lg:flex-row lg:items-end lg:justify-between">
            <SectionHeading
              eyebrow="Pricing Preview"
              title="Choose a plan that matches how much research coordination your team needs."
              body="The public pricing surface is simple on purpose: start free, move to a shared workspace, then add governance when the system becomes critical."
            />

            <Link href="/pricing" className="inline-flex items-center gap-2 text-sm font-semibold text-[var(--primary-dark)]">
              View full pricing
              <ArrowRight className="h-4 w-4" />
            </Link>
          </div>

          <div className="mt-12 grid gap-5 xl:grid-cols-3">
            {pricingTiers.map((tier) => (
              <PricingCard key={tier.name} tier={tier} compact />
            ))}
          </div>
        </div>
      </section>

      <SignupCta
        title="Start with the public surface, then move into a real workspace."
        body="The landing site now explains the product clearly. The next step is stepping into a workspace where monitors, digests, and questions stay connected."
        secondaryHref="/workspace/feed"
        secondaryLabel="Preview workspace"
      />
    </main>
  );
}
