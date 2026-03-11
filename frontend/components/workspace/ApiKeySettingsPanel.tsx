"use client";

import { useState } from "react";
import { useMutation, useQuery, useQueryClient } from "@tanstack/react-query";
import {
  AlertTriangle,
  CheckCircle2,
  Copy,
  KeyRound,
  ShieldCheck,
  Sparkles,
  Trash2,
  Undo2,
} from "lucide-react";

import { toast } from "@/components/ui/toast";
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
import { Input } from "@/components/ui/input";
import {
  Select,
  SelectContent,
  SelectItem,
  SelectTrigger,
  SelectValue,
} from "@/components/ui/select";
import {
  buildApiKeyCurlExample,
  createApiKey,
  listApiKeys,
  revokeApiKey,
  updateApiKey,
} from "@/lib/api/api-keys";
import { useScivlySession } from "@/lib/auth/scivly-session";
import type {
  ApiKeyCreateInput,
  ApiKeyCreatedOut,
  ApiKeyOut,
  PaginatedResponse,
} from "@/lib/api/types";

const DEFAULT_SCOPES = ["papers:read", "digests:read"];
const EXPIRY_OPTIONS = [
  { value: "never", label: "Never expires" },
  { value: "30d", label: "30 days" },
  { value: "90d", label: "90 days" },
  { value: "180d", label: "180 days" },
];
const SCOPE_OPTIONS = [
  {
    value: "papers:read",
    label: "Papers read",
    description: "List papers and inspect individual records.",
  },
  {
    value: "digests:read",
    label: "Digests read",
    description: "Read digest previews and digest history.",
  },
  {
    value: "digests:write",
    label: "Digests write",
    description: "Trigger digest preview or delivery mutations.",
  },
  {
    value: "chat:read",
    label: "Chat read",
    description: "Read paper and digest chat sessions.",
  },
  {
    value: "chat:write",
    label: "Chat write",
    description: "Create or continue chat sessions programmatically.",
  },
  {
    value: "interests:read",
    label: "Interests read",
    description: "Read profiles, watchlists, and channel settings.",
  },
  {
    value: "interests:write",
    label: "Interests write",
    description: "Update profiles, authors, and delivery channels.",
  },
  {
    value: "webhooks:read",
    label: "Webhooks read",
    description: "Inspect registered webhook endpoints.",
  },
  {
    value: "webhooks:write",
    label: "Webhooks write",
    description: "Create or modify outbound webhook subscriptions.",
  },
  {
    value: "usage:read",
    label: "Usage read",
    description: "Inspect workspace usage and rate-limit outcomes.",
  },
  {
    value: "workspace:read",
    label: "Workspace read",
    description: "Read workspace metadata tied to the key.",
  },
];

function addDays(days: number) {
  const date = new Date();
  date.setDate(date.getDate() + days);
  return date.toISOString();
}

function resolveExpiry(value: string) {
  switch (value) {
    case "30d":
      return addDays(30);
    case "90d":
      return addDays(90);
    case "180d":
      return addDays(180);
    default:
      return null;
  }
}

function formatDate(value?: string | null) {
  if (!value) {
    return "Never";
  }

  return new Intl.DateTimeFormat("en", {
    dateStyle: "medium",
    timeStyle: "short",
  }).format(new Date(value));
}

function sortByCreated(items: ApiKeyOut[]) {
  return [...items].sort((left, right) => right.created_at.localeCompare(left.created_at));
}

function patchApiKeyPage(
  previous: PaginatedResponse<ApiKeyOut> | undefined,
  update: (items: ApiKeyOut[]) => ApiKeyOut[]
) {
  const items = update(previous?.items ?? []);
  return {
    items,
    total: items.length,
    page: 1,
    per_page: 50,
  };
}

