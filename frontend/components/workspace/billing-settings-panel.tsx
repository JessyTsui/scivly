"use client";

import { useMutation, useQuery, useQueryClient } from "@tanstack/react-query";
import {
  AlertTriangle,
  ArrowUpRight,
  CreditCard,
  Gauge,
  RefreshCw,
  Sparkles,
} from "lucide-react";

import { Badge } from "@/components/ui/badge";
import { Button } from "@/components/ui/button";
import {
  Card,
  CardContent,
  CardDescription,
  CardFooter,
  CardHeader,
  CardTitle,
} from "@/components/ui/card";
import { toast } from "@/components/ui/toast";
import {
  cancelBillingSubscription,
  createBillingPortalSession,
  createCheckoutSession,
  getBillingSubscription,
  reactivateBillingSubscription,
} from "@/lib/api/billing";
import type { BillingUsageLimitOut } from "@/lib/api/types";
import { useScivlySession } from "@/lib/auth/scivly-session";

const PLAN_LABELS = {
  free: "Free",
  pro: "Pro",
  team: "Team",
  enterprise: "Enterprise",
} as const;

function formatDate(value?: string | null) {
  if (!value) {
    return "No renewal date yet";
  }

  return new Intl.DateTimeFormat("en", {
    dateStyle: "medium",
    timeStyle: "short",
  }).format(new Date(value));
}

function formatLimit(limit?: number | null) {
  return limit == null ? "Unlimited" : limit.toLocaleString("en");
}

function formatUsageWindow(window: BillingUsageLimitOut["window"]) {
  return window === "day" ? "this day" : "this month";
}

function limitProgress(limit: BillingUsageLimitOut) {
  if (limit.limit == null || limit.limit <= 0) {
    return 0;
  }

  return Math.min((limit.used / limit.limit) * 100, 100);
}

