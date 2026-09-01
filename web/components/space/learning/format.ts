/** Shared presentation helpers for the Mastery Path dashboard. */

export type LearningLanguage = "en" | "zh" | "ko";
export type Translate = (cn: string, en: string, ko: string) => string;

const MINUTE = 60;
const HOUR = 60 * MINUTE;
const DAY = 24 * HOUR;

function intlLocale(language: LearningLanguage): string {
  if (language === "zh") return "zh-CN";
  if (language === "ko") return "ko-KR";
  return "en";
}

/**
 * "3 分钟前" / "3분 후" / "in 2 days" — engine timestamps are epoch seconds
 * and can point either way (an attempt happened, a review is due).
 */
export function formatRelative(
  epochSeconds: number,
  language: LearningLanguage,
): string {
  const deltaSeconds = epochSeconds - Date.now() / 1000;
  const past = deltaSeconds < 0;
  const abs = Math.abs(deltaSeconds);

  const [value, unit]: [number, Intl.RelativeTimeFormatUnit] =
    abs < MINUTE
      ? [Math.round(abs), "second"]
      : abs < HOUR
        ? [Math.round(abs / MINUTE), "minute"]
        : abs < DAY
          ? [Math.round(abs / HOUR), "hour"]
          : [Math.round(abs / DAY), "day"];

  return new Intl.RelativeTimeFormat(intlLocale(language), {
    numeric: "auto",
  }).format(past ? -value : value, unit);
}

/** Calendar form, for when "in 3 days" is not precise enough. */
export function formatAbsolute(
  epochSeconds: number,
  language: LearningLanguage,
): string {
  return new Date(epochSeconds * 1000).toLocaleString(intlLocale(language), {
    month: "short",
    day: "numeric",
    hour: "2-digit",
    minute: "2-digit",
  });
}
