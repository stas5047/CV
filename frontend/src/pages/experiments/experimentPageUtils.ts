import type { ExperimentMetric, ExperimentRun, ExperimentType } from "../../api/types";

export const EXPERIMENT_EMPTY_TEXT = "Дані експерименту ще не завантажено";
export const EMPTY_VALUE = "Немає даних";

export type MetricEntry = {
  name: string;
  value: number | null;
  unit: string | null;
  metadata: Record<string, unknown>;
};

export type ModelComparisonRow = {
  metric: string;
  modelA: string;
  modelB: string;
  valueA: number | null;
  valueB: number | null;
};

export type ThresholdRow = {
  threshold: number;
  precision: number | null;
  recall: number | null;
  f1: number | null;
  falsePositiveRate: number | null;
};

export type TrackerRow = {
  metric: string;
  bytetrack: number | string | null;
  botsort: number | string | null;
  unit: string | null;
};

export type PerformanceRow = {
  label: string;
  fps: number | null;
  latencyMs: number | null;
};

const modelMetricLabels = [
  { label: "Precision", keys: ["precision"] },
  { label: "Recall", keys: ["recall"] },
  { label: "mAP@50", keys: ["map50", "mAP50", "map_50", "mAP@0.5", "mAP@50"] },
  { label: "mAP@50-95", keys: ["map50_95", "map_50_95", "mAP50_95", "mAP@0.5:0.95", "mAP@50-95"] },
];

const trackerLabels = [
  { label: "Video FPS", keys: ["video_fps", "processing_fps", "average_fps", "fps"] },
  { label: "Унікальні track IDs", keys: ["unique_track_ids", "track_ids", "tracks_count"] },
  { label: "Кадри з виявленнями", keys: ["frames_with_detections"] },
  { label: "Середня впевненість", keys: ["average_confidence", "avg_confidence"] },
  { label: "Проксі фрагментації треку", keys: ["track_fragmentation_proxy", "fragmentation_proxy", "fragmentations"] },
  { label: "Візуальна стабільність", keys: ["visual_stability", "stability_score"] },
  { label: "Спостережені ID switches", keys: ["observed_id_switches", "id_switch_examples"] },
];

const forbiddenMetricFragments = ["mota", "idf1", "hota", "trackingaccuracy", "tracking accuracy"];

export function groupExperiments(items: ExperimentRun[]) {
  return items.reduce<Record<ExperimentType, ExperimentRun[]>>(
    (groups, item) => {
      if (isExperimentType(item.experiment_type)) {
        groups[item.experiment_type].push(item);
      }
      return groups;
    },
    {
      model_comparison: [],
      threshold_analysis: [],
      tracker_comparison: [],
      false_positive_analysis: [],
    },
  );
}

function isExperimentType(value: string): value is ExperimentType {
  return (
    value === "model_comparison" ||
    value === "threshold_analysis" ||
    value === "tracker_comparison" ||
    value === "false_positive_analysis"
  );
}

export function safeText(value: string | null | undefined) {
  const trimmed = value?.trim();
  return trimmed ? trimmed : EMPTY_VALUE;
}

export function formatPercent(value: number | null) {
  if (value === null || !Number.isFinite(value)) return EMPTY_VALUE;
  const normalized = value > 1 ? value : value * 100;
  return `${normalized.toLocaleString("uk-UA", { maximumFractionDigits: 1 })}%`;
}

export function formatNumber(value: number | string | null, unit?: string | null) {
  if (value === null) return EMPTY_VALUE;
  if (typeof value === "string") return value.trim() || EMPTY_VALUE;
  if (!Number.isFinite(value)) return EMPTY_VALUE;
  const formatted = value.toLocaleString("uk-UA", { maximumFractionDigits: 2 });
  return unit ? `${formatted} ${unit}` : formatted;
}

export function formatMs(value: number | null) {
  if (value === null || !Number.isFinite(value)) return EMPTY_VALUE;
  return `${value.toLocaleString("uk-UA", { maximumFractionDigits: 1 })} ms`;
}

export function formatFps(value: number | null) {
  if (value === null || !Number.isFinite(value)) return EMPTY_VALUE;
  return `${value.toLocaleString("uk-UA", { maximumFractionDigits: 1 })} FPS`;
}

export function metricValue(run: ExperimentRun | undefined, keys: string[]) {
  if (!run) return null;
  for (const key of keys) {
    const metric = findMetric(run, key);
    if (metric && typeof metric.metric_value === "number" && Number.isFinite(metric.metric_value)) {
      return metric.metric_value;
    }
  }
  return null;
}

export function findMetric(run: ExperimentRun, key: string) {
  const target = normalizeKey(key);
  return run.metrics.find((metric) => normalizeKey(metric.metric_name) === target);
}

export function modelComparisonRows(runs: ExperimentRun[]): ModelComparisonRow[] {
  const [first, second] = runs;
  if (!first || !second) return [];
  const modelA = shortModelName(first.name);
  const modelB = shortModelName(second.name);
  return modelMetricLabels.map((metric) => ({
    metric: metric.label,
    modelA,
    modelB,
    valueA: metricValue(first, metric.keys),
    valueB: metricValue(second, metric.keys),
  })).filter((row) => row.valueA !== null || row.valueB !== null);
}

