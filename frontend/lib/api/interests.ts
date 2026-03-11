import { apiRequest, isMockApiEnabled } from "@/lib/api/client";
import type {
  AuthorWatchCreate,
  AuthorWatchlistOut,
  NotificationChannelOut,
  NotificationChannelUpdate,
  PaginatedResponse,
  TopicProfileCreate,
  TopicProfileOut,
} from "@/lib/api/types";
import {
  DEMO_WORKSPACE_ID,
  mockAuthorWatchlist,
  mockNotificationChannels,
  mockProfiles,
} from "@/lib/mock/profiles";

type BackendTopicProfile = Omit<TopicProfileOut, "description" | "match_count_24h">;

function clone<T>(value: T): T {
  return structuredClone(value);
}

function formatProfileDescription(profile: Pick<TopicProfileOut, "categories" | "keywords">) {
  const keywordLabel = profile.keywords.slice(0, 3).join(", ");
  const categoryLabel = profile.categories.slice(0, 2).join(", ");
  return `Tracks ${keywordLabel || "priority topics"} across ${categoryLabel || "selected categories"}.`;
}

function normalizeProfile(profile: BackendTopicProfile): TopicProfileOut {
  return {
    ...profile,
    description: formatProfileDescription(profile),
    match_count_24h: 0,
  };
}

let profileStore = clone(mockProfiles);
let authorStore = clone(mockAuthorWatchlist);
let channelStore = clone(mockNotificationChannels);

export async function getProfiles() {
  if (!isMockApiEnabled()) {
    const response = await apiRequest<PaginatedResponse<BackendTopicProfile>>("/interests/topic-profiles");
    return response.items.map(normalizeProfile);
  }

  return clone(profileStore);
}

export async function createProfile(input: TopicProfileCreate) {
  if (!isMockApiEnabled()) {
    const profile = await apiRequest<BackendTopicProfile>("/interests/topic-profiles", {
      method: "POST",
      body: {
        name: input.name,
        categories: input.categories,
        keywords: input.keywords,
      },
    });

    return normalizeProfile(profile);
  }

  const profile: TopicProfileOut = {
    id: `profile-${crypto.randomUUID()}`,
    workspace_id: DEMO_WORKSPACE_ID,
    name: input.name,
    description: input.description,
    categories: input.categories,
    keywords: input.keywords,
    is_default: false,
    created_at: new Date().toISOString(),
    match_count_24h: 0,
  };

  profileStore = [profile, ...profileStore];
  return clone(profile);
}

export async function getAuthorWatchlist() {
  if (!isMockApiEnabled()) {
    const response = await apiRequest<PaginatedResponse<AuthorWatchlistOut>>("/interests/author-watchlists");
    return response.items;
  }

  return clone(authorStore);
}

export async function addAuthorWatch(input: AuthorWatchCreate) {
  if (!isMockApiEnabled()) {
    return apiRequest<AuthorWatchlistOut>("/interests/author-watchlists", {
      method: "POST",
      body: input,
    });
  }

  const author: AuthorWatchlistOut = {
    id: `author-${crypto.randomUUID()}`,
    workspace_id: DEMO_WORKSPACE_ID,
    author_name: input.author_name,
    notes: input.notes,
  };

  authorStore = [author, ...authorStore];
  return clone(author);
}

export async function removeAuthorWatch(id: string) {
  if (!isMockApiEnabled()) {
    await apiRequest(`/interests/author-watchlists/${id}`, { method: "DELETE" });
    return;
  }

  authorStore = authorStore.filter((author) => author.id !== id);
}

export async function getNotificationChannels() {
  if (!isMockApiEnabled()) {
    return apiRequest<NotificationChannelOut[]>("/interests/channels");
  }

  return clone(channelStore);
}

export async function updateNotificationChannel(input: NotificationChannelUpdate) {
  if (!isMockApiEnabled()) {
    return apiRequest<NotificationChannelOut>(`/interests/channels/${input.id}`, {
      method: "PATCH",
      body: input,
    });
  }

  const existing = channelStore.find((channel) => channel.id === input.id);

  if (!existing) {
    throw new Error(`Notification channel ${input.id} was not found.`);
  }

  const updated: NotificationChannelOut = {
    ...existing,
    label: input.label ?? existing.label,
    config: input.config ?? existing.config,
    is_active: input.is_active ?? existing.is_active,
  };

  channelStore = channelStore.map((channel) => (channel.id === input.id ? updated : channel));
  return clone(updated);
}
