import type { ReactNode } from "react";
import {
  Bar,
  BarChart,
  CartesianGrid,
  Legend,
  Line,
  LineChart,
  ResponsiveContainer,
  Tooltip,
  XAxis,
  YAxis,
} from "recharts";
import {
  BarChartIcon,
  Component1Icon,
  ExclamationTriangleIcon,
  InfoCircledIcon,
  LightningBoltIcon,
  MixerHorizontalIcon,
} from "@radix-ui/react-icons";
import { Button } from "../../components/ui/button";
import { cn } from "../../lib/utils";
import {
  EMPTY_VALUE,
  EXPERIMENT_EMPTY_TEXT,
  formatFps,
  formatMs,
  formatNumber,
  formatPercent,
  type ModelComparisonRow,
  type PerformanceRow,
  type ThresholdRow,
  type TrackerRow,
} from "./experimentPageUtils";

type TabId = "models" | "threshold" | "trackers" | "fp";

const tabs: { id: TabId; label: string }[] = [
  { id: "models", label: "Порівняння моделей" },
  { id: "threshold", label: "Поріг впевненості" },
  { id: "trackers", label: "tracker behavior comparison" },
  { id: "fp", label: "Хибнопозитивні" },
];

export function ExperimentsHeader() {
  return (
    <header className="grid gap-4 md:grid-cols-[minmax(0,1fr)_auto] md:items-start">
      <div>
        <p className="av-label">Метрики навчання</p>
        <h1 className="mt-2 font-display text-2xl font-bold tracking-tight">Досліди та метрики</h1>
        <p className="mt-1 max-w-2xl text-sm leading-6 text-muted-foreground">
          Імпортовані результати експериментів для порівняння моделей, порогів, трекерів і хибнопозитивних випадків.
        </p>
      </div>
      <div className="av-card px-4 py-3 text-sm text-muted-foreground">
        <div className="flex items-center gap-2">
          <LightningBoltIcon className="h-4 w-4 text-accent-foreground" />
          <span>Recharts / YOLO / FPS</span>
        </div>
      </div>
    </header>
  );
}

export function ExperimentsTabs({ active, onChange }: { active: TabId; onChange: (tab: TabId) => void }) {
  return (
    <div className="flex gap-2 overflow-x-auto rounded-md border border-border bg-card p-1">
      {tabs.map((tab) => (
        <button
          key={tab.id}
          type="button"
          className={cn(
            "shrink-0 rounded px-3 py-2 text-sm text-muted-foreground transition active:scale-[0.98]",
            active === tab.id ? "bg-secondary text-foreground" : "hover:bg-secondary/70 hover:text-foreground",
          )}
          onClick={() => onChange(tab.id)}
        >
          {tab.label}
        </button>
      ))}
    </div>
  );
}

export function ExperimentsSkeleton() {
  return (
    <div className="space-y-5">
      <div className="space-y-2">
        <div data-testid="experiment-skeleton" className="av-skeleton h-7 w-64" />
        <div data-testid="experiment-skeleton" className="av-skeleton h-4 w-96 max-w-full" />
      </div>
      <div data-testid="experiment-skeleton" className="av-skeleton h-11 w-full" />
      <div className="grid gap-4 lg:grid-cols-[1.2fr_0.8fr]">
        <div data-testid="experiment-skeleton" className="av-card p-5"><div className="av-skeleton h-72" /></div>
        <div data-testid="experiment-skeleton" className="av-card p-5"><div className="av-skeleton h-72" /></div>
      </div>
    </div>
  );
}

