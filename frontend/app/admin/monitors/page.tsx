"use client";

import {
  ArrowRight,
  CheckCircle2,
  Clock,
  Filter,
  MoreHorizontal,
  Pause,
  Play,
  Plus,
  Radar,
  RefreshCw,
  Search,
  Settings,
} from "lucide-react";
import Link from "next/link";

const monitors = [
  {
    id: 1,
    name: "NLP Research",
    description: "Natural language processing papers from arXiv",
    sources: ["arXiv cs.CL", "arXiv cs.LG"],
    keywords: ["transformer", "BERT", "GPT", "language model"],
    papersCount: 156,
    lastMatch: "2h ago",
    status: "active",
    frequency: "Every 4 hours",
  },
  {
    id: 2,
    name: "AI Benchmarks",
    description: "Benchmark papers and evaluation methods",
    sources: ["arXiv cs.AI"],
    keywords: ["benchmark", "evaluation", "metrics"],
    papersCount: 89,
    lastMatch: "5h ago",
    status: "active",
    frequency: "Every 6 hours",
  },
  {
    id: 3,
    name: "Vision-Language",
    description: "Multimodal vision and language research",
    sources: ["arXiv cs.CV", "arXiv cs.CL"],
    keywords: ["multimodal", "CLIP", "vision-language"],
    papersCount: 67,
    lastMatch: "8h ago",
    status: "active",
    frequency: "Every 4 hours",
  },
  {
    id: 4,
    name: "RAG Systems",
    description: "Retrieval augmented generation papers",
    sources: ["arXiv cs.IR", "arXiv cs.AI"],
    keywords: ["retrieval", "RAG", "knowledge base"],
    papersCount: 34,
    lastMatch: "1d ago",
    status: "paused",
    frequency: "Every 12 hours",
  },
];

export default function MonitorsPage() {
  return (
    <div className="space-y-6">
      {/* Header */}
      <div className="flex items-center justify-between">
        <div>
          <h2 className="font-[family:var(--font-display)] text-2xl font-semibold">
            Monitors
          </h2>
          <p className="text-sm text-[var(--foreground-muted)]">
            Manage your paper tracking sources
          </p>
        </div>
        <div className="flex gap-3">
          <button className="flex items-center gap-2 rounded-lg border border-[var(--border)] bg-[var(--surface)] px-4 py-2 text-sm font-medium hover:bg-[var(--surface-hover)]">
            <RefreshCw className="h-4 w-4" />
            Sync All
          </button>
          <button className="flex items-center gap-2 rounded-lg bg-[var(--primary)] px-4 py-2 text-sm font-medium text-white hover:bg-[var(--primary-dark)]">
            <Plus className="h-4 w-4" />
            Create Monitor
          </button>
        </div>
      </div>

      {/* Stats */}
      <div className="grid gap-4 sm:grid-cols-4">
        {[
          { label: "Total Monitors", value: "12", icon: Radar },
          { label: "Active", value: "10", icon: Play, color: "text-[var(--success)]" },
          { label: "Paused", value: "2", icon: Pause, color: "text-[var(--warning)]" },
          { label: "Total Papers", value: "346", icon: CheckCircle2 },
        ].map((stat) => {
          const Icon = stat.icon;
          return (
            <div
              key={stat.label}
              className="rounded-xl border border-[var(--border)] bg-[var(--surface)] p-4"
            >
              <div className="flex items-center justify-between">
                <p className="text-xs text-[var(--foreground-muted)]">{stat.label}</p>
                <Icon className={`h-4 w-4 ${stat.color || "text-[var(--primary)]"}`} />
              </div>
              <p className="mt-2 text-2xl font-semibold">{stat.value}</p>
            </div>
          );
        })}
      </div>

      {/* Filters */}
      <div className="flex gap-3">
        <div className="relative flex-1 max-w-md">
          <Search className="absolute left-3 top-1/2 h-4 w-4 -translate-y-1/2 text-[var(--foreground-subtle)]" />
          <input
            type="text"
            placeholder="Search monitors..."
            className="w-full rounded-lg border border-[var(--border)] bg-[var(--surface)] py-2 pl-10 pr-4 text-sm outline-none focus:border-[var(--primary)]"
          />
        </div>
        <button className="flex items-center gap-2 rounded-lg border border-[var(--border)] bg-[var(--surface)] px-4 py-2 text-sm hover:bg-[var(--surface-hover)]">
          <Filter className="h-4 w-4" />
          Filter
        </button>
      </div>

      {/* Monitors List */}
      <div className="space-y-4">
        {monitors.map((monitor) => (
          <div
            key={monitor.id}
            className="rounded-xl border border-[var(--border)] bg-[var(--surface)] p-5"
          >
            <div className="flex items-start justify-between">
              <div className="flex items-start gap-4">
                <div className="rounded-lg bg-[var(--primary-subtle)] p-3">
                  <Radar className="h-5 w-5 text-[var(--primary)]" />
                </div>
                <div>
                  <div className="flex items-center gap-2">
                    <h3 className="font-medium">{monitor.name}</h3>
                    <span
                      className={`rounded-full px-2 py-0.5 text-xs ${
                        monitor.status === "active"
                          ? "bg-[var(--success)]/10 text-[var(--success)]"
                          : "bg-[var(--warning)]/10 text-[var(--warning)]"
                      }`}
                    >
                      {monitor.status}
                    </span>
                  </div>
                  <p className="mt-1 text-sm text-[var(--foreground-muted)]">
                    {monitor.description}
                  </p>
                  <div className="mt-3 flex flex-wrap gap-2">
                    {monitor.sources.map((source) => (
                      <span
                        key={source}
                        className="rounded bg-[var(--surface-elevated)] px-2 py-1 text-xs"
                      >
                        {source}
                      </span>
                    ))}
                  </div>
                  <div className="mt-2 flex flex-wrap gap-1">
                    {monitor.keywords.map((keyword) => (
                      <span
                        key={keyword}
                        className="rounded-full border border-[var(--border)] px-2 py-0.5 text-xs text-[var(--foreground-muted)]"
                      >
                        {keyword}
                      </span>
                    ))}
                  </div>
                </div>
              </div>
              <div className="flex items-center gap-2">
                <button className="rounded-lg p-2 text-[var(--foreground-muted)] hover:bg-[var(--surface-hover)]">
                  <Settings className="h-4 w-4" />
                </button>
                <button className="rounded-lg p-2 text-[var(--foreground-muted)] hover:bg-[var(--surface-hover)]">
                  <MoreHorizontal className="h-4 w-4" />
                </button>
              </div>
            </div>
            <div className="mt-4 flex items-center justify-between border-t border-[var(--border)] pt-4 text-sm">
              <div className="flex items-center gap-6">
                <span className="text-[var(--foreground-muted)]">
                  <span className="font-medium text-[var(--foreground)]">
                    {monitor.papersCount}
                  </span>{" "}
                  papers
                </span>
                <span className="flex items-center gap-1 text-[var(--foreground-muted)]">
                  <Clock className="h-3.5 w-3.5" />
                  {monitor.frequency}
                </span>
                <span className="text-[var(--foreground-muted)]">
                  Last match: {monitor.lastMatch}
                </span>
              </div>
              <Link
                href="/admin/papers"
                className="flex items-center gap-1 text-[var(--primary)] hover:underline"
              >
                View papers <ArrowRight className="h-3.5 w-3.5" />
              </Link>
            </div>
          </div>
        ))}
      </div>
    </div>
  );
}
