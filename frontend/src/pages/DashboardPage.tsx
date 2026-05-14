import { useMemo, type ReactNode } from "react";
import { useQuery } from "@tanstack/react-query";
import {
  BarChartIcon,
  ChevronRightIcon,
  Component1Icon,
  DashboardIcon,
  FileIcon,
  ImageIcon,
  LightningBoltIcon,
  ReaderIcon,
  RocketIcon,
  UploadIcon,
  VideoIcon,
} from "@radix-ui/react-icons";
import { Link } from "react-router-dom";
import {
  getActiveModels,
  getAdminDashboardJobs,
  getAdminDashboardStats,
  getUserDashboardJobs,
} from "../api/dashboard";
import type { AdminStatsResponse, JobDetail, JobListResponse, ModelVersion } from "../api/types";
import { useAuth } from "../auth/useAuth";
import { Button } from "../components/ui/button";
import { cn } from "../lib/utils";

const EMPTY_VALUE = "Немає даних";

const statusLabels: Record<string, string> = {
  queued: "У черзі",
  processing: "Обробляється",
  completed: "Завершено",
  failed: "Збій",
  cancelled: "Скасовано",
};

const statusClasses: Record<string, string> = {
  queued: "bg-muted text-muted-foreground",
  processing: "bg-primary/10 text-accent-foreground",
  completed: "bg-emerald-500/10 text-emerald-200",
  failed: "bg-destructive/10 text-red-200",
  cancelled: "bg-secondary text-muted-foreground",
};

function numberOrNull(value: unknown): number | null {
  return typeof value === "number" && Number.isFinite(value) ? value : null;
}

function firstNumber(source: Record<string, unknown> | null | undefined, keys: string[]) {
  if (!source) return null;
  for (const key of keys) {
    const value = numberOrNull(source[key]);
    if (value !== null) return value;
  }
  return null;
}

function completedJobs(jobs: JobDetail[]) {
  return jobs.filter((job) => job.status === "completed");
}

function average(values: number[]) {
  if (values.length === 0) return null;
  return values.reduce((sum, value) => sum + value, 0) / values.length;
}

function formatCount(value: number | null) {
  return value === null ? EMPTY_VALUE : value.toLocaleString("uk-UA");
}

function formatPercent(value: number | null) {
  if (value === null) return EMPTY_VALUE;
  const normalized = value > 1 ? value : value * 100;
  return `${normalized.toLocaleString("uk-UA", { maximumFractionDigits: 1 })}%`;
}

function formatFps(value: number | null) {
  if (value === null) return EMPTY_VALUE;
  return value.toLocaleString("uk-UA", { maximumFractionDigits: 1 });
}

function formatDate(value: string) {
  return new Intl.DateTimeFormat("uk-UA", {
    day: "2-digit",
    month: "2-digit",
    year: "2-digit",
    hour: "2-digit",
    minute: "2-digit",
  }).format(new Date(value));
}

function diffSeconds(start: string | null, end: string | null) {
  if (!start || !end) return null;
  const diff = new Date(end).getTime() - new Date(start).getTime();
  return Number.isFinite(diff) && diff >= 0 ? diff / 1000 : null;
}

function formatDuration(job: JobDetail) {
  const summaryDuration = firstNumber(job.summary_json, [
    "processing_duration_seconds",
    "duration_seconds",
    "elapsed_seconds",
  ]);
  const duration = summaryDuration ?? diffSeconds(job.started_at, job.completed_at);
  if (duration === null) return EMPTY_VALUE;
  if (duration < 60) return `${Math.round(duration)} с`;
  return `${Math.floor(duration / 60)} хв ${Math.round(duration % 60)} с`;
}

function detectionCount(job: JobDetail) {
  return firstNumber(job.summary_json, [
    "total_detections",
    "detections_count",
    "detections",
    "objects_detected",
  ]);
}

function confidence(job: JobDetail) {
  return firstNumber(job.summary_json, ["average_confidence", "avg_confidence", "mean_confidence"]);
}

function fps(job: JobDetail) {
  return firstNumber(job.summary_json, ["average_fps", "avg_fps", "fps", "processing_fps"]);
}

function buildUserStats(jobs: JobDetail[]) {
  const done = completedJobs(jobs);
  const detections = done.map(detectionCount).filter((value): value is number => value !== null);
  const confidenceValues = done.map(confidence).filter((value): value is number => value !== null);
  const fpsValues = done.map(fps).filter((value): value is number => value !== null);

  return {
    processedFiles: done.length,
    totalDetections: detections.length === 0 ? null : detections.reduce((sum, value) => sum + value, 0),
    avgConfidence: average(confidenceValues),
    avgFps: average(fpsValues),
  };
}

