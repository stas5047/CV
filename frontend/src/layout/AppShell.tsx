import { useState } from "react";
import {
  BarChartIcon,
  DashboardIcon,
  ExitIcon,
  HamburgerMenuIcon,
  LockClosedIcon,
  ReaderIcon,
  RocketIcon,
  UploadIcon,
} from "@radix-ui/react-icons";
import { NavLink, Outlet, useLocation, useNavigate } from "react-router-dom";
import { useAuth } from "../auth/useAuth";
import { Button } from "../components/ui/button";
import { Logo } from "../components/Logo";
import { cn } from "../lib/utils";

const navItems = [
  { path: "/dashboard", label: "Огляд", Icon: DashboardIcon },
  { path: "/upload", label: "Завантаження", Icon: UploadIcon },
  { path: "/jobs", label: "Завдання", Icon: ReaderIcon },
  { path: "/models", label: "Моделі", Icon: RocketIcon },
  { path: "/experiments", label: "Досліди", Icon: BarChartIcon },
];

const adminItem = { path: "/admin", label: "Адмін", Icon: LockClosedIcon };

function NavItems({ close }: { close?: () => void }) {
  const { user } = useAuth();
  const location = useLocation();
  const items = user?.role === "admin" ? [...navItems, adminItem] : navItems;
  const isRouteActive = (path: string) =>
    path === "/jobs" ? location.pathname === "/jobs" || location.pathname.startsWith("/jobs/") : location.pathname === path;

  return (
    <>
      {items.map(({ path, label, Icon }) => (
        <NavLink
          key={path}
          to={path}
          aria-label={label}
          title={label}
          onClick={close}
          className={({ isActive }) =>
            cn(
              "group relative flex h-10 items-center gap-3 rounded-md px-3 text-sm text-muted-foreground transition duration-300 hover:bg-secondary hover:text-foreground active:translate-y-px md:w-10 md:justify-center md:px-0",
              (isActive || isRouteActive(path)) && "bg-primary/10 text-accent-foreground",
            )
          }
        >
          {isRouteActive(path) ? (
            <span className="absolute left-0 hidden h-5 w-0.5 rounded-r bg-primary md:block" />
          ) : null}
          <Icon className="h-4 w-4 shrink-0" />
          <span className="md:sr-only">{label}</span>
        </NavLink>
      ))}
    </>
  );
}

export function AppShell() {
  const [open, setOpen] = useState(false);
  const { user, logout } = useAuth();
  const navigate = useNavigate();

  const handleLogout = () => {
    logout();
    navigate("/login", { replace: true });
  };

  return (
    <div className="min-h-[100dvh] bg-background text-foreground md:grid md:grid-cols-[56px_minmax(0,1fr)]">
      <aside className="fixed inset-y-0 left-0 hidden w-14 border-r border-border bg-card/95 p-2 md:flex md:flex-col md:items-center">
        <div className="mb-3 mt-1">
          <Logo compact />
        </div>
        <div className="mb-2 h-px w-8 bg-border" />
        <nav className="flex flex-1 flex-col gap-1">
          <NavItems />
        </nav>
        <div className="mb-2 h-px w-8 bg-border" />
        <Button variant="ghost" size="icon" aria-label="Вийти" onClick={handleLogout}>
          <ExitIcon className="h-4 w-4" />
        </Button>
      </aside>

      <div className="md:col-start-2">
        <header className="sticky top-0 flex h-14 items-center justify-between border-b border-border bg-card/95 px-4 backdrop-blur md:hidden">
          <Logo compact />
          <div className="flex items-center gap-2">
            <span className="max-w-[150px] truncate text-xs text-muted-foreground">{user?.email}</span>
            <Button variant="ghost" size="icon" aria-label="Відкрити меню" onClick={() => setOpen((value) => !value)}>
              <HamburgerMenuIcon className="h-5 w-5" />
            </Button>
          </div>
        </header>
        {open ? (
          <>
            <button
              className="fixed inset-0 bg-background/70 backdrop-blur-sm md:hidden"
              aria-label="Закрити меню"
              onClick={() => setOpen(false)}
            />
            <nav className="fixed left-3 right-3 top-16 rounded-md border border-border bg-card p-3 shadow-panel md:hidden">
              <div className="mb-3 text-xs text-muted-foreground">{user?.email}</div>
              <div className="space-y-1">
                <NavItems close={() => setOpen(false)} />
              </div>
              <Button className="mt-3 w-full" variant="secondary" onClick={handleLogout}>
                <ExitIcon className="h-4 w-4" />
                Вийти
              </Button>
            </nav>
          </>
        ) : null}
        <main className="mx-auto w-full max-w-[1400px] px-4 py-6 md:px-8 md:py-8">
          <Outlet />
        </main>
      </div>
    </div>
  );
}
