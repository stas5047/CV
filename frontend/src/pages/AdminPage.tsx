import { useQuery } from "@tanstack/react-query";
import { getAdminStats, listAdminJobs, listAdminUsers } from "../api/admin";
import {
  CleanupPanel,
  ErrorState,
  PageSkeleton,
  RecentJobs,
  Shortcuts,
  StatsGrid,
  UsersTable,
} from "./admin/AdminPageParts";

export function AdminPage() {
  const statsQuery = useQuery({ queryKey: ["admin", "stats"], queryFn: getAdminStats });
  const jobsQuery = useQuery({ queryKey: ["admin", "jobs"], queryFn: () => listAdminJobs(6) });
  const usersQuery = useQuery({ queryKey: ["admin", "users"], queryFn: () => listAdminUsers(50) });
  const isLoading = statsQuery.isLoading || jobsQuery.isLoading || usersQuery.isLoading;
  const isError = statsQuery.isError || jobsQuery.isError || usersQuery.isError;

  const retry = () => {
    void statsQuery.refetch();
    void jobsQuery.refetch();
    void usersQuery.refetch();
  };

  if (isLoading) return <PageSkeleton />;
  if (isError || !statsQuery.data || !jobsQuery.data || !usersQuery.data) return <ErrorState onRetry={retry} />;

  return (
    <div className="space-y-5">
      <header className="flex flex-col gap-2">
        <h1 className="font-display text-2xl font-bold tracking-tight">Адміністрування</h1>
        <p className="max-w-2xl text-sm leading-6 text-muted-foreground">
          Глобальна статистика, останні завдання, системні переходи, безпечне очищення та базовий список користувачів.
        </p>
      </header>

      <StatsGrid stats={statsQuery.data} />

      <section className="grid gap-4 xl:grid-cols-[minmax(0,1fr)_320px]">
        <RecentJobs jobs={jobsQuery.data.items} />
        <div className="grid content-start gap-4">
          <Shortcuts />
          <CleanupPanel />
        </div>
      </section>

      <UsersTable users={usersQuery.data.items} />
    </div>
  );
}
