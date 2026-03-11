import Link from "next/link";
import { ArrowRight } from "lucide-react";

import { siteConfig } from "@/lib/site-config";

export function SignupCta({
  title,
  body,
  secondaryHref = "/docs",
  secondaryLabel = "Read docs",
}: {
  title: string;
  body: string;
  secondaryHref?: string;
  secondaryLabel?: string;
}) {
  return (
    <section className="px-4 pb-20 sm:px-6 lg:px-8">
      <div className="mx-auto max-w-5xl">
        <div className="relative overflow-hidden rounded-[36px] border border-[var(--border)] bg-[linear-gradient(135deg,rgba(14,165,233,0.12),rgba(255,255,255,0.92),rgba(249,115,22,0.1))] px-8 py-14 shadow-[var(--shadow-lg)] sm:px-12">
          <div className="absolute inset-y-0 right-0 hidden w-1/3 bg-[radial-gradient(circle_at_center,rgba(249,115,22,0.18),transparent_70%)] lg:block" />
          <div className="relative max-w-3xl">
            <p className="text-sm font-semibold uppercase tracking-[0.24em] text-[var(--primary)]">
              Ready to start
            </p>
            <h2 className="mt-4 font-[family:var(--font-display)] text-4xl font-semibold tracking-tight text-[var(--foreground)] sm:text-5xl">
              {title}
            </h2>
            <p className="mt-5 max-w-2xl text-lg leading-8 text-[var(--foreground-muted)]">
              {body}
            </p>

            <div className="mt-8 flex flex-col gap-3 sm:flex-row">
              <Link href={siteConfig.signupPath} className="btn-primary justify-center">
                Sign up
                <ArrowRight className="h-4 w-4" />
              </Link>
              <Link href={secondaryHref} className="btn-secondary justify-center">
                {secondaryLabel}
              </Link>
            </div>
          </div>
        </div>
      </div>
    </section>
  );
}
