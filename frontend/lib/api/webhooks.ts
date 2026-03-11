import { apiRequest, isMockApiEnabled } from "@/lib/api/client";
import type {
  PaginatedResponse,
  WebhookCreateInput,
  WebhookCreatedOut,
  WebhookDeliveryPreview,
  WebhookEventType,
  WebhookOut,
  WebhookUpdateInput,
} from "@/lib/api/types";

const DEFAULT_WEBHOOK_EVENTS: WebhookEventType[] = [
  "paper.matched",
  "paper.enriched",
  "digest.ready",
  "digest.delivered",
];

function clone<T>(value: T): T {
  return structuredClone(value);
}

function buildPage(items: WebhookOut[]): PaginatedResponse<WebhookOut> {
  return {
    items,
    total: items.length,
    page: 1,
    per_page: 50,
  };
}

function buildSecretPreview(secret: string) {
  return `whsec_...${secret.slice(-4)}`;
}

function buildMockDeliveries(events: WebhookEventType[]): WebhookDeliveryPreview[] {
  return events.slice(0, 2).map((eventType, index) => ({
    event_type: eventType,
    last_status: index === 0 ? "sent" : "retrying",
    last_attempt_at: new Date(Date.now() - 1000 * 60 * 60 * (index + 1)).toISOString(),
  }));
}

let webhookStore: WebhookOut[] = [
  {
    id: "wh-demo-research-queue",
    url: "https://hooks.example.com/scivly/research-queue",
    events: ["paper.matched", "digest.delivered"],
    is_active: true,
    secret_preview: "whsec_...demo",
    created_at: new Date(Date.now() - 1000 * 60 * 60 * 24 * 12).toISOString(),
    deliveries: [
      {
        event_type: "paper.matched",
        last_status: "sent",
        last_attempt_at: new Date(Date.now() - 1000 * 60 * 18).toISOString(),
      },
      {
        event_type: "digest.delivered",
        last_status: "retrying",
        last_attempt_at: new Date(Date.now() - 1000 * 60 * 55).toISOString(),
      },
    ],
  },
];

export async function listWebhooks() {
  if (!isMockApiEnabled()) {
    return apiRequest<PaginatedResponse<WebhookOut>>("/webhooks", {
      query: { page: 1, per_page: 50 },
    });
  }

  return buildPage(clone(webhookStore));
}

export async function createWebhook(input: WebhookCreateInput) {
  if (!isMockApiEnabled()) {
    return apiRequest<WebhookCreatedOut>("/webhooks", {
      method: "POST",
      body: input,
    });
  }

  const signingSecret = input.secret ?? `whsec_${crypto.randomUUID().replaceAll("-", "")}`;
  const created: WebhookCreatedOut = {
    id: crypto.randomUUID(),
    url: input.url,
    events: input.events.length > 0 ? input.events : DEFAULT_WEBHOOK_EVENTS,
    is_active: true,
    secret_preview: buildSecretPreview(signingSecret),
    created_at: new Date().toISOString(),
    deliveries: buildMockDeliveries(input.events.length > 0 ? input.events : DEFAULT_WEBHOOK_EVENTS),
    secret_hash: signingSecret,
  };
  const stored: WebhookOut = {
    id: created.id,
    url: created.url,
    events: created.events,
    is_active: created.is_active,
    secret_preview: created.secret_preview,
    created_at: created.created_at,
    deliveries: created.deliveries,
  };

  webhookStore = [stored, ...webhookStore];
  return clone(created);
}

export async function updateWebhook(id: string, input: WebhookUpdateInput) {
  if (!isMockApiEnabled()) {
    return apiRequest<WebhookOut>(`/webhooks/${id}`, {
      method: "PATCH",
      body: input,
    });
  }

  const existing = webhookStore.find((item) => item.id === id);
  if (!existing) {
    throw new Error(`Webhook ${id} was not found.`);
  }

  const updated: WebhookOut = {
    ...existing,
    url: input.url ?? existing.url,
    events: input.events ?? existing.events,
    is_active: input.is_active ?? existing.is_active,
  };

  webhookStore = webhookStore.map((item) => (item.id === id ? updated : item));
  return clone(updated);
}

export async function deleteWebhook(id: string) {
  if (!isMockApiEnabled()) {
    await apiRequest(`/webhooks/${id}`, { method: "DELETE" });
    return;
  }

  webhookStore = webhookStore.filter((item) => item.id !== id);
}

export function buildWebhookVerificationExample(secret: string) {
  return `import crypto from "node:crypto";

const signature = request.headers.get("x-scivly-signature") ?? "";
const payload = await request.text();
const timestamp = signature.split(",").find((part) => part.startsWith("t="))?.slice(2) ?? "";
const digest = crypto
  .createHmac("sha256", "${secret}")
  .update(\`\${timestamp}.\${payload}\`)
  .digest("hex");`;
}
