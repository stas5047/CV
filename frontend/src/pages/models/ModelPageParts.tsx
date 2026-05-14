import type { FormEvent, ReactNode } from "react";
import {
  CheckCircledIcon,
  Component1Icon,
  Cross2Icon,
  ExclamationTriangleIcon,
  GearIcon,
  PlusIcon,
  RocketIcon,
} from "@radix-ui/react-icons";
import type { ModelVersion } from "../../api/types";
import { Button } from "../../components/ui/button";
import { Input } from "../../components/ui/input";
import { cn } from "../../lib/utils";
import {
  EMPTY_VALUE,
  formatFps,
  formatMegabytes,
  formatPercent,
  metrics,
  safeText,
  type ModelFormState,
} from "./modelPageUtils";

function MetricBar({ label, value }: { label: string; value: number | null }) {
  const width = value === null ? 0 : Math.max(0, Math.min(100, value > 1 ? value : value * 100));
  return (
    <div>
      <div className="mb-1.5 flex items-center justify-between gap-2">
        <span className="av-label">{label}</span>
        <span className="font-mono text-xs text-muted-foreground">{formatPercent(value)}</span>
      </div>
      <div className="h-1.5 overflow-hidden rounded-full bg-secondary">
        <div className="h-full rounded-full bg-primary transition-[width] duration-500" style={{ width: `${width}%` }} />
      </div>
    </div>
  );
}

export function ModelsSkeleton() {
  return (
    <div className="space-y-5">
      <div className="flex items-start justify-between gap-4">
        <div className="space-y-2">
          <div data-testid="model-skeleton" className="av-skeleton h-7 w-44" />
          <div data-testid="model-skeleton" className="av-skeleton h-4 w-72" />
        </div>
        <div data-testid="model-skeleton" className="av-skeleton h-10 w-44" />
      </div>
      {Array.from({ length: 3 }).map((_, index) => (
        <div data-testid="model-skeleton" className="av-card p-5" key={index}>
          <div className="av-skeleton h-28 w-full" />
        </div>
      ))}
    </div>
  );
}

export function EmptyState({ title, description, action }: { title: string; description: string; action?: ReactNode }) {
  return (
    <section className="av-card flex min-h-60 flex-col items-center justify-center gap-3 px-5 py-10 text-center">
      <Component1Icon className="h-8 w-8 text-muted-foreground/45" />
      <div>
        <p className="font-display text-lg font-semibold text-foreground">{title}</p>
        <p className="mt-1 max-w-md text-sm leading-6 text-muted-foreground">{description}</p>
      </div>
      {action ? <div className="mt-2">{action}</div> : null}
    </section>
  );
}

export function ErrorState({ onRetry }: { onRetry: () => void }) {
  return (
    <section className="av-card border-destructive/25 bg-destructive/10 p-5">
      <div className="flex flex-col gap-4 sm:flex-row sm:items-center sm:justify-between">
        <div className="flex gap-3">
          <ExclamationTriangleIcon className="mt-1 h-5 w-5 shrink-0 text-red-200" />
          <div>
            <h1 className="font-display text-xl font-semibold">Не вдалося завантажити моделі</h1>
            <p className="mt-1 text-sm text-red-100/75">Перевірте з'єднання з сервером та повторіть запит.</p>
          </div>
        </div>
        <Button variant="secondary" onClick={onRetry}>Повторити</Button>
      </div>
    </section>
  );
}

