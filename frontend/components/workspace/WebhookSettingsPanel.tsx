"use client";

import { useState } from "react";
import { useMutation, useQuery, useQueryClient } from "@tanstack/react-query";
import {
  Activity,
  AlertTriangle,
  CheckCircle2,
  Copy,
  PauseCircle,
  PlayCircle,
  Sparkles,
  Trash2,
  Webhook,
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
  buildWebhookVerificationExample,
  createWebhook,
  deleteWebhook,
  listWebhooks,
  updateWebhook,
} from "@/lib/api/webhooks";
import { useScivlySession } from "@/lib/auth/scivly-session";
import type {
  PaginatedResponse,
  WebhookCreateInput,
  WebhookCreatedOut,
  WebhookDeliveryPreview,
  WebhookEventType,
  WebhookOut,
} from "@/lib/api/types";

const EVENT_OPTIONS: Array<{
  value: WebhookEventType;
  label: string;
  description: string;
}> = [
  {
    value: "paper.matched",
    label: "paper.matched",
    description: "Fire when a workspace rule scores a paper into the matched set.",
  },
  {
    value: "paper.enriched",
    label: "paper.enriched",
    description: "Fire when enrichment finishes and the paper is digest-ready.",
  },
  {
    value: "digest.ready",
    label: "digest.ready",
    description: "Fire after digest assembly completes and content is ready to consume.",
  },
  {
    value: "digest.delivered",
    label: "digest.delivered",
    description: "Fire after delivery logging finishes for a digest run.",
  },
];

function formatDate(value?: string | null) {
  if (!value) {
    return "No attempts yet";
  }

  return new Intl.DateTimeFormat("en", {
    dateStyle: "medium",
    timeStyle: "short",
  }).format(new Date(value));
}

function patchWebhookPage(
  previous: PaginatedResponse<WebhookOut> | undefined,
  update: (items: WebhookOut[]) => WebhookOut[]
) {
  const items = update(previous?.items ?? []);
  return {
    items,
    total: items.length,
    page: 1,
    per_page: 50,
  };
}

function sortByCreated(items: WebhookOut[]) {
  return [...items].sort((left, right) => right.created_at.localeCompare(left.created_at));
}

function isValidUrl(value: string) {
  try {
    const url = new URL(value);
    return url.protocol === "https:" || url.protocol === "http:";
  } catch {
    return false;
  }
}

function statusBadgeVariant(status: WebhookDeliveryPreview["last_status"]) {
  switch (status) {
    case "sent":
      return "success";
    case "retrying":
      return "warning";
    case "failed":
      return "danger";
    default:
      return "secondary";
  }
}