export function BillingSettingsPanel() {
  const session = useScivlySession();
  const queryClient = useQueryClient();
  const queryKey = ["billing", session.workspace?.id ?? "pending"] as const;
  const isSessionReady =
    session.isLoaded &&
    session.isSignedIn &&
    !session.isSyncing &&
    session.backendUser !== null &&
    session.workspace !== null;
  const billingQuery = useQuery({
    queryKey,
    queryFn: getBillingSubscription,
    enabled: isSessionReady,
  });

  const handleRedirect = (url: string) => {
    window.location.assign(url);
  };

  const checkoutMutation = useMutation({
    mutationFn: () => createCheckoutSession({ plan: "pro" }),
    onSuccess: (payload) => handleRedirect(payload.url),
    onError: (error) => {
      toast("Checkout unavailable", {
        description: error instanceof Error ? error.message : "Stripe Checkout could not be opened.",
      });
    },
  });

  const portalMutation = useMutation({
    mutationFn: createBillingPortalSession,
    onSuccess: (payload) => handleRedirect(payload.url),
    onError: (error) => {
      toast("Portal unavailable", {
        description: error instanceof Error ? error.message : "The billing portal could not be opened.",
      });
    },
  });

  const cancelMutation = useMutation({
    mutationFn: cancelBillingSubscription,
    onSuccess: async () => {
      await queryClient.invalidateQueries({ queryKey });
      toast("Cancellation scheduled", {
        description: "The subscription will now end at the current billing period boundary.",
      });
    },
    onError: (error) => {
      toast("Cancellation failed", {
        description: error instanceof Error ? error.message : "The subscription could not be updated.",
      });
    },
  });

  const reactivateMutation = useMutation({
    mutationFn: reactivateBillingSubscription,
    onSuccess: async () => {
      await queryClient.invalidateQueries({ queryKey });
      toast("Renewal resumed", {
        description: "Stripe will continue renewing the workspace subscription.",
      });
    },
    onError: (error) => {
      toast("Resume failed", {
        description: error instanceof Error ? error.message : "The subscription could not be reactivated.",
      });
    },
  });

  const summary = billingQuery.data;
  const isBusy =
    checkoutMutation.isPending ||
    portalMutation.isPending ||
    cancelMutation.isPending ||
    reactivateMutation.isPending;

  return (
    <section className="grid gap-6 xl:grid-cols-[minmax(0,1.02fr)_minmax(0,0.98fr)]">
      <Card className="overflow-hidden">
        <CardHeader className="relative">
          <div className="absolute inset-x-0 top-0 h-1 bg-[linear-gradient(90deg,var(--accent)_0%,var(--primary)_100%)]" />
          <div className="flex items-start justify-between gap-4">
            <div>
              <CardTitle className="flex items-center gap-2 text-2xl">
                <CreditCard className="size-5 text-[var(--primary)]" />
                Billing
              </CardTitle>
              <CardDescription className="mt-2 max-w-2xl leading-7">
                Keep the workspace on the right Stripe-backed plan, watch the soft limits before
                they turn into degraded throughput, and hand long-term subscription changes to the
                portal instead of hiding them behind support requests.
              </CardDescription>
            </div>
            {summary ? (
              <Badge variant={summary.overage_warning ? "warning" : "info"} className="gap-1.5">
                {summary.overage_warning ? (
                  <AlertTriangle className="size-3.5" />
                ) : (
                  <Gauge className="size-3.5" />
                )}
                {summary.overage_warning ? "Soft limit reached" : "Within limits"}
              </Badge>
            ) : null}
          </div>
        </CardHeader>
        <CardContent className="grid gap-4 sm:grid-cols-3">
          <div className="rounded-[22px] border border-[var(--border)] bg-[var(--surface-hover)]/72 p-4">
            <p className="text-xs font-semibold uppercase tracking-[0.18em] text-[var(--foreground-subtle)]">
              Current plan
            </p>
            <p className="mt-3 font-[family:var(--font-display)] text-3xl font-semibold">
              {summary ? PLAN_LABELS[summary.plan] : "Syncing"}
            </p>
            <p className="mt-2 text-sm leading-6 text-[var(--foreground-muted)]">
              {summary
                ? `Stripe status: ${summary.subscription_status.replaceAll("_", " ")}.`
                : "Loading billing state from the backend."}
            </p>
          </div>
          <div className="rounded-[22px] border border-[var(--border)] bg-[var(--surface-hover)]/72 p-4">
            <p className="text-xs font-semibold uppercase tracking-[0.18em] text-[var(--foreground-subtle)]">
              Renewal
            </p>
            <p className="mt-3 font-[family:var(--font-display)] text-2xl font-semibold">
              {summary?.cancel_at_period_end ? "Scheduled to stop" : "Auto-renewing"}
            </p>
            <p className="mt-2 text-sm leading-6 text-[var(--foreground-muted)]">
              {summary ? formatDate(summary.current_period_end) : "Waiting for Stripe subscription state."}
            </p>
          </div>
          <div className="rounded-[22px] border border-[var(--border)] bg-[var(--surface-hover)]/72 p-4">
            <p className="text-xs font-semibold uppercase tracking-[0.18em] text-[var(--foreground-subtle)]">
              Customer
            </p>
            <p className="mt-3 font-[family:var(--font-display)] text-2xl font-semibold">
              {summary?.stripe_customer_id ? "Connected" : "Not connected"}
            </p>
            <p className="mt-2 text-sm leading-6 text-[var(--foreground-muted)]">
              {summary?.stripe_customer_id ?? "A Stripe customer record is created on first checkout."}
            </p>
          </div>
        </CardContent>
        <CardFooter className="flex flex-wrap items-center justify-between gap-3">
          <p className="text-sm text-[var(--foreground-muted)]">
            {summary?.overage_warning
              ? "Soft limits are warning-only right now. The platform should degrade gracefully instead of hard blocking."
              : "Limits are soft warnings today so teams can upgrade without a hard stop in the middle of a run."}
          </p>
          <div className="flex flex-wrap gap-3">
            {summary?.plan === "free" ? (
              <Button onClick={() => checkoutMutation.mutate()} disabled={!isSessionReady || isBusy}>
                <Sparkles />
                {checkoutMutation.isPending ? "Redirecting..." : "Upgrade to Pro"}
              </Button>
            ) : null}
            {summary?.portal_available ? (
              <Button
                variant="secondary"
                onClick={() => portalMutation.mutate()}
                disabled={!isSessionReady || isBusy}
              >
                <ArrowUpRight />
                {portalMutation.isPending ? "Opening..." : "Open billing portal"}
              </Button>
            ) : null}
            {summary && summary.plan !== "free" && !summary.cancel_at_period_end ? (
              <Button variant="secondary" onClick={() => cancelMutation.mutate()} disabled={isBusy}>
                <AlertTriangle />
                {cancelMutation.isPending ? "Scheduling..." : "Cancel at period end"}
              </Button>
            ) : null}
            {summary?.cancel_at_period_end ? (
              <Button variant="secondary" onClick={() => reactivateMutation.mutate()} disabled={isBusy}>
                <RefreshCw />
                {reactivateMutation.isPending ? "Resuming..." : "Resume renewal"}
              </Button>
            ) : null}
          </div>
        </CardFooter>
      </Card>

      <Card>
        <CardHeader>
          <CardTitle className="text-2xl">Usage limits</CardTitle>
          <CardDescription className="leading-7">
            Free and Pro use soft caps so the workspace can warn loudly before work needs to slow
            down or upgrade.
          </CardDescription>
        </CardHeader>
        <CardContent className="space-y-4">
          {!isSessionReady ? (
            <div className="rounded-[22px] border border-[var(--border)] bg-[var(--surface-hover)]/72 p-5 text-sm text-[var(--foreground-muted)]">
              Syncing authenticated workspace context...
            </div>
          ) : null}

          {isSessionReady && billingQuery.isLoading ? (
            <div className="rounded-[22px] border border-[var(--border)] bg-[var(--surface-hover)]/72 p-5 text-sm text-[var(--foreground-muted)]">
              Loading usage limits...
            </div>
          ) : null}

          {isSessionReady && billingQuery.isError ? (
            <div className="rounded-[22px] border border-rose-500/20 bg-rose-500/10 p-5 text-sm text-rose-700 dark:text-rose-200">
              Billing details could not be loaded. Verify Stripe config and authenticated backend
              access.
            </div>
          ) : null}

          {summary?.usage_limits.map((limit) => (
            <div
              key={limit.key}
              className={`rounded-[22px] border p-4 ${
                limit.soft_limited
                  ? "border-amber-500/25 bg-amber-500/8"
                  : "border-[var(--border)] bg-[var(--surface)]/84"
              }`}
            >
              <div className="flex items-start justify-between gap-4">
                <div>
                  <p className="text-sm font-medium">{limit.label}</p>
                  <p className="mt-1 text-sm leading-6 text-[var(--foreground-muted)]">
                    {limit.used.toLocaleString("en")} used {formatUsageWindow(limit.window)} of{" "}
                    {formatLimit(limit.limit)}.
                  </p>
                </div>
                <Badge variant={limit.soft_limited ? "warning" : "outline"}>
                  {limit.soft_limited ? "At limit" : `${formatLimit(limit.remaining)} left`}
                </Badge>
              </div>
              <div className="mt-4 h-2 rounded-full bg-[var(--surface-hover)]">
                <div
                  className={`h-full rounded-full ${
                    limit.soft_limited ? "bg-amber-500" : "bg-[var(--primary)]"
                  }`}
                  style={{ width: `${limitProgress(limit)}%` }}
                />
              </div>
            </div>
          ))}
        </CardContent>
      </Card>
    </section>
  );
}
