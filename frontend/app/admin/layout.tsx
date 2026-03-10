"use client";

import Link from "next/link";
import { usePathname } from "next/navigation";
import {
  BarChart3,
  BookOpen,
  FileQuestion,
  LayoutDashboard,
  ListTodo,
  Newspaper,
  Radar,
  Settings,
} from "lucide-react";

import { LogoMark } from "@/components/logo-mark";
import { ThemeToggle } from "@/components/theme-toggle";

const pageTitles: Record<string, { title: string; subtitle: string }> = {
  "/admin": { title: "Dashboard", subtitle: "Track the flow of papers, digests, and follow-up work." },
  "/admin/monitors": { title: "Monitors", subtitle: "Watch sources, manage rules, and inspect match quality." },
  "/admin/papers": { title: "Papers", subtitle: "Review matched papers, triage priorities, and keep context close." },
  "/admin/digests": { title: "Digests", subtitle: "Schedule briefings, preview content, and keep delivery reliable." },
  "/admin/pipeline": { title: "Pipeline", subtitle: "Inspect intake, enrichment, translation, and routing health." },
  "/admin/qa": { title: "Q&A", subtitle: "Keep operator questions anchored to paper evidence and history." },
  "/admin/analytics": { title: "Analytics", subtitle: "Measure throughput, engagement, and coverage across the workspace." },
  "/admin/settings": { title: "Settings", subtitle: "Adjust workspace defaults, notifications, and security controls." },
};

const adminNav = [
  { label: "Dashboard", href: "/admin", icon: LayoutDashboard },
  { label: "Monitors", href: "/admin/monitors", icon: Radar },
  { label: "Papers", href: "/admin/papers", icon: BookOpen },
  { label: "Digests", href: "/admin/digests", icon: Newspaper },
  { label: "Pipeline", href: "/admin/pipeline", icon: ListTodo },
  { label: "Q&A", href: "/admin/qa", icon: FileQuestion },
  { label: "Analytics", href: "/admin/analytics", icon: BarChart3 },
  { label: "Settings", href: "/admin/settings", icon: Settings },
];

function isActivePath(pathname: string, href: string) {
  if (href === "/admin") {
    return pathname === href;
  }

  return pathname === href || pathname.startsWith(`${href}/`);
}

function AdminNavLinks({ pathname, mobile = false }: { pathname: string; mobile?: boolean }) {
  return adminNav.map((item) => {
    const Icon = item.icon;
    const active = isActivePath(pathname, item.href);

    return (
      <Link
        key={item.href}
        href={item.href}
        className={
          mobile
            ? `inline-flex min-h-11 items-center gap-2 whitespace-nowrap rounded-full border px-3 py-2 text-sm font-medium transition-colors ${
                active
                  ? "border-[var(--primary)]/25 bg-[var(--primary-subtle)] text-[var(--primary)]"
                  : "border-[var(--border)] bg-[var(--surface)] text-[var(--foreground-muted)]"
              }`
            : `group flex items-center gap-3 rounded-2xl px-3 py-3 text-sm font-medium transition-colors ${
                active
                  ? "bg-[var(--primary-subtle)] text-[var(--primary)] shadow-[var(--shadow-sm)]"
                  : "text-[var(--foreground-muted)] hover:bg-[var(--surface-hover)] hover:text-[var(--foreground)]"
              }`
        }
      >
        <Icon className={`h-4 w-4 ${active ? "text-[var(--primary)]" : "text-[var(--foreground-subtle)] group-hover:text-[var(--foreground)]"}`} />
        <span>{item.label}</span>
      </Link>
    );
  });
}

