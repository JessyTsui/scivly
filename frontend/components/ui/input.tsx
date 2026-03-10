import * as React from "react";

import { cn } from "@/lib/utils";

function Input({ className, type, ...props }: React.ComponentProps<"input">) {
  return (
    <input
      type={type}
      data-slot="input"
      className={cn(
        "min-h-11 w-full rounded-2xl border border-[var(--border)] bg-[var(--surface)]/88 px-4 py-2.5 text-sm text-[var(--foreground)] shadow-[var(--shadow-sm)] outline-none placeholder:text-[var(--foreground-subtle)] focus:border-[var(--primary)]/35 focus:ring-2 focus:ring-[var(--primary)]/12 disabled:cursor-not-allowed disabled:opacity-60",
        className
      )}
      {...props}
    />
  );
}

export { Input };
