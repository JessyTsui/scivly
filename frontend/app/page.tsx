import Link from "next/link";
import {
  ArrowRight,
  BarChart3,
  Bell,
  BookOpen,
  BrainCircuit,
  CheckCircle2,
  ChevronRight,
  LineChart,
  MessagesSquare,
  Radar,
  Search,
  Send,
  Sparkles,
  Telescope,
  Zap,
} from "lucide-react";

import { SectionHeading } from "@/components/section-heading";
import { SiteFooter } from "@/components/site-footer";
import { SiteHeader } from "@/components/site-header";
import { productPillars, workflowSteps } from "@/lib/site-data";

const heroStats = [
  { label: "Sources monitored", value: "12k+", icon: Radar },
  { label: "Digest latency", value: "< 6 min", icon: Zap },
  { label: "Figure coverage", value: "84%", icon: LineChart },
];

const features = [
  {
    icon: Radar,
    title: "Signal over volume",
    description: "Watchlists, author graphs, and team-specific scoring keep the queue usable.",
  },
  {
    icon: BarChart3,
    title: "Operational visibility",
    description: "Intake, enrichment, delivery, and Q&A are measurable instead of hidden in scripts.",
  },
  {
    icon: MessagesSquare,
    title: "Evidence-grounded answers",
    description: "Follow-up questions stay attached to the paper, digest, and retrieval trail.",
  },
];

