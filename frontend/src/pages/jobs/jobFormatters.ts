import type { JobDetail } from "../../api/types";

export const EMPTY_VALUE = "Немає даних";

export const statusLabels: Record<string, string> = {
  queued: "У черзі",
  processing: "Обробляється",
  completed: "Завершено",
  failed: "Збій",
  cancelled: "Скасовано",
};

export const mediaTypeLabels: Record<string, string> = {
  image: "Зображення",
  video: "Відео",
};

export function safeText(value: unknown) {
  if (value === null || value === undefined || value === "") return EMPTY_VALUE;
  const text = String(value);
  if (/([A-Za-z]:\\|\/app\/|\/storage\/|\\\\)/.test(text)) return EMPTY_VALUE;
  return text;
}

export function numberOrNull(value: unknown): number | null {
  return typeof value === "number" && Number.isFinite(value) ? value : null;
}

export function firstNumber(source: Record<string, unknown> | null | undefined, keys: string[]) {
  if (!source) return null;
  for (const key of keys) {
    const value = numberOrNull(source[key]);
    if (value !== null) return value;
  }
  return null;
}

export function formatCount(value: number | null) {
  return value === null ? EMPTY_VALUE : value.toLocaleString("uk-UA");
}

export function formatPercent(value: number | null, digits = 1) {
  if (value === null) return EMPTY_VALUE;
  const normalized = value > 1 ? value : value * 100;
  return `${normalized.toLocaleString("uk-UA", { maximumFractionDigits: digits })}%`;
}

export function formatDate(value: string | null | undefined) {
  if (!value) return EMPTY_VALUE;
  const date = new Date(value);
  if (!Number.isFinite(date.getTime())) return EMPTY_VALUE;
  return new Intl.DateTimeFormat("uk-UA", {
    day: "2-digit",
    month: "2-digit",
    year: "2-digit",
    hour: "2-digit",
    minute: "2-digit",
  }).format(date);
}

export function formatSeconds(value: number | null) {
  if (value === null) return EMPTY_VALUE;
  if (value < 60) return `${Math.round(value)} с`;
  return `${Math.floor(value / 60)} хв ${Math.round(value % 60)} с`;
}

export function diffSeconds(start: string | null, end: string | null) {
  if (!start || !end) return null;
  const diff = new Date(end).getTime() - new Date(start).getTime();
  return Number.isFinite(diff) && diff >= 0 ? diff / 1000 : null;
}

export function formatDuration(job: JobDetail) {
  const duration =
    firstNumber(job.summary_json, ["processing_duration_seconds", "duration_seconds", "elapsed_seconds"]) ??
    diffSeconds(job.started_at, job.completed_at);
  return formatSeconds(duration);
}

export function detectionCount(job: JobDetail) {
  return firstNumber(job.summary_json, ["total_detections", "detections_count", "detections", "objects_detected"]);
}

export function averageConfidence(job: JobDetail) {
  return firstNumber(job.summary_json, ["average_confidence", "avg_confidence", "mean_confidence"]);
}

export function averageFps(job: JobDetail) {
  return firstNumber(job.summary_json, ["average_fps", "avg_fps", "fps", "processing_fps"]);
}

export function formatTimestampMs(value: number) {
  const totalMs = Math.max(0, value);
  const minutes = Math.floor(totalMs / 60000);
  const seconds = Math.floor((totalMs % 60000) / 1000);
  const ms = Math.floor(totalMs % 1000);
  return `${String(minutes).padStart(2, "0")}:${String(seconds).padStart(2, "0")}.${String(ms).padStart(3, "0")}`;
}

export function formatBBox(x1: number, y1: number, x2: number, y2: number) {
  return `[${Math.round(x1)}, ${Math.round(y1)}, ${Math.round(x2)}, ${Math.round(y2)}]`;
}

export function filenameFor(jobId: string, kind: "media" | "csv" | "json", mediaType?: string) {
  const safeId = jobId.replace(/[^a-zA-Z0-9_-]/g, "").slice(0, 36) || "job";
  if (kind === "csv") return `aerovision-${safeId}.csv`;
  if (kind === "json") return `aerovision-${safeId}.json`;
  return `aerovision-${safeId}.${mediaType === "image" ? "jpg" : "mp4"}`;
}
