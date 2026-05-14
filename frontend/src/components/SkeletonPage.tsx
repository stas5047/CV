export function SkeletonPage() {
  return (
    <div className="min-h-[100dvh] bg-background p-6">
      <div className="mx-auto max-w-7xl space-y-5">
        <div className="av-skeleton h-8 w-56" />
        <div className="grid gap-4 md:grid-cols-[2fr_1fr]">
          <div className="av-skeleton h-52" />
          <div className="av-skeleton h-52" />
        </div>
      </div>
    </div>
  );
}
