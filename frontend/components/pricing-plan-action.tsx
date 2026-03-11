"use client";

import { useState } from "react";
import Link from "next/link";
import { toast } from "@/components/ui/toast";
import { createCheckoutSession } from "@/lib/api/billing";
import { useScivlySession } from "@/lib/auth/scivly-session";

function resolveButtonClass(featured: boolean) {
  return featured ? "btn-primary" : "btn-secondary";
}

export function PricingPlanAction({
  plan,
  href,
  label,
  featured = false,
}: {
  plan: "free" | "pro" | "enterprise";
  href: string;
  label: string;
  featured?: boolean;
}) {
  const session = useScivlySession();
  const currentPlan = session.workspace?.plan;
  const currentPlanIsPaid =
    currentPlan === "pro" || currentPlan === "team" || currentPlan === "enterprise";
  const buttonClass = resolveButtonClass(featured);
  const [isPending, setIsPending] = useState(false);

  const handleCheckout = async () => {
    setIsPending(true);
    try {
      const result = await createCheckoutSession({ plan: "pro" });
      window.location.assign(result.url);
    } catch (error) {
      toast("Stripe Checkout unavailable", {
        description:
          error instanceof Error ? error.message : "The checkout session could not be created.",
      });
    } finally {
      setIsPending(false);
    }
  };

  if (plan === "enterprise") {
    return (
      <Link href={href} className={buttonClass}>
        {label}
      </Link>
    );
  }

  if (plan === "free") {
    if (session.isSignedIn) {
      return (
        <Link href="/workspace/settings" className={buttonClass}>
          {currentPlanIsPaid ? "Manage billing" : "Current plan"}
        </Link>
      );
    }

    return (
      <Link href={href} className={buttonClass}>
        {label}
      </Link>
    );
  }

  if (!session.isSignedIn) {
    return (
      <Link href={`${href}?plan=pro`} className={buttonClass}>
        {label}
      </Link>
    );
  }

  if (currentPlanIsPaid) {
    return (
      <Link href="/workspace/settings" className={buttonClass}>
        Manage billing
      </Link>
    );
  }

  const disabled =
    !session.isLoaded ||
    session.isSyncing ||
    session.workspace === null ||
    isPending;

  return (
    <button
      type="button"
      className={buttonClass}
      onClick={() => void handleCheckout()}
      disabled={disabled}
    >
      {isPending ? "Redirecting..." : label}
    </button>
  );
}
