import * as React from "react";

import { cn } from "@/lib/utils";

function Textarea({ className, ...props }: React.ComponentProps<"textarea">) {
  return (
    <textarea
      data-slot="textarea"
      className={cn(
        "min-h-28 w-full rounded-3xl border border-[var(--border)] bg-[var(--surface)]/88 px-4 py-3 text-sm leading-6 text-[var(--foreground)] shadow-[var(--shadow-sm)] outline-none placeholder:text-[var(--foreground-subtle)] focus:border-[var(--primary)]/35 focus:ring-2 focus:ring-[var(--primary)]/12 disabled:cursor-not-allowed disabled:opacity-60",
        className
      )}
      {...props}
    />
  );
}

export { Textarea };
