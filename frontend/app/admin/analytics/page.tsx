import Link from "next/link";
import { ArrowRight, Download, TrendingUp } from "lucide-react";

const statCards = [
  { label: "Total papers", value: "346", detail: "+23% vs last month", tone: "success" },
  { label: "Avg daily intake", value: "12.4", detail: "Peak day: Thursday", tone: "primary" },
  { label: "Translation rate", value: "87%", detail: "+2 points in 30 days", tone: "warning" },
  { label: "Read rate", value: "64%", detail: "-3 points to recover", tone: "accent" },
];

const monthlyVolume = [
  { month: "Jan", total: 40, translated: 28 },
  { month: "Feb", total: 52, translated: 37 },
  { month: "Mar", total: 48, translated: 35 },
  { month: "Apr", total: 68, translated: 46 },
  { month: "May", total: 59, translated: 42 },
  { month: "Jun", total: 74, translated: 56 },
  { month: "Jul", total: 64, translated: 48 },
  { month: "Aug", total: 81, translated: 63 },
  { month: "Sep", total: 72, translated: 54 },
  { month: "Oct", total: 88, translated: 69 },
  { month: "Nov", total: 77, translated: 58 },
  { month: "Dec", total: 61, translated: 45 },
];

const topMonitors = [
  { name: "NLP Research", papers: 156, percentage: 45 },
  { name: "AI Benchmarks", papers: 89, percentage: 26 },
  { name: "Vision-Language", papers: 67, percentage: 19 },
  { name: "RAG Systems", papers: 34, percentage: 10 },
];

const categoryDistribution = [
  { category: "NLP", count: 142, percentage: 41, trend: "up" },
  { category: "Computer Vision", count: 89, percentage: 26, trend: "up" },
  { category: "ML Theory", count: 67, percentage: 19, trend: "flat" },
  { category: "Robotics", count: 28, percentage: 8, trend: "up" },
  { category: "Systems", count: 20, percentage: 6, trend: "down" },
];

const toneStyles = {
  primary: "bg-[var(--primary-subtle)] text-[var(--primary)]",
  success: "bg-[var(--success)]/12 text-[var(--success)]",
  warning: "bg-[var(--warning)]/12 text-[var(--warning)]",
  accent: "bg-[var(--accent-subtle)] text-[var(--accent)]",
};

function trendText(trend: string) {
  if (trend === "up") {
    return "Growing";
  }

  if (trend === "down") {
    return "Cooling";
  }

  return "Stable";
}

function trendTone(trend: string) {
  if (trend === "up") {
    return "bg-[var(--success)]/12 text-[var(--success)]";
  }

  if (trend === "down") {
    return "bg-[var(--accent-subtle)] text-[var(--accent)]";
  }

  return "bg-[var(--primary-subtle)] text-[var(--primary)]";
}

