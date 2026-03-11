"use client";

import {
  ArrowRight,
  Download,
  ExternalLink,
  Filter,
  MoreHorizontal,
  Search,
  Star,
} from "lucide-react";

const papers = [
  {
    id: 1,
    title: "Attention Is All You Need: A Survey of Transformer Variants",
    authors: ["Ashish Vaswani", "Noam Shazeer", "Niki Parmar"],
    source: "arXiv",
    categories: ["cs.CL", "cs.LG"],
    abstract:
      "The dominant sequence transduction models are based on complex recurrent or convolutional neural networks...",
    matchedBy: "NLP Research",
    score: 0.94,
    date: "2024-01-15",
    status: "enriched",
    isRead: true,
    isStarred: true,
  },
  {
    id: 2,
    title: "Large Language Models for Scientific Discovery",
    authors: ["Y. Chen", "M. Smith", "A. Johnson"],
    source: "arXiv",
    categories: ["cs.AI"],
    abstract:
      "We explore the application of large language models in scientific research and discovery...",
    matchedBy: "AI Benchmarks",
    score: 0.91,
    date: "2024-01-14",
    status: "parsed",
    isRead: false,
    isStarred: false,
  },
  {
    id: 3,
    title: "Multimodal Learning with Transformers: A Review",
    authors: ["X. Li", "Y. Wang", "Z. Zhang"],
    source: "arXiv",
    categories: ["cs.CV", "cs.CL"],
    abstract:
      "A comprehensive review of multimodal learning approaches using transformer architectures...",
    matchedBy: "Vision-Language",
    score: 0.88,
    date: "2024-01-13",
    status: "translated",
    isRead: false,
    isStarred: true,
  },
  {
    id: 4,
    title: "Efficient Fine-Tuning of Large Models",
    authors: ["J. Brown", "K. Davis"],
    source: "arXiv",
    categories: ["cs.LG"],
    abstract:
      "We propose efficient methods for fine-tuning large pre-trained language models...",
    matchedBy: "NLP Research",
    score: 0.85,
    date: "2024-01-12",
    status: "queued",
    isRead: false,
    isStarred: false,
  },
];

