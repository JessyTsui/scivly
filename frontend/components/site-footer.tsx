import Link from "next/link";
import { ArrowUpRight } from "lucide-react";

import { LogoMark } from "./logo-mark";

const footerLinks = [
  { label: "Documentation", href: "/docs" },
  { label: "API", href: "/docs/api" },
  { label: "Console", href: "/admin" },
];

export function SiteFooter() {
  return (
    <footer className="border-t border-[var(--border)] bg-[var(--surface)]/72 backdrop-blur-xl">
      <div className="mx-auto max-w-7xl px-4 py-14 sm:px-6 lg:px-8">
        <div className="grid gap-10 lg:grid-cols-[minmax(0,1.2fr)_minmax(0,0.8fr)] lg:items-start">
          <div className="space-y-5">
            <div className="flex items-center gap-3">
              <LogoMark />
              <div>
                <p className="font-[family:var(--font-display)] text-lg font-semibold">Scivly</p>
                <p className="text-sm text-[var(--foreground-muted)]">
                  Research intelligence for paper teams
                </p>
              </div>
            </div>

            <p className="max-w-xl text-sm leading-7 text-[var(--foreground-muted)]">
              Monitor fast-moving literature, generate concise digests, and keep every answer tied
              to paper evidence in the same workspace.
            </p>

            <div className="flex flex-wrap gap-3">
              <Link href="/docs" className="btn-secondary text-sm">
                Read docs
              </Link>
              <Link href="/admin" className="btn-primary text-sm">
                Open console
              </Link>
            </div>
          </div>

          <div className="grid gap-4 sm:grid-cols-2">
            <div className="rounded-2xl border border-[var(--border)] bg-[var(--surface-hover)]/75 p-5">
              <p className="text-xs font-semibold uppercase tracking-[0.22em] text-[var(--foreground-subtle)]">
                Product
              </p>
              <div className="mt-4 flex flex-col gap-3">
                {footerLinks.map((link) => (
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

            <div className="rounded-2xl border border-[var(--border)] bg-[var(--surface-hover)]/75 p-5">
              <p className="text-xs font-semibold uppercase tracking-[0.22em] text-[var(--foreground-subtle)]">
                Open source
              </p>
              <a
                href="https://github.com/JessyTsui/scivly"
                target="_blank"
                rel="noreferrer"
                className="mt-4 inline-flex items-center gap-2 text-sm font-medium text-[var(--foreground)]"
              >
                GitHub repository
                <ArrowUpRight className="h-4 w-4" />
              </a>
              <p className="mt-3 text-sm leading-7 text-[var(--foreground-muted)]">
                Public-safe defaults live in the repo. Secrets and runtime credentials stay outside version control.
              </p>
            </div>
          </div>
        </div>

        <div className="mt-10 flex flex-col gap-3 border-t border-[var(--border)] pt-6 text-sm text-[var(--foreground-subtle)] sm:flex-row sm:items-center sm:justify-between">
          <p>Open source under Apache 2.0</p>
          <p>Built for researchers, by researchers</p>
        </div>
      </div>
    </footer>
  );
}
