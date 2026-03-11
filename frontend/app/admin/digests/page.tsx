"use client";

import {
  ArrowRight,
  CheckCircle2,
  Clock,
  MoreHorizontal,
  Newspaper,
  Play,
  Plus,
  Settings,
  Users,
} from "lucide-react";

const digests = [
  {
    id: 1,
    name: "Morning Research Digest",
    description: "Daily summary of new papers from all monitors",
    schedule: "Daily at 09:00",
    lastSent: "Today, 09:00",
    recipients: 3,
    papersCount: 12,
    status: "active",
    type: "daily",
  },
  {
    id: 2,
    name: "Weekly AI Summary",
    description: "Weekly roundup of AI and ML papers",
    schedule: "Monday at 08:00",
    lastSent: "Yesterday",
    recipients: 5,
    papersCount: 28,
    status: "active",
    type: "weekly",
  },
  {
    id: 3,
    name: "NLP Deep Dive",
    description: "In-depth NLP paper analysis",
    schedule: "On demand",
    lastSent: "3 days ago",
    recipients: 2,
    papersCount: 8,
    status: "paused",
    type: "manual",
  },
];

const recentDigests = [
  { date: "2024-01-15", name: "Morning Research Digest", papers: 12, sent: true },
  { date: "2024-01-14", name: "Weekly AI Summary", papers: 28, sent: true },
  { date: "2024-01-14", name: "Morning Research Digest", papers: 8, sent: true },
  { date: "2024-01-13", name: "Morning Research Digest", papers: 15, sent: true },
];

export default function DigestsPage() {
  return (
    <div className="space-y-6">
      {/* Header */}
      <div className="flex items-center justify-between">
        <div>
          <h2 className="font-[family:var(--font-display)] text-2xl font-semibold">
            Digests
          </h2>
          <p className="text-sm text-[var(--foreground-muted)]">
            Manage your paper summary digests
          </p>
        </div>
        <button className="flex items-center gap-2 rounded-lg bg-[var(--primary)] px-4 py-2 text-sm font-medium text-white hover:bg-[var(--primary-dark)]">
          <Plus className="h-4 w-4" />
          Create Digest
        </button>
      </div>

      {/* Stats */}
      <div className="grid gap-4 sm:grid-cols-4">
        {[
          { label: "Active Digests", value: "7", icon: Newspaper },
          { label: "Recipients", value: "12", icon: Users },
          { label: "Sent This Week", value: "42", icon: CheckCircle2 },
          { label: "Avg Papers/Digest", value: "15", icon: Clock },
        ].map((stat) => {
          const Icon = stat.icon;
          return (
            <div
              key={stat.label}
              className="rounded-xl border border-[var(--border)] bg-[var(--surface)] p-4"
            >
              <div className="flex items-center justify-between">
                <p className="text-xs text-[var(--foreground-muted)]">{stat.label}</p>
                <Icon className="h-4 w-4 text-[var(--primary)]" />
              </div>
              <p className="mt-2 text-2xl font-semibold">{stat.value}</p>
            </div>
          );
        })}
      </div>

      <div className="grid gap-6 lg:grid-cols-3">
        {/* Digest Schedules */}
        <div className="lg:col-span-2 space-y-4">
          <h3 className="font-medium">Digest Schedules</h3>
          {digests.map((digest) => (
            <div
              key={digest.id}
              className="rounded-xl border border-[var(--border)] bg-[var(--surface)] p-5"
            >
              <div className="flex items-start justify-between">
                <div className="flex items-start gap-4">
                  <div className="rounded-lg bg-[var(--primary-subtle)] p-3">
                    <Newspaper className="h-5 w-5 text-[var(--primary)]" />
                  </div>
                  <div>
                    <div className="flex items-center gap-2">
                      <h4 className="font-medium">{digest.name}</h4>
                      <span
                        className={`rounded-full px-2 py-0.5 text-xs ${
                          digest.status === "active"
                            ? "bg-[var(--success)]/10 text-[var(--success)]"
                            : "bg-[var(--warning)]/10 text-[var(--warning)]"
                        }`}
                      >
                        {digest.status}
                      </span>
                    </div>
                    <p className="mt-1 text-sm text-[var(--foreground-muted)]">
                      {digest.description}
                    </p>
                    <div className="mt-3 flex items-center gap-4 text-sm">
                      <span className="flex items-center gap-1 text-[var(--foreground-muted)]">
                        <Clock className="h-3.5 w-3.5" />
                        {digest.schedule}
                      </span>
                      <span className="flex items-center gap-1 text-[var(--foreground-muted)]">
                        <Users className="h-3.5 w-3.5" />
                        {digest.recipients} recipients
                      </span>
                      <span className="text-[var(--foreground-muted)]">
                        {digest.papersCount} papers
                      </span>
                    </div>
                  </div>
                </div>
                <div className="flex items-center gap-2">
                  <button className="rounded-lg p-2 text-[var(--foreground-muted)] hover:bg-[var(--surface-hover)]">
                    <Play className="h-4 w-4" />
                  </button>
                  <button className="rounded-lg p-2 text-[var(--foreground-muted)] hover:bg-[var(--surface-hover)]">
                    <Settings className="h-4 w-4" />
                  </button>
                  <button className="rounded-lg p-2 text-[var(--foreground-muted)] hover:bg-[var(--surface-hover)]">
                    <MoreHorizontal className="h-4 w-4" />
                  </button>
                </div>
              </div>
              <div className="mt-4 flex items-center justify-between border-t border-[var(--border)] pt-4 text-sm">
                <span className="text-[var(--foreground-muted)]">
                  Last sent: {digest.lastSent}
                </span>
                <button
                  type="button"
                  className="flex items-center gap-1 text-[var(--primary)] hover:underline"
                >
                  Preview <ArrowRight className="h-3.5 w-3.5" />
                </button>
              </div>
            </div>
          ))}
        </div>

        {/* Recent History */}
        <div>
          <h3 className="font-medium mb-4">Recent History</h3>
          <div className="rounded-xl border border-[var(--border)] bg-[var(--surface)]">
            {recentDigests.map((digest, index) => (
              <div
                key={index}
                className="flex items-center justify-between p-4 border-b border-[var(--border)] last:border-0"
              >
                <div>
                  <p className="text-sm font-medium">{digest.name}</p>
                  <p className="text-xs text-[var(--foreground-muted)]">{digest.date}</p>
                </div>
                <div className="text-right">
                  <p className="text-sm">{digest.papers} papers</p>
                  <span className="text-xs text-[var(--success)]">
                    Sent
                  </span>
                </div>
              </div>
            ))}
          </div>
        </div>
      </div>
    </div>
  );
}
