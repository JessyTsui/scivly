import Link from "next/link";
import { notFound } from "next/navigation";
import {
  ArrowLeft,
  ArrowUpRight,
  BookText,
  CalendarDays,
  Orbit,
  ScrollText,
  Sparkles,
} from "lucide-react";

import { SectionHeading } from "@/components/section-heading";
import { SignupCta } from "@/components/signup-cta";
import { Badge } from "@/components/ui/badge";
import { ApiError } from "@/lib/api/client";
import { getPublicPaper } from "@/lib/api/public-papers";
import type { PublicPaperOut } from "@/lib/api/types";
import { createMetadata } from "@/lib/metadata";
import { resolveArxivUrl, resolveDoiUrl } from "@/lib/public-library";
import { formatCalendarDate, formatRelativeDate } from "@/lib/utils";

export const dynamic = "force-dynamic";

type ParamsInput = Promise<{ id: string }>;

const categoryBadgeVariants = ["default", "info", "warning", "secondary", "success", "outline"] as const;

function formatApiError(error: unknown) {
  if (error instanceof ApiError) {
    return error.message;
  }

  if (error instanceof Error) {
    return error.message;
  }

  return "This paper could not be loaded right now.";
}

function isMissingPaperError(error: unknown) {
  return error instanceof ApiError && (error.status === 404 || error.status === 422);
}

async function loadPublicPaper(paperId: string) {
  try {
    return {
      paper: await getPublicPaper(paperId),
      error: null as string | null,
      missing: false,
    };
  } catch (error) {
    if (isMissingPaperError(error)) {
      return {
        paper: null as PublicPaperOut | null,
        error: null as string | null,
        missing: true,
      };
    }

    return {
      paper: null as PublicPaperOut | null,
      error: formatApiError(error),
      missing: false,
    };
  }
}

export async function generateMetadata({
  params,
}: {
  params: ParamsInput;
}) {
  const { id } = await params;
  const result = await loadPublicPaper(id);

  if (!result.paper) {
    return createMetadata({
      title: "Paper Library",
      description: "Browse public-safe paper records, summaries, and figure notes from Scivly.",
      path: `/papers/${id}`,
    });
  }

  return createMetadata({
    title: result.paper.title,
    description: result.paper.one_line_summary,
    path: `/papers/${id}`,
  });
}

