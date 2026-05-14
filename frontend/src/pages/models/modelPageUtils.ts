import type { ModelCreateRequest, ModelVersion } from "../../api/types";

export const EMPTY_VALUE = "Немає даних";
export const UNSAFE_PATH_ERROR = "Вкажіть шлях відносно сховища без абсолютних сегментів або ..";

export const metricKeys = {
  map50: ["map50", "mAP50", "map_50", "mAP@0.5", "mAP@50"],
  map5095: ["map50_95", "map_50_95", "mAP50_95", "mAP@0.5:0.95", "mAP@50-95"],
  precision: ["precision"],
  recall: ["recall"],
  size: ["model_size_mb", "size_mb", "model_size"],
  fps: ["fps", "average_fps", "processing_fps"],
};

export interface ModelFormState {
  name: string;
  model_family: "YOLO26" | "YOLO11";
  variant: string;
  weights_path: string;
  dataset_name: string;
  dataset_split_description: string;
}

export const emptyModelForm: ModelFormState = {
  name: "",
  model_family: "YOLO26",
  variant: "",
  weights_path: "",
  dataset_name: "",
  dataset_split_description: "",
};

export function firstNumber(source: Record<string, unknown>, keys: string[]) {
  for (const key of keys) {
    const value = source[key];
    if (typeof value === "number" && Number.isFinite(value)) return value;
  }
  return null;
}

export function safeText(value: string | null | undefined) {
  const trimmed = value?.trim();
  return trimmed ? trimmed : EMPTY_VALUE;
}

export function isUnsafeRelativePath(value: string) {
  const path = value.trim();
  return (
    path.length === 0 ||
    path.startsWith("/") ||
    path.startsWith("\\") ||
    /^[a-zA-Z]:[\\/]/.test(path) ||
    path.split(/[\\/]+/).includes("..")
  );
}

export function modelPayload(form: ModelFormState): ModelCreateRequest {
  return {
    name: form.name.trim(),
    model_family: form.model_family,
    variant: form.variant.trim(),
    weights_path: form.weights_path.trim(),
    dataset_name: form.dataset_name.trim() || null,
    dataset_split_description: form.dataset_split_description.trim() || null,
    metrics_json: {},
    is_active: false,
  };
}

export function formatPercent(value: number | null) {
  if (value === null) return EMPTY_VALUE;
  const normalized = value > 1 ? value : value * 100;
  return `${normalized.toLocaleString("uk-UA", { maximumFractionDigits: 1 })}%`;
}

export function formatMegabytes(value: number | null) {
  if (value === null) return EMPTY_VALUE;
  return `${value.toLocaleString("uk-UA", { maximumFractionDigits: 1 })} МБ`;
}

export function formatFps(value: number | null) {
  if (value === null) return EMPTY_VALUE;
  return `${value.toLocaleString("uk-UA", { maximumFractionDigits: 1 })} FPS`;
}

export function metrics(model: ModelVersion) {
  return {
    map50: firstNumber(model.metrics_json, metricKeys.map50),
    map5095: firstNumber(model.metrics_json, metricKeys.map5095),
    precision: firstNumber(model.metrics_json, metricKeys.precision),
    recall: firstNumber(model.metrics_json, metricKeys.recall),
    size: firstNumber(model.metrics_json, metricKeys.size),
    fps: firstNumber(model.metrics_json, metricKeys.fps),
  };
}
