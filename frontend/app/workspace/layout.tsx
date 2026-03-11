"use client";

import { UserButton } from "@clerk/nextjs";
import Link from "next/link";
import { usePathname } from "next/navigation";
import { useState } from "react";
import { QueryClient, QueryClientProvider } from "@tanstack/react-query";
import {
  BellRing,
  BookOpenText,
  ChevronDown,
  FileQuestion,
  Menu,
  Newspaper,
  Radar,
  Settings2,
} from "lucide-react";

import { ThemeToggle } from "@/components/theme-toggle";
import { Button } from "@/components/ui/button";
import {
  Dialog,
  DialogContent,
  DialogDescription,
  DialogHeader,
  DialogTitle,
  DialogTrigger,
} from "@/components/ui/dialog";
import {
  DropdownMenu,
  DropdownMenuContent,
  DropdownMenuItem,
  DropdownMenuLabel,
  DropdownMenuSeparator,
  DropdownMenuTrigger,
} from "@/components/ui/dropdown-menu";
import { Toaster } from "@/components/ui/toaster";
import { useScivlySession } from "@/lib/auth/scivly-session";

const pageMeta: Record<string, { title: string; subtitle: string }> = {
  "/workspace/feed": {
    title: "Paper Feed",
    subtitle:
      "Scan scored papers, inspect why they matched, and decide what deserves PDF, digest, or follow-up work.",
  },
  "/workspace/interests": {
    title: "Interests",
    subtitle:
      "Tune the profiles, author watchlists, and notification channels that shape your daily queue.",
  },
  "/workspace/digests": {
    title: "Digests",
    subtitle:
      "Review past briefings, inspect grouped research signals, and keep the delivery cadence aligned with your workflow.",
  },
  "/workspace/qa": {
    title: "Q&A",
    subtitle:
      "Ask follow-up questions against paper context, prior digest notes, and explainable mock evidence.",
  },
  "/workspace/settings": {
    title: "Settings",
    subtitle:
      "Manage billing, programmatic access, and the operational guardrails around how the workspace connects to the rest of the platform.",
  },
};

const navItems = [
  { href: "/workspace/feed", label: "Feed", icon: Radar },
  { href: "/workspace/interests", label: "Interests", icon: BookOpenText },
  { href: "/workspace/digests", label: "Digests", icon: Newspaper },
  { href: "/workspace/qa", label: "Q&A", icon: FileQuestion },
  { href: "/workspace/settings", label: "Settings", icon: Settings2 },
];

function isActive(pathname: string, href: string) {
  if (href.includes("#")) {
    return false;
  }

  return pathname === href || pathname.startsWith(`${href}/`);
}

function WorkspaceNav({
  pathname,
  onNavigate,
}: {
  pathname: string;
  onNavigate?: () => void;
}) {
  return (
    <nav className="flex flex-col gap-1">
      {navItems.map((item) => {
        const Icon = item.icon;
        const active = isActive(pathname, item.href);

        return (
          <Link
            key={item.href}
            href={item.href}
            onClick={onNavigate}
            className={`group flex min-h-11 items-center gap-3 rounded-2xl px-3 py-3 text-sm font-medium transition-colors ${
              active
                ? "bg-[var(--primary-subtle)] text-[var(--primary)] shadow-[var(--shadow-sm)]"
                : "text-[var(--foreground-muted)] hover:bg-[var(--surface-hover)] hover:text-[var(--foreground)]"
            }`}
          >
            <Icon
              className={`size-4 ${
                active
                  ? "text-[var(--primary)]"
                  : "text-[var(--foreground-subtle)] group-hover:text-[var(--foreground)]"
              }`}
            />
            <span>{item.label}</span>
          </Link>
        );
      })}
    </nav>
  );
}

