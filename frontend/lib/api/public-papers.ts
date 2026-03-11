import { z } from "zod";

import { apiRequest } from "@/lib/api/client";
import type { PaginatedResponse, PublicPaperListParams, PublicPaperOut } from "@/lib/api/types";

const authorSchema = z.object({
  name: z.string(),
  affiliation: z.string().nullable().optional(),
});

const publicPaperFigureSchema = z.object({
  label: z.string(),
  description: z.string(),
});

const publicPaperSchema: z.ZodType<PublicPaperOut> = z.object({
  id: z.string().uuid(),
  arxiv_id: z.string(),
  version: z.number().int().positive(),
  title: z.string(),
  abstract: z.string(),
  authors: z.array(authorSchema),
  categories: z.array(z.string()),
  primary_category: z.string(),
  comment: z.string().nullable().optional(),
  journal_ref: z.string().nullable().optional(),
  doi: z.string().nullable().optional(),
  published_at: z.string(),
  updated_at: z.string(),
  title_zh: z.string().nullable().optional(),
  abstract_zh: z.string().nullable().optional(),
  one_line_summary: z.string(),
  key_points: z.array(z.string()),
  method_summary: z.string().nullable().optional(),
  conclusion_summary: z.string().nullable().optional(),
  limitations: z.string().nullable().optional(),
  figures: z.array(publicPaperFigureSchema),
});

const paginatedPublicPaperSchema: z.ZodType<PaginatedResponse<PublicPaperOut>> = z.object({
  items: z.array(publicPaperSchema),
  total: z.number().int().nonnegative(),
  page: z.number().int().positive(),
  per_page: z.number().int().positive(),
});

const NO_STORE_OPTIONS = { cache: "no-store" as const };

export async function listPublicPapers(
  params: PublicPaperListParams = {}
): Promise<PaginatedResponse<PublicPaperOut>> {
  return apiRequest<PaginatedResponse<PublicPaperOut>>("/public/papers", {
    ...NO_STORE_OPTIONS,
    query: params,
    schema: paginatedPublicPaperSchema,
  });
}

export async function searchPublicPapers(
  params: PublicPaperListParams & { q: string }
): Promise<PaginatedResponse<PublicPaperOut>> {
  return apiRequest<PaginatedResponse<PublicPaperOut>>("/public/papers/search", {
    ...NO_STORE_OPTIONS,
    query: params,
    schema: paginatedPublicPaperSchema,
  });
}

export async function getPublicPaper(paperId: string): Promise<PublicPaperOut> {
  return apiRequest<PublicPaperOut>(`/public/papers/${paperId}`, {
    ...NO_STORE_OPTIONS,
    schema: publicPaperSchema,
  });
}
