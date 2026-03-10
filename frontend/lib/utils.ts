import { clsx, type ClassValue } from "clsx";
import { twMerge } from "tailwind-merge";

export function cn(...inputs: ClassValue[]) {
  return twMerge(clsx(inputs));
}

export function formatCalendarDate(value: string) {
  return new Intl.DateTimeFormat("en", {
    month: "short",
    day: "numeric",
    year: "numeric",
  }).format(new Date(value));
}

export function formatDateTime(value: string) {
  return new Intl.DateTimeFormat("en", {
    month: "short",
    day: "numeric",
    hour: "numeric",
    minute: "2-digit",
  }).format(new Date(value));
}

export function formatRelativeDate(value: string) {
  const now = Date.now();
  const then = new Date(value).getTime();
  const diffHours = Math.round((then - now) / (1000 * 60 * 60));

  if (Math.abs(diffHours) < 24) {
    return new Intl.RelativeTimeFormat("en", { numeric: "auto" }).format(diffHours, "hour");
  }

  const diffDays = Math.round(diffHours / 24);
  return new Intl.RelativeTimeFormat("en", { numeric: "auto" }).format(diffDays, "day");
}

export function formatScore(score: number) {
  return Math.round(score).toString();
}
