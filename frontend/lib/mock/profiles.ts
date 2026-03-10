import type {
  AuthorWatchlistOut,
  NotificationChannelOut,
  TopicProfileOut,
  WorkspaceSummary,
} from "@/lib/api/types";
import { daysAgo } from "@/lib/mock/time";

export const DEMO_WORKSPACE_ID = "workspace-signal-lab";

export const mockWorkspace: WorkspaceSummary = {
  id: DEMO_WORKSPACE_ID,
  name: "Signal Lab",
  slug: "signal-lab",
  plan: "Research Pro",
  role: "owner",
  owner_name: "Jessy Tsui",
  description:
    "A personal research workspace for triaging agent papers, digesting daily experiments, and keeping follow-up Q&A close to source evidence.",
};

export const mockProfiles: TopicProfileOut[] = [
  {
    id: "profile-scientific-qa",
    workspace_id: DEMO_WORKSPACE_ID,
    name: "Scientific QA Systems",
    description:
      "Track retrieval, verification, and benchmark work that improves question answering on papers, tables, and long-form scientific context.",
    categories: ["cs.AI", "cs.CL", "cs.IR"],
    keywords: ["scientific qa", "retrieval", "verification", "benchmark", "tool use"],
    is_default: true,
    created_at: daysAgo(8),
    match_count_24h: 7,
  },
  {
    id: "profile-vlm-agents",
    workspace_id: DEMO_WORKSPACE_ID,
    name: "Vision-Language Agents",
    description:
      "Prioritize multimodal agent papers that mention grounding, figure understanding, embodied evaluation, or visual planning loops.",
    categories: ["cs.AI", "cs.CV", "cs.RO"],
    keywords: ["multimodal", "vision-language", "grounding", "embodied", "figure reasoning"],
    is_default: false,
    created_at: daysAgo(6),
    match_count_24h: 5,
  },
  {
    id: "profile-long-context",
    workspace_id: DEMO_WORKSPACE_ID,
    name: "Long-Context Efficiency",
    description:
      "Watch adapters, memory, distillation, and efficiency work that makes long-context research analysis affordable.",
    categories: ["cs.CL", "cs.LG", "stat.ML"],
    keywords: ["long context", "memory", "adapter", "distillation", "sparse"],
    is_default: false,
    created_at: daysAgo(5),
    match_count_24h: 4,
  },
];

export const mockAuthorWatchlist: AuthorWatchlistOut[] = [
  {
    id: "author-percy-liang",
    workspace_id: DEMO_WORKSPACE_ID,
    author_name: "Percy Liang",
    notes: "Usually yields benchmark and evaluation methodology updates worth digesting.",
  },
  {
    id: "author-tianyi-zhang",
    workspace_id: DEMO_WORKSPACE_ID,
    author_name: "Tianyi Zhang",
    notes: "Track software engineering and scientific reasoning crossover work.",
  },
  {
    id: "author-sergey-levine",
    workspace_id: DEMO_WORKSPACE_ID,
    author_name: "Sergey Levine",
    notes: "Useful proxy for embodied agent and robotics-adjacent evaluation papers.",
  },
];

export const mockNotificationChannels: NotificationChannelOut[] = [
  {
    id: "channel-email-brief",
    workspace_id: DEMO_WORKSPACE_ID,
    channel_type: "email",
    label: "Morning brief",
    config: {
      target: "jessy@signal-lab.dev",
      window: "09:00 Asia/Shanghai",
    },
    is_active: true,
  },
  {
    id: "channel-webhook-sync",
    workspace_id: DEMO_WORKSPACE_ID,
    channel_type: "webhook",
    label: "Research queue webhook",
    config: {
      target: "https://hooks.signal-lab.dev/scivly/research",
      window: "send immediately",
    },
    is_active: true,
  },
  {
    id: "channel-telegram",
    workspace_id: DEMO_WORKSPACE_ID,
    channel_type: "telegram",
    label: "Quiet mobile alert",
    config: {
      target: "@signal_lab_digest",
      window: "only score >= 80",
    },
    is_active: false,
  },
];
