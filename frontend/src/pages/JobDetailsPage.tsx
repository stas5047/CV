import { useEffect, useMemo, useState, type ReactNode } from "react";
import { useQueries, useQuery } from "@tanstack/react-query";
import {
  ArrowLeftIcon,
  DownloadIcon,
  ImageIcon,
  LightningBoltIcon,
  ReaderIcon,
  TimerIcon,
  VideoIcon,
} from "@radix-ui/react-icons";
import { Link, useParams } from "react-router-dom";
import { downloadJobFile, getJob, getJobResult, listJobDetections, listJobTracks, saveBlob } from "../api/jobs";
import type { JobDownloadReference } from "../api/types";
import { useToast } from "../components/toast";
import { Button } from "../components/ui/button";
import {
  averageConfidence,
  averageFps,
  detectionCount,
  EMPTY_VALUE,
  filenameFor,
  formatBBox,
  formatCount,
  formatDate,
  formatDuration,
  formatPercent,
  formatTimestampMs,
  mediaTypeLabels,
  safeText,
} from "./jobs/jobFormatters";
import { EmptyState, ErrorState, ProgressBar, StatusBadge, TableSkeleton } from "./jobs/JobPageParts";

function terminal(status: string) {
  return status === "completed" || status === "failed" || status === "cancelled";
}

function SummaryCard({ label, value, icon }: { label: string; value: string; icon: ReactNode }) {
  return (
    <section className="av-card p-4">
      <div className="flex items-start gap-3">
        <span className="mt-0.5 text-muted-foreground">{icon}</span>
        <div>
          <p className="av-label">{label}</p>
          <p className="mt-2 font-display text-xl font-semibold leading-none">{value}</p>
        </div>
      </div>
    </section>
  );
}

