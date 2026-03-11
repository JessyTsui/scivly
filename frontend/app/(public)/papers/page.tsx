import Link from "next/link";
import { ArrowRight, BookOpenText, CalendarDays, Layers3, Search, Sparkles } from "lucide-react";

import { SectionHeading } from "@/components/section-heading";
import { SignupCta } from "@/components/signup-cta";
import { Badge } from "@/components/ui/badge";
import { Input } from "@/components/ui/input";
import { ApiError } from "@/lib/api/client";
import { listPublicPapers, searchPublicPapers } from "@/lib/api/public-papers";
import type { PublicPaperListParams, PublicPaperOut } from "@/lib/api/types";
import { createMetadata } from "@/lib/metadata";
import {
  PUBLIC_LIBRARY_DATE_OPTIONS,
  PUBLIC_LIBRARY_SORT_OPTIONS,
  buildPublicPaperHref,
  normalizeDateWindow,
  normalizePublicPaperSort,
  parsePositivePage,
  readFirstParam,
  resolveArxivUrl,
  sanitizeQueryValue,
} from "@/lib/public-library";
import { formatCalendarDate, formatRelativeDate } from "@/lib/utils";

export const metadata = createMetadata({
  title: "Public Paper Library",
  description:
    "Browse Scivly's public-safe paper library with open access summaries, author and category filters, and semantic search.",
  path: "/papers",
});

export const dynamic = "force-dynamic";

type SearchParamsInput = Promise<Record<string, string | string[] | undefined>>;

const categoryBadgeVariants = ["default", "info", "warning", "secondary", "success", "outline"] as const;
const emptyLibrary = {
  items: [] as PublicPaperOut[],
  total: 0,
  page: 1,
  per_page: 12,
};

function formatApiError(error: unknown) {
  if (error instanceof ApiError) {
    return error.message;
  }

  if (error instanceof Error) {
    return error.message;
  }

  return "The public paper library is temporarily unavailable.";
}

