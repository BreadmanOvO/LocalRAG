const timezoneSuffix = /(?:Z|[+-]\d{2}:?\d{2})$/i;
const localTimestamp = /^(\d{4})-(\d{2})-(\d{2})(?:[T ](\d{2}):(\d{2})(?::(\d{2})(?:\.(\d+))?)?)?$/;

export type DateTimeFormatOptions = Pick<Intl.DateTimeFormatOptions, "timeZone">;

/**
 * Parse API timestamps without changing the meaning of timezone-less values.
 * A value with an explicit offset is an instant; a value without one is a
 * local wall-clock timestamp, including date-only values.
 */
export function parseTimestamp(value: unknown): Date | null {
  if (value instanceof Date) return Number.isNaN(value.getTime()) ? null : new Date(value.getTime());
  if (typeof value !== "string") return null;
  const input = value.trim();
  if (!input) return null;

  if (timezoneSuffix.test(input)) {
    const parsed = new Date(input);
    return Number.isNaN(parsed.getTime()) ? null : parsed;
  }

  const match = input.match(localTimestamp);
  if (match) {
    const year = Number(match[1]);
    const month = Number(match[2]);
    const day = Number(match[3]);
    const hour = Number(match[4] ?? 0);
    const minute = Number(match[5] ?? 0);
    const second = Number(match[6] ?? 0);
    const milliseconds = Number((match[7] ?? "").slice(0, 3).padEnd(3, "0"));
    const parsed = new Date(0);
    parsed.setFullYear(year, month - 1, day);
    parsed.setHours(hour, minute, second, milliseconds);
    if (
      parsed.getFullYear() !== year ||
      parsed.getMonth() !== month - 1 ||
      parsed.getDate() !== day ||
      parsed.getHours() !== hour ||
      parsed.getMinutes() !== minute ||
      parsed.getSeconds() !== second
    ) return null;
    return parsed;
  }

  const parsed = new Date(input);
  return Number.isNaN(parsed.getTime()) ? null : parsed;
}
const dateTimeOptions: Intl.DateTimeFormatOptions = {
  year: "numeric",
  month: "2-digit",
  day: "2-digit",
  hour: "2-digit",
  minute: "2-digit",
  second: "2-digit",
  hour12: false,
};

/** Format an API timestamp for the user's local timezone in Chinese locale. */
export function formatDateTime(value: unknown, options: DateTimeFormatOptions = {}): string {
  const parsed = parseTimestamp(value);
  if (!parsed) return typeof value === "string" ? value : "";
  try {
    return new Intl.DateTimeFormat("zh-CN", { ...dateTimeOptions, ...options }).format(parsed);
  } catch {
    return parsed.toLocaleString("zh-CN", { hour12: false });
  }
}