export function ExperimentsError({ onRetry }: { onRetry: () => void }) {
  return (
    <section className="av-card border-destructive/25 bg-destructive/10 p-5">
      <div className="flex flex-col gap-4 sm:flex-row sm:items-center sm:justify-between">
        <div className="flex gap-3">
          <ExclamationTriangleIcon className="mt-1 h-5 w-5 shrink-0 text-red-200" />
          <div>
            <h1 className="font-display text-xl font-semibold">Не вдалося завантажити досліди</h1>
            <p className="mt-1 text-sm text-red-100/75">Перевірте з'єднання з сервером та повторіть запит.</p>
          </div>
        </div>
        <Button variant="secondary" onClick={onRetry}>Повторити</Button>
      </div>
    </section>
  );
}

export function SectionEmpty() {
  return (
    <div className="flex min-h-52 flex-col items-center justify-center gap-3 px-5 py-10 text-center text-muted-foreground">
      <Component1Icon className="h-8 w-8 opacity-45" />
      <p className="text-sm">{EXPERIMENT_EMPTY_TEXT}</p>
    </div>
  );
}

export function MetricCards({ cards }: { cards: { label: string; value: number | null }[] }) {
  if (cards.every((card) => card.value === null)) return <SectionEmpty />;
  return (
    <section className="grid gap-3 sm:grid-cols-2 xl:grid-cols-4">
      {cards.map((card) => (
        <div key={card.label} className="av-card p-4">
          <p className="av-label">{card.label}</p>
          <p className="mt-2 font-mono text-2xl font-semibold">{formatPercent(card.value)}</p>
        </div>
      ))}
    </section>
  );
}

export function ModelComparison({ rows }: { rows: ModelComparisonRow[] }) {
  if (rows.length === 0) return <SectionEmpty />;
  const chartRows = rows.map((row) => ({
    metric: row.metric,
    [row.modelA]: percentNumber(row.valueA),
    [row.modelB]: percentNumber(row.valueB),
  }));
  const first = rows[0];

  return (
    <section className="grid gap-5 lg:grid-cols-[0.9fr_1.1fr]">
      <div className="av-card overflow-hidden">
        <table className="w-full text-left text-sm">
          <thead className="border-b border-border text-xs uppercase tracking-[0.05em] text-muted-foreground">
            <tr>
              <th className="px-4 py-3">Метрика</th>
              <th className="px-4 py-3">{first.modelA}</th>
              <th className="px-4 py-3">{first.modelB}</th>
            </tr>
          </thead>
          <tbody className="divide-y divide-border">
            {rows.map((row) => (
              <tr key={row.metric}>
                <td className="px-4 py-3 font-medium">{row.metric}</td>
                <td className="px-4 py-3 font-mono text-muted-foreground">{formatPercent(row.valueA)}</td>
                <td className="px-4 py-3 font-mono text-accent-foreground">{formatPercent(row.valueB)}</td>
              </tr>
            ))}
          </tbody>
        </table>
      </div>
      <ChartPanel label="Порівняльна діаграма">
        <ResponsiveContainer width="100%" height={280}>
          <BarChart data={chartRows}>
            <CartesianGrid stroke="hsl(var(--border))" vertical={false} />
            <XAxis dataKey="metric" stroke="hsl(var(--muted-foreground))" tickLine={false} axisLine={false} />
            <YAxis stroke="hsl(var(--muted-foreground))" tickLine={false} axisLine={false} domain={[0, 100]} />
            <Tooltip contentStyle={tooltipStyle} />
            <Legend />
            <Bar dataKey={first.modelA} fill="hsl(var(--muted-foreground))" radius={[4, 4, 0, 0]} />
            <Bar dataKey={first.modelB} fill="hsl(var(--primary))" radius={[4, 4, 0, 0]} />
          </BarChart>
        </ResponsiveContainer>
      </ChartPanel>
    </section>
  );
}

