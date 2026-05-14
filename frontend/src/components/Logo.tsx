export function Logo({ compact = false }: { compact?: boolean }) {
  return (
    <div className="flex items-center gap-3">
      <div className="grid h-10 w-10 shrink-0 place-items-center rounded-lg bg-primary font-display text-sm font-bold text-primary-foreground">
        AV
      </div>
      {!compact && (
        <div>
          <div className="font-display text-base font-bold leading-none">AeroVision</div>
          <div className="mt-1 text-[11px] text-muted-foreground">CV subsystem</div>
        </div>
      )}
    </div>
  );
}