export function ApiKeySettingsPanel() {
  const session = useScivlySession();
  const queryClient = useQueryClient();
  const apiKeysQueryKey = ["api-keys", session.workspace?.id ?? "pending"] as const;
  const isSessionReady =
    session.isLoaded &&
    session.isSignedIn &&
    !session.isSyncing &&
    session.backendUser !== null &&
    session.workspace !== null;
  const isWaitingForSession = !session.isLoaded || (session.isSignedIn && !isSessionReady);
  const apiKeysQuery = useQuery({
    queryKey: apiKeysQueryKey,
    queryFn: listApiKeys,
    enabled: isSessionReady,
  });
  const [name, setName] = useState("");
  const [expiry, setExpiry] = useState("90d");
  const [scopes, setScopes] = useState<string[]>(DEFAULT_SCOPES);
  const [createdKey, setCreatedKey] = useState<ApiKeyCreatedOut | null>(null);

  const items = apiKeysQuery.data?.items ?? [];
  const activeCount = items.filter((item) => item.is_active).length;
  const last24hCalls = items.reduce((sum, item) => sum + item.usage_last_24h, 0);
  const totalCalls = items.reduce((sum, item) => sum + item.usage_total, 0);

  const createMutation = useMutation({
    mutationFn: (input: ApiKeyCreateInput) => createApiKey(input),
    onSuccess: (created) => {
      const storedKey: ApiKeyOut = {
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
      queryClient.setQueryData<PaginatedResponse<ApiKeyOut>>(apiKeysQueryKey, (previous) =>
        patchApiKeyPage(previous, (current) => sortByCreated([storedKey, ...current]))
      );
      setCreatedKey(created);
      setName("");
      setExpiry("90d");
      setScopes(DEFAULT_SCOPES);
      toast("API key created", {
        description: "Copy the secret now. It is only shown once.",
      });
    },
  });

  const revokeMutation = useMutation({
    mutationFn: (id: string) => revokeApiKey(id),
    onSuccess: (_, id) => {
      queryClient.setQueryData<PaginatedResponse<ApiKeyOut>>(apiKeysQueryKey, (previous) =>
        patchApiKeyPage(previous, (current) =>
          current.map((item) =>
            item.id === id
              ? {
                  ...item,
                  is_active: false,
                }
              : item
          )
        )
      );
      toast("API key revoked", {
        description: "Requests with that token will now fail authentication.",
      });
    },
  });

  const restoreMutation = useMutation({
    mutationFn: (id: string) => updateApiKey(id, { is_active: true }),
    onSuccess: (updated) => {
      queryClient.setQueryData<PaginatedResponse<ApiKeyOut>>(apiKeysQueryKey, (previous) =>
        patchApiKeyPage(previous, (current) =>
          current.map((item) => (item.id === updated.id ? updated : item))
        )
      );
      toast("API key restored", {
        description: "The key is active again with the existing scope set.",
      });
    },
  });

  const handleScopeToggle = (scope: string) => {
    setScopes((current) =>
      current.includes(scope) ? current.filter((item) => item !== scope) : [...current, scope]
    );
  };

  const handleCopy = async (value: string, label: string) => {
    await navigator.clipboard.writeText(value);
    toast(`${label} copied`, {
      description: "The value is ready to paste into your integration.",
    });
  };

  return (
    <div className="space-y-6">
      <section className="grid gap-4 lg:grid-cols-[minmax(0,1.05fr)_minmax(320px,0.95fr)]">
        <Card className="overflow-hidden">
          <CardHeader className="relative">
            <div className="absolute inset-x-0 top-0 h-1 bg-[linear-gradient(90deg,var(--primary)_0%,var(--accent)_100%)]" />
            <div className="flex items-start justify-between gap-4">
              <div>
                <CardTitle className="text-2xl">Programmatic access</CardTitle>
                <CardDescription className="mt-2 max-w-2xl leading-7">
                  Issue workspace-scoped bearer keys, keep scopes narrow, and let middleware
                  enforce per-key and per-workspace rate limits before the request fan-out reaches
                  the rest of the stack.
                </CardDescription>
              </div>
              <Badge variant="info" className="gap-1.5">
                <ShieldCheck className="size-3.5" />
                Rate-limited
              </Badge>
            </div>
          </CardHeader>
          <CardContent className="grid gap-4 sm:grid-cols-3">
            <div className="rounded-[22px] border border-[var(--border)] bg-[var(--surface-hover)]/72 p-4">
              <p className="text-xs font-semibold uppercase tracking-[0.18em] text-[var(--foreground-subtle)]">
                Active keys
              </p>
              <p className="mt-3 font-[family:var(--font-display)] text-3xl font-semibold">
                {activeCount}
              </p>
              <p className="mt-2 text-sm leading-6 text-[var(--foreground-muted)]">
                Keep the blast radius small by revoking anything you no longer deploy.
              </p>
            </div>
            <div className="rounded-[22px] border border-[var(--border)] bg-[var(--surface-hover)]/72 p-4">
              <p className="text-xs font-semibold uppercase tracking-[0.18em] text-[var(--foreground-subtle)]">
                Calls / 24h
              </p>
              <p className="mt-3 font-[family:var(--font-display)] text-3xl font-semibold">
                {last24hCalls}
              </p>
              <p className="mt-2 text-sm leading-6 text-[var(--foreground-muted)]">
                Aggregated from API key usage records written by the auth middleware.
              </p>
            </div>
            <div className="rounded-[22px] border border-[var(--border)] bg-[var(--surface-hover)]/72 p-4">
              <p className="text-xs font-semibold uppercase tracking-[0.18em] text-[var(--foreground-subtle)]">
                Lifetime calls
              </p>
              <p className="mt-3 font-[family:var(--font-display)] text-3xl font-semibold">
                {totalCalls}
              </p>
              <p className="mt-2 text-sm leading-6 text-[var(--foreground-muted)]">
                Every authenticated API key request updates usage and the key&apos;s last-used time.
              </p>
            </div>
          </CardContent>
        </Card>

        <Card className="border-amber-500/20 bg-amber-500/5">
          <CardHeader>
            <CardTitle className="flex items-center gap-2 text-xl">
              <AlertTriangle className="size-5 text-amber-600 dark:text-amber-300" />
              Operational guardrails
            </CardTitle>
            <CardDescription className="leading-7">
              Keys inherit a workspace context, obey route scopes, and are rejected immediately
              after revocation or expiry.
            </CardDescription>
          </CardHeader>
          <CardContent className="space-y-3 text-sm leading-7 text-[var(--foreground-muted)]">
            <div className="rounded-[20px] border border-amber-500/20 bg-[var(--surface)]/78 p-4">
              `Authorization: Bearer &lt;key&gt;` works against the same REST surface as signed-in
              users, but API key management itself still requires a human session.
            </div>
            <div className="rounded-[20px] border border-amber-500/20 bg-[var(--surface)]/78 p-4">
              Default limits are enforced in the backend window policy. Once the limit is crossed,
              the API returns `429` before route execution.
            </div>
          </CardContent>
        </Card>
      </section>

      <section className="grid gap-6 xl:grid-cols-[minmax(0,0.95fr)_minmax(0,1.05fr)]">
        <Card>
          <CardHeader>
            <CardTitle className="flex items-center gap-2 text-2xl">
              <KeyRound className="size-5 text-[var(--primary)]" />
              Issue a new key
            </CardTitle>
            <CardDescription className="leading-7">
              Prefer explicit names and only the scopes your integration actually needs.
            </CardDescription>
          </CardHeader>
          <CardContent className="space-y-5">
            <div className="space-y-2">
              <label htmlFor="api-key-name" className="text-sm font-medium">
                Key name
              </label>
              <Input
                id="api-key-name"
                placeholder="Agent runner, digest bot, local script..."
                value={name}
                onChange={(event) => setName(event.target.value)}
              />
            </div>

            <div className="space-y-2">
              <label htmlFor="api-key-expiry" className="text-sm font-medium">
                Expiration
              </label>
              <Select value={expiry} onValueChange={setExpiry}>
                <SelectTrigger id="api-key-expiry">
                  <SelectValue placeholder="Choose an expiration window" />
                </SelectTrigger>
                <SelectContent>
                  {EXPIRY_OPTIONS.map((option) => (
                    <SelectItem key={option.value} value={option.value}>
                      {option.label}
                    </SelectItem>
                  ))}
                </SelectContent>
              </Select>
            </div>

            <fieldset className="space-y-3">
              <legend className="text-sm font-medium">Scopes</legend>
              <div className="grid gap-3">
                {SCOPE_OPTIONS.map((option) => {
                  const selected = scopes.includes(option.value);
                  return (
                    <button
                      key={option.value}
                      type="button"
                      onClick={() => handleScopeToggle(option.value)}
                      className={`min-h-11 rounded-[22px] border px-4 py-3 text-left transition-colors ${
                        selected
                          ? "border-[var(--primary)]/35 bg-[var(--primary-subtle)]/72 text-[var(--foreground)]"
                          : "border-[var(--border)] bg-[var(--surface)]/84 text-[var(--foreground-muted)] hover:border-[var(--border-strong)] hover:text-[var(--foreground)]"
                      }`}
                    >
                      <div className="flex items-start justify-between gap-3">
                        <div>
                          <p className="text-sm font-medium">{option.label}</p>
                          <p className="mt-1 text-sm leading-6">{option.description}</p>
                        </div>
                        {selected ? (
                          <CheckCircle2 className="mt-0.5 size-4 shrink-0 text-[var(--primary)]" />
                        ) : null}
                      </div>
                    </button>
                  );
                })}
              </div>
            </fieldset>
          </CardContent>
          <CardFooter className="justify-between">
            <p className="text-sm text-[var(--foreground-muted)]">
              {scopes.length} scope{scopes.length === 1 ? "" : "s"} selected
            </p>
            <Button
              onClick={() =>
                createMutation.mutate({
                  name: name.trim(),
                  scopes,
                  expires_at: resolveExpiry(expiry),
                })
              }
              disabled={
                !isSessionReady ||
                createMutation.isPending ||
                name.trim().length < 2 ||
                scopes.length === 0
              }
            >
              <Sparkles />
              {createMutation.isPending ? "Creating..." : "Create key"}
            </Button>
          </CardFooter>
        </Card>

        <div className="space-y-6">
          {createdKey ? (
            <Card className="border-emerald-500/20 bg-emerald-500/5">
              <CardHeader>
                <CardTitle className="flex items-center gap-2 text-xl">
                  <CheckCircle2 className="size-5 text-emerald-600 dark:text-emerald-300" />
                  Copy this secret now
                </CardTitle>
                <CardDescription className="leading-7">
                  The full bearer token is only returned at creation time. Store it in your secret
                  manager before leaving this page.
                </CardDescription>
              </CardHeader>
              <CardContent className="space-y-4">
                <div className="rounded-[22px] border border-emerald-500/20 bg-[var(--surface)]/84 p-4">
                  <p className="text-xs font-semibold uppercase tracking-[0.18em] text-[var(--foreground-subtle)]">
                    Bearer token
                  </p>
                  <code className="mt-3 block overflow-x-auto font-[family:var(--font-mono)] text-sm leading-7">
                    {createdKey.token}
                  </code>
                </div>
                <div className="rounded-[22px] border border-[var(--border)] bg-[var(--surface)]/84 p-4">
                  <p className="text-xs font-semibold uppercase tracking-[0.18em] text-[var(--foreground-subtle)]">
                    Quick smoke test
                  </p>
                  <pre className="mt-3 overflow-x-auto whitespace-pre-wrap font-[family:var(--font-mono)] text-sm leading-7">
                    {buildApiKeyCurlExample(createdKey.token)}
                  </pre>
                </div>
              </CardContent>
              <CardFooter className="justify-end">
                <Button variant="secondary" onClick={() => handleCopy(createdKey.token, "API key")}>
                  <Copy />
                  Copy token
                </Button>
              </CardFooter>
            </Card>
          ) : null}

          <Card>
            <CardHeader>
              <CardTitle className="text-2xl">Issued keys</CardTitle>
              <CardDescription className="leading-7">
                Review status, scope footprint, and usage before integrations drift too far from
                what the workspace actually needs.
              </CardDescription>
            </CardHeader>
            <CardContent className="space-y-4">
              {isWaitingForSession ? (
                <div className="rounded-[22px] border border-[var(--border)] bg-[var(--surface-hover)]/72 p-5 text-sm text-[var(--foreground-muted)]">
                  Syncing authenticated session...
                </div>
              ) : null}

              {!isWaitingForSession && apiKeysQuery.isLoading ? (
                <div className="rounded-[22px] border border-[var(--border)] bg-[var(--surface-hover)]/72 p-5 text-sm text-[var(--foreground-muted)]">
                  Loading API keys...
                </div>
              ) : null}

              {!isWaitingForSession && apiKeysQuery.isError ? (
                <div className="rounded-[22px] border border-rose-500/20 bg-rose-500/10 p-5 text-sm text-rose-700 dark:text-rose-200">
                  API keys could not be loaded. Refresh the page or verify backend auth sync.
                </div>
              ) : null}

              {!isWaitingForSession && !apiKeysQuery.isLoading && !apiKeysQuery.isError && items.length === 0 ? (
                <div className="rounded-[22px] border border-dashed border-[var(--border)] bg-[var(--surface-hover)]/60 p-6 text-sm leading-7 text-[var(--foreground-muted)]">
                  No keys have been issued yet.
                </div>
              ) : null}

              {items.map((item) => {
                const busy =
                  revokeMutation.isPending && revokeMutation.variables === item.id
                    ? "revoke"
                    : restoreMutation.isPending && restoreMutation.variables === item.id
                      ? "restore"
                      : null;

                return (
                  <div
                    key={item.id}
                    className="rounded-[24px] border border-[var(--border)] bg-[var(--surface-hover)]/68 p-5"
                  >
                    <div className="flex flex-col gap-4 sm:flex-row sm:items-start sm:justify-between">
                      <div>
                        <div className="flex flex-wrap items-center gap-2">
                          <h3 className="font-[family:var(--font-display)] text-xl font-semibold">
                            {item.name}
                          </h3>
                          <Badge variant={item.is_active ? "success" : "warning"}>
                            {item.is_active ? "Active" : "Revoked"}
                          </Badge>
                        </div>
                        <p className="mt-2 font-[family:var(--font-mono)] text-sm text-[var(--foreground-muted)]">
                          {item.prefix}
                        </p>
                      </div>

                      <div className="flex gap-2">
                        {item.is_active ? (
                          <Button
                            variant="outline"
                            onClick={() => revokeMutation.mutate(item.id)}
                            disabled={busy !== null}
                          >
                            <Trash2 />
                            {busy === "revoke" ? "Revoking..." : "Revoke"}
                          </Button>
                        ) : (
                          <Button
                            variant="secondary"
                            onClick={() => restoreMutation.mutate(item.id)}
                            disabled={busy !== null}
                          >
                            <Undo2 />
                            {busy === "restore" ? "Restoring..." : "Restore"}
                          </Button>
                        )}
                      </div>
                    </div>

                    <div className="mt-4 grid gap-3 md:grid-cols-3">
                      <div className="rounded-[20px] border border-[var(--border)] bg-[var(--surface)]/82 p-4">
                        <p className="text-xs font-semibold uppercase tracking-[0.16em] text-[var(--foreground-subtle)]">
                          Last used
                        </p>
                        <p className="mt-2 text-sm">{formatDate(item.last_used_at)}</p>
                      </div>
                      <div className="rounded-[20px] border border-[var(--border)] bg-[var(--surface)]/82 p-4">
                        <p className="text-xs font-semibold uppercase tracking-[0.16em] text-[var(--foreground-subtle)]">
                          Expires
                        </p>
                        <p className="mt-2 text-sm">{formatDate(item.expires_at)}</p>
                      </div>
                      <div className="rounded-[20px] border border-[var(--border)] bg-[var(--surface)]/82 p-4">
                        <p className="text-xs font-semibold uppercase tracking-[0.16em] text-[var(--foreground-subtle)]">
                          Requests
                        </p>
                        <p className="mt-2 text-sm">
                          {item.usage_last_24h} / 24h · {item.usage_total} total
                        </p>
                      </div>
                    </div>

                    <div className="mt-4 flex flex-wrap gap-2">
                      {item.scopes.map((scope) => (
                        <Badge key={scope} variant="secondary">
                          {scope}
                        </Badge>
                      ))}
                    </div>
                  </div>
                );
              })}
            </CardContent>
          </Card>
        </div>
      </section>
    </div>
  );
}
