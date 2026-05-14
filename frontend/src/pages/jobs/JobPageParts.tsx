import type { ReactNode } from "react";
import {
  Component1Icon,
  ExclamationTriangleIcon,
  ImageIcon,
  VideoIcon,
} from "@radix-ui/react-icons";
import { cn } from "../../lib/utils";
import { statusLabels } from "./jobFormatters";

const statusClasses: Record<string, string> = {
  queued: "bg-muted text-muted-foreground",
  processing: "bg-primary/10 text-accent-foreground",
  completed: "bg-emerald-500/10 text-emerald-200",
  failed: "bg-destructive/10 text-red-200",
  cancelled: "bg-secondary text-muted-foreground",
};

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

export function MediaIcon({ mediaType }: { mediaType: string }) {
  return mediaType === "video" ? (
    <VideoIcon className="h-4 w-4 shrink-0 text-muted-foreground" />
  ) : (
    <ImageIcon className="h-4 w-4 shrink-0 text-muted-foreground" />
  );
}

export function EmptyState({
  title,
  description,
  action,
}: {
  title: string;
  description?: string;
  action?: ReactNode;
}) {
  return (
    <div className="flex min-h-48 flex-col items-center justify-center gap-3 px-5 py-10 text-center">
      <Component1Icon className="h-7 w-7 text-muted-foreground/40" />
      <div>
        <p className="font-medium text-foreground">{title}</p>
        {description ? <p className="mt-1 max-w-md text-sm leading-6 text-muted-foreground">{description}</p> : null}
      </div>
      {action ? <div className="mt-2">{action}</div> : null}
    </div>
  );
}

export function ErrorState({ title, description, onRetry }: { title: string; description: string; onRetry: () => void }) {
  return (
    <section className="av-card border-destructive/25 bg-destructive/10 p-5">
      <div className="flex flex-col gap-4 sm:flex-row sm:items-center sm:justify-between">
        <div className="flex gap-3">
          <ExclamationTriangleIcon className="mt-1 h-5 w-5 shrink-0 text-red-200" />
          <div>
            <h1 className="font-display text-xl font-semibold">{title}</h1>
            <p className="mt-1 text-sm text-red-100/75">{description}</p>
          </div>
        </div>
        <button className="rounded-md border border-border bg-secondary px-4 py-2 text-sm transition hover:bg-muted active:translate-y-px" onClick={onRetry}>
          Повторити
        </button>
      </div>
    </section>
  );
}

export function ProgressBar({ value }: { value: number }) {
  const width = Math.max(0, Math.min(100, Number.isFinite(value) ? value : 0));
  return (
    <div className="h-2 overflow-hidden rounded-full bg-secondary">
      <div className="h-full rounded-full bg-primary transition-[width] duration-500" style={{ width: `${width}%` }} />
    </div>
  );
}

export function TableSkeleton({ rows = 5 }: { rows?: number }) {
  return (
    <div className="av-card overflow-hidden">
      <div className="space-y-3 p-5">
        {Array.from({ length: rows }).map((_, index) => (
          <div className="grid grid-cols-[120px_minmax(0,1fr)_120px_90px] gap-3" key={index}>
            <div className="av-skeleton h-8" />
            <div className="av-skeleton h-8" />
            <div className="av-skeleton h-8" />
            <div className="av-skeleton h-8" />
          </div>
        ))}
      </div>
    </div>
  );
}
