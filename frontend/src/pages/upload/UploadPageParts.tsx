import { useEffect, useState } from "react";
import {
  CheckCircledIcon,
  Cross2Icon,
  ImageIcon,
  VideoIcon,
} from "@radix-ui/react-icons";
import { Link } from "react-router-dom";
import type { JobDetail, MediaResponse, ModelVersion } from "../../api/types";
import { Button } from "../../components/ui/button";
import { cn } from "../../lib/utils";
import { formatBytes, formatDate, mediaKind, statusClasses, statusLabels } from "./uploadUtils";

export function StatusBadge({ status }: { status: string }) {
  return (
    <span
      className={cn(
        "inline-flex items-center gap-1.5 rounded-full px-2.5 py-1 text-[11px] font-medium",
        statusClasses[status] ?? statusClasses.queued,
      )}
    >
      <span className={cn("h-1.5 w-1.5 rounded-full bg-current", status === "processing" && "animate-pulse")} />
      {statusLabels[status] ?? "Невідомо"}
    </span>
  );
}

export function SliderField({
  label,
  value,
  onChange,
}: {
  label: string;
  value: number;
  onChange: (value: number) => void;
}) {
  return (
    <div className="space-y-2">
      <div className="flex items-center justify-between gap-3">
        <label className="av-label" htmlFor={label}>
          {label}
        </label>
        <span className="rounded bg-primary/10 px-2 py-0.5 font-mono text-xs text-accent-foreground">
          {value.toFixed(2)}
        </span>
      </div>
      <input
        id={label}
        className="w-full accent-[hsl(var(--primary))]"
        type="range"
        min="0"
        max="1"
        step="0.01"
        value={value}
        onChange={(event) => onChange(Number(event.target.value))}
      />
      <div className="flex justify-between text-[10px] text-muted-foreground">
        <span>0</span>
        <span>1</span>
      </div>
    </div>
  );
}

export function ModelSelector({
  models,
  selectedModelId,
  setSelectedModelId,
  loading,
  error,
}: {
  models: ModelVersion[];
  selectedModelId: string;
  setSelectedModelId: (value: string) => void;
  loading: boolean;
  error: boolean;
}) {
  if (loading) {
    return (
      <div className="space-y-2">
        <p className="av-label">Модель</p>
        <div className="av-skeleton h-10 w-full" />
      </div>
    );
  }

  if (error) {
    return (
      <div className="rounded-md border border-destructive/25 bg-destructive/10 p-3 text-sm text-red-100/85">
        Не вдалося завантажити список моделей. Завдання можна створити без вибраної моделі, якщо система має активну модель.
      </div>
    );
  }

  if (models.length === 0) {
    return (
      <div className="rounded-md border border-border bg-secondary/55 p-3 text-sm text-muted-foreground">
        Модель не вибрано. Система застосує активну модель, якщо вона доступна.
      </div>
    );
  }

  return (
    <div className="space-y-2">
      <label className="av-label" htmlFor="upload-model">
        Модель
      </label>
      <select
        id="upload-model"
        className="av-input"
        value={selectedModelId}
        onChange={(event) => setSelectedModelId(event.target.value)}
      >
        {models.map((model) => (
          <option key={model.id} value={model.id}>
            {model.name} {model.is_active ? "(активна)" : ""}
          </option>
        ))}
      </select>
    </div>
  );
}