export function ThresholdAnalysis({ rows }: { rows: ThresholdRow[] }) {
  if (rows.length === 0) return <SectionEmpty />;
  const data = rows.map((row) => ({
    threshold: row.threshold.toFixed(2),
    precision: percentNumber(row.precision),
    recall: percentNumber(row.recall),
    f1: percentNumber(row.f1),
    falsePositiveRate: percentNumber(row.falsePositiveRate),
  }));

  return (
    <section className="grid gap-5 lg:grid-cols-[1.2fr_0.8fr]">
      <ChartPanel label="Точність / повнота / F1 за порогом">
        <ResponsiveContainer width="100%" height={300}>
          <LineChart data={data}>
            <CartesianGrid stroke="hsl(var(--border))" vertical={false} />
            <XAxis dataKey="threshold" stroke="hsl(var(--muted-foreground))" tickLine={false} axisLine={false} />
            <YAxis stroke="hsl(var(--muted-foreground))" tickLine={false} axisLine={false} domain={[0, 100]} />
            <Tooltip contentStyle={tooltipStyle} />
            <Legend />
            <Line type="monotone" dataKey="precision" name="Точність" stroke="hsl(var(--primary))" strokeWidth={2} dot={false} />
            <Line type="monotone" dataKey="recall" name="Повнота" stroke="#86efac" strokeWidth={2} dot={false} />
            <Line type="monotone" dataKey="f1" name="F1" stroke="#facc15" strokeWidth={2} dot={false} />
          </LineChart>
        </ResponsiveContainer>
      </ChartPanel>
      <div className="av-card overflow-hidden">
        <table className="w-full text-left text-sm">
          <thead className="border-b border-border text-xs uppercase tracking-[0.05em] text-muted-foreground">
            <tr>
              <th className="px-4 py-3">Поріг</th>
              <th className="px-4 py-3">Точність</th>
              <th className="px-4 py-3">Повнота</th>
              <th className="px-4 py-3">F1</th>
            </tr>
          </thead>
          <tbody className="divide-y divide-border">
            {rows.map((row) => (
              <tr key={row.threshold}>
                <td className="px-4 py-3 font-mono">{row.threshold.toFixed(2)}</td>
                <td className="px-4 py-3 font-mono">{formatPercent(row.precision)}</td>
                <td className="px-4 py-3 font-mono">{formatPercent(row.recall)}</td>
                <td className="px-4 py-3 font-mono">{formatPercent(row.f1)}</td>
              </tr>
            ))}
          </tbody>
        </table>
      </div>
    </section>
  );
}

export function PerformanceChart({ rows }: { rows: PerformanceRow[] }) {
  if (rows.length === 0) return <SectionEmpty />;
  return (
    <ChartPanel label="FPS / latency">
      <ResponsiveContainer width="100%" height={260}>
        <BarChart data={rows}>
          <CartesianGrid stroke="hsl(var(--border))" vertical={false} />
          <XAxis dataKey="label" stroke="hsl(var(--muted-foreground))" tickLine={false} axisLine={false} />
          <YAxis yAxisId="fps" stroke="hsl(var(--muted-foreground))" tickLine={false} axisLine={false} />
          <YAxis yAxisId="latency" orientation="right" stroke="hsl(var(--muted-foreground))" tickLine={false} axisLine={false} />
          <Tooltip contentStyle={tooltipStyle} />
          <Legend />
          <Bar yAxisId="fps" dataKey="fps" name="FPS" fill="hsl(var(--primary))" radius={[4, 4, 0, 0]} />
          <Bar yAxisId="latency" dataKey="latencyMs" name="Latency ms" fill="hsl(var(--muted-foreground))" radius={[4, 4, 0, 0]} />
        </BarChart>
      </ResponsiveContainer>
    </ChartPanel>
  );
}

