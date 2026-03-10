import { z } from "zod";

const DEFAULT_API_URL = "http://localhost:8100";

export class ApiError extends Error {
  status: number;
  details?: unknown;

  constructor(message: string, status: number, details?: unknown) {
    super(message);
    this.name = "ApiError";
    this.status = status;
    this.details = details;
  }
}

export interface ApiRequestOptions<T> extends Omit<RequestInit, "body"> {
  authToken?: string;
  body?: BodyInit | object;
  query?: object;
  schema?: z.ZodType<T>;
}

function resolveAuthToken(explicit?: string) {
  if (explicit) {
    return explicit;
  }

  if (typeof window === "undefined") {
    return undefined;
  }

  return window.localStorage.getItem("scivly_auth_token") ?? undefined;
}

function buildUrl(path: string, query?: ApiRequestOptions<unknown>["query"]) {
  const baseUrl = process.env.NEXT_PUBLIC_API_URL ?? DEFAULT_API_URL;
  const url = new URL(path, baseUrl);

  if (!query) {
    return url.toString();
  }

  for (const [key, value] of Object.entries(query)) {
    if (value === undefined || value === "") {
      continue;
    }

    url.searchParams.set(key, String(value));
  }

  return url.toString();
}

export function isMockApiEnabled() {
  return process.env.NEXT_PUBLIC_USE_MOCK_API !== "false";
}

export async function apiRequest<T>(path: string, options: ApiRequestOptions<T> = {}) {
  const { authToken, body, headers, query, schema, ...init } = options;
  const isReadableStream =
    typeof ReadableStream !== "undefined" && body instanceof ReadableStream;
  const isJsonBody =
    body !== undefined &&
    body !== null &&
    typeof body === "object" &&
    !(body instanceof FormData) &&
    !(body instanceof URLSearchParams) &&
    !(body instanceof Blob) &&
    !(body instanceof ArrayBuffer) &&
    !ArrayBuffer.isView(body) &&
    !isReadableStream;
  const resolvedBody: BodyInit | undefined = isJsonBody
    ? JSON.stringify(body)
    : (body as BodyInit | undefined);
  const response = await fetch(buildUrl(path, query), {
    ...init,
    headers: {
      Accept: "application/json",
      ...(isJsonBody ? { "Content-Type": "application/json" } : {}),
      ...(resolveAuthToken(authToken) ? { Authorization: `Bearer ${resolveAuthToken(authToken)}` } : {}),
      ...headers,
    },
    body: resolvedBody,
  });

  const contentType = response.headers.get("content-type") ?? "";
  const payload = contentType.includes("application/json") ? await response.json() : await response.text();

  if (!response.ok) {
    throw new ApiError(
      typeof payload === "object" && payload && "message" in payload
        ? String(payload.message)
        : `Request failed with status ${response.status}`,
      response.status,
      payload
    );
  }

  if (!schema) {
    return payload as T;
  }

  return schema.parse(payload);
}
