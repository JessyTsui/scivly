import type { LucideIcon } from "lucide-react";
import {
  BellRing,
  BookOpenText,
  BrainCircuit,
  DatabaseZap,
  Radar,
  Send,
  Telescope,
  Workflow,
} from "lucide-react";

export const navigation = [
  { label: "Product", href: "#product" },
  { label: "Workflow", href: "#workflow" },
  { label: "Docs", href: "/docs" },
  { label: "Console", href: "/admin" },
];

export type Pillar = {
  title: string;
  description: string;
  detail: string;
  icon: LucideIcon;
};

export const productPillars: Pillar[] = [
  {
    title: "Monitor the right sources",
    description:
      "Track authors, labs, topics, and watchlists instead of refreshing arXiv tabs all day.",
    detail: "Feeds, saved searches, and workspace-specific rules run in one ingestion layer.",
    icon: Radar,
  },
  {
    title: "Turn papers into briefings",
    description:
      "Generate translated summaries, method snapshots, and figure-first highlights that are easy to scan.",
    detail: "Every paper lands with structured context instead of raw PDFs and guesswork.",
    icon: BrainCircuit,
  },
  {
    title: "Deliver signal, not noise",
    description:
      "Pipe results into digests, channels, and alerts with a delivery trail your team can audit.",
    detail: "Email, chat, and webhook handoffs stay tied to the same paper lifecycle.",
    icon: Send,
  },
  {
    title: "Ask follow-up questions",
    description:
      "Keep Q&A anchored to paper context, prior summaries, and retrieved evidence from your own history.",
    detail: "Scivly behaves like a research operations surface, not just another search box.",
    icon: Telescope,
  },
];

export const workflowSteps = [
  {
    eyebrow: "01. Intake",
    title: "Watchlists collect new papers continuously.",
    description:
      "Source sync jobs monitor subscriptions, tags, and labs across configurable refresh windows.",
  },
  {
    eyebrow: "02. Enrichment",
    title: "Papers get normalized into usable research context.",
    description:
      "Titles, abstracts, figures, methods, and limitations are processed into a consistent structure.",
  },
  {
    eyebrow: "03. Routing",
    title: "Signals are scored before they reach people.",
    description:
      "Scivly stores why a paper matched and which digest, team, or workflow should receive it.",
  },
  {
    eyebrow: "04. Follow-through",
    title: "Digests, alerts, and Q&A stay in the same loop.",
    description:
      "Delivery status, retries, costs, and follow-up questions remain visible inside one control plane.",
  },
];

export const docCategories = [
  {
    eyebrow: "Quickstart",
    title: "Set up your first watchlist",
    href: "/docs",
    points: ["Create workspace rules", "Map authors and topics", "Preview first digest"],
  },
  {
    eyebrow: "API",
    title: "Ship Scivly inside your stack",
    href: "/docs/api",
    points: ["API keys and auth", "Monitor and digest endpoints", "Webhook payloads"],
  },
  {
    eyebrow: "Operations",
    title: "Run ingestion with confidence",
    href: "/admin",
    points: ["Queue health", "Retry policies", "Cost and delivery visibility"],
  },
];

export const apiReference = [
  {
    method: "POST",
    route: "/v1/monitors",
    summary: "Create a new paper monitor for a workspace.",
  },
  {
    method: "GET",
    route: "/v1/papers/search",
    summary: "Search indexed papers with workspace-aware filters.",
  },
  {
    method: "POST",
    route: "/v1/digests/run",
    summary: "Generate a digest preview or trigger a delivery run.",
  },
  {
    method: "POST",
    route: "/v1/questions",
    summary: "Ask follow-up questions against retrieved paper context.",
  },
];

export const adminMetrics = [
  { label: "Active monitors", value: "128", detail: "+14 this week" },
  { label: "Papers triaged", value: "2,416", detail: "88% auto-scored" },
  { label: "Digest delivery rate", value: "99.2%", detail: "6 retries pending" },
  { label: "Processing spend", value: "$184", detail: "Within monthly budget" },
];

export const signalQueue = [
  {
    paper: "Segmented reasoning for multimodal agents",
    source: "cs.AI · matched by lab list",
    score: "0.96",
    status: "Ready for digest",
  },
  {
    paper: "Self-refining retrieval for scientific QA",
    source: "cs.CL · matched by topic rule",
    score: "0.92",
    status: "Waiting for figure parse",
  },
  {
    paper: "Efficient adapters for long-context analysis",
    source: "cs.LG · matched by keyword set",
    score: "0.88",
    status: "Queued for translation",
  },
];

export const digestMoments = [
  "09:00 Asia digest sent to founders channel",
  "10:15 Admin noted a spike in GPU-heavy parses",
  "13:40 Webhook replay recovered 3 failed notifications",
];

export const surfaceCards = [
  {
    title: "Documentation that behaves like a product surface",
    description:
      "Quickstarts, API references, and operational guidance all share the same language as the app itself.",
    icon: BookOpenText,
  },
  {
    title: "A control room for queues, quality, and costs",
    description:
      "Admins can inspect intake, enrichment, delivery, and question flows without stitching together multiple tools.",
    icon: Workflow,
  },
  {
    title: "Signals designed for actual decisions",
    description:
      "Benchmarks, digest cards, and source context keep every recommendation tied to observable evidence.",
    icon: DatabaseZap,
  },
  {
    title: "Notifications with accountability",
    description:
      "Each alert is traceable back to a rule, a paper, a run, and an operator-visible outcome.",
    icon: BellRing,
  },
];