export default function WorkspaceLayout({
  children,
}: Readonly<{
  children: React.ReactNode;
}>) {
  const pathname = usePathname();
  const currentPage = pageMeta[pathname] ?? pageMeta["/workspace/feed"];
  const session = useScivlySession();
  const [queryClient] = useState(
    () =>
      new QueryClient({
        defaultOptions: {
          queries: {
            staleTime: 30_000,
            refetchOnWindowFocus: false,
          },
        },
      })
  );
  const [mobileOpen, setMobileOpen] = useState(false);
  const workspace = session.workspace;
  const workspaceName = workspace?.name ?? "Workspace";
  const workspaceDescription = session.user
    ? `Authenticated as ${session.user.name}${session.user.email ? ` · ${session.user.email}` : ""}.`
    : "Authenticating workspace context...";
  const workspacePlan = workspace?.plan.toUpperCase() ?? "SYNCING";

  return (
    <QueryClientProvider client={queryClient}>
      <div className="min-h-screen bg-[var(--background)] text-[var(--foreground)]">
        <div className="pointer-events-none fixed inset-0 -z-10 overflow-hidden">
          <div className="absolute left-[-12%] top-[-5rem] h-72 w-72 rounded-full bg-[var(--primary)]/10 blur-3xl" />
          <div className="absolute bottom-[-8rem] right-[-10%] h-80 w-80 rounded-full bg-[var(--accent)]/10 blur-3xl" />
        </div>

        <div className="mx-auto flex min-h-screen max-w-[1580px]">
          <aside className="hidden w-[300px] shrink-0 border-r border-[var(--border)] bg-[var(--background)]/82 px-4 py-6 backdrop-blur-xl lg:flex lg:flex-col">
            <div className="rounded-[28px] border border-[var(--border)] bg-[var(--surface)]/92 p-5 shadow-[var(--shadow-sm)]">
              <p className="text-xs font-semibold uppercase tracking-[0.24em] text-[var(--foreground-subtle)]">
                User workspace
              </p>
              <h2 className="mt-3 font-[family:var(--font-display)] text-2xl font-semibold tracking-tight">
                {workspaceName}
              </h2>
              <p className="mt-3 text-sm leading-6 text-[var(--foreground-muted)]">
                {workspaceDescription}
              </p>
              <div className="mt-4 flex flex-wrap gap-2">
                <span className="rounded-full bg-[var(--primary-subtle)] px-3 py-1 text-xs font-medium text-[var(--primary)]">
                  {workspacePlan}
                </span>
                <span className="rounded-full bg-emerald-500/10 px-3 py-1 text-xs font-medium text-emerald-600 dark:text-emerald-300">
                  Clerk session
                </span>
              </div>
            </div>

            <div className="mt-6">
              <WorkspaceNav pathname={pathname} />
            </div>

            {session.error ? (
              <div className="mt-6 rounded-[24px] border border-amber-500/20 bg-amber-500/10 p-4 text-sm text-amber-800 dark:text-amber-200">
                {session.error}
              </div>
            ) : null}

            <div className="mt-auto space-y-4 px-1 pt-6">
              <div className="rounded-[24px] border border-[var(--border)] bg-[var(--surface)]/82 p-4 shadow-[var(--shadow-sm)]">
                <p className="text-xs font-semibold uppercase tracking-[0.18em] text-[var(--foreground-subtle)]">
                  Delivery
                </p>
                <div className="mt-3 flex items-start gap-3">
                  <BellRing className="mt-0.5 size-4 text-[var(--accent)]" />
                  <div>
                    <p className="text-sm font-medium">Weekday 09:00 digest is active</p>
                    <p className="mt-1 text-sm text-[var(--foreground-muted)]">
                      Email brief and webhook sync will both receive today&apos;s shortlist.
                    </p>
                  </div>
                </div>
              </div>

              <ThemeToggle variant="sidebar" />
            </div>
          </aside>

          <div className="flex min-w-0 flex-1 flex-col">
            <header className="sticky top-0 z-30 border-b border-[var(--border)] bg-[var(--background)]/84 backdrop-blur-xl">
              <div className="px-4 py-4 sm:px-6 lg:px-8">
                <div className="flex flex-col gap-4">
                  <div className="flex items-start justify-between gap-4">
                    <div className="min-w-0">
                      <div className="flex items-center gap-2 text-xs font-semibold uppercase tracking-[0.22em] text-[var(--foreground-subtle)]">
                        <span>Scivly Workspace</span>
                        <span className="h-1 w-1 rounded-full bg-[var(--foreground-subtle)]" />
                        <span>{currentPage.title}</span>
                      </div>
                      <h1 className="mt-3 font-[family:var(--font-display)] text-3xl font-semibold tracking-tight sm:text-4xl">
                        {currentPage.title}
                      </h1>
                      <p className="mt-3 max-w-3xl text-sm leading-7 text-[var(--foreground-muted)] sm:text-base">
                        {currentPage.subtitle}
                      </p>
                    </div>

                    <div className="flex items-center gap-2">
                      <Dialog open={mobileOpen} onOpenChange={setMobileOpen}>
                        <DialogTrigger asChild>
                          <Button variant="secondary" size="icon" className="lg:hidden" aria-label="Open workspace navigation">
                            <Menu />
                          </Button>
                        </DialogTrigger>
                        <DialogContent
                          className="left-0 top-0 h-full w-[22rem] max-w-[calc(100%-3rem)] translate-x-0 translate-y-0 rounded-none rounded-r-[28px] border-l-0 p-0"
                          showCloseButton={false}
                        >
                            <div className="flex h-full flex-col">
                            <DialogHeader className="border-b border-[var(--border)] p-6">
                              <DialogTitle>{workspaceName}</DialogTitle>
                              <DialogDescription>{workspaceDescription}</DialogDescription>
                            </DialogHeader>
                            <div className="flex-1 px-4 py-6">
                              <WorkspaceNav pathname={pathname} onNavigate={() => setMobileOpen(false)} />
                            </div>
                            <div className="border-t border-[var(--border)] p-4">
                              <ThemeToggle variant="sidebar" />
                            </div>
                          </div>
                        </DialogContent>
                      </Dialog>

                      <DropdownMenu>
                        <DropdownMenuTrigger asChild>
                          <Button variant="secondary" size="sm" className="gap-2">
                            <span className="hidden sm:inline">{workspaceName}</span>
                            <ChevronDown className="size-4" />
                          </Button>
                        </DropdownMenuTrigger>
                        <DropdownMenuContent align="end">
                          <DropdownMenuLabel>Workspace</DropdownMenuLabel>
                          <DropdownMenuItem>{workspaceName}</DropdownMenuItem>
                          <DropdownMenuSeparator />
                          <DropdownMenuItem disabled>
                            {session.user?.email ?? "Backend workspace sync in progress"}
                          </DropdownMenuItem>
                        </DropdownMenuContent>
                      </DropdownMenu>

                      <ThemeToggle className="hidden sm:inline-flex" />
                      <UserButton afterSignOutUrl="/" />
                    </div>
                  </div>

                  <div className="flex flex-wrap items-center gap-3 text-sm text-[var(--foreground-muted)]">
                    <span className="rounded-full border border-[var(--border)] bg-[var(--surface)]/82 px-3 py-1.5">
                      {session.backendUser?.role ?? "owner"} access
                    </span>
                    <span className="rounded-full border border-[var(--border)] bg-[var(--surface)]/82 px-3 py-1.5">
                      {workspace?.slug ?? "workspace-sync"}
                    </span>
                    <span className="rounded-full border border-[var(--border)] bg-[var(--surface)]/82 px-3 py-1.5">
                      {session.isSyncing ? "Syncing backend session" : "Backend session ready"}
                    </span>
                    <span className="rounded-full border border-[var(--border)] bg-[var(--surface)]/82 px-3 py-1.5">
                      Backend default 8100
                    </span>
                  </div>
                </div>
              </div>
            </header>

            <main className="flex-1 px-4 py-6 sm:px-6 lg:px-8 lg:py-8">{children}</main>
          </div>
        </div>
      </div>
      <Toaster />
    </QueryClientProvider>
  );
}