export function precisionRecallCards(runs: ExperimentRun[]) {
  const primary = runs[1] ?? runs[0];
  return [
    { label: "Precision", value: metricValue(primary, ["precision"]) },
    { label: "Recall", value: metricValue(primary, ["recall"]) },
    { label: "mAP@50", value: metricValue(primary, ["map50", "mAP@50"]) },
    { label: "mAP@50-95", value: metricValue(primary, ["map50_95", "mAP@50-95"]) },
  ];
}

export function thresholdRows(runs: ExperimentRun[]): ThresholdRow[] {
  const rows = runs.flatMap((run) => {
    const threshold = numberFromConfig(run.config_json, ["confidence_threshold", "threshold", "conf"]);
    if (threshold === null) return [];
    return [{
      threshold,
      precision: metricValue(run, ["precision"]),
      recall: metricValue(run, ["recall"]),
      f1: metricValue(run, ["f1", "f1_score"]),
      falsePositiveRate: metricValue(run, ["false_positive_rate", "fp_rate"]),
    }];
  });
  return rows
    .filter((row) => row.precision !== null || row.recall !== null || row.f1 !== null || row.falsePositiveRate !== null)
    .sort((a, b) => a.threshold - b.threshold);
}

export function trackerRows(runs: ExperimentRun[]): TrackerRow[] {
  const byteTrack = findTrackerRun(runs, "bytetrack");
  const botSort = findTrackerRun(runs, "botsort");
  if (!byteTrack && !botSort) return [];

  return trackerLabels.map((label) => {
    const byteMetric = firstAllowedMetric(byteTrack, label.keys);
    const botMetric = firstAllowedMetric(botSort, label.keys);
    return {
      metric: label.label,
      bytetrack: metricDisplayValue(byteMetric),
      botsort: metricDisplayValue(botMetric),
      unit: byteMetric?.metric_unit ?? botMetric?.metric_unit ?? null,
    };
  }).filter((row) => row.bytetrack !== null || row.botsort !== null);
}

export function performanceRows(modelRuns: ExperimentRun[], trackerRuns: ExperimentRun[]) {
  const sources = [...modelRuns, ...trackerRuns];
  const rows: PerformanceRow[] = sources.map((run) => ({
    label: shortModelName(run.name),
    fps: metricValue(run, ["fps", "average_fps", "processing_fps", "video_fps"]),
    latencyMs: metricValue(run, ["latency_ms", "inference_latency_ms", "latency_per_frame_ms"]),
  }));
  return rows.filter((row) => row.fps !== null || row.latencyMs !== null);
}

export function falsePositiveMetrics(runs: ExperimentRun[]) {
  const run = runs[0];
  if (!run) return [];
  return [
    { label: "Частка хибнопозитивних", value: metricValue(run, ["false_positive_rate", "fp_rate"]), kind: "percent" as const },
    { label: "Хибні виявлення птахів", value: metricValue(run, ["bird_false_detections", "false_drone_detections"]), kind: "number" as const },
    { label: "Переглянуті зображення", value: metricValue(run, ["reviewed_images", "total_images", "sample_size"]), kind: "number" as const },
    { label: "Частка істиннопозитивних", value: metricValue(run, ["true_positive_rate", "tp_rate"]), kind: "percent" as const },
  ].filter((item) => item.value !== null);
}

export function hasNoSectionData(groups: ReturnType<typeof groupExperiments>) {
  return Object.values(groups).every((runs) => runs.length === 0);
}

export function hasSafeConfusionMatrixUrl() {
  return null;
}

function firstAllowedMetric(run: ExperimentRun | undefined, keys: string[]) {
  if (!run) return undefined;
  return keys
    .map((key) => findMetric(run, key))
    .find((metric): metric is ExperimentMetric => metric !== undefined && !isForbiddenMetric(metric.metric_name));
}

function metricDisplayValue(metric: ExperimentMetric | undefined) {
  if (!metric) return null;
  if (typeof metric.metric_value === "number" && Number.isFinite(metric.metric_value)) return metric.metric_value;
  const label = metadataString(metric.metadata_json, ["label", "value", "summary"]);
  return label;
}

function isForbiddenMetric(metricName: string) {
  const normalized = normalizeKey(metricName);
  return forbiddenMetricFragments.some((term) => normalized.includes(normalizeKey(term)));
}

function findTrackerRun(runs: ExperimentRun[], tracker: "bytetrack" | "botsort") {
  return runs.find((run) => {
    const trackerType = metadataString(run.config_json, ["tracker_type", "tracker", "name"]);
    return normalizeKey(trackerType ?? run.name).includes(tracker);
  });
}

function numberFromConfig(config: Record<string, unknown>, keys: string[]) {
  for (const key of keys) {
    const value = config[key];
    if (typeof value === "number" && Number.isFinite(value)) return value;
    if (typeof value === "string") {
      const parsed = Number(value);
      if (Number.isFinite(parsed)) return parsed;
    }
  }
  return null;
}

function metadataString(source: Record<string, unknown>, keys: string[]) {
  for (const key of keys) {
    const value = source[key];
    if (typeof value === "string" && value.trim()) return value.trim();
    if (typeof value === "number" && Number.isFinite(value)) return String(value);
  }
  return null;
}

function normalizeKey(value: string) {
  return value.toLowerCase().replace(/[^a-z0-9]+/g, "");
}

function shortModelName(name: string) {
  return name.replace(/\s+/g, " ").trim() || EMPTY_VALUE;
}
