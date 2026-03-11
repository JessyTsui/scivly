import type { LucideIcon } from "lucide-react";
import {
  BellRing,
  Blocks,
  Bot,
  BriefcaseBusiness,
  DatabaseZap,
  Files,
  Globe2,
  LayoutPanelTop,
  Radar,
  ScanSearch,
  ShieldCheck,
  Sparkles,
  UsersRound,
  Waypoints,
} from "lucide-react";

export const publicNavigation = [
  { label: "Product", href: "/#story" },
  { label: "Library", href: "/papers" },
  { label: "Pricing", href: "/pricing" },
  { label: "About", href: "/about" },
  { label: "Docs", href: "/docs" },
];

export type MarketingCard = {
  eyebrow?: string;
  title: string;
  description: string;
  icon: LucideIcon;
};

export const heroStats = [
  { label: "paper sources ready to monitor", value: "12k+" },
  { label: "minutes from sync to digest", value: "< 6" },
  { label: "product surfaces shipped together", value: "4" },
];

export const problemCards: MarketingCard[] = [
  {
    eyebrow: "Chapter 01",
    title: "Signal gets buried under source volume.",
    description:
      "Labs and operators still refresh arXiv, feeds, and saved searches by hand, then lose the context of why something mattered.",
    icon: Radar,
  },
  {
    eyebrow: "Chapter 02",
    title: "Raw PDFs are not a usable workflow.",
    description:
      "Without translation, extraction, and routing, a paper backlog becomes another archive instead of a research decision surface.",
    icon: Files,
  },
  {
    eyebrow: "Chapter 03",
    title: "Teams need memory, not one-off alerts.",
    description:
      "Digests, operator actions, and follow-up questions should all point back to the same paper evidence trail.",
    icon: DatabaseZap,
  },
];

export type PipelineChapter = {
  phase: string;
  title: string;
  description: string;
  bullets: string[];
};

export const pipelineChapters: PipelineChapter[] = [
  {
    phase: "01. Intake",
    title: "Sync papers continuously across topics, authors, labs, and categories.",
    description:
      "Scivly starts with the source layer, so a workspace can reason about what entered the system before anything is summarized.",
    bullets: ["arXiv and feed monitoring", "Workspace-scoped watchlists", "Idempotent ingestion keys"],
  },
  {
    phase: "02. Triage",
    title: "Score the queue before humans need to read everything.",
    description:
      "Matching reasons stay visible, which means teams can audit why a paper was surfaced instead of trusting a black box.",
    bullets: ["Rule-based scoring", "Match reasons per paper", "Priority thresholds for deeper processing"],
  },
  {
    phase: "03. Enrich",
    title: "Translate, summarize, and extract the parts that move decisions forward.",
    description:
      "The worker plane turns a PDF into something operators can route, reference, and discuss without leaving the platform.",
    bullets: ["Structured summaries", "Figure-aware highlights", "Cost and retry tracking"],
  },
  {
    phase: "04. Deliver",
    title: "Push the signal into digests, workspaces, and developer endpoints.",
    description:
      "The same data model powers user workspaces, admin visibility, and future webhook or API consumers.",
    bullets: ["Digest-ready outputs", "Operator monitoring surface", "REST, webhooks, and skill adapters"],
  },
];

export const audienceCards: MarketingCard[] = [
  {
    title: "Founders and applied research teams",
    description:
      "Replace tab sprawl with one workspace that keeps competitive papers, summaries, and follow-up questions in sync.",
    icon: BriefcaseBusiness,
  },
  {
    title: "Labs and research ops",
    description:
      "Track authors, institutions, and experiments with routing rules that preserve why the alert was triggered.",
    icon: UsersRound,
  },
  {
    title: "Developer surfaces and automation",
    description:
      "Ship monitors, digests, and downstream workflows through a thin API surface instead of duplicating logic in clients.",
    icon: Bot,
  },
];

export const architectureSurfaces: MarketingCard[] = [
  {
    title: "Public Surface",
    description: "Landing pages, pricing, docs, and public-safe resources that explain the platform clearly.",
    icon: Globe2,
  },
  {
    title: "User Workspace",
    description: "Interest setup, digests, paper detail, and Q&A tied to the same monitored research stream.",
    icon: LayoutPanelTop,
  },
  {
    title: "Operator Surface",
    description: "Queue health, usage, failures, and delivery visibility for teams running the platform day to day.",
    icon: ShieldCheck,
  },
  {
    title: "Developer Surface",
    description: "REST endpoints, webhooks, and future skills or SDKs that stay thin on top of the core APIs.",
    icon: Blocks,
  },
];

export type PricingTier = {
  billingPlan: "free" | "pro" | "enterprise";
  name: string;
  price: string;
  cadence: string;
  summary: string;
  highlight: string;
  featured?: boolean;
  ctaLabel: string;
  ctaHref: string;
  features: string[];
};