export function WebhookSettingsPanel() {
  const session = useScivlySession();
  const queryClient = useQueryClient();
  const webhooksQueryKey = ["webhooks", session.workspace?.id ?? "pending"] as const;
  const isSessionReady =
    session.isLoaded &&
    session.isSignedIn &&
    !session.isSyncing &&
    session.backendUser !== null &&
    session.workspace !== null;
  const isWaitingForSession = !session.isLoaded || (session.isSignedIn && !isSessionReady);
  const webhooksQuery = useQuery({
    queryKey: webhooksQueryKey,
    queryFn: listWebhooks,
    enabled: isSessionReady,
  });
  const [url, setUrl] = useState("");
  const [events, setEvents] = useState<WebhookEventType[]>(["paper.matched", "digest.delivered"]);
  const [createdWebhook, setCreatedWebhook] = useState<WebhookCreatedOut | null>(null);

  const items = webhooksQuery.data?.items ?? [];
  const activeCount = items.filter((item) => item.is_active).length;
  const subscriptionCount = items.reduce((sum, item) => sum + item.events.length, 0);
  const degradedCount = items.filter((item) =>
    item.deliveries.some((delivery) => delivery.last_status === "failed" || delivery.last_status === "retrying")
  ).length;

  const createMutation = useMutation({
    mutationFn: (input: WebhookCreateInput) => createWebhook(input),
    onSuccess: (created) => {
      const storedWebhook: WebhookOut = {
        id: created.id,
        url: created.url,
        events: created.events,
        is_active: created.is_active,
        secret_preview: created.secret_preview,
        created_at: created.created_at,
        deliveries: created.deliveries,
      };
      queryClient.setQueryData<PaginatedResponse<WebhookOut>>(webhooksQueryKey, (previous) =>
        patchWebhookPage(previous, (current) => sortByCreated([storedWebhook, ...current]))
      );
      setCreatedWebhook(created);
      setUrl("");
      setEvents(["paper.matched", "digest.delivered"]);
      toast("Webhook created", {
        description: "Copy the signing secret now. It will not be shown again.",
      });
    },
  });

  const toggleMutation = useMutation({
    mutationFn: ({ id, isActive }: { id: string; isActive: boolean }) =>
      updateWebhook(id, { is_active: isActive }),
    onSuccess: (updated) => {
      queryClient.setQueryData<PaginatedResponse<WebhookOut>>(webhooksQueryKey, (previous) =>
        patchWebhookPage(previous, (current) =>
          current.map((item) => (item.id === updated.id ? updated : item))
        )
      );
      toast(updated.is_active ? "Webhook resumed" : "Webhook paused", {
        description: updated.is_active
          ? "Events will be delivered to this endpoint again."
          : "Scivly will keep the endpoint but stop outbound deliveries.",
      });
    },
  });

  const deleteMutation = useMutation({
    mutationFn: (id: string) => deleteWebhook(id),
    onSuccess: (_, id) => {
      queryClient.setQueryData<PaginatedResponse<WebhookOut>>(webhooksQueryKey, (previous) =>
        patchWebhookPage(previous, (current) => current.filter((item) => item.id !== id))
      );
      toast("Webhook deleted", {
        description: "The endpoint and its delivery stream have been removed.",
      });
    },
  });

  const handleEventToggle = (event: WebhookEventType) => {
    setEvents((current) =>
      current.includes(event) ? current.filter((item) => item !== event) : [...current, event]
    );
  };

  const handleCopy = async (value: string, label: string) => {
    await navigator.clipboard.writeText(value);
    toast(`${label} copied`, {
      description: "The value is ready to paste into your receiver.",
    });
  };

  return (
    <div className="space-y-6">
      <section className="grid gap-4 lg:grid-cols-[minmax(0,1.05fr)_minmax(320px,0.95fr)]">
        <Card className="overflow-hidden">
          <CardHeader className="relative">
            <div className="absolute inset-x-0 top-0 h-1 bg-[linear-gradient(90deg,var(--accent)_0%,var(--primary)_100%)]" />
            <div className="flex items-start justify-between gap-4">
              <div>
                <CardTitle className="text-2xl">Outbound webhooks</CardTitle>
                <CardDescription className="mt-2 max-w-2xl leading-7">
                  Subscribe external automations to match, enrichment, and digest lifecycle
                  events. Scivly signs every delivery and retries transient failures three times
                  with exponential backoff.
                </CardDescription>
              </div>
              <Badge variant="info" className="gap-1.5">
                <Webhook className="size-3.5" />
                HMAC-Signed
              </Badge>
            </div>
          </CardHeader>
          <CardContent className="grid gap-4 sm:grid-cols-3">
            <div className="rounded-[22px] border border-[var(--border)] bg-[var(--surface-hover)]/72 p-4">
              <p className="text-xs font-semibold uppercase tracking-[0.18em] text-[var(--foreground-subtle)]">
                Active endpoints
              </p>
              <p className="mt-3 font-[family:var(--font-display)] text-3xl font-semibold">
                {activeCount}
              </p>
              <p className="mt-2 text-sm leading-6 text-[var(--foreground-muted)]">
                Pause endpoints during maintenance without deleting their event selection.
              </p>
            </div>
            <div className="rounded-[22px] border border-[var(--border)] bg-[var(--surface-hover)]/72 p-4">
              <p className="text-xs font-semibold uppercase tracking-[0.18em] text-[var(--foreground-subtle)]">
                Subscriptions
              </p>
              <p className="mt-3 font-[family:var(--font-display)] text-3xl font-semibold">
                {subscriptionCount}
              </p>
              <p className="mt-2 text-sm leading-6 text-[var(--foreground-muted)]">
                Counted across the four supported paper and digest event types.
              </p>
            </div>
            <div className="rounded-[22px] border border-[var(--border)] bg-[var(--surface-hover)]/72 p-4">
              <p className="text-xs font-semibold uppercase tracking-[0.18em] text-[var(--foreground-subtle)]">
                Attention needed
              </p>
              <p className="mt-3 font-[family:var(--font-display)] text-3xl font-semibold">
                {degradedCount}
              </p>
              <p className="mt-2 text-sm leading-6 text-[var(--foreground-muted)]">
                Endpoints with a recent failed or retrying delivery preview.
              </p>
            </div>
          </CardContent>
        </Card>

        <Card className="border-amber-500/20 bg-amber-500/5">
          <CardHeader>
            <CardTitle className="flex items-center gap-2 text-xl">
              <AlertTriangle className="size-5 text-amber-600 dark:text-amber-300" />
              Receiver checklist
            </CardTitle>
            <CardDescription className="leading-7">
              Keep inbound handlers deterministic. Retries reuse the same delivery id so receivers
              can de-duplicate safely.
            </CardDescription>
          </CardHeader>
          <CardContent className="space-y-3 text-sm leading-7 text-[var(--foreground-muted)]">
            <div className="rounded-[20px] border border-amber-500/20 bg-[var(--surface)]/78 p-4">
              Verify `x-scivly-signature` against the raw request body before parsing JSON.
            </div>
            <div className="rounded-[20px] border border-amber-500/20 bg-[var(--surface)]/78 p-4">
              Return any `2xx` response to mark the delivery as sent. `4xx/5xx` responses are
              logged and retried up to three times.
            </div>
          </CardContent>
        </Card>
      </section>

      <section className="grid gap-6 xl:grid-cols-[minmax(0,0.95fr)_minmax(0,1.05fr)]">
        <Card>
          <CardHeader>
            <CardTitle className="flex items-center gap-2 text-2xl">
              <Webhook className="size-5 text-[var(--primary)]" />
              Register an endpoint
            </CardTitle>
            <CardDescription className="leading-7">
              Use HTTPS in production and subscribe only to the events your integration consumes.
            </CardDescription>
          </CardHeader>
          <CardContent className="space-y-5">
            <div className="space-y-2">
              <label htmlFor="webhook-url" className="text-sm font-medium">
                Endpoint URL
              </label>
              <Input
                id="webhook-url"
                type="url"
                placeholder="https://example.com/integrations/scivly"
                value={url}
                onChange={(event) => setUrl(event.target.value)}
              />
            </div>

            <fieldset className="space-y-3">
              <legend className="text-sm font-medium">Events</legend>
              <div className="grid gap-3">
                {EVENT_OPTIONS.map((option) => {
                  const selected = events.includes(option.value);
                  return (
                    <button
                      key={option.value}
                      type="button"
                      onClick={() => handleEventToggle(option.value)}
                      className={`min-h-11 rounded-[22px] border px-4 py-3 text-left transition-colors ${
                        selected
                          ? "border-[var(--accent)]/35 bg-[var(--accent)]/10 text-[var(--foreground)]"
                          : "border-[var(--border)] bg-[var(--surface)]/84 text-[var(--foreground-muted)] hover:border-[var(--border-strong)] hover:text-[var(--foreground)]"
                      }`}
                    >
                      <div className="flex items-start justify-between gap-3">
                        <div>
                          <p className="text-sm font-medium">{option.label}</p>
                          <p className="mt-1 text-sm leading-6">{option.description}</p>
                        </div>
                        {selected ? (
                          <CheckCircle2 className="mt-0.5 size-4 shrink-0 text-[var(--accent)]" />
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
              {events.length} event{events.length === 1 ? "" : "s"} selected
            </p>
            <Button
              onClick={() =>
                createMutation.mutate({
                  url: url.trim(),
                  events,
                })
              }
              disabled={!isSessionReady || createMutation.isPending || !isValidUrl(url.trim()) || events.length === 0}
            >
              <Sparkles />
              {createMutation.isPending ? "Creating..." : "Create webhook"}
            </Button>
          </CardFooter>
        </Card>

        <div className="space-y-6">
          {createdWebhook ? (
            <Card className="border-emerald-500/20 bg-emerald-500/5">
              <CardHeader>
                <CardTitle className="flex items-center gap-2 text-xl">
                  <CheckCircle2 className="size-5 text-emerald-600 dark:text-emerald-300" />
                  Copy this signing secret now
                </CardTitle>
                <CardDescription className="leading-7">
                  Scivly only returns the raw signing secret on creation. Save it in your receiver
                  before leaving this page.
                </CardDescription>
              </CardHeader>
              <CardContent className="space-y-4">
                <div className="rounded-[22px] border border-emerald-500/20 bg-[var(--surface)]/84 p-4">
                  <p className="text-xs font-semibold uppercase tracking-[0.18em] text-[var(--foreground-subtle)]">
                    Signing secret
                  </p>
                  <code className="mt-3 block overflow-x-auto font-[family:var(--font-mono)] text-sm leading-7">
                    {createdWebhook.signing_secret}
                  </code>
                </div>
                <div className="rounded-[22px] border border-[var(--border)] bg-[var(--surface)]/84 p-4">
                  <p className="text-xs font-semibold uppercase tracking-[0.18em] text-[var(--foreground-subtle)]">
                    Verification starter
                  </p>
                  <pre className="mt-3 overflow-x-auto whitespace-pre-wrap font-[family:var(--font-mono)] text-sm leading-7">
                    {buildWebhookVerificationExample(createdWebhook.signing_secret)}
                  </pre>
                </div>
              </CardContent>
              <CardFooter className="justify-end">
                <Button
                  variant="secondary"
                  onClick={() => handleCopy(createdWebhook.signing_secret, "Signing secret")}
                >
                  <Copy />
                  Copy secret
                </Button>
              </CardFooter>
            </Card>
          ) : null}

          <Card>
            <CardHeader>
              <CardTitle className="text-2xl">Registered endpoints</CardTitle>
              <CardDescription className="leading-7">
                Review recent delivery outcomes, pause noisy receivers, and trim dead endpoints
                before they accumulate retry churn.
              </CardDescription>
            </CardHeader>
            <CardContent className="space-y-4">
              {isWaitingForSession ? (
                <div className="rounded-[22px] border border-[var(--border)] bg-[var(--surface-hover)]/72 p-5 text-sm text-[var(--foreground-muted)]">
                  Syncing authenticated session...
                </div>
              ) : null}

              {!isWaitingForSession && webhooksQuery.isLoading ? (
                <div className="rounded-[22px] border border-[var(--border)] bg-[var(--surface-hover)]/72 p-5 text-sm text-[var(--foreground-muted)]">
                  Loading webhooks...
                </div>
              ) : null}

              {!isWaitingForSession && webhooksQuery.isError ? (
                <div className="rounded-[22px] border border-rose-500/20 bg-rose-500/10 p-5 text-sm text-rose-700 dark:text-rose-200">
                  Webhooks could not be loaded. Refresh the page or verify backend delivery setup.
                </div>
              ) : null}

              {!isWaitingForSession && !webhooksQuery.isLoading && !webhooksQuery.isError && items.length === 0 ? (
                <div className="rounded-[22px] border border-dashed border-[var(--border)] bg-[var(--surface-hover)]/60 p-6 text-sm leading-7 text-[var(--foreground-muted)]">
                  No webhook endpoints are registered yet.
                </div>
              ) : null}

              {items.map((item) => {
                const isDeleting = deleteMutation.isPending && deleteMutation.variables === item.id;
                const isToggling =
                  toggleMutation.isPending && toggleMutation.variables?.id === item.id;
                const lastAttempt = [...item.deliveries]
                  .sort((left, right) => right.last_attempt_at.localeCompare(left.last_attempt_at))[0];

                return (
                  <div
                    key={item.id}
                    className="rounded-[24px] border border-[var(--border)] bg-[var(--surface-hover)]/68 p-5"
                  >
                    <div className="flex flex-col gap-4 sm:flex-row sm:items-start sm:justify-between">
                      <div>
                        <div className="flex flex-wrap items-center gap-2">
                          <h3 className="max-w-2xl break-all font-[family:var(--font-display)] text-xl font-semibold">
                            {item.url}
                          </h3>
                          <Badge variant={item.is_active ? "success" : "warning"}>
                            {item.is_active ? "Active" : "Paused"}
                          </Badge>
                        </div>
                        <p className="mt-2 font-[family:var(--font-mono)] text-sm text-[var(--foreground-muted)]">
                          {item.secret_preview}
                        </p>
                      </div>

                      <div className="flex flex-wrap gap-2">
                        <Button
                          variant="outline"
                          onClick={() => toggleMutation.mutate({ id: item.id, isActive: !item.is_active })}
                          disabled={isToggling || isDeleting}
                        >
                          {item.is_active ? <PauseCircle /> : <PlayCircle />}
                          {isToggling ? "Updating..." : item.is_active ? "Pause" : "Resume"}
                        </Button>
                        <Button
                          variant="outline"
                          onClick={() => deleteMutation.mutate(item.id)}
                          disabled={isDeleting || isToggling}
                        >
                          <Trash2 />
                          {isDeleting ? "Deleting..." : "Delete"}
                        </Button>
                      </div>
                    </div>

                    <div className="mt-4 grid gap-3 md:grid-cols-3">
                      <div className="rounded-[20px] border border-[var(--border)] bg-[var(--surface)]/82 p-4">
                        <p className="text-xs font-semibold uppercase tracking-[0.16em] text-[var(--foreground-subtle)]">
                          Created
                        </p>
                        <p className="mt-2 text-sm">{formatDate(item.created_at)}</p>
                      </div>
                      <div className="rounded-[20px] border border-[var(--border)] bg-[var(--surface)]/82 p-4">
                        <p className="text-xs font-semibold uppercase tracking-[0.16em] text-[var(--foreground-subtle)]">
                          Subscribed events
                        </p>
                        <p className="mt-2 text-sm">{item.events.length} selected</p>
                      </div>
                      <div className="rounded-[20px] border border-[var(--border)] bg-[var(--surface)]/82 p-4">
                        <p className="text-xs font-semibold uppercase tracking-[0.16em] text-[var(--foreground-subtle)]">
                          Last attempt
                        </p>
                        <p className="mt-2 text-sm">
                          {lastAttempt ? formatDate(lastAttempt.last_attempt_at) : "No attempts yet"}
                        </p>
                      </div>
                    </div>

                    <div className="mt-4 flex flex-wrap gap-2">
                      {item.events.map((event) => (
                        <Badge key={event} variant="secondary">
                          {event}
                        </Badge>
                      ))}
                    </div>

                    <div className="mt-4 space-y-3">
                      {item.deliveries.length === 0 ? (
                        <div className="rounded-[20px] border border-dashed border-[var(--border)] bg-[var(--surface)]/72 p-4 text-sm text-[var(--foreground-muted)]">
                          No delivery previews yet.
                        </div>
                      ) : (
                        item.deliveries.map((delivery) => (
                          <div
                            key={`${item.id}-${delivery.event_type}`}
                            className="flex flex-col gap-3 rounded-[20px] border border-[var(--border)] bg-[var(--surface)]/82 p-4 md:flex-row md:items-center md:justify-between"
                          >
                            <div className="flex items-center gap-3">
                              <div className="rounded-full bg-[var(--primary-subtle)]/70 p-2 text-[var(--primary)]">
                                <Activity className="size-4" />
                              </div>
                              <div>
                                <p className="text-sm font-medium">{delivery.event_type}</p>
                                <p className="text-sm text-[var(--foreground-muted)]">
                                  {formatDate(delivery.last_attempt_at)}
                                </p>
                              </div>
                            </div>
                            <Badge variant={statusBadgeVariant(delivery.last_status)}>
                              {delivery.last_status}
                            </Badge>
                          </div>
                        ))
                      )}
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
