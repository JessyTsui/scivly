import { siteConfig } from "@/lib/site-config";

function normalizeSiteUrl(candidate?: string) {
  if (!candidate) {
    return null;
  }

  const trimmed = candidate.trim();

  if (!trimmed) {
    return null;
  }

  const withProtocol =
    trimmed.startsWith("http://") || trimmed.startsWith("https://")
      ? trimmed
      : `https://${trimmed}`;

  try {
    return new URL(withProtocol).origin;
  } catch {
    return null;
  }
}

export function resolveSiteUrl() {
  return normalizeSiteUrl(process.env.NEXT_PUBLIC_SITE_URL) ?? siteConfig.defaultSiteUrl;
}

export function absoluteUrl(path = "/") {
  return new URL(path, resolveSiteUrl()).toString();
}
