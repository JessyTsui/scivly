"use client";

import {
  Clock,
  FileQuestion,
  Paperclip,
  Plus,
  RefreshCw,
  Search,
  ThumbsDown,
  ThumbsUp,
} from "lucide-react";

const questions = [
  {
    id: 1,
    question: "What are the key differences between transformer variants mentioned in the survey?",
    answer: "The survey identifies three main variants: standard transformers use multi-head self-attention, while efficient variants like Performer and Linformer use kernel methods or low-rank approximations to reduce complexity from O(n²) to O(n).",
    context: "Attention Is All You Need: A Survey...",
    askedAt: "2h ago",
    status: "answered",
    confidence: 0.92,
    feedback: "positive",
  },
  {
    id: 2,
    question: "How does the paper evaluate multimodal learning approaches?",
    answer: "The paper evaluates approaches using standard vision-language benchmarks including VQA, image captioning, and cross-modal retrieval tasks.",
    context: "Multimodal Learning with Transformers...",
    askedAt: "5h ago",
    status: "answered",
    confidence: 0.87,
    feedback: null,
  },
  {
    id: 3,
    question: "What are the main contributions of this work on RAG systems?",
    answer: "",
    context: "Retrieval Augmented Generation Survey",
    askedAt: "1h ago",
    status: "pending",
    confidence: null,
    feedback: null,
  },
];

export default function QAPage() {
  return (
    <div className="space-y-6">
      {/* Header */}
      <div className="flex items-center justify-between">
        <div>
          <h2 className="font-[family:var(--font-display)] text-2xl font-semibold">
            Q&A
          </h2>
          <p className="text-sm text-[var(--foreground-muted)]">
            Ask questions about your papers
          </p>
        </div>
        <button className="flex items-center gap-2 rounded-lg bg-[var(--primary)] px-4 py-2 text-sm font-medium text-white hover:bg-[var(--primary-dark)]">
          <Plus className="h-4 w-4" />
          New Question
        </button>
      </div>

      {/* Stats */}
      <div className="grid gap-4 sm:grid-cols-4">
        {[
          { label: "Total Questions", value: "156" },
          { label: "Answered", value: "142" },
          { label: "Pending", value: "14" },
          { label: "Avg Confidence", value: "0.89" },
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

      {/* Search */}
      <div className="relative">
        <Search className="absolute left-3 top-1/2 h-4 w-4 -translate-y-1/2 text-[var(--foreground-subtle)]" />
        <input
          type="text"
          placeholder="Search questions and answers..."
          className="w-full rounded-lg border border-[var(--border)] bg-[var(--surface)] py-2.5 pl-10 pr-4 text-sm outline-none focus:border-[var(--primary)]"
        />
      </div>

      {/* Questions List */}
      <div className="space-y-4">
        {questions.map((qa) => (
          <div
            key={qa.id}
            className="rounded-xl border border-[var(--border)] bg-[var(--surface)] p-5"
          >
            <div className="flex items-start gap-3">
              <div className="rounded-lg bg-[var(--primary-subtle)] p-2">
                <FileQuestion className="h-4 w-4 text-[var(--primary)]" />
              </div>
              <div className="flex-1">
                <div className="flex items-center justify-between">
                  <h3 className="font-medium">{qa.question}</h3>
                  <span
                    className={`rounded-full px-2 py-0.5 text-xs ${
                      qa.status === "answered"
                        ? "bg-[var(--success)]/10 text-[var(--success)]"
                        : "bg-[var(--warning)]/10 text-[var(--warning)]"
                    }`}
                  >
                    {qa.status}
                  </span>
                </div>

                <div className="mt-2 flex items-center gap-2 text-xs text-[var(--foreground-muted)]">
                  <span className="flex items-center gap-1">
                    <Paperclip className="h-3 w-3" />
                    {qa.context}
                  </span>
                  <span>•</span>
                  <span className="flex items-center gap-1">
                    <Clock className="h-3 w-3" />
                    {qa.askedAt}
                  </span>
                </div>

                {qa.answer && (
                  <div className="mt-4 rounded-lg bg-[var(--surface-elevated)] p-4">
                    <p className="text-sm text-[var(--foreground-muted)]">
                      {qa.answer}
                    </p>

                    <div className="mt-3 flex items-center justify-between">
                      <div className="flex items-center gap-2">
                        {qa.confidence && (
                          <span className="text-xs text-[var(--foreground-subtle)]">
                            Confidence: {qa.confidence}
                          </span>
                        )}
                      </div>
                      <div className="flex items-center gap-1">
                        <button
                          className={`rounded p-1 ${
                            qa.feedback === "positive"
                              ? "bg-[var(--success)]/10 text-[var(--success)]"
                              : "text-[var(--foreground-muted)] hover:bg-[var(--surface-hover)]"
                          }`}
                        >
                          <ThumbsUp className="h-4 w-4" />
                        </button>
                        <button
                          className={`rounded p-1 ${
                            qa.feedback === "negative"
                              ? "bg-red-500/10 text-red-500"
                              : "text-[var(--foreground-muted)] hover:bg-[var(--surface-hover)]"
                          }`}
                        >
                          <ThumbsDown className="h-4 w-4" />
                        </button>
                      </div>
                    </div>
                  </div>
                )}

                {qa.status === "pending" && (
                  <div className="mt-4 flex items-center gap-2 text-sm text-[var(--foreground-muted)]">
                    <RefreshCw className="h-4 w-4 animate-spin" />
                    Generating answer...
                  </div>
                )}
              </div>
            </div>
          </div>
        ))}
      </div>
    </div>
  );
}