function buildAdminStats(stats: AdminStatsResponse | undefined) {
  return {
    processedFiles: stats?.jobs.by_status.completed ?? 0,
    totalDetections: stats?.detections.total ?? null,
    avgConfidence: null,
    avgFps: null,
  };
}

function modelMetric(model: ModelVersion | undefined, keys: string[]) {
  return firstNumber(model?.metrics_json, keys);
}

function DashboardSkeleton() {
  return (
    <div className="space-y-5">
      <div className="flex items-start justify-between gap-4">
        <div className="space-y-2">
          <div className="av-skeleton h-7 w-36" />
          <div className="av-skeleton h-4 w-64" />
        </div>
        <div className="av-skeleton h-10 w-36" />
      </div>
      <div className="grid grid-cols-2 gap-4 lg:grid-cols-4">
        {Array.from({ length: 4 }).map((_, index) => (
          <div className="av-card space-y-4 p-5" key={index}>
            <div className="av-skeleton h-3 w-24" />
            <div className="av-skeleton h-7 w-20" />
            <div className="av-skeleton h-3 w-32" />
          </div>
        ))}
      </div>
      <div className="grid gap-4 lg:grid-cols-[280px_minmax(0,1fr)]">
        <div className="av-card p-5">
          <div className="av-skeleton h-40 w-full" />
        </div>
        <div className="av-card p-5">
          <div className="av-skeleton h-40 w-full" />
        </div>
      </div>
    </div>
  );
}

function MetricCard({ label, value, hint, icon }: { label: string; value: string; hint: string; icon: ReactNode }) {
  return (
    <section className="av-card p-5 transition duration-300 hover:-translate-y-0.5">
      <div className="flex items-start justify-between gap-3">
        <span className="av-label">{label}</span>
        <span className="text-muted-foreground/60">{icon}</span>
      </div>
      <div className="mt-4 font-display text-2xl font-bold leading-none text-foreground md:text-[28px]">
        {value}
      </div>
      <p className="mt-2 text-xs text-muted-foreground">{hint}</p>
    </section>
  );
}

