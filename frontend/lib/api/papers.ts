import { apiRequest, isMockApiEnabled } from "@/lib/api/client";
import type { PaginatedResponse, PaperListParams, PaperOut, PaperScoreOut } from "@/lib/api/types";
import { mockPapers } from "@/lib/mock/papers";

function clone<T>(value: T): T {
  return structuredClone(value);
}

function applyDateWindow(date: string, window: PaperListParams["date_window"]) {
  if (!window || window === "all") {
    return true;
  }

  const hoursMap: Record<Exclude<PaperListParams["date_window"], "all" | undefined>, number> = {
    "24h": 24,
    "72h": 72,
    "7d": 24 * 7,
    "30d": 24 * 30,
  };

  const cutoff = Date.now() - hoursMap[window] * 60 * 60 * 1000;
  return new Date(date).getTime() >= cutoff;
}

function sortPapers(items: PaperOut[], sort: PaperListParams["sort"]) {
  const sorted = [...items];

  switch (sort) {
    case "score_asc":
      sorted.sort((left, right) => left.score.total_score - right.score.total_score);
      break;
    case "newest":
      sorted.sort((left, right) => +new Date(right.published_at) - +new Date(left.published_at));
      break;
    case "oldest":
      sorted.sort((left, right) => +new Date(left.published_at) - +new Date(right.published_at));
      break;
    case "score_desc":
    default:
      sorted.sort((left, right) => right.score.total_score - left.score.total_score);
      break;
  }

  return sorted;
}

export async function listPapers(
  params: PaperListParams = {}
): Promise<PaginatedResponse<PaperOut>> {
  if (!isMockApiEnabled()) {
    return apiRequest<PaginatedResponse<PaperOut>>("/papers", { query: params });
  }

  const filtered = mockPapers.filter((paper) => {
    const search = params.search?.trim().toLowerCase();
    const haystack = `${paper.title} ${paper.abstract} ${paper.authors.map((author) => author.name).join(" ")}`.toLowerCase();

    if (search && !haystack.includes(search)) {
      return false;
    }

    if (params.category && params.category !== "all" && !paper.categories.includes(params.category)) {
      return false;
    }

    if (params.min_score && paper.score.total_score < params.min_score) {
      return false;
    }

    return applyDateWindow(paper.published_at, params.date_window);
  });

  const sorted = sortPapers(filtered, params.sort);
  const page = params.page ?? 1;
  const perPage = params.per_page ?? 10;
  const start = (page - 1) * perPage;

  return {
    items: clone(sorted.slice(start, start + perPage)),
    total: sorted.length,
    page,
    per_page: perPage,
  };
}

export async function getPaper(paperId: string): Promise<PaperOut> {
  if (!isMockApiEnabled()) {
    return apiRequest<PaperOut>(`/papers/${paperId}`);
  }

  const paper = mockPapers.find((item) => item.id === paperId);

  if (!paper) {
    throw new Error(`Paper ${paperId} was not found in mock data.`);
  }

  return clone(paper);
}

export async function getPaperScores(paperId: string): Promise<PaperScoreOut> {
  const paper = await getPaper(paperId);
  return clone(paper.score);
}
