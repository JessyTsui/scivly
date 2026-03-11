"use client";

import Link from "next/link";
import { usePathname } from "next/navigation";
import { ArrowRight } from "lucide-react";

import { LogoMark } from "@/components/logo-mark";
import { ThemeToggle } from "@/components/theme-toggle";
import { publicNavigation } from "@/lib/public-site";
import { siteConfig } from "@/lib/site-config";

function isActive(pathname: string, href: string) {
  if (href.startsWith("/#")) {
    return pathname === "/";
  }

  return pathname === href || pathname.startsWith(`${href}/`);
}

export function MarketingHeader() {
  const pathname = usePathname();

  return (
    <header className="sticky top-0 z-40 border-b border-[var(--border)] bg-[var(--background)]/86 backdrop-blur-2xl">
      <div className="mx-auto max-w-7xl px-4 py-4 sm:px-6 lg:px-8">
        <div className="flex items-center justify-between gap-4">
          <Link
            href="/"
            className="flex items-center gap-3 rounded-2xl pr-2 focus-visible:outline focus-visible:outline-2 focus-visible:outline-offset-4 focus-visible:outline-[var(--primary)]"
          >
            <LogoMark className="h-9 w-9" />
            <div>
              <span className="block font-[family:var(--font-display)] text-xl font-semibold tracking-tight">
                Scivly
              </span>
              <span className="block text-xs uppercase tracking-[0.22em] text-[var(--foreground-subtle)]">
                Public Surface
              </span>
            </div>
          </Link>

          <nav className="hidden items-center gap-1 lg:flex">
            {publicNavigation.map((item) => (
              <Link
                key={item.href}
                href={item.href}
                className={`rounded-full px-4 py-2 text-sm font-medium transition-colors focus-visible:outline focus-visible:outline-2 focus-visible:outline-offset-2 focus-visible:outline-[var(--primary)] ${
                  isActive(pathname, item.href)
                    ? "bg-[var(--primary-subtle)] text-[var(--primary-dark)]"
                    : "text-[var(--foreground-muted)] hover:bg-[var(--surface-hover)] hover:text-[var(--foreground)]"
                }`}
              >
                {item.label}
              </Link>
            ))}
          </nav>

          <div className="flex items-center gap-2 sm:gap-3">
            <ThemeToggle />
            <Link
              href="/docs"
              className="hidden rounded-full px-4 py-2 text-sm font-medium text-[var(--foreground-muted)] transition-colors hover:bg-[var(--surface-hover)] hover:text-[var(--foreground)] sm:inline-flex"
            >
              Docs
            </Link>
            <Link href={siteConfig.signupPath} className="btn-primary text-sm">
              Sign up
              <ArrowRight className="h-4 w-4" />
            </Link>
          </div>
        </div>

        <nav className="mt-4 flex gap-2 overflow-x-auto pb-1 lg:hidden">
          {publicNavigation.map((item) => (
            <Link
              key={item.href}
              href={item.href}
              className={`whitespace-nowrap rounded-full border px-3 py-2 text-sm font-medium transition-colors ${
                isActive(pathname, item.href)
                  ? "border-[var(--primary)]/30 bg-[var(--primary-subtle)] text-[var(--primary-dark)]"
                  : "border-[var(--border)] bg-[var(--surface)] text-[var(--foreground-muted)]"
              }`}
            >
              {item.label}
            </Link>
          ))}
        </nav>
      </div>
    </header>
  );
}
