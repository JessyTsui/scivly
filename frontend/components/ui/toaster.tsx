"use client";

import { Toaster as Sonner } from "sonner";

import { useTheme } from "@/app/providers";

export function Toaster() {
  const { theme } = useTheme();

  return (
    <Sonner
      closeButton
      richColors
      position="top-right"
      theme={theme}
      toastOptions={{
        classNames: {
          toast:
            "rounded-[20px] border border-[var(--border)] bg-[var(--surface)]/94 text-[var(--foreground)] shadow-[var(--shadow-lg)] backdrop-blur-xl",
          title: "font-medium",
          description: "text-[var(--foreground-muted)]",
        },
      }}
    />
  );
}