export default function AdminLayout({
  children,
}: Readonly<{
  children: React.ReactNode;
}>) {
  const pathname = usePathname();
  const currentPage = pageTitles[pathname] ?? pageTitles["/admin"];

  return (
    <div className="min-h-screen bg-[var(--background)] text-[var(--foreground)]">
      <div className="pointer-events-none fixed inset-0 -z-10 overflow-hidden">
        <div className="absolute left-[-10%] top-[-6rem] h-64 w-64 rounded-full bg-[var(--primary)]/10 blur-3xl" />
        <div className="absolute bottom-[-8rem] right-[-8%] h-72 w-72 rounded-full bg-[var(--accent)]/8 blur-3xl" />
      </div>

      <div className="mx-auto flex min-h-screen max-w-[1600px] flex-col lg:flex-row">
        <aside className="hidden lg:flex lg:h-screen lg:w-[292px] lg:flex-col lg:border-r lg:border-[var(--border)] lg:bg-[var(--background)]/82 lg:px-4 lg:py-6 lg:backdrop-blur-xl">
          <Link
            href="/"
            className="flex items-center gap-3 rounded-2xl px-3 py-3 focus-visible:outline focus-visible:outline-2 focus-visible:outline-offset-4 focus-visible:outline-[var(--primary)]"
          >
            <LogoMark />
            <div>
              <p className="font-[family:var(--font-display)] text-lg font-semibold">Scivly</p>
              <p className="text-xs text-[var(--foreground-subtle)]">Operator console</p>
            </div>
          </Link>

          <div className="mt-6 rounded-3xl border border-[var(--border)] bg-[var(--surface)]/78 p-4 shadow-[var(--shadow-sm)]">
            <p className="text-xs font-semibold uppercase tracking-[0.24em] text-[var(--foreground-subtle)]">
              Workspace
            </p>
            <p className="mt-3 font-[family:var(--font-display)] text-xl font-semibold">
              Personal Research
            </p>
            <p className="mt-2 text-sm leading-6 text-[var(--foreground-muted)]">
              One place for source coverage, daily digests, and evidence-backed follow-up work.
            </p>
            <div className="mt-4 flex flex-wrap gap-2">
              <span className="rounded-full bg-[var(--success)]/12 px-3 py-1 text-xs font-medium text-[var(--success)]">
                12 monitors live
              </span>
              <span className="rounded-full bg-[var(--primary-subtle)] px-3 py-1 text-xs font-medium text-[var(--primary)]">
                4 digests scheduled
              </span>
            </div>
          </div>

          <nav className="mt-6 flex flex-col gap-1">
            <AdminNavLinks pathname={pathname} />
          </nav>

          <div className="mt-auto space-y-3 px-1 pt-6">
            <ThemeToggle variant="sidebar" />
            <Link
              href="/docs"
              className="flex min-h-11 items-center justify-center rounded-2xl border border-[var(--border)] bg-[var(--surface)]/70 px-4 py-3 text-sm font-medium text-[var(--foreground-muted)] shadow-[var(--shadow-sm)] transition-colors hover:border-[var(--border-strong)] hover:bg-[var(--surface-hover)] hover:text-[var(--foreground)]"
            >
              Open docs
            </Link>
          </div>
        </aside>

        <div className="flex min-w-0 flex-1 flex-col">
          <header className="sticky top-0 z-30 border-b border-[var(--border)] bg-[var(--background)]/82 backdrop-blur-xl">
            <div className="px-4 py-4 sm:px-6 lg:px-8">
              <div className="flex flex-col gap-4 sm:flex-row sm:items-start sm:justify-between">
                <div className="min-w-0">
                  <div className="flex items-center gap-2 text-xs font-medium uppercase tracking-[0.24em] text-[var(--foreground-subtle)]">
                    <span>Scivly Console</span>
                    <span className="h-1 w-1 rounded-full bg-[var(--foreground-subtle)]" />
                    <span>{currentPage.title}</span>
                  </div>
                  <h1 className="mt-2 font-[family:var(--font-display)] text-2xl font-semibold tracking-tight sm:text-3xl">
                    {currentPage.title}
                  </h1>
                  <p className="mt-2 max-w-2xl text-sm leading-6 text-[var(--foreground-muted)]">
                    {currentPage.subtitle}
                  </p>
                </div>

                <div className="flex items-center gap-2 self-start sm:self-auto">
                  <div className="hidden items-center gap-2 rounded-full border border-[var(--success)]/25 bg-[var(--success)]/10 px-3 py-2 text-xs font-medium text-[var(--success)] sm:inline-flex">
                    <span className="h-2 w-2 rounded-full bg-[var(--success)] animate-pulse" />
                    System online
                  </div>
                  <ThemeToggle className="lg:hidden" />
                  <Link href="/docs" className="btn-secondary text-sm">
                    Docs
                  </Link>
                </div>
              </div>

              <nav className="mt-4 flex gap-2 overflow-x-auto pb-1 lg:hidden">
                <AdminNavLinks pathname={pathname} mobile />
              </nav>
            </div>
          </header>

          <main className="flex-1 px-4 py-6 sm:px-6 lg:px-8 lg:py-8">{children}</main>
        </div>
      </div>
    </div>
  );
}
