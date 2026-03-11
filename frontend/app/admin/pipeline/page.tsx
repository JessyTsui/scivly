"use client";

import {
  ArrowRight,
  CheckCircle2,
  MoreHorizontal,
  RefreshCw,
  Settings,
  XCircle,
} from "lucide-react";

const pipelineStages = [
  { name: "Intake", count: 12, processing: 2, failed: 0, avgTime: "5m" },
  { name: "Parsing", count: 8, processing: 1, failed: 0, avgTime: "3m" },
  { name: "Enrichment", count: 5, processing: 3, failed: 1, avgTime: "12m" },
  { name: "Translation", count: 3, processing: 1, failed: 0, avgTime: "8m" },
  { name: "Routing", count: 15, processing: 0, failed: 0, avgTime: "1m" },
];

const recentJobs = [
  {
    id: "job-1234",
    paper: "Attention Is All You Need: A Survey...",
    stage: "Enrichment",
    status: "processing",
    progress: 65,
    startedAt: "2m ago",
  },
  {
    id: "job-1233",
    paper: "Large Language Models for Scientific...",
    stage: "Parsing",
    status: "completed",
    progress: 100,
    startedAt: "5m ago",
  },
  {
    id: "job-1232",
    paper: "Multimodal Learning with Transformers...",
    stage: "Translation",
    status: "failed",
    progress: 30,
    startedAt: "8m ago",
    error: "API rate limit exceeded",
  },
];

export default function PipelinePage() {
  return (
    <div className="space-y-6">
      {/* Header */}
      <div className="flex items-center justify-between">
        <div>
          <h2 className="font-[family:var(--font-display)] text-2xl font-semibold">
            Pipeline
          </h2>
          <p className="text-sm text-[var(--foreground-muted)]">
            Monitor paper processing workflow
          </p>
        </div>
        <div className="flex gap-3">
          <button className="flex items-center gap-2 rounded-lg border border-[var(--border)] bg-[var(--surface)] px-4 py-2 text-sm font-medium hover:bg-[var(--surface-hover)]">
            <RefreshCw className="h-4 w-4" />
            Retry Failed
          </button>
          <button className="flex items-center gap-2 rounded-lg bg-[var(--primary)] px-4 py-2 text-sm font-medium text-white hover:bg-[var(--primary-dark)]">
            <Settings className="h-4 w-4" />
            Configure
          </button>
        </div>
      </div>

      {/* Pipeline Flow */}
      <div className="rounded-xl border border-[var(--border)] bg-[var(--surface)] p-5">
        <h3 className="font-medium mb-4">Processing Stages</h3>
        <div className="grid gap-4 sm:grid-cols-5">
          {pipelineStages.map((stage, index) => (
            <div key={stage.name} className="relative">
              <div className="rounded-lg border border-[var(--border)] bg-[var(--surface-elevated)] p-4">
                <p className="text-xs text-[var(--foreground-muted)]">{stage.name}</p>
                <p className="mt-1 text-2xl font-semibold">{stage.count}</p>
                <div className="mt-2 space-y-1 text-xs">
                  {stage.processing > 0 && (
                    <p className="text-[var(--warning)]">{stage.processing} processing</p>
                  )}
                  {stage.failed > 0 && (
                    <p className="text-red-500">{stage.failed} failed</p>
                  )}
                  <p className="text-[var(--foreground-subtle)]">Avg: {stage.avgTime}</p>
                </div>
              </div>
              {index < pipelineStages.length - 1 && (
                <div className="absolute -right-2 top-1/2 hidden h-px w-4 -translate-y-1/2 bg-[var(--border)] sm:block" />
              )}
            </div>
          ))}
        </div>
      </div>

      {/* Active Jobs */}
      <div className="rounded-xl border border-[var(--border)] bg-[var(--surface)]">
        <div className="flex items-center justify-between border-b border-[var(--border)] p-4">
          <h3 className="font-medium">Active Jobs</h3>
          <button
            type="button"
            className="flex items-center gap-1 text-sm text-[var(--primary)] hover:underline"
          >
            View all <ArrowRight className="h-3.5 w-3.5" />
          </button>
        </div>
        <div className="divide-y divide-[var(--border)]">
          {recentJobs.map((job) => (
            <div key={job.id} className="p-4">
              <div className="flex items-center justify-between">
                <div className="flex items-center gap-3">
                  {job.status === "processing" && (
                    <RefreshCw className="h-5 w-5 text-[var(--warning)] animate-spin" />
                  )}
                  {job.status === "completed" && (
                    <CheckCircle2 className="h-5 w-5 text-[var(--success)]" />
                  )}
                  {job.status === "failed" && (
                    <XCircle className="h-5 w-5 text-red-500" />
                  )}
                  <div>
                    <p className="font-medium">{job.paper}</p>
                    <p className="text-sm text-[var(--foreground-muted)]">
                      {job.stage} • Started {job.startedAt}
                    </p>
                  </div>
                </div>
                <div className="flex items-center gap-2">
                  {job.status === "failed" && (
                    <button className="rounded-lg bg-[var(--primary)] px-3 py-1.5 text-xs text-white hover:bg-[var(--primary-dark)]">
                      Retry
                    </button>
                  )}
                  <button className="rounded-lg p-2 text-[var(--foreground-muted)] hover:bg-[var(--surface-hover)]">
                    <MoreHorizontal className="h-4 w-4" />
                  </button>
                </div>
              </div>
              {job.status !== "completed" && (
                <div className="mt-3">
                  <div className="flex items-center justify-between text-xs mb-1">
                    <span className="text-[var(--foreground-muted)]">Progress</span>
                    <span className={job.status === "failed" ? "text-red-500" : ""}>
                      {job.progress}%
                    </span>
                  </div>
                  <div className="h-2 rounded-full bg-[var(--border)]">
                    <div
                      className={`h-2 rounded-full ${
                        job.status === "failed"
                          ? "bg-red-500"
                          : "bg-[var(--primary)]"
                      }`}
                      style={{ width: `${job.progress}%` }}
                    />
                  </div>
                  {job.error && (
                    <p className="mt-2 text-xs text-red-500">{job.error}</p>
                  )}
                </div>
              )}
            </div>
          ))}
        </div>
      </div>
    </div>
  );
}
