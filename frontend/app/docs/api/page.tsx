import Link from "next/link";
import { ArrowLeft, ArrowRight, KeyRound, ServerCog, Zap } from "lucide-react";

import { SectionHeading } from "@/components/section-heading";
import { SiteFooter } from "@/components/site-footer";
import { SiteHeader } from "@/components/site-header";
import { apiReference } from "@/lib/site-data";

const authSteps = [
  "Issue workspace-scoped API keys for backend services and operator tooling.",
  "Attach monitor, digest, and question actions to the same workspace context.",
  "Replay failed deliveries with idempotency keys instead of one-off scripts.",
];

const curlExample = `curl -X POST https://api.scivly.dev/v1/monitors \\
  -H "Authorization: Bearer scivly_test_key" \\
  -H "Content-Type: application/json" \\
  -d '{
    "workspace_id": "ws_research",
    "name": "agent-benchmarks",
    "filters": {
      "topics": ["agents", "retrieval", "multimodal reasoning"],
      "authors": ["Research Lab A", "Research Lab B"]
    }
  }'`;

const webhookExample = `{
  "event": "digest.delivered",
  "workspace_id": "ws_research",
  "digest_id": "digest_2403",
  "status": "sent",
  "paper_count": 12,
  "matched_monitors": ["agent-benchmarks", "vision-reasoning"]
}`;

