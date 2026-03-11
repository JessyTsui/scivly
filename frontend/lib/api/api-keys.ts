import { apiRequest, isMockApiEnabled } from "@/lib/api/client";
import type {
  ApiKeyCreateInput,
  ApiKeyCreatedOut,
  ApiKeyOut,
  ApiKeyUpdateInput,
  PaginatedResponse,
} from "@/lib/api/types";

function clone<T>(value: T): T {
  return structuredClone(value);
}

let apiKeyStore: ApiKeyOut[] = [
  {
    id: "key-demo-sdk",
    name: "Demo SDK Key",
    prefix: "scv_demo",
    scopes: ["papers:read", "digests:read", "chat:write"],
    last_used_at: new Date(Date.now() - 1000 * 60 * 42).toISOString(),
    expires_at: new Date(Date.now() + 1000 * 60 * 60 * 24 * 120).toISOString(),
    is_active: true,
    created_at: new Date(Date.now() - 1000 * 60 * 60 * 24 * 9).toISOString(),
    usage_last_24h: 18,
    usage_total: 264,
  },
];

function buildPage(items: ApiKeyOut[]): PaginatedResponse<ApiKeyOut> {
  return {
    items,
    total: items.length,
    page: 1,
    per_page: 50,
  };
}

function buildMockSecret(prefix: string) {
  return `${prefix}_${crypto.randomUUID().replaceAll("-", "")}`;
}

export async function listApiKeys() {
  if (!isMockApiEnabled()) {
    return apiRequest<PaginatedResponse<ApiKeyOut>>("/api-keys", {
      query: { page: 1, per_page: 50 },
    });
  }

  return buildPage(clone(apiKeyStore));
}

export async function createApiKey(input: ApiKeyCreateInput) {
  if (!isMockApiEnabled()) {
    return apiRequest<ApiKeyCreatedOut>("/api-keys", {
      method: "POST",
      body: input,
    });
  }

  const prefix = `scv_${crypto.randomUUID().slice(0, 8).replaceAll("-", "")}`;
  const created: ApiKeyCreatedOut = {
    id: crypto.randomUUID(),
    name: input.name,
    prefix,
    scopes: input.scopes,
    last_used_at: null,
    expires_at: input.expires_at ?? null,
    is_active: true,
    created_at: new Date().toISOString(),
    usage_last_24h: 0,
    usage_total: 0,
    token: buildMockSecret(prefix),
  };
  const stored: ApiKeyOut = {
    id: created.id,
    name: created.name,
    prefix: created.prefix,
    scopes: created.scopes,
    last_used_at: created.last_used_at,
    expires_at: created.expires_at,
    is_active: created.is_active,
    created_at: created.created_at,
    usage_last_24h: created.usage_last_24h,
    usage_total: created.usage_total,
  };

  apiKeyStore = [stored, ...apiKeyStore];

  return clone(created);
}

export async function updateApiKey(id: string, input: ApiKeyUpdateInput) {
  if (!isMockApiEnabled()) {
    return apiRequest<ApiKeyOut>(`/api-keys/${id}`, {
      method: "PATCH",
      body: input,
    });
  }

  const existing = apiKeyStore.find((item) => item.id === id);
  if (!existing) {
    throw new Error(`API key ${id} was not found.`);
  }

  const updated: ApiKeyOut = {
    ...existing,
    name: input.name ?? existing.name,
    scopes: input.scopes ?? existing.scopes,
    is_active: input.is_active ?? existing.is_active,
  };

  apiKeyStore = apiKeyStore.map((item) => (item.id === id ? updated : item));
  return clone(updated);
}

export async function revokeApiKey(id: string) {
  if (!isMockApiEnabled()) {
    await apiRequest(`/api-keys/${id}`, { method: "DELETE" });
    return;
  }

  apiKeyStore = apiKeyStore.map((item) =>
    item.id === id
      ? {
          ...item,
          is_active: false,
        }
      : item
  );
}

export function buildApiKeyCurlExample(apiKey: string) {
  return `curl "${process.env.NEXT_PUBLIC_API_URL ?? "http://localhost:8100"}/papers" \\
  -H "Authorization: Bearer ${apiKey}"`;
}