export function ModelCard({
  model,
  isAdmin,
  isActivating,
  onActivate,
}: {
  model: ModelVersion;
  isAdmin: boolean;
  isActivating: boolean;
  onActivate: (modelId: string) => void;
}) {
  const modelMetrics = metrics(model);
  const isFallback = model.model_family === "YOLO11";

  return (
    <article
      data-testid={`model-card-${model.id}`}
      className={cn(
        "av-card overflow-hidden border-l-2 p-5 transition duration-300 hover:-translate-y-0.5",
        model.is_active ? "border-l-primary" : "border-l-transparent",
      )}
    >
      <div className="flex flex-col gap-4 lg:flex-row lg:items-start lg:justify-between">
        <div className="flex min-w-0 gap-3">
          <div className={cn("grid h-10 w-10 shrink-0 place-items-center rounded-md", model.is_active ? "bg-primary/10 text-accent-foreground" : "bg-secondary text-muted-foreground")}>
            {model.is_active ? <RocketIcon className="h-5 w-5" /> : <GearIcon className="h-5 w-5" />}
          </div>
          <div className="min-w-0">
            <div className="flex flex-wrap items-center gap-2">
              <h2 className="font-mono text-sm font-semibold text-foreground">{safeText(model.name)}</h2>
              {model.is_active ? (
                <span className="rounded-full bg-emerald-500/10 px-2 py-0.5 text-[10px] font-semibold uppercase tracking-[0.05em] text-emerald-200">
                  Активна
                </span>
              ) : null}
              {isFallback ? (
                <span className="rounded bg-secondary px-2 py-0.5 text-[11px] text-muted-foreground">Документований fallback</span>
              ) : null}
            </div>
            <p className="mt-1 text-sm text-muted-foreground">{safeText(model.dataset_name)}</p>
            <p className="mt-1 text-xs text-muted-foreground">{safeText(model.dataset_split_description)}</p>
          </div>
        </div>
        <div className="flex flex-col gap-3 sm:flex-row sm:items-center lg:justify-end">
          <div className="text-left font-mono text-xs text-muted-foreground sm:text-right">
            <div>{model.model_family} · {safeText(model.variant)}</div>
            <div>{formatMegabytes(modelMetrics.size)} · {formatFps(modelMetrics.fps)}</div>
          </div>
          {isAdmin && !model.is_active ? (
            <Button variant="secondary" size="sm" disabled={isActivating} onClick={() => onActivate(model.id)}>
              <CheckCircledIcon className="h-3.5 w-3.5" />
              {isActivating ? "Активація" : "Активувати"}
            </Button>
          ) : null}
        </div>
      </div>

      <div className="mt-5 grid gap-4 sm:grid-cols-2 xl:grid-cols-4">
        <MetricBar label="mAP@50" value={modelMetrics.map50} />
        <MetricBar label="mAP@50-95" value={modelMetrics.map5095} />
        <MetricBar label="Точність" value={modelMetrics.precision} />
        <MetricBar label="Повнота" value={modelMetrics.recall} />
      </div>
    </article>
  );
}

export function ModelForm({
  form,
  error,
  isSubmitting,
  onChange,
  onClose,
  onSubmit,
}: {
  form: ModelFormState;
  error: string | null;
  isSubmitting: boolean;
  onChange: (next: ModelFormState) => void;
  onClose: () => void;
  onSubmit: (event: FormEvent<HTMLFormElement>) => void;
}) {
  return (
    <form className="av-card p-5" onSubmit={onSubmit}>
      <div className="mb-5 flex items-start justify-between gap-4">
        <div>
          <h2 className="font-display text-lg font-semibold">Нова модель</h2>
          <p className="mt-1 text-sm text-muted-foreground">Використовуйте наявний шлях у спільному сховищі моделей.</p>
        </div>
        <Button type="button" variant="ghost" size="icon" aria-label="Закрити форму" onClick={onClose}>
          <Cross2Icon className="h-4 w-4" />
        </Button>
      </div>
      <div className="grid gap-4 lg:grid-cols-3">
        <label className="flex flex-col gap-2">
          <span className="av-label">Назва моделі</span>
          <Input value={form.name} onChange={(event) => onChange({ ...form, name: event.target.value })} required />
        </label>
        <label className="flex flex-col gap-2">
          <span className="av-label">Сімейство</span>
          <select className="av-input" value={form.model_family} onChange={(event) => onChange({ ...form, model_family: event.target.value as "YOLO26" | "YOLO11" })}>
            <option value="YOLO26">YOLO26</option>
            <option value="YOLO11">YOLO11</option>
          </select>
        </label>
        <label className="flex flex-col gap-2">
          <span className="av-label">Варіант</span>
          <Input value={form.variant} onChange={(event) => onChange({ ...form, variant: event.target.value })} required />
        </label>
        <label className="flex flex-col gap-2 lg:col-span-2">
          <span className="av-label">Відносний шлях до ваг</span>
          <Input value={form.weights_path} onChange={(event) => onChange({ ...form, weights_path: event.target.value })} required placeholder="models/yolo26s-seraphim-v1/weights.pt" />
          <span className="text-xs text-muted-foreground">Без абсолютного шляху, диска Windows або сегментів ..</span>
        </label>
        <label className="flex flex-col gap-2">
          <span className="av-label">Датасет</span>
          <Input value={form.dataset_name} onChange={(event) => onChange({ ...form, dataset_name: event.target.value })} />
        </label>
        <label className="flex flex-col gap-2 lg:col-span-3">
          <span className="av-label">Опис split</span>
          <Input value={form.dataset_split_description} onChange={(event) => onChange({ ...form, dataset_split_description: event.target.value })} />
        </label>
      </div>
      {error ? <p className="mt-4 text-sm text-red-200">{error}</p> : null}
      <div className="mt-5 flex flex-wrap gap-2">
        <Button type="submit" disabled={isSubmitting}>
          <PlusIcon className="h-4 w-4" />
          {isSubmitting ? "Збереження" : "Зберегти модель"}
        </Button>
        <Button type="button" variant="secondary" onClick={onClose}>Скасувати</Button>
      </div>
    </form>
  );
}

