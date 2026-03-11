import { apiRequest, isMockApiEnabled } from "@/lib/api/client";
import type {
  DigestOut,
  DigestScheduleOut,
  DigestScheduleUpdate,
  NotificationChannelOut,
  PaginatedResponse,
  PaperOut,
} from "@/lib/api/types";
import { getNotificationChannels } from "@/lib/api/interests";
import { listPapers } from "@/lib/api/papers";
import { mockDigests, mockDigestSchedule } from "@/lib/mock/digests";
import { getNextRunAt } from "@/lib/mock/time";

type BackendDigestSection = {
  paper_ids?: string[];
  summary?: string | null;
  title: string;
};

type BackendDigest = {
  id: string;
  workspace_id: string;
  schedule_id: string;
  title: string;
  period_start: string;
  period_end: string;
  paper_ids: string[];
  status: DigestOut["status"];
  channel_types: NotificationChannelOut["channel_type"][];
  summary_markdown: string;
  content?: {
    headline?: string | null;
    sections?: BackendDigestSection[];
  };
  created_at: string;
};

type BackendDigestSchedule = {
  id: string;
  workspace_id: string;
  cron_expression: string;
  timezone: string;
  channel_types: NotificationChannelOut["channel_type"][];
  is_active: boolean;
  created_at: string;
};

function clone<T>(value: T): T {
  return structuredClone(value);
}

