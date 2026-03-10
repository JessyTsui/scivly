"use client";

import Link from "next/link";
import { usePathname } from "next/navigation";
import { ArrowRight } from "lucide-react";

import { LogoMark } from "@/components/logo-mark";
import { ThemeToggle } from "@/components/theme-toggle";

const homeNavigation = [
  { label: "Product", href: "/#product" },
  { label: "Workflow", href: "/#workflow" },
  { label: "Docs", href: "/docs" },
];

const docsNavigation = [
  { label: "Overview", href: "/docs" },
  { label: "API", href: "/docs/api" },
  { label: "Console", href: "/admin" },
];

function isNavItemActive(pathname: string, href: string) {
  if (href.startsWith("/#")) {
    return pathname === "/";
  }

  return pathname === href || pathname.startsWith(`${href}/`);
}

export function SiteHeader() {
  const pathname = usePathname();
  const navigation = pathname.startsWith("/docs") ? docsNavigation : homeNavigation;

  return (
    <header className="sticky top-0 z-40 border-b border-[var(--border)] bg-[var(--background)]/95 backdrop-blur-xl">
      <div className="mx-auto max-w-7xl px-4 py-4 sm:px-6 lg:px-8">
        <div className="flex items-center justify-between gap-4">
          <Link
            href="/"
            className="flex items-center gap-2.5 rounded-xl pr-2 focus-visible:outline focus-visible:outline-2 focus-visible:outline-offset-4 focus-visible:outline-[var(--primary)]"
          >
            <LogoMark />
            <div>
              <span className="block font-[family:var(--font-display)] text-lg font-semibold">
                Scivly
              </span>
              <span className="block text-xs text-[var(--foreground-subtle)]">
                Research intelligence
              </span>
            </div>
          </Link>

          <nav className="hidden items-center gap-1 lg:flex">
            {navigation.map((item) => {
              const active = isNavItemActive(pathname, item.href);

              return (
                <Link
                  key={item.href}
                  href={item.href}
                  className={`rounded-full px-4 py-2 text-sm font-medium transition-colors focus-visible:outline focus-visible:outline-2 focus-visible:outline-offset-2 focus-visible:outline-[var(--primary)] ${
                    active
                      ? "bg-[var(--primary-subtle)] text-[var(--primary)]"
                      : "text-[var(--foreground-muted)] hover:bg-[var(--surface-hover)] hover:text-[var(--foreground)]"
                  }`}
                >
                  {item.label}
                </Link>
              );
            })}
          </nav>

          <div className="flex items-center gap-2 sm:gap-3">
            <ThemeToggle />
            <Link
              href="/docs"
              className="hidden rounded-full px-4 py-2 text-sm font-medium text-[var(--foreground-muted)] transition-colors hover:bg-[var(--surface-hover)] hover:text-[var(--foreground)] sm:inline-flex"
            >
              Docs
            </Link>
            <Link href="/admin" className="btn-primary text-sm">
              Console
              <ArrowRight className="h-4 w-4" />
            </Link>
          </div>
        </div>

        <nav className="mt-4 flex gap-2 overflow-x-auto pb-1 lg:hidden">
          {navigation.map((item) => {
            const active = isNavItemActive(pathname, item.href);

            return (
              <Link
                key={item.href}
                href={item.href}
                className={`whitespace-nowrap rounded-full border px-3 py-2 text-sm font-medium transition-colors ${
                  active
                    ? "border-[var(--primary)]/25 bg-[var(--primary-subtle)] text-[var(--primary)]"
                    : "border-[var(--border)] bg-[var(--surface)] text-[var(--foreground-muted)]"
                }`}
              >
                {item.label}
              </Link>
            );
          })}
        </nav>
      </div>
    </header>
  );
}
