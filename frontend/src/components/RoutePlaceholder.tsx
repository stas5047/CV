export function RoutePlaceholder({
  title,
  description,
}: {
  title: string;
  description: string;
}) {
  return (
    <section className="space-y-6">
      <div>
        <h1 className="font-display text-2xl font-bold tracking-tight">{title}</h1>
        <p className="mt-2 max-w-[65ch] text-sm text-muted-foreground">{description}</p>
      </div>
      <div className="av-card grid min-h-56 place-items-center p-8 text-center">
        <div>
          <p className="font-display text-lg font-semibold">Розділ готується</p>
          <p className="mt-2 text-sm text-muted-foreground">
            Цей екран буде заповнено у наступних фазах без зміни поточних маршрутів.
          </p>
        </div>
      </div>
    </section>
  );
}