function StatusBadge({ status }: { status: string }) {
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

function EmptyState({ title, description, action }: { title: string; description: string; action?: ReactNode }) {
  return (
    <div className="flex min-h-48 flex-col items-center justify-center gap-3 px-5 py-10 text-center">
      <Component1Icon className="h-7 w-7 text-muted-foreground/40" />
      <div>
        <p className="font-medium text-foreground">{title}</p>
        <p className="mt-1 max-w-sm text-sm leading-6 text-muted-foreground">{description}</p>
      </div>
      {action ? <div className="mt-2">{action}</div> : null}
    </div>
  );
}

function ErrorState({ onRetry }: { onRetry: () => void }) {
  return (
    <section className="av-card border-destructive/25 bg-destructive/10 p-5">
      <div className="flex flex-col gap-4 sm:flex-row sm:items-center sm:justify-between">
        <div>
          <h1 className="font-display text-xl font-semibold">Не вдалося завантажити огляд</h1>
          <p className="mt-1 text-sm text-red-100/75">Перевірте з'єднання з backend API та повторіть запит.</p>
        </div>
        <Button variant="secondary" onClick={onRetry}>
          Повторити
        </Button>
      </div>
    </section>
  );
}

function ActiveModelPanel({ model }: { model: ModelVersion | undefined }) {
  const map = modelMetric(model, ["mAP50", "map50", "map_50", "map"]);
  const precision = modelMetric(model, ["precision"]);
  const recall = modelMetric(model, ["recall"]);

  return (
    <section className="av-card p-5">
      <p className="av-label">Активна модель</p>
      <div className="mt-4 flex items-center gap-3">
        <div className="flex h-10 w-10 shrink-0 items-center justify-center rounded-md bg-primary/10 text-accent-foreground">
          <RocketIcon className="h-5 w-5" />
        </div>
        <div className="min-w-0">
          <p className="truncate font-mono text-sm font-medium text-foreground">{model ? model.name : EMPTY_VALUE}</p>
          <p className="mt-1 text-xs text-muted-foreground">
            {model ? `${model.model_family} · ${model.variant}` : "Модель ще не активована"}
          </p>
        </div>
      </div>
      <div className="mt-5 space-y-3">
        <ModelMetric label="mAP@50" value={map} />
        <ModelMetric label="Точність" value={precision} />
        <ModelMetric label="Повнота" value={recall} />
      </div>
    </section>
  );
}

function ModelMetric({ label, value }: { label: string; value: number | null }) {
  const width = value === null ? 0 : Math.max(0, Math.min(100, (value > 1 ? value : value * 100)));
  return (
    <div>
      <div className="mb-1 flex items-center justify-between text-xs">
        <span className="text-muted-foreground">{label}</span>
        <span className="font-mono text-muted-foreground">{value === null ? EMPTY_VALUE : formatPercent(value)}</span>
      </div>
      <div className="h-1 overflow-hidden rounded-full bg-secondary">
        <div className="h-full rounded-full bg-primary transition-[width] duration-500" style={{ width: `${width}%` }} />
      </div>
    </div>
  );
}

function ActivityPanel({ jobs }: { jobs: JobDetail[] }) {
  const points = useMemo(() => {
    const done = completedJobs(jobs)
      .slice()
      .sort((a, b) => new Date(a.created_at).getTime() - new Date(b.created_at).getTime())
      .slice(-7);
    const values = done.map((job) => detectionCount(job) ?? 0);
    const max = Math.max(1, ...values);
    return done.map((job, index) => ({
      label: new Intl.DateTimeFormat("uk-UA", { day: "2-digit", month: "2-digit" }).format(new Date(job.created_at)),
      height: Math.max(8, Math.round((values[index] / max) * 92)),
      value: values[index],
    }));
  }, [jobs]);

  return (
    <section className="av-card p-5">
      <div className="mb-4 flex items-center justify-between">
        <h2 className="font-display text-base font-semibold">Виявлення за останні задачі</h2>
        <BarChartIcon className="h-4 w-4 text-muted-foreground" />
      </div>
      {points.length === 0 ? (
        <EmptyState title="Даних ще немає" description="Графік з'явиться після першого завершеного завдання." />
      ) : (
        <div className="flex h-36 items-end gap-2">
          {points.map((point, index) => (
            <div className="flex flex-1 flex-col items-center gap-2" key={`${point.label}-${index}`}>
              <div className="flex h-24 w-full items-end rounded bg-secondary/60 px-1">
                <div
                  className="w-full rounded-sm bg-primary/80 transition-all duration-300"
                  style={{ height: `${point.height}%` }}
                  title={`${point.value.toLocaleString("uk-UA")} виявлень`}
                />
              </div>
              <span className="text-[10px] text-muted-foreground">{point.label}</span>
            </div>
          ))}
        </div>
      )}
    </section>
  );
}

function RecentJobsTable({ jobs }: { jobs: JobDetail[] }) {
  const visibleJobs = jobs.slice(0, 5);

  return (
    <section className="av-card overflow-hidden">
      <div className="flex items-center justify-between gap-4 border-b border-border px-5 py-4">
        <h2 className="font-display text-base font-semibold">Останні завдання</h2>
        <Button variant="ghost" size="sm" asChild>
          <Link to="/jobs">
            Усі завдання
            <ChevronRightIcon className="h-3.5 w-3.5" />
          </Link>
        </Button>
      </div>
      {visibleJobs.length === 0 ? (
        <EmptyState
          title="Завдань ще немає"
          description="Завантажте перший файл, щоб створити задачу обробки."
          action={
            <Button size="sm" asChild>
              <Link to="/upload">
                <UploadIcon className="h-3.5 w-3.5" />
                Завантажити
              </Link>
            </Button>
          }
        />
      ) : (
        <div className="overflow-x-auto">
          <table className="w-full min-w-[860px] border-collapse text-sm">
            <thead className="bg-secondary">
              <tr className="text-left text-[11px] uppercase tracking-[0.055em] text-muted-foreground">
                <th className="px-4 py-3 font-semibold">Статус</th>
                <th className="px-4 py-3 font-semibold">Файл</th>
                <th className="px-4 py-3 font-semibold">Тип</th>
                <th className="px-4 py-3 font-semibold">Модель</th>
                <th className="px-4 py-3 font-semibold">Дата</th>
                <th className="px-4 py-3 font-semibold">Виявлень</th>
                <th className="px-4 py-3 font-semibold">Час</th>
                <th className="px-4 py-3" />
              </tr>
            </thead>
            <tbody>
              {visibleJobs.map((job) => (
                <tr className="border-t border-border/70 transition hover:bg-secondary/45" key={job.id}>
                  <td className="px-4 py-3">
                    <StatusBadge status={job.status} />
                  </td>
                  <td className="px-4 py-3">
                    <div className="flex items-center gap-2">
                      {job.media.media_type === "video" ? (
                        <VideoIcon className="h-4 w-4 shrink-0 text-muted-foreground" />
                      ) : (
                        <ImageIcon className="h-4 w-4 shrink-0 text-muted-foreground" />
                      )}
                      <span className="max-w-[220px] truncate font-mono text-xs">{job.media.original_filename}</span>
                    </div>
                  </td>
                  <td className="px-4 py-3 text-muted-foreground">
                    {job.media.media_type === "video" ? "Відео" : "Зображення"}
                  </td>
                  <td className="px-4 py-3 font-mono text-xs text-muted-foreground">
                    {job.model ? job.model.name : EMPTY_VALUE}
                  </td>
                  <td className="whitespace-nowrap px-4 py-3 text-muted-foreground">{formatDate(job.created_at)}</td>
                  <td className="px-4 py-3 font-mono">{formatCount(detectionCount(job))}</td>
                  <td className="px-4 py-3 text-muted-foreground">{formatDuration(job)}</td>
                  <td className="px-4 py-3 text-right">
                    <Button variant="ghost" size="sm" asChild>
                      <Link to={`/jobs/${job.id}`}>Відкрити</Link>
                    </Button>
                  </td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>
      )}
    </section>
  );
}

export function DashboardPage() {
  const { user } = useAuth();
  const isAdmin = user?.role === "admin";

  const userJobsQuery = useQuery({
    queryKey: ["dashboard", "jobs", "user"],
    queryFn: getUserDashboardJobs,
    enabled: !isAdmin,
  });
  const adminStatsQuery = useQuery({
    queryKey: ["dashboard", "admin", "stats"],
    queryFn: getAdminDashboardStats,
    enabled: isAdmin,
  });
  const adminJobsQuery = useQuery({
    queryKey: ["dashboard", "admin", "jobs"],
    queryFn: getAdminDashboardJobs,
    enabled: isAdmin,
  });
  const activeModelQuery = useQuery({
    queryKey: ["dashboard", "models", "active"],
    queryFn: getActiveModels,
  });

  const jobsResponse: JobListResponse | undefined = isAdmin ? adminJobsQuery.data : userJobsQuery.data;
  const jobs = jobsResponse?.items ?? [];
  const activeModel = activeModelQuery.data?.items[0];
  const stats = isAdmin ? buildAdminStats(adminStatsQuery.data) : buildUserStats(jobs);
  const isLoading =
    activeModelQuery.isLoading || (isAdmin ? adminStatsQuery.isLoading || adminJobsQuery.isLoading : userJobsQuery.isLoading);
  const isError =
    activeModelQuery.isError || (isAdmin ? adminStatsQuery.isError || adminJobsQuery.isError : userJobsQuery.isError);

  const retry = () => {
    void activeModelQuery.refetch();
    if (isAdmin) {
      void adminStatsQuery.refetch();
      void adminJobsQuery.refetch();
    } else {
      void userJobsQuery.refetch();
    }
  };

  if (isLoading) return <DashboardSkeleton />;
  if (isError) return <ErrorState onRetry={retry} />;

  return (
    <div className="space-y-5">
      <header className="flex flex-col gap-4 sm:flex-row sm:items-start sm:justify-between">
        <div>
          <h1 className="font-display text-2xl font-bold tracking-tight">Огляд</h1>
          <p className="mt-1 text-sm text-muted-foreground">
            {isAdmin ? "Глобальна статистика системи" : "Ваша статистика обробки"}
          </p>
        </div>
        <Button asChild>
          <Link to="/upload">
            <UploadIcon className="h-4 w-4" />
            Завантажити
          </Link>
        </Button>
      </header>

      <section className="grid grid-cols-2 gap-4 lg:grid-cols-4">
        <MetricCard label="Оброблено файлів" value={formatCount(stats.processedFiles)} hint="Завершені завдання" icon={<FileIcon />} />
        <MetricCard label="Виявлено дронів" value={formatCount(stats.totalDetections)} hint="Сумарно" icon={<DashboardIcon />} />
        <MetricCard label="Сер. впевненість" value={formatPercent(stats.avgConfidence)} hint="З доступних підсумків" icon={<ReaderIcon />} />
        <MetricCard label="Середній FPS" value={formatFps(stats.avgFps)} hint="З доступних підсумків" icon={<LightningBoltIcon />} />
      </section>

      <section className="grid gap-4 lg:grid-cols-[280px_minmax(0,1fr)]">
        <ActiveModelPanel model={activeModel} />
        <ActivityPanel jobs={jobs} />
      </section>

      <RecentJobsTable jobs={jobs} />
    </div>
  );
}
