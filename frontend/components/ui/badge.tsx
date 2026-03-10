import * as React from "react";
import { cva, type VariantProps } from "class-variance-authority";

import { cn } from "@/lib/utils";

const badgeVariants = cva(
  "inline-flex items-center gap-1 rounded-full border px-2.5 py-1 text-xs font-semibold whitespace-nowrap transition-colors",
  {
    variants: {
      variant: {
        default: "border-[var(--primary)]/10 bg-[var(--primary-subtle)] text-[var(--primary)]",
        secondary: "border-[var(--border)] bg-[var(--surface-hover)] text-[var(--foreground-muted)]",
        outline: "border-[var(--border)] bg-transparent text-[var(--foreground)]",
        success: "border-emerald-500/15 bg-emerald-500/10 text-emerald-600 dark:text-emerald-300",
        warning: "border-amber-500/15 bg-amber-500/10 text-amber-600 dark:text-amber-300",
        danger: "border-rose-500/15 bg-rose-500/10 text-rose-600 dark:text-rose-300",
        info: "border-sky-500/15 bg-sky-500/10 text-sky-600 dark:text-sky-300",
      },
    },
    defaultVariants: {
      variant: "default",
    },
  }
);

function Badge({
  className,
  variant,
  ...props
}: React.ComponentProps<"span"> & VariantProps<typeof badgeVariants>) {
  return <span data-slot="badge" className={cn(badgeVariants({ variant }), className)} {...props} />;
}

export { Badge, badgeVariants };
