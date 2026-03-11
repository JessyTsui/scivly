import Link from "next/link";
import { ArrowRight } from "lucide-react";

import { SectionHeading } from "@/components/section-heading";
import { SignupCta } from "@/components/signup-cta";
import { aboutPrinciples, architectureSurfaces, roadmapMilestones } from "@/lib/public-site";
import { createMetadata } from "@/lib/metadata";

export const metadata = createMetadata({
  title: "About",
  description:
    "Learn how Scivly approaches multi-tenant paper intelligence across public, workspace, operator, and developer surfaces.",
  path: "/about",
  ogImage: "/about/opengraph-image",
});

export default function AboutPage() {
  return (
    <main>
      <section className="px-4 pb-16 pt-12 sm:px-6 lg:px-8 lg:pb-24 lg:pt-20">
        <div className="mx-auto max-w-7xl">
          <div className="grid gap-10 lg:grid-cols-[0.86fr_1.14fr] lg:items-start">
            <div>
              <SectionHeading
                eyebrow="About Scivly"
                title="A paper intelligence platform should explain itself as clearly as it processes research."
                body="Scivly is being built as a platform from day one: public-facing marketing, workspace product flows, operator visibility, and developer access all share the same architectural language."
              />

              <div className="mt-8 flex flex-col gap-3 sm:flex-row">
                <Link href="/pricing" className="btn-secondary justify-center">
                  View pricing
                </Link>
                <Link href="/signup" className="btn-primary justify-center">
                  Sign up
                  <ArrowRight className="h-4 w-4" />
                </Link>
              </div>
            </div>

            <div className="card rounded-[36px] p-6 sm:p-8">
              <p className="text-sm font-semibold uppercase tracking-[0.22em] text-[var(--primary)]">
                Product scope
              </p>
              <div className="mt-6 grid gap-4 sm:grid-cols-2">
                {architectureSurfaces.map((surface) => {
                  const Icon = surface.icon;

                  return (
                    <div key={surface.title} className="rounded-[28px] border border-[var(--border)] bg-[var(--surface-hover)] p-5">
                      <div className="flex h-11 w-11 items-center justify-center rounded-2xl bg-[var(--primary-subtle)] text-[var(--primary-dark)]">
                        <Icon className="h-5 w-5" />
                      </div>
                      <h2 className="mt-5 font-[family:var(--font-display)] text-2xl font-semibold tracking-tight text-[var(--foreground)]">
                        {surface.title}
                      </h2>
                      <p className="mt-3 text-sm leading-7 text-[var(--foreground-muted)]">
                        {surface.description}
                      </p>
                    </div>
                  );
                })}
              </div>
            </div>
          </div>
        </div>
      </section>

      <section className="border-y border-[var(--border)] bg-[var(--surface)]/75 px-4 py-16 sm:px-6 lg:px-8 lg:py-24">
        <div className="mx-auto max-w-7xl">
          <SectionHeading
            eyebrow="Principles"
            title="The product follows the same system design principles described in the architecture."
            body="These principles are less about branding language and more about making sure the platform scales beyond a single prototype."
          />

          <div className="mt-12 grid gap-5 lg:grid-cols-2">
            {aboutPrinciples.map((principle) => {
              const Icon = principle.icon;

              return (
                <div key={principle.title} className="card rounded-[32px] p-6 sm:p-7">
                  <div className="flex h-12 w-12 items-center justify-center rounded-2xl bg-[var(--primary-subtle)] text-[var(--primary-dark)]">
                    <Icon className="h-5 w-5" />
                  </div>
                  <h2 className="mt-6 font-[family:var(--font-display)] text-3xl font-semibold tracking-tight text-[var(--foreground)]">
                    {principle.title}
                  </h2>
                  <p className="mt-4 text-base leading-7 text-[var(--foreground-muted)]">
                    {principle.description}
                  </p>
                </div>
              );
            })}
          </div>
        </div>
      </section>

      <section className="px-4 py-16 sm:px-6 lg:px-8 lg:py-24">
        <div className="mx-auto max-w-7xl">
          <SectionHeading
            eyebrow="Roadmap Shape"
            title="The public surface ships first so the rest of the platform has a coherent front door."
            body="Scivly is intentionally building outward from clear product boundaries instead of hiding unfinished work behind vague placeholders."
          />

          <div className="mt-12 grid gap-5 lg:grid-cols-2">
            {roadmapMilestones.map((milestone) => (
              <div key={milestone.title} className="card rounded-[32px] p-6 sm:p-7">
                <p className="text-sm font-semibold uppercase tracking-[0.22em] text-[var(--primary)]">
                  {milestone.label}
                </p>
                <h2 className="mt-4 font-[family:var(--font-display)] text-3xl font-semibold tracking-tight text-[var(--foreground)]">
                  {milestone.title}
                </h2>
                <p className="mt-4 text-base leading-7 text-[var(--foreground-muted)]">
                  {milestone.detail}
                </p>
              </div>
            ))}
          </div>
        </div>
      </section>

      <SignupCta
        title="Follow the platform as it moves from public surface to full product loop."
        body="The marketing site now explains the platform boundaries. The next layers wire in auth, database access, and the deeper worker pipeline."
        secondaryHref="/docs"
        secondaryLabel="Read the docs"
      />
    </main>
  );
}
