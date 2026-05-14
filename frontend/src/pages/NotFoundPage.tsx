import { Link } from "react-router-dom";

export function NotFoundPage() {
  return (
    <section className="av-card max-w-2xl p-8">
      <h1 className="font-display text-2xl font-bold tracking-tight">Сторінку не знайдено</h1>
      <p className="mt-3 text-sm text-muted-foreground">Перейдіть до панелі огляду або перевірте адресу.</p>
      <Link className="av-link mt-5 inline-block" to="/dashboard">
        До огляду
      </Link>
    </section>
  );
}
