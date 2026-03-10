"use client";

import { Moon, Sun } from "lucide-react";

import { useTheme } from "@/app/providers";

export function ThemeToggle({
  className = "",
  variant = "default",
}: {
  className?: string;
  variant?: "default" | "sidebar" | "ghost";
}) {
  const { theme, toggleTheme } = useTheme();

  if (variant === "sidebar") {
    return (
      <button
        type="button"
        onClick={toggleTheme}
        className={`flex min-h-11 w-full items-center gap-3 rounded-2xl border border-[var(--border)] bg-[var(--surface)]/70 px-3 py-3 text-sm font-medium text-[var(--foreground-muted)] shadow-[var(--shadow-sm)] backdrop-blur transition-colors hover:border-[var(--border-strong)] hover:bg-[var(--surface-hover)] hover:text-[var(--foreground)] ${className}`}
        aria-label={theme === "light" ? "Switch to dark theme" : "Switch to light theme"}
      >
        {theme === "light" ? (
          <>
            <Moon className="h-4 w-4" />
            <span>Dark Mode</span>
          </>
        ) : (
          <>
            <Sun className="h-4 w-4" />
            <span>Light Mode</span>
          </>
        )}
      </button>
    );
  }

  return (
    <button
      type="button"
      onClick={toggleTheme}
      className={`inline-flex min-h-11 min-w-11 items-center justify-center rounded-xl border border-[var(--border)] bg-[var(--surface)]/80 p-2 text-[var(--foreground-muted)] shadow-[var(--shadow-sm)] backdrop-blur transition-colors hover:border-[var(--border-strong)] hover:bg-[var(--surface-hover)] hover:text-[var(--foreground)] ${className}`}
      aria-label={theme === "light" ? "Switch to dark theme" : "Switch to light theme"}
    >
      {theme === "light" ? (
        <Moon className="h-4 w-4" />
      ) : (
        <Sun className="h-4 w-4" />
      )}
    </button>
  );
}