export default function PapersPage() {
  return (
    <div className="space-y-6">
      {/* Header */}
      <div className="flex items-center justify-between">
        <div>
          <h2 className="font-[family:var(--font-display)] text-2xl font-semibold">
            Papers
          </h2>
          <p className="text-sm text-[var(--foreground-muted)]">
            Browse and manage your collected papers
          </p>
        </div>
        <div className="flex gap-3">
          <button className="flex items-center gap-2 rounded-lg border border-[var(--border)] bg-[var(--surface)] px-4 py-2 text-sm font-medium hover:bg-[var(--surface-hover)]">
            <Download className="h-4 w-4" />
            Export
          </button>
          <button className="flex items-center gap-2 rounded-lg bg-[var(--primary)] px-4 py-2 text-sm font-medium text-white hover:bg-[var(--primary-dark)]">
            <ExternalLink className="h-4 w-4" />
            Add Paper
          </button>
        </div>
      </div>

      {/* Stats */}
      <div className="grid gap-4 sm:grid-cols-5">
        {[
          { label: "Total Papers", value: "346" },
          { label: "This Week", value: "48" },
          { label: "Unread", value: "23" },
          { label: "Starred", value: "56" },
          { label: "Translated", value: "128" },
        ].map((stat) => (
          <div
            key={stat.label}
            className="rounded-xl border border-[var(--border)] bg-[var(--surface)] p-4 text-center"
          >
            <p className="text-2xl font-semibold">{stat.value}</p>
            <p className="text-xs text-[var(--foreground-muted)]">{stat.label}</p>
          </div>
        ))}
      </div>

      {/* Filters */}
      <div className="flex flex-wrap gap-3">
        <div className="relative flex-1 min-w-[300px]">
          <Search className="absolute left-3 top-1/2 h-4 w-4 -translate-y-1/2 text-[var(--foreground-subtle)]" />
          <input
            type="text"
            placeholder="Search papers by title, author, or keywords..."
            className="w-full rounded-lg border border-[var(--border)] bg-[var(--surface)] py-2 pl-10 pr-4 text-sm outline-none focus:border-[var(--primary)]"
          />
        </div>
        <select className="rounded-lg border border-[var(--border)] bg-[var(--surface)] px-4 py-2 text-sm">
          <option>All Status</option>
          <option>Enriched</option>
          <option>Parsed</option>
          <option>Queued</option>
        </select>
        <select className="rounded-lg border border-[var(--border)] bg-[var(--surface)] px-4 py-2 text-sm">
          <option>All Monitors</option>
          <option>NLP Research</option>
          <option>AI Benchmarks</option>
        </select>
        <button className="flex items-center gap-2 rounded-lg border border-[var(--border)] bg-[var(--surface)] px-4 py-2 text-sm hover:bg-[var(--surface-hover)]">
          <Filter className="h-4 w-4" />
          More Filters
        </button>
      </div>

      {/* Papers List */}
      <div className="space-y-4">
        {papers.map((paper) => (
          <div
            key={paper.id}
            className="rounded-xl border border-[var(--border)] bg-[var(--surface)] p-5"
          >
            <div className="flex items-start justify-between">
              <div className="flex-1">
                <div className="flex items-start gap-3">
                  <button
                    className={`mt-1 ${paper.isStarred ? "text-[var(--warning)]" : "text-[var(--border-strong)]"}`}
                  >
                    <Star
                      className={`h-5 w-5 ${paper.isStarred ? "fill-current" : ""}`}
                    />
                  </button>
                  <div className="flex-1">
                    <h3 className="font-medium">{paper.title}</h3>
                    <p className="mt-1 text-sm text-[var(--foreground-muted)]">
                      {paper.authors.join(", ")}
                    </p>
                    <p className="mt-2 text-sm text-[var(--foreground-subtle)] line-clamp-2">
                      {paper.abstract}
                    </p>
                  </div>
                </div>
              </div>
              <div className="flex items-center gap-2">
                <button className="rounded-lg p-2 text-[var(--foreground-muted)] hover:bg-[var(--surface-hover)]">
                  <MoreHorizontal className="h-4 w-4" />
                </button>
              </div>
            </div>
            <div className="mt-4 flex items-center justify-between border-t border-[var(--border)] pt-4">
              <div className="flex items-center gap-4">
                <div className="flex items-center gap-2">
                  <span className="text-xs text-[var(--foreground-muted)]">
                    {paper.source}
                  </span>
                  {paper.categories.map((cat) => (
                    <span
                      key={cat}
                      className="rounded bg-[var(--surface-elevated)] px-1.5 py-0.5 text-xs"
                    >
                      {cat}
                    </span>
                  ))}
                </div>
                <span className="text-xs text-[var(--foreground-muted)]">
                  Matched by: {paper.matchedBy}
                </span>
                <span className="rounded-full bg-[var(--primary-subtle)] px-2 py-0.5 text-xs text-[var(--primary)]">
                  Score: {paper.score}
                </span>
                <span
                  className={`rounded-full px-2 py-0.5 text-xs ${
                    paper.status === "enriched"
                      ? "bg-[var(--success)]/10 text-[var(--success)]"
                      : paper.status === "translated"
                      ? "bg-blue-500/10 text-blue-500"
                      : "bg-[var(--warning)]/10 text-[var(--warning)]"
                  }`}
                >
                  {paper.status}
                </span>
              </div>
              <div className="flex items-center gap-3">
                <span className="text-xs text-[var(--foreground-subtle)]">
                  {paper.date}
                </span>
                <button
                  type="button"
                  className="flex items-center gap-1 text-sm text-[var(--primary)] hover:underline"
                >
                  Read more <ArrowRight className="h-3.5 w-3.5" />
                </button>
              </div>
            </div>
          </div>
        ))}
      </div>
    </div>
  );
}