export default function ApiReferencePage() {
  return (
    <div>
      <SiteHeader />

      <main className="px-4 pb-12 pt-10 sm:px-6 lg:px-8 lg:pt-16">
        <div className="mx-auto max-w-7xl">
          <section className="grid gap-10 lg:grid-cols-[0.92fr_1.08fr]">
            <div>
              <Link
                href="/docs"
                className="inline-flex items-center gap-2 rounded-full border border-[var(--line)] bg-white/70 px-4 py-2 text-sm font-semibold text-[var(--ink)] hover:bg-white focus-visible:outline focus-visible:outline-2 focus-visible:outline-offset-4 focus-visible:outline-[var(--accent)]"
              >
                <ArrowLeft className="h-4 w-4" />
                Back to docs
              </Link>
              <div className="mt-6">
                <SectionHeading
                  eyebrow="API reference"
                  title="A thin API surface for monitors, digests, questions, and delivery hooks."
                  body="The public API is intentionally narrow. It exposes the monitor lifecycle, search, digest orchestration, and evidence-aware questions without leaking internal pipeline mechanics."
                />
              </div>
            </div>

            <div className="rounded-[32px] p-[1px] dark-panel">
              <div className="rounded-[31px] p-6 sm:p-8">
                <div className="grid gap-4 sm:grid-cols-3">
                  <div className="rounded-[24px] border border-white/10 bg-white/[0.06] p-5">
                    <KeyRound className="h-5 w-5 text-[var(--accent-bright)]" />
                    <p className="mt-4 text-sm font-semibold text-white">Auth</p>
                    <p className="mt-2 text-sm leading-6 text-slate-300">
                      Workspace-scoped bearer keys for platform and self-hosted flows.
                    </p>
                  </div>
                  <div className="rounded-[24px] border border-white/10 bg-white/[0.06] p-5">
                    <ServerCog className="h-5 w-5 text-sky-300" />
                    <p className="mt-4 text-sm font-semibold text-white">Webhook-safe</p>
                    <p className="mt-2 text-sm leading-6 text-slate-300">
                      Delivery events carry deterministic ids for retries and replays.
                    </p>
                  </div>
                  <div className="rounded-[24px] border border-white/10 bg-white/[0.06] p-5">
                    <Zap className="h-5 w-5 text-orange-300" />
                    <p className="mt-4 text-sm font-semibold text-white">Low ceremony</p>
                    <p className="mt-2 text-sm leading-6 text-slate-300">
                      A small endpoint surface is easier to maintain across product phases.
                    </p>
                  </div>
                </div>

                <div className="mt-8 rounded-[24px] border border-white/10 bg-[rgba(5,10,20,0.5)] p-5">
                  <p className="text-sm font-semibold text-white">Create a monitor</p>
                  <pre className="mt-4 overflow-x-auto font-[family:var(--font-mono)] text-sm leading-7 text-slate-300">
                    <code>{curlExample}</code>
                  </pre>
                </div>
              </div>
            </div>
          </section>

          <section className="mt-16 grid gap-6 xl:grid-cols-[0.88fr_1.12fr]">
            <div className="glass-panel rounded-[32px] p-6 sm:p-8">
              <p className="text-sm font-semibold uppercase tracking-[0.24em] text-[var(--accent-strong)]">
                Authentication flow
              </p>
              <div className="mt-6 space-y-4">
                {authSteps.map((step, index) => (
                  <div key={step} className="flex gap-4 rounded-[24px] border border-[var(--line)] bg-white/70 p-5">
                    <div className="flex h-10 w-10 shrink-0 items-center justify-center rounded-full bg-[rgba(15,118,110,0.08)] text-sm font-semibold text-[var(--accent)]">
                      {index + 1}
                    </div>
                    <p className="text-sm leading-7 text-[var(--ink-soft)]">{step}</p>
                  </div>
                ))}
              </div>
            </div>

            <div className="glass-panel rounded-[32px] p-6 sm:p-8">
              <p className="text-sm font-semibold uppercase tracking-[0.24em] text-[var(--accent-strong)]">
                Endpoint reference
              </p>
              <div className="mt-6 space-y-4">
                {apiReference.map((item) => (
                  <div
                    key={item.route}
                    className="rounded-[24px] border border-[var(--line)] bg-white/70 p-5"
                  >
                    <div className="flex flex-wrap items-center gap-3">
                      <span className="rounded-full bg-[rgba(15,118,110,0.08)] px-3 py-1 text-xs font-semibold text-[var(--accent-strong)]">
                        {item.method}
                      </span>
                      <code className="font-[family:var(--font-mono)] text-sm text-[var(--ink)]">
                        {item.route}
                      </code>
                    </div>
                    <p className="mt-4 text-sm leading-6 text-[var(--ink-soft)]">{item.summary}</p>
                  </div>
                ))}
              </div>
            </div>
          </section>

          <section className="mt-16 grid gap-6 xl:grid-cols-[1.08fr_0.92fr]">
            <div className="glass-panel rounded-[32px] p-6 sm:p-8">
              <p className="text-sm font-semibold uppercase tracking-[0.24em] text-[var(--accent-strong)]">
                Webhook payload
              </p>
              <pre className="mt-4 overflow-x-auto rounded-[24px] bg-[var(--ink)] p-5 font-[family:var(--font-mono)] text-sm leading-7 text-slate-200">
                <code>{webhookExample}</code>
              </pre>
            </div>

            <div className="rounded-[32px] border border-[var(--line)] bg-[rgba(255,255,255,0.72)] p-6 sm:p-8">
              <p className="text-sm font-semibold uppercase tracking-[0.24em] text-[var(--accent-coral)]">
                Next step
              </p>
              <h2 className="mt-4 font-[family:var(--font-display)] text-3xl font-semibold">
                Pair the API with the admin surface.
              </h2>
              <p className="mt-4 text-base leading-7 text-[var(--ink-soft)]">
                The API is intentionally small; most operational confidence comes from seeing monitor
                state, queue health, digest runs, and webhook behavior in one admin console.
              </p>
              <Link
                href="/admin"
                className="mt-8 inline-flex items-center gap-2 rounded-full bg-[var(--ink)] px-5 py-3 text-sm font-semibold text-white hover:-translate-y-0.5 hover:bg-[var(--surface-dark-soft)] focus-visible:outline focus-visible:outline-2 focus-visible:outline-offset-4 focus-visible:outline-[var(--accent)]"
              >
                Open admin console
                <ArrowRight className="h-4 w-4" />
              </Link>
            </div>
          </section>
        </div>
      </main>

      <SiteFooter />
    </div>
  );
}
