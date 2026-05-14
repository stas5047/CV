import { RoutePlaceholder } from "../components/RoutePlaceholder";

export function DashboardPage() {
  return <RoutePlaceholder title="Огляд" description="Початкова захищена сторінка для майбутніх показників і останніх завдань." />;
}

export function UploadPage() {
  return <RoutePlaceholder title="Завантаження" description="Місце для майбутнього завантаження файлів і створення задач обробки." />;
}

export function JobsPage() {
  return <RoutePlaceholder title="Завдання" description="Місце для майбутньої історії задач, фільтрів і статусів обробки." />;
}

export function JobDetailsPage() {
  return <RoutePlaceholder title="Деталі завдання" description="Місце для майбутніх результатів, таблиць детекцій і завантажень." />;
}

export function ModelsPage() {
  return <RoutePlaceholder title="Моделі" description="Місце для майбутнього реєстру моделей і стану активної моделі." />;
}

export function ExperimentsPage() {
  return <RoutePlaceholder title="Досліди" description="Місце для майбутніх метрик експериментів і порівнянь." />;
}

export function AdminPage() {
  return <RoutePlaceholder title="Адмін" description="Адміністративний маршрут для майбутніх глобальних даних і безпечного обслуговування." />;
}
