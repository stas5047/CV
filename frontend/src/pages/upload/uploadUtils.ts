import type { ModelVersion } from "../../api/types";

export const IMAGE_EXTENSIONS = [".jpg", ".jpeg", ".png", ".webp"];
export const VIDEO_EXTENSIONS = [".mp4", ".avi", ".mov", ".mkv"];
export const ALL_EXTENSIONS = [...IMAGE_EXTENSIONS, ...VIDEO_EXTENSIONS];
export const DEFAULT_CONFIDENCE = 0.25;
export const DEFAULT_IOU = 0.45;

export const statusLabels: Record<string, string> = {
  queued: "У черзі",
  processing: "Обробляється",
  completed: "Завершено",
  failed: "Збій",
  cancelled: "Скасовано",
};

export const statusClasses: Record<string, string> = {
  queued: "bg-muted text-muted-foreground",
  processing: "bg-primary/10 text-accent-foreground",
  completed: "bg-emerald-500/10 text-emerald-200",
  failed: "bg-destructive/10 text-red-200",
  cancelled: "bg-secondary text-muted-foreground",
};

export function extensionOf(fileName: string) {
  const index = fileName.lastIndexOf(".");
  return index >= 0 ? fileName.slice(index).toLowerCase() : "";
}

export function mediaKind(file: File | null): "image" | "video" | null {
  if (!file) return null;
  const extension = extensionOf(file.name);
  if (IMAGE_EXTENSIONS.includes(extension)) return "image";
  if (VIDEO_EXTENSIONS.includes(extension)) return "video";
  return null;
}

export function formatBytes(bytes: number) {
  if (!Number.isFinite(bytes)) return "Немає даних";
  const mb = bytes / 1024 / 1024;
  if (mb >= 1) return `${mb.toLocaleString("uk-UA", { maximumFractionDigits: 1 })} МБ`;
  return `${(bytes / 1024).toLocaleString("uk-UA", { maximumFractionDigits: 1 })} КБ`;
}

export function formatDate(value: string | null | undefined) {
  if (!value) return "Немає даних";
  return new Intl.DateTimeFormat("uk-UA", {
    day: "2-digit",
    month: "2-digit",
    year: "2-digit",
    hour: "2-digit",
    minute: "2-digit",
  }).format(new Date(value));
}

export function safeSubmitError(step: "media" | "job") {
  if (step === "media") {
    return "Не вдалося завантажити файл. Перевірте формат і розмір, потім повторіть.";
  }
  return "Не вдалося створити завдання. Перевірте параметри й повторіть.";
}

export function selectDefaultModel(models: ModelVersion[]) {
  return models.find((model) => model.is_active)?.id ?? models[0]?.id ?? "";
}