function summarizeMarkdown(markdown: string) {
  return markdown
    .replace(/[#*`>-]/g, " ")
    .replace(/\s+/g, " ")
    .trim();
}

function makeSectionId(title: string, index: number) {
  const base = title
    .toLowerCase()
    .replace(/[^a-z0-9]+/g, "-")
    .replace(/^-+|-+$/g, "");
  return base || `section-${index + 1}`;
}

function parseCronExpression(cronExpression: string) {
  const [minuteRaw, hourRaw, , , dayRaw = "*"] = cronExpression.trim().split(/\s+/);
  const safeMinute = minuteRaw ?? "0";
  const safeHour = hourRaw ?? "9";
  const hour = Number.parseInt(safeHour, 10);
  const minute = Number.parseInt(safeMinute, 10);
  const weekdays =
    dayRaw === "*"
      ? undefined
      : dayRaw.split(",").flatMap((token) => {
          if (token.includes("-")) {
            const [start, end] = token.split("-").map((value) => Number.parseInt(value, 10));
            if (Number.isNaN(start) || Number.isNaN(end)) {
              return [];
            }

            return Array.from({ length: end - start + 1 }, (_, index) => start + index);
          }

          const day = Number.parseInt(token, 10);
          return Number.isNaN(day) ? [] : [day];
        });

  return {
    cadenceLabel:
      dayRaw === "*"
        ? `Daily at ${safeHour.padStart(2, "0")}:${safeMinute.padStart(2, "0")}`
        : `Scheduled at ${safeHour.padStart(2, "0")}:${safeMinute.padStart(2, "0")}`,
    hour: Number.isNaN(hour) ? 9 : hour,
    minute: Number.isNaN(minute) ? 0 : minute,
    weekdays,
  };
}

function mapChannelIds(
  channelTypes: NotificationChannelOut["channel_type"][],
  channels: NotificationChannelOut[]
) {
  const matched = channels.filter((channel) => channelTypes.includes(channel.channel_type));
  return {
    channel_ids: matched.map((channel) => channel.id),
    channel_labels: matched.map((channel) => channel.label),
  };
}

function mapDigest(
  digest: BackendDigest,
  papersById: Record<string, PaperOut>
): DigestOut {
  const sections = (digest.content?.sections ?? []).map((section, index) => {
    const papers = (section.paper_ids ?? [])
      .map((paperId) => papersById[paperId])
      .filter((paper): paper is PaperOut => Boolean(paper));

    return {
      id: makeSectionId(section.title, index),
      title: section.title,
      summary:
        section.summary?.trim() ||
        `${papers.length} paper${papers.length === 1 ? "" : "s"} grouped into this digest section.`,
      papers,
    };
  });

  const overview = summarizeMarkdown(digest.summary_markdown) || `Digest covers ${digest.paper_ids.length} papers.`;

  return {
    id: digest.id,
    workspace_id: digest.workspace_id,
    schedule_id: digest.schedule_id,
    period_start: digest.period_start,
    period_end: digest.period_end,
    paper_ids: digest.paper_ids,
    paper_count: digest.paper_ids.length,
    content: {
      title: digest.content?.headline?.trim() || digest.title,
      overview,
      sections,
    },
    status: digest.status,
    created_at: digest.created_at,
  };
}

async function getBackendSchedule() {
  const response = await apiRequest<PaginatedResponse<BackendDigestSchedule>>("/digests/schedules");
  return response.items[0] ?? null;
}

function mapSchedule(
  schedule: BackendDigestSchedule,
  channels: NotificationChannelOut[]
): DigestScheduleOut {
  const parsed = parseCronExpression(schedule.cron_expression);
  const channelMap = mapChannelIds(schedule.channel_types, channels);

  return {
    id: schedule.id,
    workspace_id: schedule.workspace_id,
    cron_expression: schedule.cron_expression,
    timezone: schedule.timezone,
    channel_ids: channelMap.channel_ids,
    channel_labels: channelMap.channel_labels,
    is_active: schedule.is_active,
    cadence_label: parsed.cadenceLabel,
    created_at: schedule.created_at,
    next_run_at: getNextRunAt({
      timeZone: schedule.timezone,
      hour: parsed.hour,
      weekdays: parsed.weekdays,
    }),
  };
}

export async function listDigests(): Promise<PaginatedResponse<DigestOut>> {
  if (!isMockApiEnabled()) {
    const [digests, papers] = await Promise.all([
      apiRequest<PaginatedResponse<BackendDigest>>("/digests"),
      listPapers({ per_page: 100, sort: "score_desc" }),
    ]);
    const papersById = Object.fromEntries(papers.items.map((paper) => [paper.id, paper]));

    return {
      ...digests,
      items: digests.items.map((digest) => mapDigest(digest, papersById)),
    };
  }

  return {
    items: clone(mockDigests),
    total: mockDigests.length,
    page: 1,
    per_page: mockDigests.length,
  };
}

export async function getDigest(digestId: string) {
  if (!isMockApiEnabled()) {
    const [digest, papers] = await Promise.all([
      apiRequest<BackendDigest>(`/digests/${digestId}`),
      listPapers({ per_page: 100, sort: "score_desc" }),
    ]);
    const papersById = Object.fromEntries(papers.items.map((paper) => [paper.id, paper]));
    return mapDigest(digest, papersById);
  }

  const digest = mockDigests.find((item) => item.id === digestId);

  if (!digest) {
    throw new Error(`Digest ${digestId} was not found in mock data.`);
  }

  return clone(digest);
}

export async function getDigestSchedule() {
  if (!isMockApiEnabled()) {
    const [schedule, channels] = await Promise.all([getBackendSchedule(), getNotificationChannels()]);

    if (!schedule) {
      throw new Error("No digest schedule is configured for this workspace.");
    }

    return mapSchedule(schedule, channels);
  }

  return clone(mockDigestSchedule);
}

export async function updateDigestSchedule(input: DigestScheduleUpdate) {
  if (!isMockApiEnabled()) {
    const [schedule, channels] = await Promise.all([getBackendSchedule(), getNotificationChannels()]);
    const selectedChannels = channels.filter((channel) => input.channel_ids?.includes(channel.id));
    const payload = {
      cron_expression: input.cron_expression,
      timezone: input.timezone,
      is_active: input.is_active,
      channel_types: selectedChannels.map((channel) => channel.channel_type),
    };

    const response = schedule
      ? await apiRequest<BackendDigestSchedule>(`/digests/schedules/${schedule.id}`, {
          method: "PATCH",
          body: payload,
        })
      : await apiRequest<BackendDigestSchedule>("/digests/schedules", {
          method: "POST",
          body: {
            workspace_id: channels[0]?.workspace_id,
            ...payload,
          },
        });

    return mapSchedule(response, channels);
  }

  scheduleStore = {
    ...scheduleStore,
    ...input,
  };

  return clone(scheduleStore);
}

let scheduleStore = clone(mockDigestSchedule);