export default function AnalyticsPage() {
  return (
    <div className="space-y-6">
      <section className="card p-6">
        <div className="flex flex-col gap-5 lg:flex-row lg:items-start lg:justify-between">
          <div className="max-w-2xl">
            <div className="inline-flex items-center gap-2 rounded-full bg-[var(--primary-subtle)] px-3 py-1 text-xs font-semibold uppercase tracking-[0.22em] text-[var(--primary)]">
              <TrendingUp className="h-3.5 w-3.5" />
              Insights
            </div>
            <h2 className="mt-4 font-[family:var(--font-display)] text-3xl font-semibold tracking-tight">
              Analytics should show movement, not decorative placeholders.
            </h2>
            <p className="mt-3 max-w-xl text-sm leading-7 text-[var(--foreground-muted)] sm:text-base">
              The charts below are now deterministic, easier to scan, and aligned with the same
              surface system as the rest of the admin console.
            </p>
          </div>

          <button
            type="button"
            className="btn-secondary self-start text-sm"
          >
            <Download className="h-4 w-4" />
            Export report
          </button>
        </div>
      </section>

      <section className="grid gap-4 sm:grid-cols-2 xl:grid-cols-4">
        {statCards.map((stat) => (
          <div key={stat.label} className="card p-5">
            <div className="flex items-start justify-between gap-4">
              <div>
                <p className="text-sm font-medium text-[var(--foreground-muted)]">{stat.label}</p>
                <p className="mt-3 font-[family:var(--font-display)] text-3xl font-semibold">
                  {stat.value}
                </p>
                <p className="mt-2 text-sm text-[var(--foreground-subtle)]">{stat.detail}</p>
              </div>
              <span className={`rounded-full px-3 py-1 text-xs font-semibold ${toneStyles[stat.tone as keyof typeof toneStyles]}`}>
                {stat.detail.split(" ")[0]}
              </span>
            </div>
          </div>
        ))}
      </section>

      <section className="grid gap-6 xl:grid-cols-[minmax(0,1.5fr)_minmax(320px,0.9fr)]">
        <div className="card p-5">
          <div className="flex items-center justify-between gap-4">
            <div>
              <h3 className="font-[family:var(--font-display)] text-xl font-semibold">Paper volume over time</h3>
              <p className="mt-1 text-sm text-[var(--foreground-muted)]">
                Total intake compared with translated output each month.
              </p>
            </div>
            <div className="flex items-center gap-2 text-xs font-medium text-[var(--foreground-muted)]">
              <span className="inline-flex items-center gap-2">
                <span className="h-2.5 w-2.5 rounded-full bg-[var(--primary)]" />
                Total
              </span>
              <span className="inline-flex items-center gap-2">
                <span className="h-2.5 w-2.5 rounded-full bg-[var(--success)]" />
                Translated
              </span>
            </div>
          </div>

          <div className="mt-6 grid grid-cols-12 gap-3">
            {monthlyVolume.map((point) => (
              <div key={point.month} className="flex flex-col items-center gap-3">
                <div className="flex h-56 w-full items-end justify-center gap-1 rounded-2xl bg-[var(--surface-hover)]/75 px-1.5 py-3">
                  <div
                    className="w-full rounded-full bg-[var(--primary-subtle)]"
                    style={{ height: `${point.total}%` }}
                  >
                    <div className="h-full w-full rounded-full bg-[var(--primary)]" />
                  </div>
                  <div
                    className="w-full rounded-full bg-[color:rgb(16_185_129_/_0.18)]"
                    style={{ height: `${point.translated}%` }}
                  >
                    <div className="h-full w-full rounded-full bg-[var(--success)]" />
                  </div>
                </div>
                <span className="text-xs font-medium text-[var(--foreground-subtle)]">{point.month}</span>
              </div>
            ))}
          </div>
        </div>

        <div className="space-y-6">
          <div className="card p-5">
            <div className="flex items-center justify-between">
              <div>
                <h3 className="font-[family:var(--font-display)] text-xl font-semibold">Top monitors</h3>
                <p className="mt-1 text-sm text-[var(--foreground-muted)]">
                  Which watchlists are driving most of the queue.
                </p>
              </div>
              <Link href="/admin/monitors" className="inline-flex items-center gap-1 text-sm font-medium text-[var(--primary)]">
                Manage
                <ArrowRight className="h-4 w-4" />
              </Link>
            </div>

            <div className="mt-5 space-y-4">
              {topMonitors.map((monitor) => (
                <div key={monitor.name}>
                  <div className="flex items-center justify-between text-sm">
                    <span className="font-medium">{monitor.name}</span>
                    <span className="text-[var(--foreground-muted)]">{monitor.papers} papers</span>
                  </div>
                  <div className="mt-2 h-3 rounded-full bg-[var(--surface-hover)]">
                    <div
                      className="h-3 rounded-full bg-gradient-to-r from-[var(--primary)] to-[var(--primary-light)]"
                      style={{ width: `${monitor.percentage}%` }}
                    />
                  </div>
                </div>
              ))}
            </div>
          </div>

          <div className="card-dark p-5">
            <p className="text-sm font-medium text-[var(--primary-light)]">Coverage insight</p>
            <h3 className="mt-2 font-[family:var(--font-display)] text-2xl font-semibold text-white">
              Translation output is keeping up with volume.
            </h3>
            <p className="mt-3 text-sm leading-6 text-slate-300">
              Monthly translated papers stayed above 70% of intake in 9 of 12 months. The next
              improvement should be read-through rate, not queue throughput.
            </p>
            <div className="mt-5 grid gap-3 sm:grid-cols-2">
              <div className="rounded-2xl border border-white/10 bg-white/[0.06] p-4">
                <p className="text-xs uppercase tracking-[0.22em] text-slate-400">Best month</p>
                <p className="mt-2 text-2xl font-semibold text-white">October</p>
                <p className="mt-1 text-sm text-slate-300">88 papers, 69 translated</p>
              </div>
              <div className="rounded-2xl border border-white/10 bg-white/[0.06] p-4">
                <p className="text-xs uppercase tracking-[0.22em] text-slate-400">Focus area</p>
                <p className="mt-2 text-2xl font-semibold text-white">Read rate</p>
                <p className="mt-1 text-sm text-slate-300">Recover 3 points with better routing.</p>
              </div>
            </div>
          </div>
        </div>
      </section>

      <section className="card overflow-hidden">
        <div className="flex flex-col gap-3 border-b border-[var(--border)] px-5 py-4 sm:flex-row sm:items-center sm:justify-between">
          <div>
            <h3 className="font-[family:var(--font-display)] text-xl font-semibold">Category distribution</h3>
            <p className="mt-1 text-sm text-[var(--foreground-muted)]">
              Current mix of paper categories from active monitors.
            </p>
          </div>
          <Link href="/admin/papers" className="inline-flex items-center gap-1 text-sm font-medium text-[var(--primary)]">
            Open paper library
            <ArrowRight className="h-4 w-4" />
          </Link>
        </div>

        <div className="grid gap-4 p-5 md:grid-cols-2 xl:grid-cols-5">
          {categoryDistribution.map((category) => (
            <div
              key={category.category}
              className="rounded-2xl border border-[var(--border)] bg-[var(--surface-hover)]/75 p-4"
            >
              <div className="flex items-start justify-between gap-3">
                <div>
                  <p className="font-medium">{category.category}</p>
                  <p className="mt-2 font-[family:var(--font-display)] text-3xl font-semibold">
                    {category.count}
                  </p>
                  <p className="mt-1 text-sm text-[var(--foreground-muted)]">{category.percentage}% of all papers</p>
                </div>
                <span className={`rounded-full px-3 py-1 text-xs font-semibold ${trendTone(category.trend)}`}>
                  {trendText(category.trend)}
                </span>
              </div>
            </div>
          ))}
        </div>
      </section>
    </div>
  );
}
