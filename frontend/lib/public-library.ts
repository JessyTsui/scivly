import type { DateWindow, PublicPaperListParams, PublicPaperSortOption } from "@/lib/api/types";

export const PUBLIC_LIBRARY_DATE_OPTIONS: Array<{ label: string; value: DateWindow }> = [
  { label: "Any time", value: "all" },
  { label: "Last 24h", value: "24h" },
  { label: "Last 72h", value: "72h" },
  { label: "Last 7 days", value: "7d" },
  { label: "Last 30 days", value: "30d" },
];

export const PUBLIC_LIBRARY_SORT_OPTIONS: Array<{
  label: string;
  value: PublicPaperSortOption;
}> = [
  { label: "Most relevant", value: "relevance" },
  { label: "Newest first", value: "newest" },
  { label: "Oldest first", value: "oldest" },
];

export function readFirstParam(value: string | string[] | undefined) {
  return Array.isArray(value) ? value[0] : value;
}

export function sanitizeQueryValue(value: string | undefined) {
  const trimmed = value?.trim();
  return trimmed ? trimmed : undefined;
}

export function normalizeDateWindow(value: string | undefined): DateWindow {
  if (PUBLIC_LIBRARY_DATE_OPTIONS.some((option) => option.value === value)) {
    return value as DateWindow;
  }

  return "all";
}

export function normalizePublicPaperSort(
  value: string | undefined,
  hasQuery: boolean
): PublicPaperSortOption {
  if (PUBLIC_LIBRARY_SORT_OPTIONS.some((option) => option.value === value)) {
    return value as PublicPaperSortOption;
  }

  return hasQuery ? "relevance" : "newest";
}

export function parsePositivePage(value: string | undefined) {
  const parsed = Number(value);
  return Number.isInteger(parsed) && parsed > 0 ? parsed : 1;
}

export function buildPublicPaperHref(
  params: PublicPaperListParams,
  overrides: Partial<PublicPaperListParams> = {}
) {
  const merged = { ...params, ...overrides };
  const searchParams = new URLSearchParams();

  for (const [key, value] of Object.entries(merged)) {
    if (value === undefined || value === null || value === "" || value === "all") {
      continue;
    }

    searchParams.set(key, String(value));
  }

  const query = searchParams.toString();
  return query ? `/papers?${query}` : "/papers";
}

export function resolveArxivUrl(arxivId: string) {
  return `https://arxiv.org/abs/${encodeURIComponent(arxivId)}`;
}

export function resolveDoiUrl(doi: string | null | undefined) {
  return doi ? `https://doi.org/${encodeURIComponent(doi)}` : null;
}