export default function HomePage() {
  return (
    <div className="min-h-screen">
      <SiteHeader />

      <main>
        {/* Hero Section */}
        <section className="relative overflow-hidden px-4 pt-16 pb-20 sm:px-6 lg:px-8 lg:pt-24 lg:pb-32">
          {/* Background gradient */}
          <div className="absolute inset-0 -z-10">
            <div className="absolute inset-0 bg-gradient-to-br from-[var(--primary-subtle)]/50 via-transparent to-transparent" />
            <div className="absolute top-0 right-0 h-[500px] w-[500px] bg-gradient-to-bl from-[var(--primary)]/5 to-transparent blur-3xl" />
          </div>

          <div className="mx-auto max-w-7xl">
            <div className="grid gap-12 lg:grid-cols-2 lg:gap-16 lg:items-center">
              {/* Left content */}
              <div className="animate-in">
                {/* Badge */}
                <div className="inline-flex items-center gap-2 rounded-full border border-[var(--border)] bg-white px-4 py-2 text-sm font-medium text-[var(--foreground-muted)] shadow-sm">
                  <Sparkles className="h-4 w-4 text-[var(--primary)]" />
                  <span>Now in open beta</span>
                </div>

                {/* Headline */}
                <h1 className="mt-6 font-[family:var(--font-display)] text-4xl font-semibold tracking-tight text-[var(--foreground)] sm:text-5xl lg:text-6xl">
                  Research intelligence for{" "}
                  <span className="gradient-text">fast-moving teams</span>
                </h1>

                {/* Description */}
                <p className="mt-6 max-w-xl text-lg leading-relaxed text-[var(--foreground-muted)]">
                  Scivly monitors papers, authors, and labs in real-time. Get translated briefings,
                  figure highlights, and keep every insight in one searchable workspace.
                </p>

                {/* CTA Buttons */}
                <div className="mt-8 flex flex-col gap-3 sm:flex-row">
                  <Link href="/docs" className="btn-primary justify-center text-base">
                    Get started
                    <ArrowRight className="h-4 w-4" />
                  </Link>
                  <Link
                    href="/admin"
                    className="btn-secondary justify-center text-base"
                  >
                    View demo
                  </Link>
                </div>

                {/* Stats */}
                <div className="mt-12 grid grid-cols-3 gap-6">
                  {heroStats.map((stat) => {
                    const Icon = stat.icon;
                    return (
                      <div key={stat.label}>
                        <div className="flex items-center gap-2 text-[var(--primary)]">
                          <Icon className="h-4 w-4" />
                        </div>
                        <p className="mt-2 font-[family:var(--font-display)] text-2xl font-semibold text-[var(--foreground)]">
                          {stat.value}
                        </p>
                        <p className="text-sm text-[var(--foreground-muted)]">{stat.label}</p>
                      </div>
                    );
                  })}
                </div>
              </div>

              {/* Right - Visual */}
              <div className="animate-in-delay-1 relative">
                <div className="card-dark relative overflow-hidden p-6 sm:p-8">
                  {/* Header */}
                  <div className="flex items-center justify-between">
                    <div className="flex items-center gap-3">
                      <div className="flex h-10 w-10 items-center justify-center rounded-xl bg-[var(--primary)]">
                        <BrainCircuit className="h-5 w-5 text-white" />
                      </div>
                      <div>
                        <p className="text-sm font-medium text-white">Research Pipeline</p>
                        <p className="text-xs text-slate-400">Live monitoring active</p>
                      </div>
                    </div>
                    <div className="flex items-center gap-2 rounded-full bg-[var(--success)]/20 px-3 py-1">
                      <div className="h-2 w-2 rounded-full bg-[var(--success)] animate-pulse" />
                      <span className="text-xs font-medium text-[var(--success)]">Online</span>
                    </div>
                  </div>

                  {/* Activity feed */}
                  <div className="mt-8 space-y-4">
                    {[
                      { icon: Search, text: "Found 3 new papers matching 'multimodal reasoning'", time: "2m ago" },
                      { icon: CheckCircle2, text: "Figure extraction completed for arXiv:2403.xxxx", time: "5m ago" },
                      { icon: Send, text: "Morning digest sent to 42 subscribers", time: "12m ago" },
                    ].map((item, i) => {
                      const Icon = item.icon;
                      return (
                        <div key={i} className="flex items-start gap-3 rounded-xl bg-white/5 p-3">
                          <div className="rounded-lg bg-white/10 p-2">
                            <Icon className="h-4 w-4 text-[var(--primary-light)]" />
                          </div>
                          <div className="flex-1 min-w-0">
                            <p className="text-sm text-slate-200 truncate">{item.text}</p>
                            <p className="text-xs text-slate-500 mt-0.5">{item.time}</p>
                          </div>
                        </div>
                      );
                    })}
                  </div>

                  {/* Progress bars */}
                  <div className="mt-6 space-y-4">
                    <div>
                      <div className="flex justify-between text-xs mb-2">
                        <span className="text-slate-400">Queue processing</span>
                        <span className="text-[var(--primary-light)]">78%</span>
                      </div>
                      <div className="h-2 rounded-full bg-white/10">
                        <div className="h-2 w-[78%] rounded-full bg-gradient-to-r from-[var(--primary)] to-[var(--primary-light)]" />
                      </div>
                    </div>
                    <div>
                      <div className="flex justify-between text-xs mb-2">
                        <span className="text-slate-400">Translation queue</span>
                        <span className="text-[var(--success)]">92%</span>
                      </div>
                      <div className="h-2 rounded-full bg-white/10">
                        <div className="h-2 w-[92%] rounded-full bg-[var(--success)]" />
                      </div>
                    </div>
                  </div>
                </div>

                {/* Floating card */}
                <div className="absolute -bottom-6 -left-6 hidden lg:block">
                  <div className="card p-4 shadow-xl">
                    <div className="flex items-center gap-3">
                      <div className="flex h-10 w-10 items-center justify-center rounded-xl bg-[var(--accent-subtle)]">
                        <Bell className="h-5 w-5 text-[var(--accent)]" />
                      </div>
                      <div>
                        <p className="text-sm font-medium">New match</p>
                        <p className="text-xs text-[var(--foreground-muted)]">Vision transformers</p>
                      </div>
                    </div>
                  </div>
                </div>
              </div>
            </div>
          </div>
        </section>

        {/* Features Section */}
        <section className="border-y border-[var(--border)] bg-[var(--surface-elevated)] px-4 py-16 sm:px-6 lg:px-8">
          <div className="mx-auto max-w-7xl">
            <div className="grid gap-8 md:grid-cols-3">
              {features.map((feature) => {
                const Icon = feature.icon;
                return (
                  <div key={feature.title} className="flex gap-4">
                    <div className="flex h-12 w-12 shrink-0 items-center justify-center rounded-xl bg-white shadow-sm">
                      <Icon className="h-6 w-6 text-[var(--primary)]" />
                    </div>
                    <div>
                      <h3 className="font-[family:var(--font-display)] text-lg font-semibold text-[var(--foreground)]">
                        {feature.title}
                      </h3>
                      <p className="mt-2 text-sm leading-relaxed text-[var(--foreground-muted)]">
                        {feature.description}
                      </p>
                    </div>
                  </div>
                );
              })}
            </div>
          </div>
        </section>

        {/* Product Pillars Section */}
        <section id="product" className="px-4 py-20 sm:px-6 lg:px-8 lg:py-28">
          <div className="mx-auto max-w-7xl">
            <SectionHeading
              eyebrow="Product"
              title="Everything you need to stay on top of research"
              body="From monitoring sources to delivering insights, Scivly handles the full paper lifecycle in one integrated platform."
              align="center"
            />

            <div className="mt-16 grid gap-6 md:grid-cols-2">
              {productPillars.map((pillar) => {
                const Icon = pillar.icon;
                return (
                  <div
                    key={pillar.title}
                    className="card card-hover p-6 sm:p-8"
                  >
                    <div className="flex items-start justify-between">
                      <div className="flex h-12 w-12 items-center justify-center rounded-xl bg-[var(--primary-subtle)]">
                        <Icon className="h-6 w-6 text-[var(--primary)]" />
                      </div>
                      <ChevronRight className="h-5 w-5 text-[var(--foreground-subtle)]" />
                    </div>
                    <h3 className="mt-6 font-[family:var(--font-display)] text-xl font-semibold text-[var(--foreground)]">
                      {pillar.title}
                    </h3>
                    <p className="mt-3 text-[var(--foreground-muted)] leading-relaxed">
                      {pillar.description}
                    </p>
                    <p className="mt-4 text-sm text-[var(--foreground-subtle)]">
                      {pillar.detail}
                    </p>
                  </div>
                );
              })}
            </div>
          </div>
        </section>

        {/* Workflow Section */}
        <section id="workflow" className="bg-[var(--surface-dark)] px-4 py-20 sm:px-6 lg:px-8 lg:py-28">
          <div className="mx-auto max-w-7xl">
            <SectionHeading
              eyebrow="How it works"
              title="From source to insight in four steps"
              body="Scivly structures your research workflow so nothing falls through the cracks."
              light
              align="center"
            />

            <div className="mt-16 grid gap-6 sm:grid-cols-2 lg:grid-cols-4">
              {workflowSteps.map((step, index) => (
                <div key={step.eyebrow} className="relative">
                  <div className="card-dark p-6 h-full">
                    <div className="flex items-center justify-between">
                      <span className="text-xs font-semibold uppercase tracking-wider text-[var(--primary-light)]">
                        {step.eyebrow}
                      </span>
                      <span className="flex h-6 w-6 items-center justify-center rounded-full bg-white/10 text-xs font-semibold text-white">
                        {index + 1}
                      </span>
                    </div>
                    <h3 className="mt-4 font-[family:var(--font-display)] text-lg font-semibold text-white">
                      {step.title}
                    </h3>
                    <p className="mt-3 text-sm leading-relaxed text-slate-400">
                      {step.description}
                    </p>
                  </div>
                  {index < workflowSteps.length - 1 && (
                    <div className="hidden lg:block absolute top-1/2 -right-3 transform -translate-y-1/2 z-10">
                      <ChevronRight className="h-5 w-5 text-slate-600" />
                    </div>
                  )}
                </div>
              ))}
            </div>
          </div>
        </section>

        {/* Docs & Admin Section */}
        <section className="px-4 py-20 sm:px-6 lg:px-8 lg:py-28">
          <div className="mx-auto max-w-7xl">
            <div className="grid gap-8 lg:grid-cols-2">
              {/* Documentation Card */}
              <div className="card p-8">
                <div className="flex items-center gap-3">
                  <div className="flex h-12 w-12 items-center justify-center rounded-xl bg-[var(--primary-subtle)]">
                    <BookOpen className="h-6 w-6 text-[var(--primary)]" />
                  </div>
                  <div>
                    <p className="text-sm font-medium text-[var(--primary)]">Documentation</p>
                    <h3 className="font-[family:var(--font-display)] text-2xl font-semibold text-[var(--foreground)]">
                      Get started in minutes
                    </h3>
                  </div>
                </div>

                <div className="mt-8 space-y-4">
                  {[
                    "Create your first watchlist",
                    "Connect paper sources",
                    "Configure digest delivery",
                    "Invite your team",
                  ].map((item, i) => (
                    <div key={i} className="flex items-center gap-3">
                      <div className="flex h-6 w-6 items-center justify-center rounded-full bg-[var(--primary-subtle)] text-xs font-semibold text-[var(--primary)]">
                        {i + 1}
                      </div>
                      <span className="text-[var(--foreground-muted)]">{item}</span>
                    </div>
                  ))}
                </div>

                <Link
                  href="/docs"
                  className="btn-primary mt-8"
                >
                  Read the docs
                  <ArrowRight className="h-4 w-4" />
                </Link>
              </div>

              {/* Admin Console Card */}
              <div className="card-dark p-8">
                <div className="flex items-center gap-3">
                  <div className="flex h-12 w-12 items-center justify-center rounded-xl bg-white/10">
                    <Telescope className="h-6 w-6 text-[var(--primary-light)]" />
                  </div>
                  <div>
                    <p className="text-sm font-medium text-[var(--primary-light)]">Admin Console</p>
                    <h3 className="font-[family:var(--font-display)] text-2xl font-semibold text-white">
                      Monitor operations
                    </h3>
                  </div>
                </div>

                <div className="mt-8 grid grid-cols-2 gap-4">
                  {[
                    { label: "Active monitors", value: "128" },
                    { label: "Papers today", value: "2.4k" },
                    { label: "Delivery rate", value: "99.2%" },
                    { label: "Avg latency", value: "4.2m" },
                  ].map((stat) => (
                    <div key={stat.label} className="rounded-xl bg-white/5 p-4">
                      <p className="text-xs text-slate-400">{stat.label}</p>
                      <p className="mt-1 font-[family:var(--font-display)] text-xl font-semibold text-white">
                        {stat.value}
                      </p>
                    </div>
                  ))}
                </div>

                <Link
                  href="/admin"
                  className="mt-8 inline-flex items-center gap-2 rounded-xl bg-white px-5 py-3 text-sm font-semibold text-[var(--surface-dark)] hover:bg-[var(--primary-light)] transition-colors"
                >
                  Open console
                  <ArrowRight className="h-4 w-4" />
                </Link>
              </div>
            </div>
          </div>
        </section>

        {/* CTA Section */}
        <section className="px-4 pb-20 sm:px-6 lg:px-8">
          <div className="mx-auto max-w-4xl">
            <div className="relative overflow-hidden rounded-2xl bg-gradient-to-br from-[var(--primary)] to-[var(--primary-dark)] px-8 py-16 text-center sm:px-16">
              <div className="hero-grid-overlay absolute inset-0 opacity-50" />
              <h2 className="relative font-[family:var(--font-display)] text-3xl font-semibold text-white sm:text-4xl">
                Ready to streamline your research?
              </h2>
              <p className="relative mx-auto mt-4 max-w-xl text-lg text-white/80">
                Join researchers who use Scivly to stay ahead of the literature.
              </p>
              <div className="relative mt-8 flex flex-col justify-center gap-3 sm:flex-row">
                <Link
                  href="/docs"
                  className="inline-flex items-center justify-center gap-2 rounded-xl bg-white px-6 py-3 text-base font-semibold text-[var(--primary)] hover:bg-white/90"
                >
                  Get started
                  <ArrowRight className="h-4 w-4" />
                </Link>
                <a
                  href="https://github.com/JessyTsui/scivly"
                  className="inline-flex items-center justify-center gap-2 rounded-xl border border-white/20 bg-white/10 px-6 py-3 text-base font-semibold text-white hover:bg-white/20"
                >
                  View on GitHub
                </a>
              </div>
            </div>
          </div>
        </section>
      </main>

      <SiteFooter />
    </div>
  );
}
