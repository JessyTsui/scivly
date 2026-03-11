import Link from "next/link";
import { ArrowRight, BookOpen, Code2, FileCode, Search, ShieldCheck } from "lucide-react";

import { SectionHeading } from "@/components/section-heading";
import { SiteFooter } from "@/components/site-footer";
import { SiteHeader } from "@/components/site-header";
import { apiReference, docCategories } from "@/lib/site-data";

const guideLinks = [
  "Create a workspace and add your first monitor",
  "Understand paper scoring and match reasons",
  "Generate a translated digest preview",
  "Route alerts into chat or webhooks",
];

export default function DocsPage() {
  return (
    <div className="min-h-screen bg-[var(--background)]">
      <SiteHeader />

      <main className="px-4 pb-16 pt-12 sm:px-6 lg:px-8 lg:pt-20">
        <div className="mx-auto max-w-7xl">
          {/* Hero Section */}
          <section className="grid gap-12 lg:grid-cols-2 lg:items-center">
            <div>
              <SectionHeading
                eyebrow="Documentation"
                title="Everything you need to get started"
                body="Comprehensive guides, API references, and examples to help you build with Scivly."
              />
              <div className="mt-8 flex flex-col gap-3 sm:flex-row">
                <Link
                  href="/docs/api"
                  className="btn-primary justify-center"
                >
                  API Reference
                  <ArrowRight className="h-4 w-4" />
                </Link>
                <Link
                  href="/admin"
                  className="btn-secondary justify-center"
                >
                  Open Console
                  <ShieldCheck className="h-4 w-4" />
                </Link>
              </div>
            </div>

            <div className="card p-6">
              <div className="flex items-center gap-3 mb-5">
                <Search className="h-5 w-5 text-[var(--foreground-subtle)]" />
                <span className="text-[var(--foreground-subtle)]">
                  Search documentation...
                </span>
              </div>
              <div className="grid gap-4 sm:grid-cols-2">
                <div className="rounded-xl bg-[var(--primary-subtle)]/50 p-5">
                  <p className="text-sm font-medium text-[var(--primary)]">Most read</p>
                  <p className="mt-2 font-[family:var(--font-display)] text-xl font-semibold text-[var(--foreground)]">
                    Monitor lifecycle
                  </p>
                  <p className="mt-2 text-sm text-[var(--foreground-muted)]">
                    Learn how matching, scoring, enrichment, and delivery fit together.
                  </p>
                </div>
                <div className="rounded-xl bg-white border border-[var(--border)] p-5">
                  <p className="text-sm font-medium text-[var(--accent)]">Recently updated</p>
                  <p className="mt-2 font-[family:var(--font-display)] text-xl font-semibold text-[var(--foreground)]">
                    Webhook retries
                  </p>
                  <p className="mt-2 text-sm text-[var(--foreground-muted)]">
                    Delivery replay, status checks, and idempotency behavior.
                  </p>
                </div>
              </div>
            </div>
          </section>

          {/* Categories */}
          <section className="mt-16 grid gap-6 md:grid-cols-3">
            {docCategories.map((category) => (
              <Link
                key={category.title}
                href={category.href}
                className="card card-hover p-6 group"
              >
                <p className="text-sm font-semibold text-[var(--primary)]">
                  {category.eyebrow}
                </p>
                <h2 className="mt-3 font-[family:var(--font-display)] text-xl font-semibold text-[var(--foreground)]">
                  {category.title}
                </h2>
                <ul className="mt-4 space-y-2">
                  {category.points.map((point) => (
                    <li key={point} className="flex items-start gap-2 text-sm text-[var(--foreground-muted)]">
                      <span className="mt-1.5 h-1.5 w-1.5 rounded-full bg-[var(--primary)]" />
                      <span>{point}</span>
                    </li>
                  ))}
                </ul>
                <span className="mt-6 inline-flex items-center gap-2 text-sm font-medium text-[var(--foreground)]">
                  Read more
                  <ArrowRight className="h-4 w-4 transition-transform group-hover:translate-x-1" />
                </span>
              </Link>
            ))}
          </section>

          {/* Guides & API */}
          <section className="mt-16 grid gap-8 lg:grid-cols-2">
            <div className="card p-6">
              <div className="flex items-center gap-3">
                <div className="flex h-10 w-10 items-center justify-center rounded-xl bg-[var(--primary-subtle)]">
                  <BookOpen className="h-5 w-5 text-[var(--primary)]" />
                </div>
                <h2 className="font-[family:var(--font-display)] text-2xl font-semibold text-[var(--foreground)]">
                  Popular guides
                </h2>
              </div>
              <div className="mt-6 space-y-3">
                {guideLinks.map((guide, index) => (
                  <div
                    key={guide}
                    className="flex items-center gap-3 rounded-xl bg-[var(--surface-elevated)] px-4 py-3"
                  >
                    <div className="flex h-8 w-8 items-center justify-center rounded-lg bg-[var(--primary-subtle)] text-sm font-semibold text-[var(--primary)]">
                      {index + 1}
                    </div>
                    <p className="text-sm font-medium text-[var(--foreground)]">{guide}</p>
                  </div>
                ))}
              </div>
            </div>

            <div className="card-dark p-6">
              <div className="flex items-center gap-3">
                <div className="flex h-10 w-10 items-center justify-center rounded-xl bg-white/10">
                  <Code2 className="h-5 w-5 text-[var(--primary-light)]" />
                </div>
                <h2 className="font-[family:var(--font-display)] text-2xl font-semibold text-white">
                  API Reference
                </h2>
              </div>
              <div className="mt-6 space-y-3">
                {apiReference.map((item) => (
                  <div
                    key={item.route}
                    className="rounded-xl bg-white/5 p-4"
                  >
                    <div className="flex items-center gap-2">
                      <span className="rounded-md bg-[var(--primary)]/20 px-2 py-0.5 text-xs font-semibold text-[var(--primary-light)]">
                        {item.method}
                      </span>
                      <code className="font-[family:var(--font-mono)] text-sm text-white">
                        {item.route}
                      </code>
                    </div>
                    <p className="mt-2 text-sm text-slate-400">{item.summary}</p>
                  </div>
                ))}
              </div>
              <div className="mt-4 rounded-xl border border-white/10 bg-white/5 p-4">
                <div className="flex items-center gap-2">
                  <FileCode className="h-4 w-4 text-[var(--primary-light)]" />
                  <p className="text-sm font-medium text-white">Example request</p>
                </div>
                <pre className="mt-3 overflow-x-auto font-[family:var(--font-mono)] text-xs leading-5 text-slate-300">
                  <code>{`POST /v1/questions
{
  "workspace_id": "ws_research",
  "paper_id": "paper_1024",
  "question": "What changed?"
}`}</code>
                </pre>
              </div>
            </div>
          </section>
        </div>
      </main>

      <SiteFooter />
    </div>
  );
}