export default async function PublicPaperLibraryPage({
  searchParams,
}: {
  searchParams: SearchParamsInput;
}) {
  const params = await searchParams;
  const q = sanitizeQueryValue(readFirstParam(params.q));
  const author = sanitizeQueryValue(readFirstParam(params.author));
  const category = sanitizeQueryValue(readFirstParam(params.category));
  const dateWindow = normalizeDateWindow(readFirstParam(params.date_window));
  const sort = normalizePublicPaperSort(readFirstParam(params.sort), Boolean(q));
  const page = parsePositivePage(readFirstParam(params.page));

  const filters: PublicPaperListParams = {
    q,
    author,
    category,
    date_window: dateWindow,
    sort,
    page,
    per_page: 12,
  };

  let library = emptyLibrary;
  let fetchError: string | null = null;

  try {
    library = q
      ? await searchPublicPapers({ ...filters, q })
      : await listPublicPapers(filters);
  } catch (error) {
    fetchError = formatApiError(error);
  }

  const totalPages = Math.max(1, Math.ceil(Math.max(library.total, 1) / library.per_page));
  const visibleCategories = Array.from(
    new Set([
      ...library.items.flatMap((paper) => paper.categories),
      ...(category ? [category] : []),
    ])
  )
    .filter(Boolean)
    .sort();
  const sortOptions = q
    ? PUBLIC_LIBRARY_SORT_OPTIONS
    : PUBLIC_LIBRARY_SORT_OPTIONS.filter((option) => option.value !== "relevance");
  const papersWithFigures = library.items.filter((paper) => paper.figures.length > 0).length;

  return (
    <main>
      <section className="px-4 pb-14 pt-12 sm:px-6 lg:px-8 lg:pb-16 lg:pt-18">
        <div className="mx-auto grid max-w-7xl gap-8 lg:grid-cols-[1.08fr_0.92fr] lg:items-start">
          <div className="animate-in">
            <div className="inline-flex items-center gap-2 rounded-full border border-[var(--border)] bg-[var(--surface)]/88 px-4 py-2 text-sm font-medium text-[var(--foreground-muted)] shadow-[var(--shadow-sm)] backdrop-blur">
              <span className="h-2.5 w-2.5 rounded-full bg-[var(--accent)]" />
              Public-safe research archive
            </div>

            <h1 className="mt-7 max-w-4xl font-[family:var(--font-display)] text-5xl font-semibold tracking-[-0.06em] text-[var(--foreground)] sm:text-6xl lg:leading-[0.95]">
              Browse papers the same way Scivly turns raw research into a readable surface.
            </h1>

            <p className="mt-6 max-w-3xl text-lg leading-8 text-[var(--foreground-muted)] sm:text-xl">
              Search by title or concept, narrow by author, category, and recency, then open a
              paper page that keeps the summary, figures, and source metadata in one place.
            </p>

            <div className="mt-10 grid gap-4 sm:grid-cols-3">
              {[
                {
                  label: "papers in the current result set",
                  value: library.total.toString(),
                  icon: BookOpenText,
                },
                {
                  label: "results with extracted figure notes",
                  value: papersWithFigures.toString(),
                  icon: Sparkles,
                },
                {
                  label: q ? "semantic search is active" : "latest archive view",
                  value: q ? "ON" : "LIVE",
                  icon: Layers3,
                },
              ].map((stat) => {
                const Icon = stat.icon;

                return (
                  <div key={stat.label} className="card rounded-[28px] p-5">
                    <div className="flex items-center justify-between gap-3">
                      <p className="text-xs font-semibold uppercase tracking-[0.22em] text-[var(--foreground-subtle)]">
                        {stat.label}
                      </p>
                      <div className="flex h-10 w-10 items-center justify-center rounded-2xl bg-[var(--primary-subtle)] text-[var(--primary-dark)]">
                        <Icon className="h-4 w-4" />
                      </div>
                    </div>
                    <p className="mt-5 font-[family:var(--font-display)] text-3xl font-semibold tracking-tight text-[var(--foreground)]">
                      {stat.value}
                    </p>
                  </div>
                );
              })}
            </div>
          </div>

          <div className="animate-in-delay-1">
            <div className="card rounded-[32px] p-6 sm:p-7">
              <div className="flex items-center gap-3">
                <div className="flex h-12 w-12 items-center justify-center rounded-2xl bg-[var(--primary-subtle)] text-[var(--primary-dark)]">
                  <Search className="h-5 w-5" />
                </div>
                <div>
                  <p className="text-xs font-semibold uppercase tracking-[0.22em] text-[var(--primary)]">
                    Explore the library
                  </p>
                  <h2 className="mt-2 font-[family:var(--font-display)] text-3xl font-semibold tracking-tight">
                    Search-ready and shareable
                  </h2>
                </div>
              </div>

              <form action="/papers" method="get" className="mt-7 grid gap-4">
                <div>
                  <label htmlFor="q" className="mb-2 block text-sm font-medium text-[var(--foreground)]">
                    Title or concept
                  </label>
                  <Input
                    id="q"
                    name="q"
                    defaultValue={q}
                    placeholder="Agentic retrieval, diffusion policy, world models..."
                  />
                </div>

                <div className="grid gap-4 sm:grid-cols-2">
                  <div>
                    <label htmlFor="author" className="mb-2 block text-sm font-medium text-[var(--foreground)]">
                      Author
                    </label>
                    <Input
                      id="author"
                      name="author"
                      defaultValue={author}
                      placeholder="Sara Hooker, Chelsea Finn..."
                    />
                  </div>

                  <div>
                    <label htmlFor="category" className="mb-2 block text-sm font-medium text-[var(--foreground)]">
                      Category
                    </label>
                    <Input
                      id="category"
                      name="category"
                      defaultValue={category}
                      placeholder="cs.CL, cs.LG, stat.ML..."
                    />
                  </div>
                </div>

                <div className="grid gap-4 sm:grid-cols-2">
                  <div>
                    <label htmlFor="date_window" className="mb-2 block text-sm font-medium text-[var(--foreground)]">
                      Date window
                    </label>
                    <select
                      id="date_window"
                      name="date_window"
                      defaultValue={dateWindow}
                      className="min-h-11 w-full rounded-2xl border border-[var(--border)] bg-[var(--surface)]/88 px-4 py-2.5 text-sm text-[var(--foreground)] shadow-[var(--shadow-sm)] outline-none focus:border-[var(--primary)]/35 focus:ring-2 focus:ring-[var(--primary)]/12"
                    >
                      {PUBLIC_LIBRARY_DATE_OPTIONS.map((option) => (
                        <option key={option.value} value={option.value}>
                          {option.label}
                        </option>
                      ))}
                    </select>
                  </div>

                  <div>
                    <label htmlFor="sort" className="mb-2 block text-sm font-medium text-[var(--foreground)]">
                      Sort
                    </label>
                    <select
                      id="sort"
                      name="sort"
                      defaultValue={sort}
                      className="min-h-11 w-full rounded-2xl border border-[var(--border)] bg-[var(--surface)]/88 px-4 py-2.5 text-sm text-[var(--foreground)] shadow-[var(--shadow-sm)] outline-none focus:border-[var(--primary)]/35 focus:ring-2 focus:ring-[var(--primary)]/12"
                    >
                      {sortOptions.map((option) => (
                        <option key={option.value} value={option.value}>
                          {option.label}
                        </option>
                      ))}
                    </select>
                  </div>
                </div>

                <div className="mt-2 flex flex-col gap-3 sm:flex-row">
                  <button type="submit" className="btn-primary justify-center">
                    Browse library
                    <ArrowRight className="h-4 w-4" />
                  </button>
                  <Link href="/papers" className="btn-secondary justify-center">
                    Reset filters
                  </Link>
                </div>
              </form>
            </div>
          </div>
        </div>
      </section>

      <section className="border-y border-[var(--border)] bg-[var(--surface)]/72 px-4 py-18 sm:px-6 lg:px-8 lg:py-20">
        <div className="mx-auto max-w-7xl">
          <SectionHeading
            eyebrow={q ? "Semantic Results" : "Latest Papers"}
            title={
              q
                ? `Results for “${q}”`
                : "A public research shelf designed for scanning before you commit to deeper review."
            }
            body={
              q
                ? "Semantic search is ranked against the indexed paper corpus, then narrowed by your public filters."
                : "The public library emphasizes readability: brief summaries, visible provenance, and enough structure to decide what to open next."
            }
          />

          {visibleCategories.length > 0 ? (
            <div className="mt-8 flex flex-wrap gap-2">
              {visibleCategories.map((item, index) => (
                <Link
                  key={item}
                  href={buildPublicPaperHref(filters, { category: item, page: 1 })}
                  className="focus-visible:outline focus-visible:outline-2 focus-visible:outline-offset-2 focus-visible:outline-[var(--primary)]"
                >
                  <Badge variant={categoryBadgeVariants[index % categoryBadgeVariants.length]}>
                    {item}
                  </Badge>
                </Link>
              ))}
            </div>
          ) : null}

          {fetchError ? (
            <div className="mt-10 rounded-[30px] border border-amber-500/20 bg-amber-500/10 p-6 text-sm text-amber-900 dark:text-amber-200">
              {fetchError}
            </div>
          ) : null}

          {!fetchError && library.items.length === 0 ? (
            <div className="mt-10 card rounded-[32px] p-8 text-center">
              <p className="text-sm font-semibold uppercase tracking-[0.22em] text-[var(--foreground-subtle)]">
                No matches yet
              </p>
              <h2 className="mt-4 font-[family:var(--font-display)] text-3xl font-semibold tracking-tight">
                Try a broader title phrase or remove one of the filters.
              </h2>
              <p className="mt-4 text-base leading-7 text-[var(--foreground-muted)]">
                Public library search currently indexes titles, abstracts, authors, and enrichment
                summaries where available.
              </p>
            </div>
          ) : null}

          <div className="mt-10 grid gap-5 xl:grid-cols-2">
            {library.items.map((paper) => (
              <article key={paper.id} className="card card-hover rounded-[32px] p-6 sm:p-7">
                <div className="flex flex-wrap items-center gap-2">
                  {paper.categories.slice(0, 3).map((item, index) => (
                    <Badge key={item} variant={categoryBadgeVariants[index % categoryBadgeVariants.length]}>
                      {item}
                    </Badge>
                  ))}
                  {paper.figures.length > 0 ? (
                    <span className="rounded-full border border-[var(--border)] bg-[var(--surface-hover)] px-3 py-1 text-xs font-medium text-[var(--foreground-muted)]">
                      {paper.figures.length} figure note{paper.figures.length > 1 ? "s" : ""}
                    </span>
                  ) : null}
                </div>

                <div className="mt-5">
                  {paper.title_zh ? (
                    <p className="text-sm font-medium text-[var(--primary-dark)]">{paper.title_zh}</p>
                  ) : null}
                  <h2 className="mt-2 font-[family:var(--font-display)] text-3xl font-semibold tracking-tight text-[var(--foreground)]">
                    <Link href={`/papers/${paper.id}`} className="hover:text-[var(--primary-dark)]">
                      {paper.title}
                    </Link>
                  </h2>
                  <p className="mt-3 text-sm leading-7 text-[var(--foreground-muted)]">
                    {paper.authors.map((authorItem) => authorItem.name).join(", ")}
                  </p>
                </div>

                <div className="mt-5 grid gap-3 sm:grid-cols-2">
                  <div className="rounded-[22px] bg-[var(--surface-hover)]/85 p-4">
                    <p className="text-xs font-semibold uppercase tracking-[0.2em] text-[var(--foreground-subtle)]">
                      Summary
                    </p>
                    <p className="mt-3 text-sm leading-7 text-[var(--foreground)]">
                      {paper.one_line_summary}
                    </p>
                  </div>
                  <div className="rounded-[22px] bg-[var(--surface-hover)]/85 p-4">
                    <div className="flex items-center gap-2 text-xs font-semibold uppercase tracking-[0.2em] text-[var(--foreground-subtle)]">
                      <CalendarDays className="h-3.5 w-3.5" />
                      Published
                    </div>
                    <p className="mt-3 text-sm font-medium text-[var(--foreground)]">
                      {formatCalendarDate(paper.published_at)}
                    </p>
                    <p className="mt-1 text-xs text-[var(--foreground-muted)]">
                      {formatRelativeDate(paper.published_at)}
                    </p>
                  </div>
                </div>

                <div className="mt-6 flex flex-wrap items-center gap-3">
                  <Link href={`/papers/${paper.id}`} className="btn-primary text-sm">
                    Open paper
                    <ArrowRight className="h-4 w-4" />
                  </Link>
                  <a
                    href={resolveArxivUrl(paper.arxiv_id)}
                    target="_blank"
                    rel="noreferrer"
                    className="btn-secondary text-sm"
                  >
                    arXiv {paper.arxiv_id}
                  </a>
                </div>
              </article>
            ))}
          </div>

          {library.items.length > 0 ? (
            <div className="mt-10 flex flex-col gap-4 rounded-[30px] border border-[var(--border)] bg-[var(--surface)]/78 p-5 sm:flex-row sm:items-center sm:justify-between">
              <p className="text-sm text-[var(--foreground-muted)]">
                Page {library.page} of {totalPages}
              </p>
              <div className="flex flex-wrap gap-3">
                {library.page > 1 ? (
                  <Link
                    href={buildPublicPaperHref(filters, { page: library.page - 1 })}
                    className="btn-secondary text-sm"
                  >
                    Previous
                  </Link>
                ) : (
                  <span className="btn-secondary cursor-not-allowed justify-center text-sm opacity-50">
                    Previous
                  </span>
                )}

                {library.page < totalPages ? (
                  <Link
                    href={buildPublicPaperHref(filters, { page: library.page + 1 })}
                    className="btn-primary text-sm"
                  >
                    Next page
                    <ArrowRight className="h-4 w-4" />
                  </Link>
                ) : null}
              </div>
            </div>
          ) : null}
        </div>
      </section>

      <SignupCta
        title="Turn the public library into a monitored workspace."
        body="Create a workspace when you want digests, routing rules, scored queues, and paper-level question answering on top of the same research stream."
        secondaryHref="/pricing"
        secondaryLabel="See plans"
      />
    </main>
  );
}
