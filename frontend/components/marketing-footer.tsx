import Link from "next/link";
import { ArrowUpRight } from "lucide-react";

import { LogoMark } from "@/components/logo-mark";
import { publicNavigation } from "@/lib/public-site";
import { siteConfig } from "@/lib/site-config";

const footerGroups = [
  {
    label: "Explore",
    links: publicNavigation,
  },
  {
    label: "Platform",
    links: [
      { label: "Workspace preview", href: "/workspace/feed" },
      { label: "Admin surface", href: "/admin" },
      { label: "API docs", href: "/docs/api" },
    ],
  },
];

export function MarketingFooter() {
  return (
    <footer className="border-t border-[var(--border)] bg-[var(--surface)]/78 backdrop-blur-xl">
      <div className="mx-auto max-w-7xl px-4 py-14 sm:px-6 lg:px-8">
        <div className="grid gap-10 lg:grid-cols-[minmax(0,1.15fr)_minmax(0,0.85fr)] lg:items-start">
          <div className="space-y-5">
            <div className="flex items-center gap-3">
              <LogoMark />
              <div>
                <p className="font-[family:var(--font-display)] text-lg font-semibold">Scivly</p>
                <p className="text-sm text-[var(--foreground-muted)]">
                  Paper intelligence for fast-moving research teams.
                </p>
              </div>
            </div>

            <p className="max-w-xl text-sm leading-7 text-[var(--foreground-muted)]">
              Monitor new papers, convert raw PDFs into briefings, and keep every alert tied to a
              workspace, a digest, and a source trail.
            </p>

            <div className="flex flex-wrap gap-3">
              <Link href={siteConfig.signupPath} className="btn-primary text-sm">
                Start free
              </Link>
              <Link href="/pricing" className="btn-secondary text-sm">
                View pricing
              </Link>
            </div>
          </div>

          <div className="grid gap-4 sm:grid-cols-3">
            {footerGroups.map((group) => (
              <div key={group.label} className="rounded-3xl border border-[var(--border)] bg-[var(--surface-hover)]/80 p-5">
                <p className="text-xs font-semibold uppercase tracking-[0.22em] text-[var(--foreground-subtle)]">
                  {group.label}
                </p>
                <div className="mt-4 flex flex-col gap-3">
                  {group.links.map((link) => (
                    <Link
                      key={link.href}
                      href={link.href}
                      className="text-sm font-medium text-[var(--foreground-muted)] transition-colors hover:text-[var(--foreground)]"
                    >
                      {link.label}
                    </Link>
                  ))}
                </div>
              </div>
            ))}

            <div className="rounded-3xl border border-[var(--border)] bg-[var(--surface-hover)]/80 p-5">
              <p className="text-xs font-semibold uppercase tracking-[0.22em] text-[var(--foreground-subtle)]">
                Open source
              </p>
              <a
                href={siteConfig.githubUrl}
                target="_blank"
                rel="noreferrer"
                className="mt-4 inline-flex items-center gap-2 text-sm font-medium text-[var(--foreground)]"
              >
                GitHub repository
                <ArrowUpRight className="h-4 w-4" />
              </a>
              <p className="mt-3 text-sm leading-7 text-[var(--foreground-muted)]">
                Public-safe defaults live in the repository. Private prompts, data, and secrets stay outside version control.
              </p>
            </div>
          </div>
        </div>

        <div className="mt-10 flex flex-col gap-3 border-t border-[var(--border)] pt-6 text-sm text-[var(--foreground-subtle)] sm:flex-row sm:items-center sm:justify-between">
          <p>Open source under Apache 2.0</p>
          <p>Built around public, workspace, operator, and developer surfaces</p>
        </div>
      </div>
    </footer>
  );
}
