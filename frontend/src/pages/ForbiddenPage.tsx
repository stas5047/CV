export function ForbiddenPage() {
  return (
    <section className="av-card max-w-2xl p-8">
      <h1 className="font-display text-2xl font-bold tracking-tight">Доступ заборонено</h1>
      <p className="mt-3 text-sm text-muted-foreground">
        Цей маршрут доступний лише адміністратору. Backend API все одно перевіряє роль для захищених дій.
      </p>
    </section>
  );
}
