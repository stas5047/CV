import { useMemo, useState, type ReactNode } from "react";
import { useMutation } from "@tanstack/react-query";
import {
  BarChartIcon,
  Component1Icon,
  DashboardIcon,
  ExclamationTriangleIcon,
  ImageIcon,
  LockClosedIcon,
  ReaderIcon,
  RocketIcon,
  VideoIcon,
} from "@radix-ui/react-icons";
import { Link } from "react-router-dom";
import { cleanupStorage } from "../../api/admin";
import type { AdminStatsResponse, JobDetail, StorageCleanupResponse, User } from "../../api/types";
import { useToast } from "../../components/toast";
import { Button } from "../../components/ui/button";
import { cn } from "../../lib/utils";
import {
  detectionCount,
  formatDate,
  formatDuration,
  formatPercent,
  safeText,
} from "../jobs/jobFormatters";

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

function formatCount(value: number | null | undefined) {
  return typeof value === "number" && Number.isFinite(value) ? value.toLocaleString("uk-UA") : EMPTY_VALUE;
}

function StatusBadge({ status }: { status: string }) {
  return (
    <span className={cn("inline-flex items-center gap-1.5 rounded-full px-2.5 py-1 text-[11px] font-medium", statusClasses[status] ?? statusClasses.queued)}>
      <span className={cn("h-1.5 w-1.5 rounded-full bg-current", status === "processing" && "animate-pulse")} />
      {statusLabels[status] ?? "Невідомо"}
    </span>
  );
}

export function PageSkeleton() {
  return (
    <div className="space-y-5">
      <div className="space-y-2">
        <div className="av-skeleton h-7 w-52" />
        <div className="av-skeleton h-4 w-96 max-w-full" />
      </div>
      <div className="grid grid-cols-2 gap-4 lg:grid-cols-4">
        {Array.from({ length: 4 }).map((_, index) => (
          <div className="av-card space-y-4 p-5" key={index}>
            <div className="av-skeleton h-3 w-24" />
            <div className="av-skeleton h-7 w-16" />
            <div className="av-skeleton h-3 w-28" />
          </div>
        ))}
      </div>
      <div className="grid gap-4 xl:grid-cols-[minmax(0,1fr)_320px]">
        <div className="av-card p-5"><div className="av-skeleton h-56 w-full" /></div>
        <div className="av-card p-5"><div className="av-skeleton h-56 w-full" /></div>
      </div>
    </div>
  );
}

export function ErrorState({ onRetry }: { onRetry: () => void }) {
  return (
    <section className="av-card border-destructive/25 bg-destructive/10 p-5">
      <div className="flex flex-col gap-4 sm:flex-row sm:items-center sm:justify-between">
        <div className="flex gap-3">
          <ExclamationTriangleIcon className="mt-1 h-5 w-5 shrink-0 text-red-200" />
          <div>
            <h1 className="font-display text-xl font-semibold">Не вдалося завантажити адмін-дані</h1>
            <p className="mt-1 text-sm text-red-100/75">Перевірте з'єднання з API бекенду та повторіть запит.</p>
          </div>
        </div>
        <Button variant="secondary" onClick={onRetry}>Повторити</Button>
      </div>
    </section>
  );
}

export function MetricCard({ label, value, hint, icon }: { label: string; value: string; hint: string; icon: ReactNode }) {
  return (
    <section className="av-card p-5 transition duration-300 hover:-translate-y-0.5">
      <div className="flex items-start justify-between gap-3">
        <span className="av-label">{label}</span>
        <span className="text-muted-foreground/60">{icon}</span>
      </div>
      <div className="mt-4 font-display text-2xl font-bold leading-none text-foreground md:text-[28px]">{value}</div>
      <p className="mt-2 text-xs text-muted-foreground">{hint}</p>
    </section>
  );
}

function EmptyState({ title, description }: { title: string; description?: string }) {
  return (
    <div className="flex min-h-44 flex-col items-center justify-center gap-3 px-5 py-10 text-center">
      <Component1Icon className="h-7 w-7 text-muted-foreground/40" />
      <div>
        <p className="font-medium text-foreground">{title}</p>
        {description ? <p className="mt-1 max-w-md text-sm leading-6 text-muted-foreground">{description}</p> : null}
      </div>
    </div>
  );
}

function mediaLabel(mediaType: string) {
  return mediaType === "video" ? "Відео" : "Зображення";
}

function mediaIcon(mediaType: string) {
  return mediaType === "video" ? <VideoIcon className="h-4 w-4 shrink-0 text-muted-foreground" /> : <ImageIcon className="h-4 w-4 shrink-0 text-muted-foreground" />;
}

