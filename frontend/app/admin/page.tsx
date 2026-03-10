import Link from "next/link";
import {
  Activity,
  ArrowRight,
  BookOpen,
  CheckCircle2,
  FileQuestion,
  FileText,
  MessagesSquare,
  Newspaper,
  Radar,
  RefreshCw,
  Sparkles,
  Telescope,
  TrendingUp,
  Zap,
} from "lucide-react";

const toneStyles = {
  primary: "bg-[var(--primary-subtle)] text-[var(--primary)]",
  success: "bg-[var(--success)]/12 text-[var(--success)]",
  warning: "bg-[var(--warning)]/12 text-[var(--warning)]",
  accent: "bg-[var(--accent-subtle)] text-[var(--accent)]",
};

const quickStats = [
  {
    label: "Active monitors",
    value: "12",
    detail: "+2 this week",
    icon: Radar,
    tone: "primary" as const,
  },
  {
    label: "Papers triaged",
    value: "48",
    detail: "83% auto-scored",
    icon: BookOpen,
    tone: "success" as const,
  },
  {
    label: "Digests scheduled",
    value: "7",
    detail: "Next send at 09:00",
    icon: Newspaper,
    tone: "warning" as const,
  },
  {
    label: "Open questions",
    value: "8",
    detail: "2 need manual review",
    icon: FileQuestion,
    tone: "accent" as const,
  },
];

const pipelineStatus = [
  { stage: "Intake", count: "12", detail: "8 sources healthy", status: "Healthy" },
  { stage: "Enrichment", count: "5", detail: "2 figure jobs running", status: "Processing" },
  { stage: "Routing", count: "3", detail: "1 digest waiting review", status: "Attention" },
  { stage: "Q&A", count: "14", detail: "Avg confidence 0.89", status: "Healthy" },
];

const recentPapers = [
  {
    title: "Segmented reasoning for multimodal agents",
    source: "arXiv · cs.AI",
    matchedBy: "Vision-Language track",
    score: "0.96",
    status: "Ready for digest",
    time: "12m ago",
  },
  {
    title: "Self-refining retrieval for scientific QA",
    source: "arXiv · cs.CL",
    matchedBy: "Scientific QA monitor",
    score: "0.92",
    status: "Waiting for figure parse",
    time: "35m ago",
  },
  {
    title: "Efficient adapters for long-context analysis",
    source: "arXiv · cs.LG",
    matchedBy: "Long-context lab list",
    score: "0.88",
    status: "Queued for translation",
    time: "58m ago",
  },
  {
    title: "Benchmarking grounded review generation",
    source: "OpenReview · NLP",
    matchedBy: "Digest QA benchmarks",
    score: "0.84",
    status: "Needs operator review",
    time: "1h ago",
  },
];

const recentActivity = [
  {
    icon: CheckCircle2,
    title: "Morning digest delivered",
    detail: "Sent to founders channel and email list.",
    time: "09:00",
  },
  {
    icon: RefreshCw,
    title: "Retry recovered 3 failed notifications",
    detail: "Webhook replay cleared the delivery backlog.",
    time: "08:42",
  },
  {
    icon: MessagesSquare,
    title: "Operator answered a paper follow-up",
    detail: "Response attached to the RAG systems digest.",
    time: "08:15",
  },
];

const activeMonitors = [
  { name: "NLP Research", source: "arXiv cs.CL", papers: "156", freshness: "2h ago" },
  { name: "AI Benchmarks", source: "arXiv cs.AI", papers: "89", freshness: "5h ago" },
  { name: "Vision-Language", source: "arXiv cs.CV", papers: "67", freshness: "8h ago" },
];

const actions = [
  {
    title: "Create a monitor",
    detail: "Track a new topic, lab, or author graph.",
    href: "/admin/monitors",
    icon: Radar,
    tone: "primary" as const,
  },
  {
    title: "Preview digest",
    detail: "Check what the next briefing will actually ship.",
    href: "/admin/digests",
    icon: Sparkles,
    tone: "warning" as const,
  },
  {
    title: "Ask a follow-up",
    detail: "Keep evidence and answer history attached to papers.",
    href: "/admin/qa",
    icon: Telescope,
    tone: "accent" as const,
  },
];

function statusTone(status: string) {
  if (status === "Healthy") {
    return "bg-[var(--success)]/12 text-[var(--success)]";
  }

  if (status === "Processing") {
    return "bg-[var(--warning)]/12 text-[var(--warning)]";
  }

  return "bg-[var(--accent-subtle)] text-[var(--accent)]";
}