export const pricingTiers: PricingTier[] = [
  {
    billingPlan: "free",
    name: "Free",
    price: "$0",
    cadence: "per workspace / month",
    summary: "For early validation when one workspace needs a narrow daily budget and a direct way to see whether the workflow sticks.",
    highlight: "Best for initial validation",
    ctaLabel: "Start free",
    ctaHref: "/signup",
    features: [
      "10 processed papers per day",
      "50k LLM tokens per month",
      "10 digests per month",
      "Workspace feed and paper detail",
    ],
  },
  {
    billingPlan: "pro",
    name: "Pro",
    price: "$49",
    cadence: "per workspace / month",
    summary: "For teams that want Stripe-backed self-serve billing, materially higher usage ceilings, and a workspace that can run every day without babysitting.",
    highlight: "Recommended for most teams",
    featured: true,
    ctaLabel: "Upgrade to Pro",
    ctaHref: "/signup",
    features: [
      "250 processed papers per day",
      "1M LLM tokens per month",
      "200 digests per month",
      "Stripe billing portal and usage visibility",
    ],
  },
  {
    billingPlan: "enterprise",
    name: "Enterprise",
    price: "Custom",
    cadence: "deployment + support",
    summary: "For organizations that need workspace isolation, integrations, and operator-grade controls.",
    highlight: "Private deployment and support",
    ctaLabel: "Talk to us",
    ctaHref: "/signup",
    features: [
      "SSO and workspace governance",
      "Webhook and API onboarding",
      "Custom ingestion and delivery policies",
      "Priority support and roadmap input",
    ],
  },
];

export const pricingComparison = [
  {
    label: "Processed papers",
    values: ["10 / day", "250 / day", "Custom policy"],
  },
  {
    label: "LLM tokens",
    values: ["50k / month", "1M / month", "Custom budget"],
  },
  {
    label: "Digests",
    values: ["10 / month", "200 / month", "Custom delivery policy"],
  },
  {
    label: "Billing flow",
    values: ["No card required", "Stripe Checkout + portal", "Contracted billing"],
  },
  {
    label: "Operator visibility",
    values: ["Basic workspace view", "Usage limits and billing state", "Admin controls and reporting"],
  },
];

export const pricingFaqs = [
  {
    question: "Is there a free tier?",
    answer:
      "Yes. The Free plan is intentionally constrained so a workspace can validate the workflow before usage grows into a real operating surface.",
  },
  {
    question: "Can I switch plans later?",
    answer:
      "Yes. Workspaces can start free, move to Pro through Stripe Checkout, and then use the billing portal for the ongoing subscription lifecycle.",
  },
  {
    question: "Does Enterprise mean self-hosted?",
    answer:
      "Enterprise can include private deployment, security review, and tighter workspace controls, depending on the deployment model.",
  },
  {
    question: "Why is signup a lightweight flow right now?",
    answer:
      "The public funnel is in place first. Full auth and self-serve account creation are scheduled in the dedicated auth integration task.",
  },
];

export const aboutPrinciples: MarketingCard[] = [
  {
    title: "Platform-first from day one",
    description:
      "Scivly is designed as a multi-tenant product surface, not a collection of scripts hidden behind a thin UI.",
    icon: Waypoints,
  },
  {
    title: "API-first boundaries",
    description:
      "The frontend, skill adapters, and future SDKs should all consume the same backend capabilities without forking the logic.",
    icon: ScanSearch,
  },
  {
    title: "Step pipeline reliability",
    description:
      "Paper processing needs retries, idempotency, observability, and replay support because that is where the real operational risk lives.",
    icon: BellRing,
  },
  {
    title: "Open-core with public-safe defaults",
    description:
      "The code and public-safe references belong in the repository; production data, secrets, and hosted-only internals do not.",
    icon: Sparkles,
  },
];

export const roadmapMilestones = [
  {
    label: "Now",
    title: "Public surface and core workspace scaffolding",
    detail:
      "Marketing pages, docs, admin concepts, and workspace shells establish the platform shape before deeper data wiring lands.",
  },
  {
    label: "Next",
    title: "Authentication and real data connections",
    detail:
      "Self-serve login, PostgreSQL-backed APIs, and workspace scoping turn the current shells into a real multi-tenant product.",
  },
  {
    label: "Pipeline",
    title: "PDF fetch, parse, enrich, and orchestration",
    detail:
      "The worker plane expands from feed sync into full paper processing with persistent status tracking and retries.",
  },
  {
    label: "Platform",
    title: "Billing, developer access, and public library",
    detail:
      "Subscriptions, public paper browsing, and API-facing integrations complete the broader platform surface described in the architecture.",
  },
];
