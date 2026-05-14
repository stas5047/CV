import { useEffect, useMemo, useState } from "react";
import { useQuery } from "@tanstack/react-query";
import { EyeOpenIcon, MagnifyingGlassIcon, UploadIcon } from "@radix-ui/react-icons";
import { Link } from "react-router-dom";
import { listJobFilterModels, listJobs } from "../api/jobs";
import { Button } from "../components/ui/button";
import { Input } from "../components/ui/input";
import {
  averageConfidence,
  detectionCount,
  EMPTY_VALUE,
  formatCount,
  formatDate,
  formatDuration,
  formatPercent,
  mediaTypeLabels,
  safeText,
} from "./jobs/jobFormatters";
import { EmptyState, ErrorState, MediaIcon, StatusBadge, TableSkeleton } from "./jobs/JobPageParts";

const PAGE_SIZE = 10;

export function JobsPage() {
  const [status, setStatus] = useState("");
  const [mediaType, setMediaType] = useState("");
  const [modelVersionId, setModelVersionId] = useState("");
  const [createdFrom, setCreatedFrom] = useState("");
  const [createdTo, setCreatedTo] = useState("");
  const [search, setSearch] = useState("");
  const [page, setPage] = useState(0);

  useEffect(() => {
    setPage(0);
  }, [status, mediaType, modelVersionId, createdFrom, createdTo]);

  const modelsQuery = useQuery({
    queryKey: ["jobs-filter-models"],
    queryFn: listJobFilterModels,
  });

  const jobsQuery = useQuery({
    queryKey: ["jobs", { status, mediaType, modelVersionId, createdFrom, createdTo, page }],
    queryFn: () =>
      listJobs({
        limit: PAGE_SIZE,
        offset: page * PAGE_SIZE,
        status: status || undefined,
        media_type: mediaType || undefined,
        model_version_id: modelVersionId || undefined,
        created_from: createdFrom || undefined,
        created_to: createdTo || undefined,
      }),
  });

  const models = modelsQuery.data?.items ?? [];
  const jobs = useMemo(() => jobsQuery.data?.items ?? [], [jobsQuery.data?.items]);
  const visibleJobs = useMemo(() => {
    const needle = search.trim().toLocaleLowerCase("uk-UA");
    if (!needle) return jobs;
    return jobs.filter((job) => job.media.original_filename.toLocaleLowerCase("uk-UA").includes(needle));
  }, [jobs, search]);
  const total = jobsQuery.data?.total ?? 0;
  const pageCount = Math.max(1, Math.ceil(total / PAGE_SIZE));

  if (jobsQuery.isLoading) return <TableSkeleton />;
  if (jobsQuery.isError) {
    return (
      <ErrorState
        title="Не вдалося завантажити завдання"
        description="Перевірте з'єднання з сервером та повторіть запит."
        onRetry={() => void jobsQuery.refetch()}
      />
    );
  }

  return (
    <div className="space-y-5">
      <header className="flex flex-col gap-4 sm:flex-row sm:items-start sm:justify-between">
        <div>
          <h1 className="font-display text-2xl font-bold tracking-tight">Черга завдань</h1>
          <p className="mt-1 text-sm text-muted-foreground">Історія обробки ваших медіафайлів</p>
        </div>
        <Button asChild>
          <Link to="/upload">
            <UploadIcon className="h-4 w-4" />
            Нове завдання
          </Link>
        </Button>
      </header>

      <section className="av-card p-4">
        <div className="grid gap-3 lg:grid-cols-[minmax(220px,1fr)_150px_140px_180px_150px_150px]">
          <label className="space-y-2">
            <span className="av-label">Пошук на цій сторінці</span>
            <span className="relative block">
              <MagnifyingGlassIcon className="pointer-events-none absolute left-3 top-1/2 h-4 w-4 -translate-y-1/2 text-muted-foreground" />
              <Input className="pl-9" value={search} onChange={(event) => setSearch(event.target.value)} placeholder="Назва файлу" />
            </span>
          </label>
          <label className="space-y-2">
            <span className="av-label">Статус</span>
            <select className="av-input" value={status} onChange={(event) => setStatus(event.target.value)}>
              <option value="">Усі</option>
              <option value="queued">У черзі</option>
              <option value="processing">Обробляється</option>
              <option value="completed">Завершено</option>
              <option value="failed">Збій</option>
              <option value="cancelled">Скасовано</option>
            </select>
          </label>
          <label className="space-y-2">
            <span className="av-label">Тип</span>
            <select className="av-input" value={mediaType} onChange={(event) => setMediaType(event.target.value)}>
              <option value="">Усі</option>
              <option value="image">Зображення</option>
              <option value="video">Відео</option>
            </select>
          </label>
          <label className="space-y-2">
            <span className="av-label">Модель</span>
            <select className="av-input" value={modelVersionId} onChange={(event) => setModelVersionId(event.target.value)}>
              <option value="">Усі</option>
              {models.map((model) => (
                <option key={model.id} value={model.id}>
                  {safeText(model.name)}
                </option>
              ))}
            </select>
          </label>
          <label className="space-y-2">
            <span className="av-label">Від дати</span>
            <Input type="date" value={createdFrom} onChange={(event) => setCreatedFrom(event.target.value)} />
          </label>
          <label className="space-y-2">
            <span className="av-label">До дати</span>
            <Input type="date" value={createdTo} onChange={(event) => setCreatedTo(event.target.value)} />
          </label>
        </div>
      </section>

      <section className="av-card overflow-hidden">
        {jobs.length === 0 ? (
          <EmptyState
            title="Завдань ще немає"
            description="Завантажте перший файл, щоб створити завдання обробки."
            action={
              <Button size="sm" asChild>
                <Link to="/upload">
                  <UploadIcon className="h-3.5 w-3.5" />
                  Завантажити
                </Link>
              </Button>
            }
          />
        ) : visibleJobs.length === 0 ? (
          <EmptyState title="Нічого не знайдено" description="Пошук працює тільки в межах поточної сторінки результатів." />
        ) : (
          <div className="overflow-x-auto">
            <table className="w-full min-w-[980px] border-collapse text-sm">
              <thead className="bg-secondary">
                <tr className="text-left text-[11px] uppercase tracking-[0.055em] text-muted-foreground">
                  <th className="px-4 py-3 font-semibold">Статус</th>
                  <th className="px-4 py-3 font-semibold">Файл</th>
                  <th className="px-4 py-3 font-semibold">Тип</th>
                  <th className="px-4 py-3 font-semibold">Модель</th>
                  <th className="px-4 py-3 font-semibold">Дата</th>
                  <th className="px-4 py-3 font-semibold">Тривалість</th>
                  <th className="px-4 py-3 font-semibold">Виявлень</th>
                  <th className="px-4 py-3 font-semibold">Впевненість</th>
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
                        <MediaIcon mediaType={job.media.media_type} />
                        <span className="max-w-[240px] truncate font-mono text-xs">{safeText(job.media.original_filename)}</span>
                      </div>
                    </td>
                    <td className="px-4 py-3 text-muted-foreground">{mediaTypeLabels[job.media.media_type] ?? EMPTY_VALUE}</td>
                    <td className="px-4 py-3 font-mono text-xs text-muted-foreground">{job.model ? safeText(job.model.name) : EMPTY_VALUE}</td>
                    <td className="whitespace-nowrap px-4 py-3 text-muted-foreground">{formatDate(job.created_at)}</td>
                    <td className="px-4 py-3 text-muted-foreground">{formatDuration(job)}</td>
                    <td className="px-4 py-3 font-mono">{formatCount(detectionCount(job))}</td>
                    <td className="px-4 py-3 font-mono">{formatPercent(averageConfidence(job))}</td>
                    <td className="px-4 py-3 text-right">
                      <Button variant="ghost" size="sm" asChild>
                        <Link to={`/jobs/${job.id}`}>
                          <EyeOpenIcon className="h-3.5 w-3.5" />
                          Відкрити
                        </Link>
                      </Button>
                    </td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
        )}
      </section>

      {total > 0 ? (
        <div className="flex flex-col gap-3 text-sm text-muted-foreground sm:flex-row sm:items-center sm:justify-between">
          <span>
            Показано {Math.min(page * PAGE_SIZE + 1, total).toLocaleString("uk-UA")}-
            {Math.min((page + 1) * PAGE_SIZE, total).toLocaleString("uk-UA")} із {total.toLocaleString("uk-UA")}
          </span>
          <div className="flex items-center gap-2">
            <Button variant="secondary" size="sm" disabled={page === 0} onClick={() => setPage((value) => Math.max(0, value - 1))}>
              Назад
            </Button>
            <span className="font-mono text-xs">
              {page + 1} / {pageCount}
            </span>
            <Button variant="secondary" size="sm" disabled={page + 1 >= pageCount} onClick={() => setPage((value) => value + 1)}>
              Далі
            </Button>
          </div>
        </div>
      ) : null}
    </div>
  );
}
