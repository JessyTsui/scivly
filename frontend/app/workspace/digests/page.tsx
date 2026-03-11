"use client";

import { useState } from "react";
import { useMutation, useQuery, useQueryClient } from "@tanstack/react-query";
import { CalendarClock, Clock3, Send } from "lucide-react";

import { getNotificationChannels } from "@/lib/api/interests";
import {
  getDigestSchedule,
  listDigests,
  updateDigestSchedule,
} from "@/lib/api/digests";
import { Button } from "@/components/ui/button";
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";
import { Select, SelectContent, SelectItem, SelectTrigger, SelectValue } from "@/components/ui/select";
import { Tabs, TabsContent, TabsList, TabsTrigger } from "@/components/ui/tabs";
import { toast } from "@/components/ui/toast";
import { ScoreBadge } from "@/components/workspace/ScoreBadge";
import { useScivlySession } from "@/lib/auth/scivly-session";
import { getNextRunAt } from "@/lib/mock/time";
import { formatCalendarDate, formatDateTime } from "@/lib/utils";

type CadencePreset = {
  label: string;
  cron_expression: string;
  hour: number;
  weekdays?: readonly number[];
};

const cadencePresets: Record<"weekday" | "evening" | "friday", CadencePreset> = {
  weekday: {
    label: "Weekdays at 09:00",
    cron_expression: "0 9 * * 1-5",
    hour: 9,
    weekdays: [1, 2, 3, 4, 5],
  },
  evening: {
    label: "Daily at 18:00",
    cron_expression: "0 18 * * *",
    hour: 18,
  },
  friday: {
    label: "Fridays at 17:00",
    cron_expression: "0 17 * * 5",
    hour: 17,
    weekdays: [5],
  },
} as const;

type CadenceKey = keyof typeof cadencePresets;
type ScheduleDraft = {
  activeChannelIds: string[];
  cadenceKey: CadenceKey;
  scheduleActive: boolean;
  timezone: string;
};

function resolveCadenceKey(cronExpression: string | undefined): CadenceKey {
  return (
    Object.entries(cadencePresets).find(([, preset]) => preset.cron_expression === cronExpression)?.[0] ??
    "weekday"
  ) as CadenceKey;
}

function buildScheduleDraft(
  schedule: Awaited<ReturnType<typeof getDigestSchedule>> | undefined
): ScheduleDraft {
  if (!schedule) {
    return {
      activeChannelIds: [],
      cadenceKey: "weekday",
      scheduleActive: true,
      timezone: "Asia/Shanghai",
    };
  }

  return {
    activeChannelIds: schedule.channel_ids,
    cadenceKey: resolveCadenceKey(schedule.cron_expression),
    scheduleActive: schedule.is_active,
    timezone: schedule.timezone,
  };
}

function getNextRunPreview(cadenceKey: CadenceKey, timezone: string) {
  const preset = cadencePresets[cadenceKey];

  return getNextRunAt({
    timeZone: timezone,
    hour: preset.hour,
    weekdays: preset.weekdays ? [...preset.weekdays] : undefined,
  });
}

