"use client";

import { useDeferredValue, useState } from "react";
import { useQuery } from "@tanstack/react-query";
import {
  ArrowDownWideNarrow,
  BrainCircuit,
  Search,
  Sparkles,
  TrendingUp,
} from "lucide-react";

import type { DateWindow, FeedSortOption } from "@/lib/api/types";
import { RESEARCH_CATEGORIES } from "@/lib/api/types";
import { listPapers } from "@/lib/api/papers";
import { Button } from "@/components/ui/button";
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";
import {
  DropdownMenu,
  DropdownMenuContent,
  DropdownMenuItem,
  DropdownMenuLabel,
  DropdownMenuRadioGroup,
  DropdownMenuRadioItem,
  DropdownMenuSeparator,
  DropdownMenuTrigger,
} from "@/components/ui/dropdown-menu";
import { Input } from "@/components/ui/input";
import {
  Select,
  SelectContent,
  SelectItem,
  SelectTrigger,
  SelectValue,
} from "@/components/ui/select";
import { PaperCard } from "@/components/workspace/PaperCard";

const minScoreOptions = [
  { label: "Any score", value: "0" },
  { label: "55+", value: "55" },
  { label: "65+", value: "65" },
  { label: "75+", value: "75" },
];

const dateWindowOptions: { label: string; value: DateWindow }[] = [
  { label: "Last 24h", value: "24h" },
  { label: "Last 72h", value: "72h" },
  { label: "Last 7 days", value: "7d" },
  { label: "Last 30 days", value: "30d" },
  { label: "Any time", value: "all" },
];

const sortLabels: Record<FeedSortOption, string> = {
  score_desc: "Score high to low",
  score_asc: "Score low to high",
  newest: "Newest first",
  oldest: "Oldest first",
};