export function Header({ isAdmin, onToggleForm }: { isAdmin: boolean; onToggleForm: () => void }) {
  return (
    <header className="grid gap-4 md:grid-cols-[minmax(0,1fr)_auto] md:items-start">
      <div>
        <p className="av-label">Реєстр YOLO</p>
        <h1 className="mt-2 font-display text-2xl font-bold tracking-tight">Реєстр моделей</h1>
        <p className="mt-1 max-w-2xl text-sm leading-6 text-muted-foreground">Зареєстровані версії моделей виявлення, активний вибір для запуску та метрики навчання.</p>
      </div>
      {isAdmin ? (
        <Button onClick={onToggleForm}>
          <PlusIcon className="h-4 w-4" />
          Зареєструвати модель
        </Button>
      ) : null}
    </header>
  );
}

export function SummaryStrip({ models }: { models: ModelVersion[] }) {
  const activeModel = models.find((model) => model.is_active);
  const fallbackCount = models.filter((model) => model.model_family === "YOLO11").length;
  return (
    <section className="grid gap-4 md:grid-cols-[1.4fr_1fr_1fr]">
      <div className="av-card p-5">
        <div className="flex items-center gap-3">
          <RocketIcon className="h-5 w-5 text-accent-foreground" />
          <div>
            <p className="av-label">Активна модель</p>
            <p className="mt-1 font-mono text-sm text-foreground">{activeModel ? safeText(activeModel.name) : EMPTY_VALUE}</p>
          </div>
        </div>
      </div>
      <div className="av-card p-5">
        <p className="av-label">У реєстрі</p>
        <p className="mt-2 font-mono text-2xl font-semibold">{models.length.toLocaleString("uk-UA")}</p>
      </div>
      <div className="av-card p-5">
        <p className="av-label">Fallback YOLO11</p>
        <p className="mt-2 font-mono text-2xl font-semibold">{fallbackCount.toLocaleString("uk-UA")}</p>
      </div>
    </section>
  );
}

export function ModelList({
  models,
  isAdmin,
  activatingId,
  onActivate,
}: {
  models: ModelVersion[];
  isAdmin: boolean;
  activatingId: string | null;
  onActivate: (modelId: string) => void;
}) {
  return (
    <div className="flex flex-col gap-3">
      {models.map((model) => (
        <ModelCard
          key={model.id}
          model={model}
          isAdmin={isAdmin}
          isActivating={activatingId === model.id}
          onActivate={onActivate}
        />
      ))}
    </div>
  );
}
