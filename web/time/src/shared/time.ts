export const SECONDS_PER_DAY = 24 * 3600;

const TIME_OF_DAY_RE = /^([01]\d|2[0-3]):([0-5]\d)(?::([0-5]\d))?$/;

/** Formats a date as [HH, mm, ss] in the given IANA timezone, 24-hour clock. */
export function timeParts(
  date: Date,
  timeZone: string,
): [string, string, string] {
  const parts = new Intl.DateTimeFormat("en-GB", {
    timeZone,
    hourCycle: "h23",
    hour: "2-digit",
    minute: "2-digit",
    second: "2-digit",
  }).formatToParts(date);
  const get = (type: Intl.DateTimeFormatPartTypes) =>
    parts.find((p) => p.type === type)?.value ?? "00";
  return [get("hour"), get("minute"), get("second")];
}

/** Parses "HH:mm" or "HH:mm:ss" into seconds since midnight, or null. */
export function parseTimeOfDay(text: string): number | null {
  const match = TIME_OF_DAY_RE.exec(text.trim());
  if (!match) return null;
  return (
    Number(match[1]) * 3600 + Number(match[2]) * 60 + Number(match[3] ?? 0)
  );
}

/** Distance in seconds between two times of day, wrapping around midnight. */
export function secondsBetween(a: number, b: number): number {
  const diff = Math.abs(a - b);
  return Math.min(diff, SECONDS_PER_DAY - diff);
}