export function RecentJobs({ jobs }: { jobs: JobDetail[] }) {
  return (
    <section className="av-card overflow-hidden">
      <div className="flex items-center justify-between gap-4 border-b border-border px-5 py-4">
        <div>
          <h2 className="font-display text-base font-semibold">Останні глобальні завдання</h2>
          <p className="mt-1 text-xs text-muted-foreground">Усі користувачі, останні записи обробки</p>
        </div>
        <Button variant="ghost" size="sm" asChild><Link to="/jobs">Усі завдання</Link></Button>
      </div>
      {jobs.length === 0 ? (
        <EmptyState title="Глобальних завдань ще немає" description="Коли користувачі створять обробку, вона з'явиться тут." />
      ) : (
        <div className="overflow-x-auto">
          <table className="w-full min-w-[820px] border-collapse text-sm">
            <thead className="bg-secondary">
              <tr className="text-left text-[11px] uppercase tracking-[0.055em] text-muted-foreground">
                <th className="px-4 py-3 font-semibold">Статус</th>
                <th className="px-4 py-3 font-semibold">Файл</th>
                <th className="px-4 py-3 font-semibold">Тип</th>
                <th className="px-4 py-3 font-semibold">Модель</th>
                <th className="px-4 py-3 font-semibold">Дата</th>
                <th className="px-4 py-3 font-semibold">Виявлень</th>
                <th className="px-4 py-3 font-semibold">Час</th>
              </tr>
            </thead>
            <tbody>
              {jobs.map((item) => (
                <tr className="border-t border-border/70 transition hover:bg-secondary/45" key={item.id}>
                  <td className="px-4 py-3"><StatusBadge status={item.status} /></td>
                  <td className="px-4 py-3">
                    <div className="flex items-center gap-2">
                      {mediaIcon(item.media.media_type)}
                      <span className="max-w-[220px] truncate font-mono text-xs">{safeText(item.media.original_filename)}</span>
                    </div>
                  </td>
                  <td className="px-4 py-3 text-muted-foreground">{mediaLabel(item.media.media_type)}</td>
                  <td className="px-4 py-3 font-mono text-xs text-muted-foreground">{item.model ? safeText(item.model.name) : EMPTY_VALUE}</td>
                  <td className="whitespace-nowrap px-4 py-3 text-muted-foreground">{formatDate(item.created_at)}</td>
                  <td className="px-4 py-3 font-mono">{formatCount(detectionCount(item))}</td>
                  <td className="px-4 py-3 text-muted-foreground">{formatDuration(item)}</td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>
      )}
    </section>
  );
}

export function Shortcuts() {
  return (
    <section className="av-card p-5">
      <h2 className="font-display text-base font-semibold">Управління системою</h2>
      <p className="mt-1 text-xs text-muted-foreground">Швидкі переходи до адміністративних робочих зон.</p>
      <div className="mt-5 grid gap-3">
        <Button variant="secondary" className="justify-start" asChild><Link to="/models"><RocketIcon className="h-4 w-4" />Реєстр моделей</Link></Button>
        <Button variant="secondary" className="justify-start" asChild><Link to="/experiments"><BarChartIcon className="h-4 w-4" />Імпорт метрик</Link></Button>
      </div>
    </section>
  );
}

function cleanupLine(label: string, value: number) {
  return (
    <div className="flex items-center justify-between gap-3 text-sm">
      <span className="text-muted-foreground">{label}: {formatCount(value)}</span>
    </div>
  );
}

export function CleanupPanel() {
  const [confirmed, setConfirmed] = useState(false);
  const [result, setResult] = useState<StorageCleanupResponse | null>(null);
  const { toast } = useToast();
  const mutation = useMutation({
    mutationFn: cleanupStorage,
    onSuccess: (data) => {
      setResult(data);
      if (data.dry_run) setConfirmed(false);
      toast({
        variant: "success",
        title: data.dry_run ? "Перевірку сховища завершено" : "Очищення сховища завершено",
        description: data.dry_run ? "Перегляньте підсумок перед підтвердженням." : "Захищені файли залишено без змін.",
      });
    },
    onError: () => {
      toast({
        variant: "error",
        title: "Очищення не вдалося",
        description: "Повторіть запит після перевірки сервера.",
      });
    },
  });
  const canConfirm = Boolean(result?.dry_run) && confirmed && !mutation.isPending;

  return (
    <section className="av-card p-5" data-testid="cleanup-panel">
      <div className="flex items-start gap-3">
        <div className="grid h-9 w-9 shrink-0 place-items-center rounded-md bg-destructive/10 text-red-200"><LockClosedIcon className="h-4 w-4" /></div>
        <div>
          <h2 className="font-display text-base font-semibold">Безпечне очищення сховища</h2>
          <p className="mt-1 text-xs leading-5 text-muted-foreground">Спершу виконується перевірка. Активні моделі, видимі результати та файли з посиланнями в базі не видаляються.</p>
        </div>
      </div>
      {mutation.isError ? <div className="mt-4 rounded-md border border-destructive/25 bg-destructive/10 p-3 text-sm text-red-100/80">Не вдалося виконати очищення. Повторіть запит після перевірки сервера.</div> : null}
      {result ? (
        <div className="mt-4 space-y-2 rounded-md border border-border bg-secondary/45 p-3">
          {result.dry_run ? (
            <>
              {cleanupLine("Перевірено файлів", result.scanned_files)}
              {cleanupLine("Можна видалити", result.would_delete_files)}
              {cleanupLine("Захищено", result.protected_files)}
              {cleanupLine("Потребують звіту", result.reported_files)}
            </>
          ) : (
            <>
              {cleanupLine("Видалено файлів", result.deleted_files)}
              {cleanupLine("Захищено", result.protected_files)}
              {cleanupLine("Пропущено", result.skipped_files)}
            </>
          )}
        </div>
      ) : null}
      <div className="mt-5 flex flex-col gap-3">
        <Button variant="secondary" onClick={() => mutation.mutate({ dry_run: true })} disabled={mutation.isPending}>
          {mutation.isPending ? "Перевіряється..." : "Перевірити сховище"}
        </Button>
        {result?.dry_run ? (
          <label className="flex items-center gap-2 text-sm text-muted-foreground">
            <input className="h-4 w-4 accent-primary" type="checkbox" checked={confirmed} onChange={(event) => setConfirmed(event.target.checked)} />
            Підтверджую безпечне очищення
          </label>
        ) : null}
        <Button variant="danger" onClick={() => mutation.mutate({ dry_run: false })} disabled={!canConfirm}>Підтвердити очищення</Button>
      </div>
    </section>
  );
}

function roleLabel(role: User["role"]) {
  return role === "admin" ? "Адмін" : "Користувач";
}

export function UsersTable({ users }: { users: User[] }) {
  return (
    <section className="av-card overflow-hidden">
      <div className="border-b border-border px-5 py-4">
        <h2 className="font-display text-base font-semibold">Користувачі системи</h2>
        <p className="mt-1 text-xs text-muted-foreground">Базовий список без керування обліковими записами.</p>
      </div>
      {users.length === 0 ? (
        <EmptyState title="Користувачів не знайдено" description="Список стане доступним після створення облікових записів." />
      ) : (
        <div className="overflow-x-auto">
          <table className="w-full min-w-[680px] border-collapse text-sm">
            <thead className="bg-secondary">
              <tr className="text-left text-[11px] uppercase tracking-[0.055em] text-muted-foreground">
                <th className="px-4 py-3 font-semibold">Email</th>
                <th className="px-4 py-3 font-semibold">Роль</th>
                <th className="px-4 py-3 font-semibold">Стан</th>
                <th className="px-4 py-3 font-semibold">Створено</th>
              </tr>
            </thead>
            <tbody>
              {users.map((item) => (
                <tr className="border-t border-border/70 transition hover:bg-secondary/45" key={item.id}>
                  <td className="px-4 py-3 font-mono text-xs">{safeText(item.email)}</td>
                  <td className="px-4 py-3">
                    <span className={cn("inline-flex rounded-full px-2.5 py-1 text-[11px] font-medium", item.role === "admin" ? "bg-primary/10 text-accent-foreground" : "bg-secondary text-muted-foreground")}>{roleLabel(item.role)}</span>
                  </td>
                  <td className="px-4 py-3 text-muted-foreground">{item.is_active ? "Активний" : "Вимкнений"}</td>
                  <td className="px-4 py-3 text-muted-foreground">{formatDate(item.created_at)}</td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>
      )}
    </section>
  );
}

export function StatsGrid({ stats }: { stats: AdminStatsResponse }) {
  const cards = useMemo(() => {
    const completed = stats.jobs.by_status.completed ?? 0;
    const completionRate = stats.jobs.total > 0 ? completed / stats.jobs.total : null;
    return [
      { label: "Користувачі", value: formatCount(stats.users.total), hint: `${formatCount(stats.users.active)} активних, ${formatCount(stats.users.admins)} адмін`, icon: <DashboardIcon /> },
      { label: "Завдання", value: formatCount(stats.jobs.total), hint: `Завершено: ${formatCount(completed)}`, icon: <ReaderIcon /> },
      { label: "Виявлення", value: formatCount(stats.detections.total), hint: `Треки: ${formatCount(stats.tracks.total)}`, icon: <Component1Icon /> },
      { label: "Моделі і досліди", value: formatCount(stats.models.total), hint: `Активних моделей: ${formatCount(stats.models.active)} · опубл. дослідів: ${formatCount(stats.experiments.published)}`, icon: <RocketIcon /> },
      { label: "Медіафайли", value: formatCount(stats.media.total), hint: `${formatCount(stats.media.images)} зображень · ${formatCount(stats.media.videos)} відео`, icon: <ImageIcon /> },
      { label: "Частка завершених", value: formatPercent(completionRate), hint: "Від усіх глобальних завдань", icon: <BarChartIcon /> },
    ];
  }, [stats]);

  return (
    <section className="grid grid-cols-2 gap-4 lg:grid-cols-3 xl:grid-cols-6">
      {cards.map((card) => (
        <MetricCard key={card.label} {...card} />
      ))}
    </section>
  );
}
