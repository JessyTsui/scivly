"use client";

import { useState } from "react";
import { ChevronDown, ChevronUp, Sparkles } from "lucide-react";

import type { PaperOut } from "@/lib/api/types";
import { Button } from "@/components/ui/button";
import {
  Card,
  CardContent,
  CardDescription,
  CardFooter,
  CardHeader,
  CardTitle,
} from "@/components/ui/card";
import { Separator } from "@/components/ui/separator";
import { CategoryTag } from "@/components/workspace/CategoryTag";
import { ScoreBadge } from "@/components/workspace/ScoreBadge";
import { formatCalendarDate, formatRelativeDate } from "@/lib/utils";

type PaperCardProps = {
  paper: PaperOut;
  defaultExpanded?: boolean;
};

export function PaperCard({ paper, defaultExpanded = false }: PaperCardProps) {
  const [expanded, setExpanded] = useState(defaultExpanded);

  return (
    <Card className="card-hover overflow-hidden">
      <CardHeader className="gap-4">
        <div className="flex flex-col gap-4 lg:flex-row lg:items-start lg:justify-between">
          <div className="min-w-0 space-y-3">
            <div className="flex flex-wrap items-center gap-2">
              <CategoryTag category={paper.primary_category} />
              {paper.profile_labels.map((label) => (
                <span
                  key={label}
                  className="rounded-full border border-[var(--border)] bg-[var(--surface-hover)] px-3 py-1 text-xs font-medium text-[var(--foreground-muted)]"
                >
                  {label}
                </span>
              ))}
            </div>

            <div>
              <CardTitle className="text-2xl leading-tight">{paper.title}</CardTitle>
              <CardDescription className="mt-3 text-base leading-7">
                {paper.authors.map((author) => author.name).join(", ")}
              </CardDescription>
            </div>
          </div>

          <div className="flex shrink-0 items-center gap-3 self-start">
            <ScoreBadge score={paper.score.total_score} />
            <Button
              variant="outline"
              size="sm"
              type="button"
              onClick={() => setExpanded((value) => !value)}
              aria-expanded={expanded}
            >
              {expanded ? <ChevronUp /> : <ChevronDown />}
              {expanded ? "Hide details" : "Details"}
            </Button>
          </div>
        </div>
      </CardHeader>

      <CardContent className="space-y-5">
        <div className="grid gap-3 text-sm text-[var(--foreground-muted)] sm:grid-cols-3">
          <div>
            <p className="text-xs font-semibold uppercase tracking-[0.2em] text-[var(--foreground-subtle)]">
              Published
            </p>
            <p className="mt-2 font-medium text-[var(--foreground)]">{formatCalendarDate(paper.published_at)}</p>
            <p className="mt-1 text-xs">{formatRelativeDate(paper.published_at)}</p>
          </div>
          <div>
            <p className="text-xs font-semibold uppercase tracking-[0.2em] text-[var(--foreground-subtle)]">
              arXiv
            </p>
            <p className="mt-2 font-medium text-[var(--foreground)]">
              {paper.arxiv_id}v{paper.version}
            </p>
            <p className="mt-1 text-xs">{paper.comment ?? "Metadata-first triage candidate"}</p>
          </div>
          <div>
            <p className="text-xs font-semibold uppercase tracking-[0.2em] text-[var(--foreground-subtle)]">
              Summary
            </p>
            <p className="mt-2 text-[var(--foreground)]">{paper.one_line_summary}</p>
          </div>
        </div>

        {expanded ? (
          <>
            <Separator />

            <div className="grid gap-6 lg:grid-cols-[minmax(0,1.2fr)_minmax(280px,0.8fr)]">
              <div className="space-y-4">
                <div>
                  <p className="text-xs font-semibold uppercase tracking-[0.2em] text-[var(--foreground-subtle)]">
                    Abstract
                  </p>
                  <p className="mt-3 text-sm leading-7 text-[var(--foreground-muted)]">{paper.abstract}</p>
                </div>

                <div>
                  <p className="text-xs font-semibold uppercase tracking-[0.2em] text-[var(--foreground-subtle)]">
                    Key points
                  </p>
                  <div className="mt-3 space-y-2">
                    {paper.key_points.map((point) => (
                      <div
                        key={point}
                        className="flex gap-3 rounded-2xl bg-[var(--surface-hover)]/80 px-4 py-3 text-sm text-[var(--foreground-muted)]"
                      >
                        <Sparkles className="mt-0.5 size-4 shrink-0 text-[var(--accent)]" />
                        <span>{point}</span>
                      </div>
                    ))}
                  </div>
                </div>
              </div>

              <div className="space-y-4">
                <div className="rounded-[22px] border border-[var(--border)] bg-[var(--surface-hover)]/75 p-4">
                  <p className="text-xs font-semibold uppercase tracking-[0.2em] text-[var(--foreground-subtle)]">
                    Score breakdown
                  </p>
                  <div className="mt-4 space-y-3 text-sm">
                    {[
                      ["Topical relevance", paper.score.topical_relevance],
                      ["Prestige priors", paper.score.prestige_priors],
                      ["Actionability", paper.score.actionability],
                      ["Profile fit", paper.score.profile_fit],
                      ["Novelty", paper.score.novelty_diversity],
                      ["Penalties", paper.score.penalties],
                    ].map(([label, value]) => (
                      <div key={label} className="flex items-center justify-between gap-3">
                        <span className="text-[var(--foreground-muted)]">{label}</span>
                        <span className="font-semibold text-[var(--foreground)]">{value}</span>
                      </div>
                    ))}
                  </div>
                </div>

                <div className="rounded-[22px] border border-[var(--border)] bg-[var(--surface-hover)]/75 p-4">
                  <p className="text-xs font-semibold uppercase tracking-[0.2em] text-[var(--foreground-subtle)]">
                    Matched rules
                  </p>
                  <div className="mt-4 flex flex-wrap gap-2">
                    {paper.score.matched_rules.positive.map((rule) => (
                      <span
                        key={rule}
                        className="rounded-full border border-emerald-500/15 bg-emerald-500/10 px-3 py-1 text-xs font-medium text-emerald-700 dark:text-emerald-300"
                      >
                        {rule}
                      </span>
                    ))}
                    {paper.score.matched_rules.negative.map((rule) => (
                      <span
                        key={rule}
                        className="rounded-full border border-rose-500/15 bg-rose-500/10 px-3 py-1 text-xs font-medium text-rose-700 dark:text-rose-300"
                      >
                        {rule}
                      </span>
                    ))}
                  </div>
                </div>
              </div>
            </div>
          </>
        ) : null}
      </CardContent>

      <CardFooter className="justify-between">
        <div className="text-sm text-[var(--foreground-muted)]">
          Decision: <span className="font-medium text-[var(--foreground)]">{paper.score.threshold_decision}</span>
        </div>
        <div className="text-sm text-[var(--foreground-muted)]">
          LLM delta: <span className="font-medium text-[var(--foreground)]">{paper.score.llm_rerank_delta}</span>
        </div>
      </CardFooter>
    </Card>
  );
}