export function FilePreview({
  file,
  uploadedMedia,
  onClear,
}: {
  file: File;
  uploadedMedia: MediaResponse | null;
  onClear: () => void;
}) {
  const kind = mediaKind(file);
  const [previewUrl, setPreviewUrl] = useState<string | null>(null);

  useEffect(() => {
    if (typeof URL.createObjectURL !== "function") return undefined;
    const url = URL.createObjectURL(file);
    setPreviewUrl(url);
    return () => URL.revokeObjectURL(url);
  }, [file]);

  return (
    <section className="av-card p-4">
      <div className="flex items-center gap-3">
        <div className="grid h-11 w-11 shrink-0 place-items-center rounded-md bg-secondary text-accent-foreground">
          {kind === "video" ? <VideoIcon className="h-5 w-5" /> : <ImageIcon className="h-5 w-5" />}
        </div>
        <div className="min-w-0 flex-1">
          <p className="truncate font-mono text-sm font-medium text-foreground">{file.name}</p>
          <p className="mt-1 text-xs text-muted-foreground">
            {kind === "video" ? "Відео" : "Зображення"} · {formatBytes(file.size)}
          </p>
        </div>
        <Button variant="ghost" size="icon" aria-label="Очистити файл" onClick={onClear}>
          <Cross2Icon className="h-4 w-4" />
        </Button>
      </div>

      <div className="mt-4 overflow-hidden rounded-md border border-border bg-secondary/50">
        {previewUrl && kind === "image" ? (
          <img className="h-56 w-full object-contain" src={previewUrl} alt="Попередній перегляд файлу" />
        ) : (
          <div className="flex h-56 flex-col items-center justify-center gap-2 text-muted-foreground">
            {kind === "video" ? <VideoIcon className="h-8 w-8" /> : <ImageIcon className="h-8 w-8" />}
            <span className="text-sm">Попередній перегляд недоступний</span>
          </div>
        )}
      </div>

      <div className="mt-4 grid gap-2 text-xs text-muted-foreground sm:grid-cols-3">
        <span>Ширина: {uploadedMedia?.width ? uploadedMedia.width.toLocaleString("uk-UA") : "після завантаження"}</span>
        <span>Висота: {uploadedMedia?.height ? uploadedMedia.height.toLocaleString("uk-UA") : "після завантаження"}</span>
        <span>Тривалість: {uploadedMedia?.duration_seconds ? `${uploadedMedia.duration_seconds} с` : "немає даних"}</span>
      </div>
    </section>
  );
}

export function JobStatusPanel({ job }: { job: JobDetail }) {
  const progress = Math.max(0, Math.min(100, Number(job.progress_percent) || 0));
  const isDone = job.status === "completed";
  const isProblem = job.status === "failed" || job.status === "cancelled";
  const lastUpdate = job.last_heartbeat_at ?? job.updated_at;

  return (
    <section className="av-card p-4" data-testid="upload-job-status">
      <div className="mb-3 flex items-center justify-between gap-3">
        <div className="min-w-0">
          <p className="truncate text-sm font-medium text-foreground">Завдання {job.id}</p>
          <p className="mt-1 text-xs text-muted-foreground">Оновлено: {formatDate(lastUpdate)}</p>
        </div>
        <StatusBadge status={job.status} />
      </div>
      {!isDone ? (
        <>
          <div className="h-2 overflow-hidden rounded-full bg-secondary">
            <div className="h-full rounded-full bg-primary transition-[width] duration-500" style={{ width: `${progress}%` }} />
          </div>
          <div className="mt-2 flex items-center justify-between text-xs">
            <span className={cn(isProblem ? "text-red-100/85" : "text-muted-foreground")}>
              {isProblem ? "Обробку зупинено. Перевірте деталі завдання." : "Очікується або виконується обробка."}
            </span>
            <span className="font-mono text-accent-foreground">{progress}%</span>
          </div>
        </>
      ) : (
        <div className="flex flex-col gap-3 sm:flex-row sm:items-center">
          <div className="flex items-center gap-2 text-sm text-emerald-100">
            <CheckCircledIcon className="h-4 w-4" />
            <span>Обробку завершено успішно</span>
          </div>
          <Button className="sm:ml-auto" size="sm" variant="secondary" asChild>
            <Link to={`/jobs/${job.id}`}>Відкрити результати</Link>
          </Button>
        </div>
      )}
    </section>
  );
}
