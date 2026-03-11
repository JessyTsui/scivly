import { apiRequest, isMockApiEnabled } from "@/lib/api/client";
import type { BillingSessionOut, BillingSubscriptionOut } from "@/lib/api/types";

function clone<T>(value: T): T {
  return structuredClone(value);
}

function buildUsageLimits(plan: BillingSubscriptionOut["plan"]) {
  if (plan === "free") {
    return [
      {
        key: "papers_processed" as const,
        label: "Papers processed",
        window: "day" as const,
        used: 0,
        limit: 10,
        remaining: 10,
        soft_limited: false,
      },
      {
        key: "llm_tokens" as const,
        label: "LLM tokens",
        window: "month" as const,
        used: 0,
        limit: 50000,
        remaining: 50000,
        soft_limited: false,
      },
      {
        key: "digests_sent" as const,
        label: "Digests sent",
        window: "month" as const,
        used: 0,
        limit: 10,
        remaining: 10,
        soft_limited: false,
      },
    ];
  }

  if (plan === "enterprise") {
    return [
      {
        key: "papers_processed" as const,
        label: "Papers processed",
        window: "day" as const,
        used: 0,
        limit: null,
        remaining: null,
        soft_limited: false,
      },
      {
        key: "llm_tokens" as const,
        label: "LLM tokens",
        window: "month" as const,
        used: 0,
        limit: null,
        remaining: null,
        soft_limited: false,
      },
      {
        key: "digests_sent" as const,
        label: "Digests sent",
        window: "month" as const,
        used: 0,
        limit: null,
        remaining: null,
        soft_limited: false,
      },
    ];
  }

  return [
    {
      key: "papers_processed" as const,
      label: "Papers processed",
      window: "day" as const,
      used: 0,
      limit: 250,
      remaining: 250,
      soft_limited: false,
    },
    {
      key: "llm_tokens" as const,
      label: "LLM tokens",
      window: "month" as const,
      used: 0,
      limit: 1000000,
      remaining: 1000000,
      soft_limited: false,
    },
    {
      key: "digests_sent" as const,
      label: "Digests sent",
      window: "month" as const,
      used: 0,
      limit: 200,
      remaining: 200,
      soft_limited: false,
    },
  ];
}

let mockBillingSummary: BillingSubscriptionOut = {
  workspace_id: "mock-workspace",
  plan: "free",
  subscription_status: "free",
  stripe_customer_id: null,
  stripe_subscription_id: null,
  stripe_price_id: null,
  cancel_at_period_end: false,
  current_period_end: null,
  portal_available: false,
  usage_limits: buildUsageLimits("free"),
  overage_warning: false,
};

export async function getBillingSubscription() {
  if (!isMockApiEnabled()) {
    return apiRequest<BillingSubscriptionOut>("/billing/subscription");
  }

  return clone(mockBillingSummary);
}

export async function createCheckoutSession(input: { plan: "pro" }) {
  if (!isMockApiEnabled()) {
    return apiRequest<BillingSessionOut>("/billing/checkout-session", {
      method: "POST",
      body: input,
    });
  }

  mockBillingSummary = {
    ...mockBillingSummary,
    plan: input.plan,
    subscription_status: "active",
    stripe_customer_id: mockBillingSummary.stripe_customer_id ?? "cus_mock_checkout_123",
    stripe_subscription_id: "sub_mock_checkout_123",
    stripe_price_id: "price_mock_pro_123",
    cancel_at_period_end: false,
    current_period_end: new Date(Date.now() + 1000 * 60 * 60 * 24 * 30).toISOString(),
    portal_available: true,
    usage_limits: buildUsageLimits("pro"),
    overage_warning: false,
  };

  return {
    id: "cs_mock_checkout_123",
    url: "/workspace/settings?billing=mock-checkout",
  };
}

export async function createBillingPortalSession() {
  if (!isMockApiEnabled()) {
    return apiRequest<BillingSessionOut>("/billing/portal-session", {
      method: "POST",
      body: {},
    });
  }

  return {
    id: "bps_mock_portal_123",
    url: "/workspace/settings?billing=mock-portal",
  };
}

export async function cancelBillingSubscription() {
  if (!isMockApiEnabled()) {
    return apiRequest<BillingSubscriptionOut>("/billing/subscription/cancel", {
      method: "POST",
    });
  }

  mockBillingSummary = {
    ...mockBillingSummary,
    cancel_at_period_end: true,
  };
  return clone(mockBillingSummary);
}

export async function reactivateBillingSubscription() {
  if (!isMockApiEnabled()) {
    return apiRequest<BillingSubscriptionOut>("/billing/subscription/reactivate", {
      method: "POST",
    });
  }

  mockBillingSummary = {
    ...mockBillingSummary,
    cancel_at_period_end: false,
  };
  return clone(mockBillingSummary);
}
