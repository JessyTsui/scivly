export type ApiDateString = string;

export type WorkspaceRole = "owner" | "admin" | "member";
export type WorkspacePlan = "Personal" | "Research Pro" | "Lab";
export type NotificationChannelType = "email" | "telegram" | "discord" | "webhook";
export type DigestStatus = "draft" | "sent" | "failed";
export type PaperDecision =
  | "drop"
  | "metadata_only"
  | "pdf_queue"
  | "rerank"
  | "digest_candidate"
  | "source_fetch";
export type ChatRole = "user" | "assistant";
export type FeedSortOption = "score_desc" | "score_asc" | "newest" | "oldest";
export type DateWindow = "24h" | "72h" | "7d" | "30d" | "all";

export type ArxivCategory =
  | "cs.AI"
  | "cs.CL"
  | "cs.CV"
  | "cs.IR"
  | "cs.LG"
  | "cs.RO"
  | "stat.ML";

export const RESEARCH_CATEGORIES: ArxivCategory[] = [
  "cs.AI",
  "cs.CL",
  "cs.CV",
  "cs.IR",
  "cs.LG",
  "cs.RO",
  "stat.ML",
];

export interface PaginatedResponse<T> {
  items: T[];
  total: number;
  page: number;
  per_page: number;
}

export interface WorkspaceSummary {
  id: string;
  name: string;
  slug: string;
  plan: WorkspacePlan;
  role: WorkspaceRole;
  owner_name: string;
  description: string;
}

export interface AuthorInfo {
  name: string;
  affiliation?: string | null;
}

export interface PaperScoreMatchedRules {
  positive: string[];
  negative: string[];
}

export interface PaperScoreOut {
  id: string;
  paper_id: string;
  workspace_id: string;
  profile_id: string;
  score_version: string;
  total_score: number;
  topical_relevance: number;
  prestige_priors: number;
  actionability: number;
  profile_fit: number;
  novelty_diversity: number;
  penalties: number;
  matched_rules: PaperScoreMatchedRules;
  threshold_decision: PaperDecision;
  llm_rerank_delta: number;
  llm_rerank_reasons: string[];
  created_at: ApiDateString;
}

export interface PaperOut {
  id: string;
  arxiv_id: string;
  version: number;
  title: string;
  abstract: string;
  authors: AuthorInfo[];
  categories: ArxivCategory[];
  primary_category: ArxivCategory;
  comment?: string | null;
  journal_ref?: string | null;
  doi?: string | null;
  published_at: ApiDateString;
  updated_at: ApiDateString;
  title_zh?: string | null;
  abstract_zh?: string | null;
  one_line_summary: string;
  key_points: string[];
  method_summary?: string | null;
  conclusion_summary?: string | null;
  limitations?: string | null;
  figure_descriptions: string[];
  profile_labels: string[];
  score: PaperScoreOut;
}

export interface PaperListParams {
  page?: number;
  per_page?: number;
  category?: ArxivCategory | "all";
  min_score?: number;
  sort?: FeedSortOption;
  date_window?: DateWindow;
  search?: string;
}

export interface TopicProfileOut {
  id: string;
  workspace_id: string;
  name: string;
  description: string;
  categories: ArxivCategory[];
  keywords: string[];
  is_default: boolean;
  created_at: ApiDateString;
  match_count_24h: number;
}

export interface TopicProfileCreate {
  name: string;
  description: string;
  categories: ArxivCategory[];
  keywords: string[];
}

export interface AuthorWatchlistOut {
  id: string;
  workspace_id: string;
  author_name: string;
  arxiv_author_id?: string | null;
  notes?: string | null;
}

export interface AuthorWatchCreate {
  author_name: string;
  notes?: string;
}

export interface NotificationChannelOut {
  id: string;
  workspace_id: string;
  channel_type: NotificationChannelType;
  label: string;
  config: Record<string, string>;
  is_active: boolean;
}

export interface NotificationChannelUpdate {
  id: string;
  label?: string;
  config?: Record<string, string>;
  is_active?: boolean;
}

export interface DigestSection {
  id: string;
  title: string;
  summary: string;
  papers: PaperOut[];
}

export interface DigestContent {
  title: string;
  overview: string;
  sections: DigestSection[];
}

export interface DigestOut {
  id: string;
  workspace_id: string;
  schedule_id: string;
  period_start: ApiDateString;
  period_end: ApiDateString;
  paper_ids: string[];
  paper_count: number;
  content: DigestContent;
  status: DigestStatus;
  created_at: ApiDateString;
  sent_at?: ApiDateString | null;
}

export interface DigestScheduleOut {
  id: string;
  workspace_id: string;
  cron_expression: string;
  timezone: string;
  channel_ids: string[];
  channel_labels: string[];
  is_active: boolean;
  cadence_label: string;
  created_at: ApiDateString;
  next_run_at: ApiDateString;
}

export interface DigestScheduleUpdate {
  cron_expression?: string;
  timezone?: string;
  channel_ids?: string[];
  channel_labels?: string[];
  is_active?: boolean;
  cadence_label?: string;
  next_run_at?: ApiDateString;
}

export interface ChatMessageOut {
  id: string;
  role: ChatRole;
  content: string;
  created_at: ApiDateString;
  model?: string;
}

export interface ChatSessionOut {
  id: string;
  workspace_id: string;
  paper_id: string;
  title: string;
  model: string;
  created_at: ApiDateString;
  messages: ChatMessageOut[];
}