export default function WorkspaceFeedPage() {
  const [search, setSearch] = useState("");
  const [category, setCategory] = useState<"all" | (typeof RESEARCH_CATEGORIES)[number]>("all");
  const [minScore, setMinScore] = useState("55");
  const [dateWindow, setDateWindow] = useState<DateWindow>("7d");
  const [sort, setSort] = useState<FeedSortOption>("score_desc");
  const deferredSearch = useDeferredValue(search);

  const paperQuery = useQuery({
    queryKey: ["papers", deferredSearch, category, minScore, dateWindow, sort],
    queryFn: () =>
      listPapers({
        search: deferredSearch,
        category,
        min_score: minScore === "0" ? undefined : Number(minScore),
        date_window: dateWindow,
        sort,
        per_page: 12,
      }),
  });
  const papers = paperQuery.data?.items ?? [];
  const averageScore = papers.length
    ? Math.round(papers.reduce((total, paper) => total + paper.score.total_score, 0) / papers.length)
    : 0;
  const digestCandidates = papers.filter((paper) => paper.score.total_score >= 75).length;

  return (
    <div className="space-y-6">
      <section className="grid gap-6 xl:grid-cols-[minmax(0,1.55fr)_minmax(320px,0.8fr)]">
        <Card className="overflow-hidden">
          <CardHeader className="gap-4">
            <div className="inline-flex w-fit items-center gap-2 rounded-full bg-[var(--primary-subtle)] px-3 py-1 text-xs font-semibold uppercase tracking-[0.2em] text-[var(--primary)]">
              <TrendingUp className="size-3.5" />
              Feed pulse
            </div>
            <CardTitle className="max-w-3xl text-3xl sm:text-4xl">
              Research triage should feel like a clear queue, not a pile of tabs.
            </CardTitle>
            <p className="max-w-3xl text-sm leading-7 text-[var(--foreground-muted)] sm:text-base">
              This mock feed mirrors the future backend schema: scored papers, explainable
              reasons, and enough metadata to decide what deserves a digest or deeper review.
            </p>
          </CardHeader>
          <CardContent className="grid gap-4 md:grid-cols-3">
            <div className="rounded-[22px] border border-[var(--border)] bg-[var(--surface-hover)]/75 p-4">
              <p className="text-xs font-semibold uppercase tracking-[0.18em] text-[var(--foreground-subtle)]">
                Visible papers
              </p>
              <p className="mt-3 font-[family:var(--font-display)] text-3xl font-semibold">
                {paperQuery.data?.total ?? 0}
              </p>
              <p className="mt-2 text-sm text-[var(--foreground-muted)]">
                Filtered by category, score band, and recency.
              </p>
            </div>
            <div className="rounded-[22px] border border-[var(--border)] bg-[var(--surface-hover)]/75 p-4">
              <p className="text-xs font-semibold uppercase tracking-[0.18em] text-[var(--foreground-subtle)]">
                Avg score
              </p>
              <p className="mt-3 font-[family:var(--font-display)] text-3xl font-semibold">
                {averageScore}
              </p>
              <p className="mt-2 text-sm text-[var(--foreground-muted)]">
                Good enough to spot whether the queue is drifting.
              </p>
            </div>
            <div className="rounded-[22px] border border-[var(--border)] bg-[var(--surface-hover)]/75 p-4">
              <p className="text-xs font-semibold uppercase tracking-[0.18em] text-[var(--foreground-subtle)]">
                Digest-ready
              </p>
              <p className="mt-3 font-[family:var(--font-display)] text-3xl font-semibold">
                {digestCandidates}
              </p>
              <p className="mt-2 text-sm text-[var(--foreground-muted)]">
                Papers already above the default digest threshold.
              </p>
            </div>
          </CardContent>
        </Card>

        <Card className="bg-[linear-gradient(160deg,rgba(15,23,42,0.98),rgba(23,37,84,0.92))] text-white shadow-[var(--shadow-lg)]">
          <CardHeader className="gap-3">
            <div className="inline-flex w-fit items-center gap-2 rounded-full bg-white/10 px-3 py-1 text-xs font-semibold uppercase tracking-[0.18em] text-white/80">
              <BrainCircuit className="size-3.5" />
              Explainability
            </div>
            <CardTitle className="text-2xl text-white">What the score actually means</CardTitle>
          </CardHeader>
          <CardContent className="space-y-3 text-sm text-slate-200">
            <div className="rounded-[20px] bg-white/6 px-4 py-3">
              Topical relevance remains dominant, so prestige cannot rescue irrelevant papers.
            </div>
            <div className="rounded-[20px] bg-white/6 px-4 py-3">
              Actionability rewards code, benchmarks, and project pages that speed up follow-up work.
            </div>
            <div className="rounded-[20px] bg-white/6 px-4 py-3">
              Matched rules are visible on every card so false positives are easy to tune later.
            </div>
          </CardContent>
        </Card>
      </section>

      <Card>
        <CardContent className="grid gap-4 pt-6 lg:grid-cols-[minmax(0,1.3fr)_repeat(3,minmax(0,0.8fr))_auto]">
          <div className="relative">
            <Search className="pointer-events-none absolute left-4 top-1/2 size-4 -translate-y-1/2 text-[var(--foreground-subtle)]" />
            <Input
              className="pl-11"
              placeholder="Search titles, authors, or abstract language"
              value={search}
              onChange={(event) => setSearch(event.target.value)}
            />
          </div>

          <Select value={category} onValueChange={(value) => setCategory(value as typeof category)}>
            <SelectTrigger>
              <SelectValue placeholder="Category" />
            </SelectTrigger>
            <SelectContent>
              <SelectItem value="all">All categories</SelectItem>
              {RESEARCH_CATEGORIES.map((item) => (
                <SelectItem key={item} value={item}>
                  {item}
                </SelectItem>
              ))}
            </SelectContent>
          </Select>

          <Select value={minScore} onValueChange={setMinScore}>
            <SelectTrigger>
              <SelectValue placeholder="Min score" />
            </SelectTrigger>
            <SelectContent>
              {minScoreOptions.map((option) => (
                <SelectItem key={option.value} value={option.value}>
                  {option.label}
                </SelectItem>
              ))}
            </SelectContent>
          </Select>

          <Select value={dateWindow} onValueChange={(value) => setDateWindow(value as DateWindow)}>
            <SelectTrigger>
              <SelectValue placeholder="Recency" />
            </SelectTrigger>
            <SelectContent>
              {dateWindowOptions.map((option) => (
                <SelectItem key={option.value} value={option.value}>
                  {option.label}
                </SelectItem>
              ))}
            </SelectContent>
          </Select>

          <DropdownMenu>
            <DropdownMenuTrigger asChild>
              <Button variant="secondary" className="justify-between">
                <ArrowDownWideNarrow className="size-4" />
                {sortLabels[sort]}
              </Button>
            </DropdownMenuTrigger>
            <DropdownMenuContent align="end">
              <DropdownMenuLabel>Sort feed</DropdownMenuLabel>
              <DropdownMenuSeparator />
              <DropdownMenuRadioGroup value={sort} onValueChange={(value) => setSort(value as FeedSortOption)}>
                {Object.entries(sortLabels).map(([value, label]) => (
                  <DropdownMenuRadioItem key={value} value={value}>
                    {label}
                  </DropdownMenuRadioItem>
                ))}
              </DropdownMenuRadioGroup>
              <DropdownMenuSeparator />
              <DropdownMenuItem
                onClick={() => {
                  setSearch("");
                  setCategory("all");
                  setMinScore("55");
                  setDateWindow("7d");
                  setSort("score_desc");
                }}
              >
                Reset filters
              </DropdownMenuItem>
            </DropdownMenuContent>
          </DropdownMenu>
        </CardContent>
      </Card>

      <div className="space-y-4">
        {paperQuery.isLoading ? (
          <Card>
            <CardContent className="pt-6 text-sm text-[var(--foreground-muted)]">
              Loading mock papers...
            </CardContent>
          </Card>
        ) : papers.length ? (
          papers.map((paper, index) => (
            <PaperCard key={paper.id} paper={paper} defaultExpanded={index === 0} />
          ))
        ) : (
          <Card>
            <CardContent className="flex flex-col items-center justify-center gap-3 py-14 text-center">
              <Sparkles className="size-6 text-[var(--accent)]" />
              <div>
                <p className="font-medium text-[var(--foreground)]">No papers match the current filter set.</p>
                <p className="mt-2 text-sm text-[var(--foreground-muted)]">
                  Try widening the score band or searching across more categories.
                </p>
              </div>
            </CardContent>
          </Card>
        )}
      </div>
    </div>
  );
}