export function TrackerComparison({ rows }: { rows: TrackerRow[] }) {
  if (rows.length === 0) return <SectionEmpty />;
  return (
    <section className="space-y-3">
      <div className="rounded-md border border-primary/20 bg-primary/10 px-4 py-3 text-sm text-accent-foreground">
        <div className="flex gap-2">
          <InfoCircledIcon className="mt-0.5 h-4 w-4 shrink-0" />
          <p>tracker behavior comparison: порівняння показує поведінку трекерів на відео без абсолютної оцінки точності.</p>
        </div>
      </div>
      <div className="av-card overflow-hidden">
        <table className="w-full text-left text-sm">
          <thead className="border-b border-border text-xs uppercase tracking-[0.05em] text-muted-foreground">
            <tr>
              <th className="px-4 py-3">Показник</th>
              <th className="px-4 py-3">ByteTrack</th>
              <th className="px-4 py-3">BoT-SORT</th>
            </tr>
          </thead>
          <tbody className="divide-y divide-border">
            {rows.map((row) => (
              <tr key={row.metric}>
                <td className="px-4 py-3 font-medium">{row.metric}</td>
                <td className="px-4 py-3 font-mono">{formatNumber(row.bytetrack, row.unit)}</td>
                <td className="px-4 py-3 font-mono">{formatNumber(row.botsort, row.unit)}</td>
              </tr>
            ))}
          </tbody>
        </table>
      </div>
    </section>
  );
}

export function FalsePositiveSummary({ metrics }: { metrics: { label: string; value: number | null; kind: "percent" | "number" }[] }) {
  if (metrics.length === 0) return <SectionEmpty />;
  return (
    <section className="grid gap-3 sm:grid-cols-2 xl:grid-cols-4">
      {metrics.map((metric) => (
        <div key={metric.label} className="av-card p-4">
          <p className="av-label">{metric.label}</p>
          <p className="mt-2 font-mono text-2xl font-semibold">
            {metric.kind === "percent" ? formatPercent(metric.value) : formatNumber(metric.value)}
          </p>
        </div>
      ))}
    </section>
  );
}

export function ConfusionMatrix({ src }: { src: string | null }) {
  if (!src) return <SectionEmpty />;
  return (
    <div className="av-card overflow-hidden p-4">
      <img src={src} alt="Матриця помилок" className="max-h-[420px] w-full rounded object-contain" />
    </div>
  );
}

export function SectionShell({ title, icon, children }: { title: string; icon?: ReactNode; children: ReactNode }) {
  return (
    <section className="space-y-3">
      <div className="flex items-center gap-2">
        {icon ? <span className="text-accent-foreground">{icon}</span> : null}
        <h2 className="font-display text-lg font-semibold">{title}</h2>
      </div>
      {children}
    </section>
  );
}

export function ChartSectionIcon() {
  return <BarChartIcon className="h-4 w-4" />;
}

export function MixerSectionIcon() {
  return <MixerHorizontalIcon className="h-4 w-4" />;
}

function ChartPanel({ label, children }: { label: string; children: ReactNode }) {
  return (
    <div className="av-card p-4">
      <div className="mb-3 flex items-center justify-between gap-2">
        <p className="av-label">{label}</p>
        <span className="font-mono text-[11px] text-muted-foreground">Recharts</span>
      </div>
      {children}
    </div>
  );
}

function percentNumber(value: number | null) {
  if (value === null || !Number.isFinite(value)) return null;
  return value > 1 ? value : value * 100;
}

export function CompactPerformanceList({ rows }: { rows: PerformanceRow[] }) {
  if (rows.length === 0) return <p className="sr-only">{EMPTY_VALUE}</p>;
  return (
    <div className="grid gap-3 sm:grid-cols-2 xl:grid-cols-4">
      {rows.map((row) => (
        <div key={row.label} className="av-card p-4">
          <p className="av-label">{row.label}</p>
          <div className="mt-2 space-y-1 font-mono text-sm">
            <p>{formatFps(row.fps)}</p>
            <p className="text-muted-foreground">{formatMs(row.latencyMs)}</p>
          </div>
        </div>
      ))}
    </div>
  );
}

const tooltipStyle = {
  background: "hsl(var(--card))",
  border: "1px solid hsl(var(--border))",
  borderRadius: "0.5rem",
  color: "hsl(var(--foreground))",
};
