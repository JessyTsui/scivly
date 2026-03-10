const HOUR_MS = 60 * 60 * 1000;
const DAY_MS = 24 * HOUR_MS;

type NextRunOptions = {
  timeZone: string;
  hour: number;
  minute?: number;
  weekdays?: number[];
};

function shiftFromNow(offsetMs: number) {
  return new Date(Date.now() + offsetMs).toISOString();
}

function getLocalTimeParts(date: Date, formatter: Intl.DateTimeFormat) {
  const formatted = formatter.formatToParts(date);
  const weekday = formatted.find((part) => part.type === "weekday")?.value;
  const hour = Number(formatted.find((part) => part.type === "hour")?.value);
  const minute = Number(formatted.find((part) => part.type === "minute")?.value);

  return { weekday, hour, minute };
}

function matchesWeekday(weekday: string | undefined, weekdays?: number[]) {
  if (!weekdays?.length || !weekday) {
    return true;
  }

  const weekdayMap: Record<string, number> = {
    Sun: 0,
    Mon: 1,
    Tue: 2,
    Wed: 3,
    Thu: 4,
    Fri: 5,
    Sat: 6,
  };

  return weekdays.includes(weekdayMap[weekday]);
}

export function hoursAgo(hours: number) {
  return shiftFromNow(-hours * HOUR_MS);
}

export function daysAgo(days: number) {
  return shiftFromNow(-days * DAY_MS);
}

export function hoursFromNow(hours: number) {
  return shiftFromNow(hours * HOUR_MS);
}

export function getNextRunAt({
  timeZone,
  hour,
  minute = 0,
  weekdays,
}: NextRunOptions) {
  const now = Date.now();
  const maxSearchMs = 14 * DAY_MS;
  const stepMs = 15 * 60 * 1000;
  const formatter = new Intl.DateTimeFormat("en-US", {
    timeZone,
    weekday: "short",
    hour: "2-digit",
    minute: "2-digit",
    hourCycle: "h23",
  });

  for (let offsetMs = stepMs; offsetMs <= maxSearchMs; offsetMs += stepMs) {
    const candidate = new Date(now + offsetMs);
    const localParts = getLocalTimeParts(candidate, formatter);

    if (
      localParts.hour === hour &&
      localParts.minute === minute &&
      matchesWeekday(localParts.weekday, weekdays)
    ) {
      return candidate.toISOString();
    }
  }

  return hoursFromNow(24);
}
