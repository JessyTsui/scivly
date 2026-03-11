import Link from "next/link";
import { ArrowRight, BookOpen, LayoutPanelLeft, ShieldCheck } from "lucide-react";

import { SectionHeading } from "@/components/section-heading";
import { createMetadata } from "@/lib/metadata";

export const metadata = createMetadata({
  title: "Sign Up",
  description:
    "Start a Scivly workspace, review pricing, or preview the current product surfaces while full auth integration is being wired.",
  path: "/signup",
});

const nextSteps = [
  {
    title: "Preview the workspace",
    description: "Open the current feed surface and inspect how papers, digests, and QA are structured today.",
    href: "/workspace/feed",
    icon: LayoutPanelLeft,
  },
  {
    title: "Review docs and API shape",
    description: "Understand the product boundaries, API surface, and operator flows before full auth lands.",
    href: "/docs",
    icon: BookOpen,
  },
  {
    title: "Pick the right plan",
    description: "See which pricing tier matches solo validation, team routing, or enterprise governance needs.",
    href: "/pricing",
    icon: ShieldCheck,
  },
];

export default function SignupPage() {
  return (
    <main className="px-4 pb-20 pt-12 sm:px-6 lg:px-8 lg:pb-24 lg:pt-20">
      <div className="mx-auto max-w-5xl">
        <section className="card rounded-[40px] p-8 sm:p-10 lg:p-12">
          <SectionHeading
            eyebrow="Sign up"
            title="The public funnel is live. Self-serve auth is the next layer to land."
            body="Task F1 brings the public marketing surface online. The actual account creation flow is scheduled in the auth integration task, so this page keeps the CTA path intact without pretending that authentication already exists."
          />

          <div className="mt-8 flex flex-col gap-3 sm:flex-row">
            <Link href="/workspace/feed" className="btn-primary justify-center">
              Preview workspace
              <ArrowRight className="h-4 w-4" />
            </Link>
            <Link href="/pricing" className="btn-secondary justify-center">
              Review pricing
            </Link>
          </div>
        </section>

        <section className="mt-10 grid gap-5 lg:grid-cols-3">
          {nextSteps.map((step) => {
            const Icon = step.icon;

            return (
              <Link key={step.title} href={step.href} className="card card-hover rounded-[32px] p-6">
                <div className="flex h-12 w-12 items-center justify-center rounded-2xl bg-[var(--primary-subtle)] text-[var(--primary-dark)]">
                  <Icon className="h-5 w-5" />
                </div>
                <h2 className="mt-6 font-[family:var(--font-display)] text-3xl font-semibold tracking-tight text-[var(--foreground)]">
                  {step.title}
                </h2>
                <p className="mt-4 text-base leading-7 text-[var(--foreground-muted)]">
                  {step.description}
                </p>
                <span className="mt-6 inline-flex items-center gap-2 text-sm font-semibold text-[var(--primary-dark)]">
                  Continue
                  <ArrowRight className="h-4 w-4" />
                </span>
              </Link>
            );
          })}
        </section>
      </div>
    </main>
  );
}