function queueTone(status: string) {
  if (status.includes("Ready")) {
    return "bg-[var(--success)]/12 text-[var(--success)]";
  }

  if (status.includes("Waiting") || status.includes("Queued")) {
    return "bg-[var(--warning)]/12 text-[var(--warning)]";
  }

  return "bg-[var(--accent-subtle)] text-[var(--accent)]";
}

export default function AdminDashboard() {
  return (
    <div className="space-y-6">
      <section className="grid gap-6 xl:grid-cols-[minmax(0,1.5fr)_minmax(320px,0.9fr)]">
        <div className="card relative overflow-hidden p-6 sm:p-7">
          <div className="absolute inset-x-0 top-0 h-px bg-gradient-to-r from-transparent via-[var(--primary)]/45 to-transparent" />
          <div className="flex flex-col gap-6 lg:flex-row lg:items-start lg:justify-between">
            <div className="max-w-2xl">
              <div className="inline-flex items-center gap-2 rounded-full bg-[var(--primary-subtle)] px-3 py-1 text-xs font-semibold uppercase tracking-[0.22em] text-[var(--primary)]">
                <TrendingUp className="h-3.5 w-3.5" />
                Ops snapshot
              </div>
              <h2 className="mt-4 font-[family:var(--font-display)] text-3xl font-semibold tracking-tight">
                Research operations should feel like one control room.
              </h2>
              <p className="mt-4 max-w-xl text-sm leading-7 text-[var(--foreground-muted)] sm:text-base">
                Intake, translation, digest delivery, and paper follow-up are all moving. The
                dashboard now surfaces what changed, what is blocked, and what needs operator attention.
              </p>
            </div>

            <div className="grid gap-3 sm:grid-cols-2 lg:w-[300px] lg:grid-cols-1">
              <Link href="/admin/pipeline" className="btn-primary justify-center text-sm">
                View pipeline
                <ArrowRight className="h-4 w-4" />
              </Link>
              <Link href="/admin/papers" className="btn-secondary justify-center text-sm">
                Review latest papers
              </Link>
            </div>
          </div>

          <div className="mt-7 grid gap-4 md:grid-cols-3">
            <div className="rounded-2xl border border-[var(--border)] bg-[var(--surface-hover)]/75 p-4">
              <div className="flex items-center gap-2 text-sm font-medium text-[var(--foreground-muted)]">
                <Zap className="h-4 w-4 text-[var(--primary)]" />
                Queue freshness
              </div>
              <p className="mt-3 font-[family:var(--font-display)] text-2xl font-semibold">6 min</p>
              <p className="mt-1 text-sm text-[var(--foreground-subtle)]">
                Median time from match to digest-ready summary.
              </p>
            </div>

            <div className="rounded-2xl border border-[var(--border)] bg-[var(--surface-hover)]/75 p-4">
              <div className="flex items-center gap-2 text-sm font-medium text-[var(--foreground-muted)]">
                <Activity className="h-4 w-4 text-[var(--success)]" />
                Delivery confidence
              </div>
              <p className="mt-3 font-[family:var(--font-display)] text-2xl font-semibold">99.2%</p>
              <p className="mt-1 text-sm text-[var(--foreground-subtle)]">
                Only 3 retries are still pending across all channels.
              </p>
            </div>

            <div className="rounded-2xl border border-[var(--border)] bg-[var(--surface-hover)]/75 p-4">
              <div className="flex items-center gap-2 text-sm font-medium text-[var(--foreground-muted)]">
                <Sparkles className="h-4 w-4 text-[var(--accent)]" />
                Coverage
              </div>
              <p className="mt-3 font-[family:var(--font-display)] text-2xl font-semibold">84%</p>
              <p className="mt-1 text-sm text-[var(--foreground-subtle)]">
                Figure extraction completed for the top-scoring papers today.
              </p>
            </div>
          </div>
        </div>

        <div className="card-dark p-6">
          <div className="flex items-center justify-between">
            <div>
              <p className="text-sm font-medium text-[var(--primary-light)]">Live activity</p>
              <h3 className="mt-1 font-[family:var(--font-display)] text-2xl font-semibold text-white">
                What changed this morning
              </h3>
            </div>
            <span className="inline-flex items-center gap-2 rounded-full bg-[var(--success)]/12 px-3 py-1 text-xs font-medium text-[var(--success)]">
              <span className="h-2 w-2 rounded-full bg-[var(--success)] animate-pulse" />
              Healthy
            </span>
          </div>

          <div className="mt-6 space-y-3">
            {recentActivity.map((item) => {
              const Icon = item.icon;

              return (
                <div key={item.title} className="rounded-2xl border border-white/[0.08] bg-white/[0.06] p-4">
                  <div className="flex items-start gap-3">
                    <div className="rounded-xl bg-white/10 p-2">
                      <Icon className="h-4 w-4 text-[var(--primary-light)]" />
                    </div>
                    <div className="min-w-0 flex-1">
                      <div className="flex items-start justify-between gap-3">
                        <p className="text-sm font-medium text-white">{item.title}</p>
                        <span className="shrink-0 text-xs text-slate-400">{item.time}</span>
                      </div>
                      <p className="mt-1 text-sm leading-6 text-slate-300">{item.detail}</p>
                    </div>
                  </div>
                </div>
              );
            })}
          </div>

          <div className="mt-6 rounded-2xl border border-white/[0.08] bg-white/[0.06] p-4">
            <div className="flex items-center justify-between">
              <div>
                <p className="text-sm font-medium text-white">Next scheduled digest</p>
                <p className="mt-1 text-sm text-slate-300">Asia research roundup at 09:00 UTC+8</p>
              </div>
              <Link
                href="/admin/digests"
                className="inline-flex items-center gap-1 text-sm font-medium text-[var(--primary-light)]"
              >
                Preview
                <ArrowRight className="h-4 w-4" />
              </Link>
            </div>
          </div>
        </div>
      </section>

      <section className="grid gap-4 sm:grid-cols-2 xl:grid-cols-4">
        {quickStats.map((stat) => {
          const Icon = stat.icon;

          return (
            <div key={stat.label} className="card p-5">
              <div className="flex items-start justify-between gap-4">
                <div>
                  <p className="text-sm font-medium text-[var(--foreground-muted)]">{stat.label}</p>
                  <p className="mt-3 font-[family:var(--font-display)] text-3xl font-semibold">
                    {stat.value}
                  </p>
                  <p className="mt-2 text-sm text-[var(--foreground-subtle)]">{stat.detail}</p>
                </div>
                <div className={`rounded-2xl p-3 ${toneStyles[stat.tone]}`}>
                  <Icon className="h-5 w-5" />
                </div>
              </div>
            </div>
          );
        })}
      </section>

      <section className="grid gap-6 xl:grid-cols-[minmax(0,1.55fr)_minmax(320px,0.95fr)]">
        <div className="space-y-6">
          <div className="card overflow-hidden">
            <div className="flex flex-col gap-3 border-b border-[var(--border)] px-5 py-4 sm:flex-row sm:items-center sm:justify-between">
              <div>
                <h3 className="font-[family:var(--font-display)] text-xl font-semibold">Incoming queue</h3>
                <p className="mt-1 text-sm text-[var(--foreground-muted)]">
                  Highest-signal papers matched by monitors in the last hour.
                </p>
              </div>
              <Link href="/admin/papers" className="inline-flex items-center gap-1 text-sm font-medium text-[var(--primary)]">
                Open papers
                <ArrowRight className="h-4 w-4" />
              </Link>
            </div>

            <div className="divide-y divide-[var(--border)]">
              {recentPapers.map((paper) => (
                <div key={paper.title} className="px-5 py-4">
                  <div className="flex flex-col gap-4 lg:flex-row lg:items-start lg:justify-between">
                    <div className="min-w-0">
                      <div className="flex items-start gap-3">
                        <div className="mt-0.5 rounded-xl bg-[var(--surface-hover)] p-2">
                          <FileText className="h-4 w-4 text-[var(--foreground-subtle)]" />
                        </div>
                        <div className="min-w-0">
                          <p className="font-medium leading-6 text-[var(--foreground)]">{paper.title}</p>
                          <p className="mt-1 text-sm text-[var(--foreground-muted)]">{paper.source}</p>
                          <p className="mt-2 text-sm text-[var(--foreground-subtle)]">
                            Matched by {paper.matchedBy}
                          </p>
                        </div>
                      </div>
                    </div>

                    <div className="flex flex-wrap items-center gap-2 lg:justify-end">
                      <span className="rounded-full bg-[var(--primary-subtle)] px-3 py-1 text-xs font-medium text-[var(--primary)]">
                        Score {paper.score}
                      </span>
                      <span className={`rounded-full px-3 py-1 text-xs font-medium ${queueTone(paper.status)}`}>
                        {paper.status}
                      </span>
                      <span className="text-xs text-[var(--foreground-subtle)]">{paper.time}</span>
                    </div>
                  </div>
                </div>
              ))}
            </div>
          </div>

          <div className="card p-5">
            <div className="flex items-center justify-between">
              <div>
                <h3 className="font-[family:var(--font-display)] text-xl font-semibold">Pipeline overview</h3>
                <p className="mt-1 text-sm text-[var(--foreground-muted)]">
                  Stage-by-stage pressure and operator attention.
                </p>
              </div>
              <Link href="/admin/pipeline" className="inline-flex items-center gap-1 text-sm font-medium text-[var(--primary)]">
                Details
                <ArrowRight className="h-4 w-4" />
              </Link>
            </div>

            <div className="mt-5 grid gap-4 sm:grid-cols-2 xl:grid-cols-4">
              {pipelineStatus.map((item) => (
                <div key={item.stage} className="rounded-2xl border border-[var(--border)] bg-[var(--surface-hover)]/80 p-4">
                  <div className="flex items-center justify-between gap-2">
                    <p className="text-sm font-medium text-[var(--foreground-muted)]">{item.stage}</p>
                    <span className={`rounded-full px-2.5 py-1 text-[11px] font-semibold ${statusTone(item.status)}`}>
                      {item.status}
                    </span>
                  </div>
                  <p className="mt-4 font-[family:var(--font-display)] text-3xl font-semibold">{item.count}</p>
                  <p className="mt-2 text-sm leading-6 text-[var(--foreground-subtle)]">{item.detail}</p>
                </div>
              ))}
            </div>
          </div>
        </div>

        <div className="space-y-6">
          <div className="card p-5">
            <div className="flex items-center justify-between">
              <div>
                <h3 className="font-[family:var(--font-display)] text-xl font-semibold">Watchlist health</h3>
                <p className="mt-1 text-sm text-[var(--foreground-muted)]">
                  Monitor freshness and paper flow at a glance.
                </p>
              </div>
              <Link href="/admin/monitors" className="inline-flex items-center gap-1 text-sm font-medium text-[var(--primary)]">
                Manage
                <ArrowRight className="h-4 w-4" />
              </Link>
            </div>

            <div className="mt-5 space-y-3">
              {activeMonitors.map((monitor) => (
                <div key={monitor.name} className="rounded-2xl border border-[var(--border)] bg-[var(--surface-hover)]/80 p-4">
                  <div className="flex items-start justify-between gap-4">
                    <div>
                      <p className="font-medium">{monitor.name}</p>
                      <p className="mt-1 text-sm text-[var(--foreground-muted)]">{monitor.source}</p>
                    </div>
                    <span className="rounded-full bg-[var(--success)]/12 px-3 py-1 text-xs font-medium text-[var(--success)]">
                      Healthy
                    </span>
                  </div>
                  <div className="mt-4 flex items-center justify-between text-sm">
                    <span className="text-[var(--foreground-subtle)]">{monitor.papers} papers indexed</span>
                    <span className="text-[var(--foreground-subtle)]">Last match {monitor.freshness}</span>
                  </div>
                </div>
              ))}
            </div>
          </div>

          <div className="card p-5">
            <div>
              <h3 className="font-[family:var(--font-display)] text-xl font-semibold">Operator actions</h3>
              <p className="mt-1 text-sm text-[var(--foreground-muted)]">
                Fast paths for the work you actually do every day.
              </p>
            </div>

            <div className="mt-5 space-y-3">
              {actions.map((action) => {
                const Icon = action.icon;

                return (
                  <Link
                    key={action.title}
                    href={action.href}
                    className="group flex items-center justify-between rounded-2xl border border-[var(--border)] bg-[var(--surface-hover)]/75 p-4 hover:border-[var(--border-strong)] hover:bg-[var(--surface-hover)]"
                  >
                    <div className="flex items-start gap-3">
                      <div className={`rounded-2xl p-3 ${toneStyles[action.tone]}`}>
                        <Icon className="h-4 w-4" />
                      </div>
                      <div>
                        <p className="font-medium">{action.title}</p>
                        <p className="mt-1 text-sm text-[var(--foreground-muted)]">{action.detail}</p>
                      </div>
                    </div>
                    <ArrowRight className="h-4 w-4 text-[var(--foreground-subtle)] transition-transform group-hover:translate-x-1" />
                  </Link>
                );
              })}
            </div>
          </div>
        </div>
      </section>
    </div>
  );
}