export default function WorkspaceDigestsPage() {
  const session = useScivlySession();
  const queryClient = useQueryClient();
  const queriesEnabled =
    session.isLoaded &&
    session.isSignedIn &&
    !session.isSyncing &&
    !session.error &&
    Boolean(session.workspace);
  const digestsQuery = useQuery({
    queryKey: ["digests"],
    queryFn: listDigests,
    enabled: queriesEnabled,
  });
  const scheduleQuery = useQuery({
    queryKey: ["digest-schedule"],
    queryFn: getDigestSchedule,
    enabled: queriesEnabled,
  });
  const channelsQuery = useQuery({
    queryKey: ["channels"],
    queryFn: getNotificationChannels,
    enabled: queriesEnabled,
  });
  const [selectedDigestId, setSelectedDigestId] = useState("");
  const [scheduleDraft, setScheduleDraft] = useState<ScheduleDraft | null>(null);
  const combinedError =
    digestsQuery.error ?? scheduleQuery.error ?? channelsQuery.error ?? null;
  const effectiveSelectedDigestId = selectedDigestId || digestsQuery.data?.items[0]?.id || "";
  const { activeChannelIds, cadenceKey, scheduleActive, timezone } =
    scheduleDraft ?? buildScheduleDraft(scheduleQuery.data);

  const updateScheduleMutation = useMutation({
    mutationFn: updateDigestSchedule,
    onSuccess: (schedule) => {
      queryClient.setQueryData(["digest-schedule"], schedule);
      setScheduleDraft(null);
      toast("Schedule saved", {
        description: `Next digest run is set for ${formatDateTime(schedule.next_run_at)}.`,
      });
    },
  });

  const selectedDigest = digestsQuery.data?.items.find((digest) => digest.id === effectiveSelectedDigestId);

  return (
    <div className="space-y-6">
      {!queriesEnabled ? (
        <Card>
          <CardContent className="pt-6 text-sm text-[var(--foreground-muted)]">
            Syncing authenticated workspace context with the backend...
          </CardContent>
        </Card>
      ) : null}

      {combinedError ? (
        <Card>
          <CardContent className="pt-6 text-sm text-rose-500">
            {combinedError instanceof Error
              ? combinedError.message
              : "Failed to load digests from the backend API."}
          </CardContent>
        </Card>
      ) : null}

      <section className="grid gap-4 md:grid-cols-3">
        <Card>
          <CardContent className="pt-6">
            <p className="text-xs font-semibold uppercase tracking-[0.2em] text-[var(--foreground-subtle)]">
              Digests sent
            </p>
            <p className="mt-3 font-[family:var(--font-display)] text-3xl font-semibold">
              {digestsQuery.data?.items.filter((digest) => digest.status === "sent").length ?? 0}
            </p>
            <p className="mt-2 text-sm text-[var(--foreground-muted)]">
              Archive items available for review and QA follow-through.
            </p>
          </CardContent>
        </Card>
        <Card>
          <CardContent className="pt-6">
            <p className="text-xs font-semibold uppercase tracking-[0.2em] text-[var(--foreground-subtle)]">
              Next run
            </p>
            <p className="mt-3 font-[family:var(--font-display)] text-2xl font-semibold">
              {scheduleQuery.data ? formatDateTime(scheduleQuery.data.next_run_at) : "Loading"}
            </p>
            <p className="mt-2 text-sm text-[var(--foreground-muted)]">
              Delivery stays on one visible schedule instead of hiding in cron jobs.
            </p>
          </CardContent>
        </Card>
        <Card>
          <CardContent className="pt-6">
            <p className="text-xs font-semibold uppercase tracking-[0.2em] text-[var(--foreground-subtle)]">
              Active channels
            </p>
            <p className="mt-3 font-[family:var(--font-display)] text-3xl font-semibold">
              {activeChannelIds.length}
            </p>
            <p className="mt-2 text-sm text-[var(--foreground-muted)]">
              Current schedule fans out to multiple delivery surfaces.
            </p>
          </CardContent>
        </Card>
      </section>

      <Tabs defaultValue="archive">
        <TabsList>
          <TabsTrigger value="archive">Archive</TabsTrigger>
          <TabsTrigger value="schedule">Schedule</TabsTrigger>
        </TabsList>

        <TabsContent value="archive">
          <div className="grid gap-6 xl:grid-cols-[320px_minmax(0,1fr)]">
            <Card>
              <CardHeader>
                <CardTitle className="text-2xl">Digest history</CardTitle>
              </CardHeader>
              <CardContent className="space-y-3">
                {digestsQuery.data?.items.map((digest) => {
                  const active = digest.id === effectiveSelectedDigestId;

                  return (
                    <button
                      key={digest.id}
                      type="button"
                      onClick={() => setSelectedDigestId(digest.id)}
                      className={`w-full rounded-[22px] border px-4 py-4 text-left transition-colors ${
                        active
                          ? "border-[var(--primary)]/18 bg-[var(--primary-subtle)]/70"
                          : "border-[var(--border)] bg-[var(--surface-hover)]/70 hover:border-[var(--border-strong)]"
                      }`}
                    >
                      <div className="flex items-center justify-between gap-3">
                        <div>
                          <p className="font-medium text-[var(--foreground)]">
                            {digest.content.title}
                          </p>
                          <p className="mt-1 text-sm text-[var(--foreground-muted)]">
                            {formatCalendarDate(digest.period_start)} to{" "}
                            {formatCalendarDate(digest.period_end)}
                          </p>
                        </div>
                        <div className="rounded-full bg-emerald-500/10 px-3 py-1 text-xs font-semibold uppercase tracking-[0.18em] text-emerald-600 dark:text-emerald-300">
                          {digest.status}
                        </div>
                      </div>
                      <p className="mt-3 text-sm text-[var(--foreground-muted)]">
                        {digest.paper_count} papers grouped into {digest.content.sections.length} sections.
                      </p>
                    </button>
                  );
                })}
              </CardContent>
            </Card>

            {selectedDigest ? (
              <Card>
                <CardHeader className="gap-4">
                  <div className="flex flex-col gap-4 lg:flex-row lg:items-start lg:justify-between">
                    <div>
                      <CardTitle className="text-3xl">{selectedDigest.content.title}</CardTitle>
                      <p className="mt-3 max-w-3xl text-sm leading-7 text-[var(--foreground-muted)]">
                        {selectedDigest.content.overview}
                      </p>
                    </div>
                    <div className="rounded-full bg-[var(--primary-subtle)] px-3 py-1 text-xs font-semibold uppercase tracking-[0.18em] text-[var(--primary)]">
                      {selectedDigest.paper_count} papers
                    </div>
                  </div>
                </CardHeader>
                <CardContent className="space-y-5">
                  {selectedDigest.content.sections.map((section) => (
                    <div
                      key={section.id}
                      className="rounded-[24px] border border-[var(--border)] bg-[var(--surface-hover)]/75 p-5"
                    >
                      <div className="flex items-start justify-between gap-4">
                        <div>
                          <h3 className="font-[family:var(--font-display)] text-xl font-semibold">
                            {section.title}
                          </h3>
                          <p className="mt-2 text-sm leading-7 text-[var(--foreground-muted)]">
                            {section.summary}
                          </p>
                        </div>
                      </div>

                      <div className="mt-5 space-y-3">
                        {section.papers.map((paper) => (
                          <div
                            key={paper.id}
                            className="rounded-[20px] border border-[var(--border)] bg-[var(--surface)] px-4 py-4"
                          >
                            <div className="flex flex-col gap-3 sm:flex-row sm:items-start sm:justify-between">
                              <div>
                                <p className="font-medium text-[var(--foreground)]">{paper.title}</p>
                                <p className="mt-2 text-sm leading-6 text-[var(--foreground-muted)]">
                                  {paper.one_line_summary}
                                </p>
                              </div>
                              <ScoreBadge score={paper.score.total_score} />
                            </div>
                          </div>
                        ))}
                      </div>
                    </div>
                  ))}
                </CardContent>
              </Card>
            ) : null}
          </div>
        </TabsContent>

        <TabsContent value="schedule">
          <div className="grid gap-6 xl:grid-cols-[minmax(0,1.1fr)_minmax(320px,0.85fr)]">
            <Card>
              <CardHeader>
                <CardTitle className="text-2xl">Digest schedule</CardTitle>
              <p className="text-sm leading-7 text-[var(--foreground-muted)]">
                  Keep the schedule visible and editable while using the real backend delivery settings.
                </p>
              </CardHeader>
              <CardContent className="space-y-5">
                <div className="grid gap-4 md:grid-cols-2">
                  <div className="space-y-2">
                    <label className="text-sm font-medium text-[var(--foreground)]">Cadence</label>
                    <Select
                      value={cadenceKey}
                      onValueChange={(value) =>
                        setScheduleDraft((current) => ({
                          ...(current ?? buildScheduleDraft(scheduleQuery.data)),
                          cadenceKey: value as CadenceKey,
                        }))
                      }
                    >
                      <SelectTrigger>
                        <SelectValue placeholder="Cadence" />
                      </SelectTrigger>
                      <SelectContent>
                        {Object.entries(cadencePresets).map(([key, preset]) => (
                          <SelectItem key={key} value={key}>
                            {preset.label}
                          </SelectItem>
                        ))}
                      </SelectContent>
                    </Select>
                  </div>

                  <div className="space-y-2">
                    <label className="text-sm font-medium text-[var(--foreground)]">Timezone</label>
                    <Select
                      value={timezone}
                      onValueChange={(value) =>
                        setScheduleDraft((current) => ({
                          ...(current ?? buildScheduleDraft(scheduleQuery.data)),
                          timezone: value,
                        }))
                      }
                    >
                      <SelectTrigger>
                        <SelectValue placeholder="Timezone" />
                      </SelectTrigger>
                      <SelectContent>
                        <SelectItem value="Asia/Shanghai">Asia/Shanghai</SelectItem>
                        <SelectItem value="America/Los_Angeles">America/Los_Angeles</SelectItem>
                        <SelectItem value="Europe/London">Europe/London</SelectItem>
                      </SelectContent>
                    </Select>
                  </div>
                </div>

                <div className="space-y-3">
                  <label className="text-sm font-medium text-[var(--foreground)]">Destination channels</label>
                  <div className="flex flex-wrap gap-2">
                    {channelsQuery.data?.map((channel) => {
                      const active = activeChannelIds.includes(channel.id);

                      return (
                        <button
                          key={channel.id}
                          type="button"
                          onClick={() =>
                            setScheduleDraft((current) => {
                              const draft = current ?? buildScheduleDraft(scheduleQuery.data);
                              return {
                                ...draft,
                                activeChannelIds: draft.activeChannelIds.includes(channel.id)
                                  ? draft.activeChannelIds.filter((id) => id !== channel.id)
                                  : [...draft.activeChannelIds, channel.id],
                              };
                            })
                          }
                          className={`min-h-11 rounded-full border px-4 text-sm font-medium transition-colors ${
                            active
                              ? "border-[var(--primary)]/18 bg-[var(--primary-subtle)] text-[var(--primary)]"
                              : "border-[var(--border)] bg-[var(--surface)] text-[var(--foreground-muted)]"
                          }`}
                        >
                          {channel.label}
                        </button>
                      );
                    })}
                  </div>
                </div>

                <div className="flex flex-wrap gap-3">
                  <Button
                    onClick={() =>
                      updateScheduleMutation.mutate({
                        cron_expression: cadencePresets[cadenceKey].cron_expression,
                        cadence_label: cadencePresets[cadenceKey].label,
                        timezone,
                        is_active: scheduleActive,
                        channel_ids: activeChannelIds,
                        channel_labels:
                          channelsQuery.data
                            ?.filter((channel) => activeChannelIds.includes(channel.id))
                            .map((channel) => channel.label) ?? [],
                        next_run_at: getNextRunPreview(cadenceKey, timezone),
                      })
                    }
                    disabled={!queriesEnabled || updateScheduleMutation.isPending}
                  >
                    <Send />
                    Save schedule
                  </Button>
                  <Button
                    variant="outline"
                    disabled={!queriesEnabled}
                    onClick={() =>
                      setScheduleDraft((current) => {
                        const draft = current ?? buildScheduleDraft(scheduleQuery.data);
                        return {
                          ...draft,
                          scheduleActive: !draft.scheduleActive,
                        };
                      })
                    }
                  >
                    {scheduleActive ? "Pause digest" : "Resume digest"}
                  </Button>
                </div>
              </CardContent>
            </Card>

            <Card>
              <CardHeader>
                <CardTitle className="text-2xl">Current run plan</CardTitle>
              </CardHeader>
              <CardContent className="space-y-4">
                <div className="rounded-[22px] border border-[var(--border)] bg-[var(--surface-hover)]/80 p-4">
                  <div className="flex items-start gap-3">
                    <CalendarClock className="mt-0.5 size-4 text-[var(--primary)]" />
                    <div>
                      <p className="font-medium text-[var(--foreground)]">{cadencePresets[cadenceKey].label}</p>
                      <p className="mt-1 text-sm text-[var(--foreground-muted)]">
                        {timezone}
                      </p>
                    </div>
                  </div>
                </div>

                <div className="rounded-[22px] border border-[var(--border)] bg-[var(--surface-hover)]/80 p-4">
                  <div className="flex items-start gap-3">
                    <Clock3 className="mt-0.5 size-4 text-[var(--accent)]" />
                    <div>
                      <p className="font-medium text-[var(--foreground)]">
                        Next send
                      </p>
                      <p className="mt-1 text-sm text-[var(--foreground-muted)]">
                        {formatDateTime(getNextRunPreview(cadenceKey, timezone))}
                      </p>
                    </div>
                  </div>
                </div>

                <div className="rounded-[22px] border border-[var(--border)] bg-[var(--surface-hover)]/80 p-4 text-sm text-[var(--foreground-muted)]">
                  {scheduleActive
                    ? "The schedule is active. The next digest will use the selected channels and cadence."
                    : "The schedule is paused. You can keep editing the cadence without sending anything yet."}
                </div>
              </CardContent>
            </Card>
          </div>
        </TabsContent>
      </Tabs>
    </div>
  );
}