export default async function PublicPaperDetailPage({
  params,
}: {
  params: ParamsInput;
}) {
  const { id } = await params;
  const result = await loadPublicPaper(id);

  if (result.missing) {
    notFound();
  }

  if (!result.paper) {
    return (
      <main>
        <section className="px-4 pb-20 pt-12 sm:px-6 lg:px-8">
          <div className="mx-auto max-w-4xl rounded-[36px] border border-amber-500/20 bg-amber-500/10 p-8">
            <p className="text-sm font-semibold uppercase tracking-[0.22em] text-amber-900 dark:text-amber-200">
              Public library unavailable
            </p>
            <h1 className="mt-4 font-[family:var(--font-display)] text-4xl font-semibold tracking-tight text-[var(--foreground)]">
              This paper could not be loaded.
            </h1>
            <p className="mt-4 text-base leading-7 text-[var(--foreground-muted)]">{result.error}</p>
            <div className="mt-8">
              <Link href="/papers" className="btn-secondary">
                <ArrowLeft className="h-4 w-4" />
                Back to library
              </Link>
            </div>
          </div>
        </section>

        <SignupCta
          title="Need monitored papers instead of one-off browsing?"
          body="Create a workspace to score new papers, route digests, and keep follow-up questions attached to the evidence trail."
          secondaryHref="/pricing"
          secondaryLabel="Compare plans"
        />
      </main>
    );
  }

  const paper = result.paper;
  const doiUrl = resolveDoiUrl(paper.doi);

  return (
    <main>
      <section className="px-4 pb-14 pt-12 sm:px-6 lg:px-8 lg:pb-16 lg:pt-18">
        <div className="mx-auto max-w-7xl">
          <Link href="/papers" className="inline-flex items-center gap-2 text-sm font-semibold text-[var(--primary-dark)]">
            <ArrowLeft className="h-4 w-4" />
            Back to public library
          </Link>

          <div className="mt-8 grid gap-8 xl:grid-cols-[minmax(0,1.08fr)_minmax(320px,0.92fr)]">
            <div className="animate-in">
              <div className="flex flex-wrap items-center gap-2">
                {paper.categories.map((item, index) => (
                  <Badge key={item} variant={categoryBadgeVariants[index % categoryBadgeVariants.length]}>
                    {item}
                  </Badge>
                ))}
              </div>

              {paper.title_zh ? (
                <p className="mt-6 text-base font-medium text-[var(--primary-dark)]">{paper.title_zh}</p>
              ) : null}

              <h1 className="mt-3 max-w-5xl font-[family:var(--font-display)] text-5xl font-semibold tracking-[-0.05em] text-[var(--foreground)] sm:text-6xl lg:leading-[0.94]">
                {paper.title}
              </h1>

              <p className="mt-6 max-w-3xl text-lg leading-8 text-[var(--foreground-muted)] sm:text-xl">
                {paper.one_line_summary}
              </p>

              <div className="mt-8 flex flex-wrap items-center gap-3 text-sm text-[var(--foreground-muted)]">
                <span>{paper.authors.map((author) => author.name).join(", ")}</span>
                <span className="text-[var(--border-strong)]">/</span>
                <span>
                  Published {formatCalendarDate(paper.published_at)} ({formatRelativeDate(paper.published_at)})
                </span>
              </div>

              <div className="mt-8 flex flex-wrap gap-3">
                <a
                  href={resolveArxivUrl(paper.arxiv_id)}
                  target="_blank"
                  rel="noreferrer"
                  className="btn-primary"
                >
                  Open arXiv
                  <ArrowUpRight className="h-4 w-4" />
                </a>
                {doiUrl ? (
                  <a href={doiUrl} target="_blank" rel="noreferrer" className="btn-secondary">
                    DOI
                    <ArrowUpRight className="h-4 w-4" />
                  </a>
                ) : null}
              </div>
            </div>

            <div className="animate-in-delay-1">
              <div className="card rounded-[32px] p-6 sm:p-7">
                <div className="flex items-center gap-3">
                  <div className="flex h-12 w-12 items-center justify-center rounded-2xl bg-[var(--primary-subtle)] text-[var(--primary-dark)]">
                    <Orbit className="h-5 w-5" />
                  </div>
                  <div>
                    <p className="text-xs font-semibold uppercase tracking-[0.22em] text-[var(--primary)]">
                      Metadata
                    </p>
                    <h2 className="mt-2 font-[family:var(--font-display)] text-3xl font-semibold tracking-tight">
                      Source record
                    </h2>
                  </div>
                </div>

                <div className="mt-7 space-y-4 text-sm">
                  {[
                    ["arXiv", `${paper.arxiv_id}v${paper.version}`],
                    ["Primary category", paper.primary_category],
                    ["Journal", paper.journal_ref ?? "Not listed"],
                    ["DOI", paper.doi ?? "Not listed"],
                    ["Updated", formatCalendarDate(paper.updated_at)],
                  ].map(([label, value]) => (
                    <div
                      key={label}
                      className="flex items-start justify-between gap-4 rounded-[22px] bg-[var(--surface-hover)]/82 px-4 py-3"
                    >
                      <span className="text-[var(--foreground-subtle)]">{label}</span>
                      <span className="text-right font-medium text-[var(--foreground)]">{value}</span>
                    </div>
                  ))}
                </div>

                {paper.comment ? (
                  <div className="mt-6 rounded-[24px] border border-dashed border-[var(--border-strong)] bg-[var(--surface)]/82 p-4">
                    <p className="text-xs font-semibold uppercase tracking-[0.2em] text-[var(--foreground-subtle)]">
                      Notes
                    </p>
                    <p className="mt-3 text-sm leading-7 text-[var(--foreground-muted)]">{paper.comment}</p>
                  </div>
                ) : null}
              </div>
            </div>
          </div>
        </div>
      </section>

      <section className="border-y border-[var(--border)] bg-[var(--surface)]/72 px-4 py-18 sm:px-6 lg:px-8 lg:py-20">
        <div className="mx-auto grid max-w-7xl gap-10 xl:grid-cols-[minmax(0,1.02fr)_minmax(320px,0.98fr)]">
          <div>
            <SectionHeading
              eyebrow="Abstract"
              title="A single page for the source text and its public-safe enrichment."
              body="Scivly keeps the original abstract visible, then layers translated context and structured highlights on top when enrichment data is available."
            />

            <div className="mt-10 space-y-6">
              <article className="card rounded-[32px] p-6 sm:p-7">
                <div className="flex items-center gap-3">
                  <BookText className="h-5 w-5 text-[var(--primary-dark)]" />
                  <h2 className="font-[family:var(--font-display)] text-2xl font-semibold tracking-tight">
                    Original abstract
                  </h2>
                </div>
                <p className="mt-5 text-base leading-8 text-[var(--foreground-muted)]">{paper.abstract}</p>
              </article>

              {paper.abstract_zh ? (
                <article className="card rounded-[32px] p-6 sm:p-7">
                  <div className="flex items-center gap-3">
                    <Sparkles className="h-5 w-5 text-[var(--accent)]" />
                    <h2 className="font-[family:var(--font-display)] text-2xl font-semibold tracking-tight">
                      Translated abstract
                    </h2>
                  </div>
                  <p className="mt-5 text-base leading-8 text-[var(--foreground-muted)]">
                    {paper.abstract_zh}
                  </p>
                </article>
              ) : null}
            </div>
          </div>

          <div className="space-y-6">
            <article className="card rounded-[32px] p-6 sm:p-7">
              <div className="flex items-center gap-3">
                <ScrollText className="h-5 w-5 text-[var(--primary-dark)]" />
                <h2 className="font-[family:var(--font-display)] text-2xl font-semibold tracking-tight">
                  Key points
                </h2>
              </div>

              <div className="mt-5 space-y-3">
                {(paper.key_points.length > 0 ? paper.key_points : [paper.one_line_summary]).map((point) => (
                  <div
                    key={point}
                    className="rounded-[22px] bg-[var(--surface-hover)]/82 px-4 py-4 text-sm leading-7 text-[var(--foreground-muted)]"
                  >
                    {point}
                  </div>
                ))}
              </div>
            </article>

            <article className="card rounded-[32px] p-6 sm:p-7">
              <div className="grid gap-4 sm:grid-cols-3">
                {[
                  ["Method", paper.method_summary ?? "No method summary has been extracted yet."],
                  ["Conclusion", paper.conclusion_summary ?? "No conclusion summary has been extracted yet."],
                  ["Limitations", paper.limitations ?? "No limitations note has been extracted yet."],
                ].map(([label, value]) => (
                  <div key={label} className="rounded-[24px] bg-[var(--surface-hover)]/82 p-4">
                    <p className="text-xs font-semibold uppercase tracking-[0.2em] text-[var(--foreground-subtle)]">
                      {label}
                    </p>
                    <p className="mt-3 text-sm leading-7 text-[var(--foreground-muted)]">{value}</p>
                  </div>
                ))}
              </div>
            </article>
          </div>
        </div>
      </section>

      <section className="px-4 py-18 sm:px-6 lg:px-8 lg:py-20">
        <div className="mx-auto max-w-7xl">
          <SectionHeading
            eyebrow="Figures"
            title="Figure descriptions stay attached to the paper record, even when the image asset is not public."
            body="The public surface exposes extracted figure notes and captions as structured reading aids, which is often enough to decide whether the full PDF deserves attention."
          />

          <div className="mt-10 grid gap-5 xl:grid-cols-2">
            {(paper.figures.length > 0
              ? paper.figures
              : [
                  {
                    label: "No extracted figures yet",
                    description:
                      "This record does not currently have public-safe figure descriptions attached to it.",
                  },
                ]).map((figure) => (
              <article
                key={`${figure.label}-${figure.description}`}
                className="card rounded-[32px] overflow-hidden"
              >
                <div className="h-32 bg-[linear-gradient(135deg,rgba(14,165,233,0.18),rgba(255,255,255,0.4),rgba(249,115,22,0.16))]" />
                <div className="p-6 sm:p-7">
                  <p className="text-xs font-semibold uppercase tracking-[0.22em] text-[var(--primary)]">
                    {figure.label}
                  </p>
                  <p className="mt-4 text-base leading-8 text-[var(--foreground-muted)]">
                    {figure.description}
                  </p>
                </div>
              </article>
            ))}
          </div>
        </div>
      </section>

      <section className="border-t border-[var(--border)] px-4 py-18 sm:px-6 lg:px-8 lg:py-20">
        <div className="mx-auto max-w-7xl">
          <SectionHeading
            eyebrow="Contributors"
            title="Author and source context stays visible on the public detail page."
            body="This keeps the public library readable without introducing workspace-only scoring or tenant-specific signals."
          />

          <div className="mt-10 grid gap-5 xl:grid-cols-[minmax(0,1.08fr)_minmax(320px,0.92fr)]">
            <article className="card rounded-[32px] p-6 sm:p-7">
              <h2 className="font-[family:var(--font-display)] text-2xl font-semibold tracking-tight">
                Authors
              </h2>
              <div className="mt-6 grid gap-4 md:grid-cols-2">
                {paper.authors.map((author) => (
                  <div key={`${author.name}-${author.affiliation ?? "na"}`} className="rounded-[24px] bg-[var(--surface-hover)]/82 p-4">
                    <p className="text-base font-semibold text-[var(--foreground)]">{author.name}</p>
                    <p className="mt-2 text-sm leading-7 text-[var(--foreground-muted)]">
                      {author.affiliation ?? "Affiliation not listed"}
                    </p>
                  </div>
                ))}
              </div>
            </article>

            <article className="card rounded-[32px] p-6 sm:p-7">
              <div className="flex items-center gap-3">
                <CalendarDays className="h-5 w-5 text-[var(--primary-dark)]" />
                <h2 className="font-[family:var(--font-display)] text-2xl font-semibold tracking-tight">
                  Archive timing
                </h2>
              </div>

              <div className="mt-6 space-y-4 text-sm">
                {[
                  ["Published", `${formatCalendarDate(paper.published_at)} (${formatRelativeDate(paper.published_at)})`],
                  ["Updated", `${formatCalendarDate(paper.updated_at)} (${formatRelativeDate(paper.updated_at)})`],
                  ["Public route", `/papers/${paper.id}`],
                ].map(([label, value]) => (
                  <div
                    key={label}
                    className="flex items-start justify-between gap-4 rounded-[22px] bg-[var(--surface-hover)]/82 px-4 py-3"
                  >
                    <span className="text-[var(--foreground-subtle)]">{label}</span>
                    <span className="text-right font-medium text-[var(--foreground)]">{value}</span>
                  </div>
                ))}
              </div>
            </article>
          </div>
        </div>
      </section>

      <SignupCta
        title="Need this archive to work like a team operating surface?"
        body="Scivly workspaces add monitored interests, scored queues, digests, and question answering on top of the same paper records."
        secondaryHref="/pricing"
        secondaryLabel="Explore pricing"
      />
    </main>
  );
}
