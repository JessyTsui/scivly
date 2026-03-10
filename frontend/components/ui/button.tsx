import * as React from "react";
import { cva, type VariantProps } from "class-variance-authority";
import { Slot } from "radix-ui";

import { cn } from "@/lib/utils";

const buttonVariants = cva(
  "inline-flex items-center justify-center gap-2 rounded-full border text-sm font-medium whitespace-nowrap transition-all duration-200 focus-visible:outline-none focus-visible:ring-2 focus-visible:ring-[var(--primary)] focus-visible:ring-offset-2 focus-visible:ring-offset-[var(--background)] disabled:pointer-events-none disabled:opacity-50 [&_svg]:pointer-events-none [&_svg]:size-4 [&_svg]:shrink-0",
  {
    variants: {
      variant: {
        default:
          "border-transparent bg-[linear-gradient(135deg,var(--primary)_0%,var(--primary-dark)_100%)] text-white shadow-[var(--shadow)] hover:-translate-y-0.5 hover:shadow-[var(--shadow-md)]",
        secondary:
          "border-[var(--border)] bg-[var(--surface)]/88 text-[var(--foreground)] shadow-[var(--shadow-sm)] backdrop-blur hover:border-[var(--border-strong)] hover:bg-[var(--surface-hover)]",
        outline:
          "border-[var(--border)] bg-transparent text-[var(--foreground)] hover:border-[var(--primary)]/30 hover:bg-[var(--primary-subtle)]/60 hover:text-[var(--primary)]",
        ghost:
          "border-transparent bg-transparent text-[var(--foreground-muted)] shadow-none hover:bg-[var(--surface-hover)] hover:text-[var(--foreground)]",
        destructive:
          "border-transparent bg-rose-600 text-white shadow-[var(--shadow-sm)] hover:bg-rose-500",
        link: "border-transparent bg-transparent px-0 text-[var(--primary)] shadow-none hover:text-[var(--primary-dark)] hover:underline",
      },
      size: {
        default: "min-h-11 px-4 py-2.5",
        sm: "min-h-10 px-3.5 py-2 text-sm",
        lg: "min-h-12 px-5 py-3 text-base",
        icon: "min-h-11 min-w-11 p-0",
      },
    },
    defaultVariants: {
      variant: "default",
      size: "default",
    },
  }
);

function Button({
  className,
  variant,
  size,
  asChild = false,
  ...props
}: React.ComponentProps<"button"> &
  VariantProps<typeof buttonVariants> & {
    asChild?: boolean;
  }) {
  const Comp = asChild ? Slot.Root : "button";

  return (
    <Comp
      data-slot="button"
      className={cn(buttonVariants({ variant, size, className }))}
      {...props}
    />
  );
}

export { Button, buttonVariants };
