import { apiRequest, isMockApiEnabled } from "@/lib/api/client";
import type {
  DigestOut,
  DigestScheduleOut,
  DigestScheduleUpdate,
  PaginatedResponse,
} from "@/lib/api/types";
import { mockDigests, mockDigestSchedule } from "@/lib/mock/digests";

function clone<T>(value: T): T {
  return structuredClone(value);
}

let scheduleStore = clone(mockDigestSchedule);

export async function listDigests(): Promise<PaginatedResponse<DigestOut>> {
  if (!isMockApiEnabled()) {
    return apiRequest<PaginatedResponse<DigestOut>>("/digests");
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
    return apiRequest<DigestOut>(`/digests/${digestId}`);
  }

  const digest = mockDigests.find((item) => item.id === digestId);

  if (!digest) {
    throw new Error(`Digest ${digestId} was not found in mock data.`);
  }

  return clone(digest);
}

export async function getDigestSchedule() {
  if (!isMockApiEnabled()) {
    return apiRequest<DigestScheduleOut>("/digests/schedule");
  }

  return clone(scheduleStore);
}

export async function updateDigestSchedule(input: DigestScheduleUpdate) {
  if (!isMockApiEnabled()) {
    return apiRequest<DigestScheduleOut>("/digests/schedule", {
      method: "PATCH",
      body: input,
    });
  }

  scheduleStore = {
    ...scheduleStore,
    ...input,
  };

  return clone(scheduleStore);
}