function DownloadButton({
  reference,
  label,
  filename,
}: {
  reference: JobDownloadReference | undefined;
  label: string;
  filename: string;
}) {
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState(false);
  const { toast } = useToast();

  const handleDownload = async () => {
    if (!reference?.available) return;
    setLoading(true);
    setError(false);
    try {
      const blob = await downloadJobFile(reference.download_url);
      saveBlob(blob, filename);
      toast({ variant: "success", title: "Завантаження підготовлено", description: label });
    } catch {
      setError(true);
      toast({ variant: "error", title: "Завантаження не вдалося", description: "Не вдалося підготувати файл." });
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="space-y-1">
      <Button variant="secondary" size="sm" disabled={!reference?.available || loading} onClick={handleDownload}>
        <DownloadIcon className="h-3.5 w-3.5" />
        {loading ? "Готується..." : label}
      </Button>
      {error ? <p className="text-xs text-red-200">Не вдалося підготувати завантаження.</p> : null}
    </div>
  );
}

function usePreviewUrl(reference: JobDownloadReference | undefined, enabled: boolean) {
  const [previewUrl, setPreviewUrl] = useState<string | null>(null);
  const [previewError, setPreviewError] = useState(false);

  useEffect(() => {
    let objectUrl: string | null = null;
    let cancelled = false;
    setPreviewUrl(null);
    setPreviewError(false);

    if (!enabled || !reference?.available) return undefined;

    void downloadJobFile(reference.download_url)
      .then((blob) => {
        if (cancelled) return;
        objectUrl = URL.createObjectURL(blob);
        setPreviewUrl(objectUrl);
      })
      .catch(() => {
        if (!cancelled) setPreviewError(true);
      });

    return () => {
      cancelled = true;
      if (objectUrl) URL.revokeObjectURL(objectUrl);
    };
  }, [enabled, reference?.available, reference?.download_url]);

  return { previewUrl, previewError };
}

export function JobDetailsPage() {
  const { jobId } = useParams();
  const id = jobId ?? "";

  const jobQuery = useQuery({
    queryKey: ["jobs", id],
    queryFn: () => getJob(id),
    enabled: Boolean(id),
    refetchInterval: (query) => {
      const status = query.state.data?.status;
      return status && !terminal(status) ? 3000 : false;
    },
  });

  const job = jobQuery.data;
  const isCompleted = job?.status === "completed";
  const isVideo = job?.media.media_type === "video";

  const [resultQuery, detectionsQuery, tracksQuery] = useQueries({
    queries: [
      {
        queryKey: ["jobs", id, "result"],
        queryFn: () => getJobResult(id),
        enabled: Boolean(id) && Boolean(job) && (isCompleted || Boolean(job?.result)),
      },
      {
        queryKey: ["jobs", id, "detections"],
        queryFn: () => listJobDetections(id, { limit: 100, offset: 0 }),
        enabled: Boolean(id) && isCompleted,
      },
      {
        queryKey: ["jobs", id, "tracks"],
        queryFn: () => listJobTracks(id, { limit: 100, offset: 0 }),
        enabled: Boolean(id) && isCompleted && isVideo,
      },
    ],
  });

  const result = resultQuery.data;
  const resultRefs = result ?? job?.result;
  const canPreview = Boolean(isCompleted && resultRefs?.media.available && (job?.media.media_type === "image" || job?.media.media_type === "video"));
  const { previewUrl, previewError } = usePreviewUrl(resultRefs?.media, canPreview);
  const [playbackError, setPlaybackError] = useState(false);

  useEffect(() => {
    setPlaybackError(false);
  }, [previewUrl]);

  const summary = useMemo(() => ({ ...(job?.summary_json ?? {}), ...(result?.summary ?? {}) }), [job?.summary_json, result?.summary]);
  const previewUnavailable = previewError || playbackError;

  if (!id) {
    return <ErrorState title="Завдання не знайдено" description="Маршрут не містить коректного ідентифікатора." onRetry={() => window.history.back()} />;
  }
  if (jobQuery.isLoading) return <TableSkeleton rows={7} />;
  if (jobQuery.isError || !job) {
    return (
      <ErrorState
        title="Не вдалося завантажити деталі"
        description="Перевірте доступ до завдання та повторіть запит."
        onRetry={() => void jobQuery.refetch()}
      />
    );
  }

  const detections = detectionsQuery.data?.items ?? [];
  const tracks = tracksQuery.data?.items ?? [];
  const totalDetections = detectionCount({ ...job, summary_json: summary }) ?? detectionsQuery.data?.total ?? null;

  return (
    <div className="space-y-5">
      <header className="flex flex-col gap-3">
        <div className="flex flex-wrap items-center gap-2">
          <Button variant="ghost" size="sm" asChild>
            <Link to="/jobs">
              <ArrowLeftIcon className="h-3.5 w-3.5" />
              Черга
            </Link>
          </Button>
          <span className="text-muted-foreground">/</span>
          <span className="max-w-[320px] truncate font-mono text-xs text-muted-foreground">{safeText(job.media.original_filename)}</span>
          <StatusBadge status={job.status} />
        </div>
        <div>
          <h1 className="font-display text-2xl font-bold tracking-tight">Деталі завдання</h1>
          <p className="mt-1 text-sm text-muted-foreground">Виявлення, треки та файли експорту</p>
        </div>
      </header>

      {!terminal(job.status) ? (
        <section className="av-card p-4">
          <div className="mb-3 flex items-center justify-between gap-4">
            <div>
              <p className="font-medium">{job.status === "queued" ? "Очікує в черзі" : "Завдання обробляється"}</p>
              <p className="mt-1 text-xs text-muted-foreground">Останнє оновлення: {formatDate(job.last_heartbeat_at ?? job.updated_at)}</p>
            </div>
            <span className="font-mono text-sm text-accent-foreground">{Math.round(job.progress_percent)}%</span>
          </div>
          <ProgressBar value={job.progress_percent} />
        </section>
      ) : null}

      {job.status === "failed" ? (
        <section className="av-card border-destructive/25 bg-destructive/10 p-4">
          <p className="font-semibold text-red-100">Помилка обробки</p>
          <p className="mt-1 text-sm text-red-100/75">Обробку зупинено. Перевірте файл або параметри та створіть нове завдання.</p>
        </section>
      ) : null}

      <section className="grid gap-4 xl:grid-cols-[minmax(0,1fr)_320px]">
        <div className="av-card min-h-[280px] overflow-hidden">
          {previewUrl && job.media.media_type === "image" ? (
            <img className="h-full max-h-[520px] w-full object-contain" src={previewUrl} alt="Анотований результат" />
          ) : previewUrl && job.media.media_type === "video" && !previewUnavailable ? (
            <video
              aria-label="processed-video-preview"
              className="h-full max-h-[520px] w-full bg-secondary"
              src={previewUrl}
              controls
              onError={() => setPlaybackError(true)}
            />
          ) : (
            <div
              className="flex min-h-[280px] flex-col items-center justify-center gap-3 p-6 text-center text-muted-foreground"
              data-testid="preview-unavailable-notice"
            >
              {job.media.media_type === "video" ? <VideoIcon className="h-10 w-10" /> : <ImageIcon className="h-10 w-10" />}
              <p className="font-medium text-foreground">
                {isCompleted ? "Попередній перегляд недоступний" : "Результат ще не готовий"}
              </p>
              <p className="max-w-md text-sm leading-6">
                {previewUnavailable || job.media.media_type === "video"
                  ? "Перегляд відео у браузері може бути недоступним. Використайте кнопку завантаження нижче."
                  : "Анотований файл з'явиться після завершення обробки."}
              </p>
            </div>
          )}
        </div>

        <div className="grid gap-3 sm:grid-cols-2 xl:grid-cols-1">
          <SummaryCard label="Виявлень" value={formatCount(totalDetections)} icon={<ReaderIcon className="h-4 w-4" />} />
          <SummaryCard label="Сер. впевненість" value={formatPercent(averageConfidence({ ...job, summary_json: summary }))} icon={<LightningBoltIcon className="h-4 w-4" />} />
          <SummaryCard label="Середній FPS" value={averageFps({ ...job, summary_json: summary })?.toLocaleString("uk-UA", { maximumFractionDigits: 1 }) ?? EMPTY_VALUE} icon={<VideoIcon className="h-4 w-4" />} />
          <SummaryCard label="Тривалість" value={formatDuration({ ...job, summary_json: summary })} icon={<TimerIcon className="h-4 w-4" />} />
        </div>
      </section>

      <section className="grid gap-4 lg:grid-cols-[minmax(0,1fr)_320px]">
        <div className="av-card p-4">
          <h2 className="font-display text-base font-semibold">Завантаження</h2>
          <div className="mt-4 flex flex-wrap gap-3">
            <DownloadButton
              reference={resultRefs?.media}
              label={job.media.media_type === "video" ? "Анотоване відео" : "Анотоване зображення"}
              filename={filenameFor(job.id, "media", job.media.media_type)}
            />
            <DownloadButton reference={resultRefs?.csv} label="CSV-звіт" filename={filenameFor(job.id, "csv")} />
            <DownloadButton reference={resultRefs?.json} label="JSON-дані" filename={filenameFor(job.id, "json")} />
          </div>
        </div>

        <div className="av-card p-4">
          <h2 className="font-display text-base font-semibold">Параметри</h2>
          <dl className="mt-4 space-y-2 text-sm">
            <Row label="Файл" value={safeText(job.media.original_filename)} />
            <Row label="Тип" value={mediaTypeLabels[job.media.media_type] ?? EMPTY_VALUE} />
            <Row label="Розмір кадру" value={job.media.width && job.media.height ? `${job.media.width} x ${job.media.height}` : EMPTY_VALUE} />
            <Row label="Модель" value={job.model ? safeText(job.model.name) : EMPTY_VALUE} />
            <Row label="Впевненість" value={formatParam(job.input_params_json.confidence_threshold)} />
            <Row label="IoU" value={formatParam(job.input_params_json.iou_threshold)} />
            {job.media.media_type === "video" ? <Row label="Трекер" value={safeText(job.input_params_json.tracker_type ?? "ByteTrack")} /> : null}
            <Row label="Створено" value={formatDate(job.created_at)} />
            <Row label="Оновлено" value={formatDate(job.last_heartbeat_at ?? job.updated_at)} />
          </dl>
        </div>
      </section>

      {isCompleted ? (
        <section className="av-card overflow-hidden">
          <div className="border-b border-border px-5 py-4">
            <h2 className="font-display text-base font-semibold">Виявлення</h2>
          </div>
          {detectionsQuery.isLoading ? (
            <div className="p-5">
              <div className="av-skeleton h-32 w-full" />
            </div>
          ) : totalDetections === 0 || detections.length === 0 ? (
            <EmptyState title="Виявлень не знайдено" description="Модель не виявила об'єктів drone у цьому файлі. Це успішний результат, не помилка." />
          ) : (
            <div className="overflow-x-auto">
              <table className="w-full min-w-[940px] border-collapse text-sm">
                <thead className="bg-secondary">
                  <tr className="text-left text-[11px] uppercase tracking-[0.055em] text-muted-foreground">
                    <th className="px-4 py-3 font-semibold">Кадр</th>
                    <th className="px-4 py-3 font-semibold">Час</th>
                    <th className="px-4 py-3 font-semibold">Клас</th>
                    <th className="px-4 py-3 font-semibold">Впевненість</th>
                    <th className="px-4 py-3 font-semibold">Координати рамки</th>
                    <th className="px-4 py-3 font-semibold">ID треку</th>
                  </tr>
                </thead>
                <tbody>
                  {detections.map((detection) => (
                    <tr className="border-t border-border/70" key={detection.id}>
                      <td className="px-4 py-3 font-mono">{detection.frame_index}</td>
                      <td className="px-4 py-3 font-mono text-muted-foreground">{formatTimestampMs(detection.timestamp_ms)}</td>
                      <td className="px-4 py-3">
                        <span className="rounded bg-primary/10 px-2 py-1 text-xs text-accent-foreground">{safeText(detection.class_name)}</span>
                      </td>
                      <td className="px-4 py-3 font-mono">{formatPercent(detection.confidence, 0)}</td>
                      <td className="px-4 py-3 font-mono text-xs text-muted-foreground">
                        {formatBBox(detection.bbox_x1, detection.bbox_y1, detection.bbox_x2, detection.bbox_y2)}
                      </td>
                      <td className="px-4 py-3 font-mono">{detection.track_id ?? EMPTY_VALUE}</td>
                    </tr>
                  ))}
                </tbody>
              </table>
            </div>
          )}
        </section>
      ) : null}

      {isCompleted && isVideo ? (
        <section className="av-card overflow-hidden">
          <div className="border-b border-border px-5 py-4">
            <h2 className="font-display text-base font-semibold">Треки об'єктів</h2>
          </div>
          {tracksQuery.isLoading ? (
            <div className="p-5">
              <div className="av-skeleton h-24 w-full" />
            </div>
          ) : tracks.length === 0 ? (
            <EmptyState title="Треки відсутні" description="Для цього відео не побудовано жодного треку." />
          ) : (
            <div className="overflow-x-auto">
              <table className="w-full min-w-[780px] border-collapse text-sm">
                <thead className="bg-secondary">
                  <tr className="text-left text-[11px] uppercase tracking-[0.055em] text-muted-foreground">
                    <th className="px-4 py-3 font-semibold">ID треку</th>
                    <th className="px-4 py-3 font-semibold">Клас</th>
                    <th className="px-4 py-3 font-semibold">Перший кадр</th>
                    <th className="px-4 py-3 font-semibold">Останній кадр</th>
                    <th className="px-4 py-3 font-semibold">Кадрів</th>
                    <th className="px-4 py-3 font-semibold">Сер. впевненість</th>
                    <th className="px-4 py-3 font-semibold">Макс. впевненість</th>
                  </tr>
                </thead>
                <tbody>
                  {tracks.map((track) => (
                    <tr className="border-t border-border/70" key={track.id}>
                      <td className="px-4 py-3 font-mono">{track.track_id}</td>
                      <td className="px-4 py-3">{safeText(track.class_name)}</td>
                      <td className="px-4 py-3 font-mono text-muted-foreground">{track.first_frame_index}</td>
                      <td className="px-4 py-3 font-mono text-muted-foreground">{track.last_frame_index}</td>
                      <td className="px-4 py-3 font-mono">{track.frames_count}</td>
                      <td className="px-4 py-3 font-mono">{formatPercent(track.average_confidence)}</td>
                      <td className="px-4 py-3 font-mono">{formatPercent(track.max_confidence)}</td>
                    </tr>
                  ))}
                </tbody>
              </table>
            </div>
          )}
        </section>
      ) : null}
    </div>
  );
}

function Row({ label, value }: { label: string; value: string }) {
  return (
    <div className="flex items-start justify-between gap-3">
      <dt className="text-muted-foreground">{label}</dt>
      <dd className="max-w-[180px] truncate text-right font-mono text-xs text-foreground">{value}</dd>
    </div>
  );
}

function formatParam(value: unknown) {
  if (typeof value === "number" && Number.isFinite(value)) return value.toFixed(2);
  return EMPTY_VALUE;
}
