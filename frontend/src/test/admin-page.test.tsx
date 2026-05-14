import { render, screen, waitFor, within } from "@testing-library/react";
import userEvent from "@testing-library/user-event";
import { beforeEach, describe, expect, it, vi } from "vitest";
import { App } from "../App";
import type { AuthApi } from "../api/auth";
import type { JobDetail, User } from "../api/types";
import { tokenStorage } from "../auth/tokenStorage";

const adminUser: User = {
  id: "admin-1",
  email: "admin@aerovision.ua",
  role: "admin",
  is_active: true,
  created_at: "2026-05-14T00:00:00Z",
  updated_at: "2026-05-14T00:00:00Z",
};

const regularUser: User = {
  ...adminUser,
  id: "user-1",
  email: "operator@aerovision.ua",
  role: "user",
};

const job: JobDetail = {
  id: "job-1",
  user_id: "user-1",
  media_file_id: "media-1",
  model_version_id: "model-1",
  status: "completed",
  input_params_json: {},
  summary_json: { total_detections: 17, average_confidence: 0.847, processing_duration_seconds: 64 },
  error_message: null,
  progress_percent: 100,
  last_heartbeat_at: null,
  locked_by: null,
  locked_at: null,
  retry_count: 0,
  started_at: "2026-05-14T09:00:00Z",
  completed_at: "2026-05-14T09:01:04Z",
  created_at: "2026-05-14T08:58:00Z",
  updated_at: "2026-05-14T09:01:04Z",
  media: {
    id: "media-1",
    original_filename: "global-flight-review.mp4",
    media_type: "video",
    width: 1920,
    height: 1080,
    frame_count: 300,
    fps: 25,
    duration_seconds: 12,
  },
  model: {
    id: "model-1",
    name: "YOLO26s-v1.2",
    model_family: "YOLO26",
    variant: "s",
  },
};

const stats = {
  users: { total: 9, active: 8, admins: 1 },
  media: { total: 31, images: 18, videos: 13 },
  jobs: { total: 44, by_status: { completed: 27, processing: 3, queued: 4, failed: 2 } },
  detections: { total: 216 },
  tracks: { total: 48 },
  models: { total: 3, active: 1 },
  experiments: { total: 6, published: 4 },
};

function authApi(user: User = adminUser): AuthApi {
  return {
    login: vi.fn(),
    register: vi.fn(),
    getCurrentUser: vi.fn().mockResolvedValue(user),
  };
}

function json(data: unknown, status = 200) {
  return Promise.resolve(
    new Response(JSON.stringify(data), { status, headers: { "Content-Type": "application/json" } }),
  );
}

function cleanupResponse(dryRun: boolean) {
  return {
    dry_run: dryRun,
    scanned_files: 12,
    deleted_files: dryRun ? 0 : 4,
    would_delete_files: dryRun ? 4 : 0,
    protected_files: 5,
    reported_files: 2,
    skipped_files: 1,
    deleted_by_category: dryRun ? {} : { temp: 4 },
    would_delete_by_category: dryRun ? { temp: 4 } : {},
    protected_by_category: { models: 2, results: 3 },
    reported_by_category: { reports: 2 },
    skipped_by_category: { unknown: 1 },
  };
}

function mockFetch({ failAdmin = false, empty = false } = {}) {
  const fetchMock = vi.fn((input: RequestInfo | URL, init?: RequestInit) => {
    const url = new URL(String(input));
    if (failAdmin && url.pathname.startsWith("/api/admin")) {
      return json({ detail: "database password leaked? /app/storage/private" }, 500);
    }
    if (url.pathname === "/api/admin/stats") return json(stats);
    if (url.pathname === "/api/admin/jobs") {
      return json({ items: empty ? [] : [job], total: empty ? 0 : 1, limit: 6, offset: 0 });
    }
    if (url.pathname === "/api/admin/users") {
      return json({
        items: empty ? [] : [adminUser, regularUser],
        total: empty ? 0 : 2,
        limit: 50,
        offset: 0,
      });
    }
    if (url.pathname === "/api/admin/storage/cleanup") {
      const body = JSON.parse(String(init?.body ?? "{}")) as { dry_run?: boolean };
      return json(cleanupResponse(Boolean(body.dry_run)));
    }
    return json({ detail: `unexpected ${url.pathname}${url.search}` }, 500);
  });
  vi.stubGlobal("fetch", fetchMock);
  return fetchMock;
}

describe("Phase 30 admin page", () => {
  beforeEach(() => {
    localStorage.clear();
    vi.restoreAllMocks();
  });

  it("renders admin stats, recent global jobs, shortcuts, and users without unsafe values", async () => {
    tokenStorage.set("jwt-token");
    const fetchMock = mockFetch();

    const { container } = render(<App authApi={authApi()} initialEntries={["/admin"]} />);

    expect(await screen.findByRole("heading", { name: "Адміністрування" })).toBeInTheDocument();
    expect(screen.getByText("44")).toBeInTheDocument();
    expect(screen.getByText("216")).toBeInTheDocument();
    expect(screen.getByText("global-flight-review.mp4")).toBeInTheDocument();
    expect(screen.getAllByText("admin@aerovision.ua").length).toBeGreaterThan(0);
    expect(screen.getByRole("link", { name: /Реєстр моделей/ })).toHaveAttribute("href", "/models");
    expect(screen.getByRole("link", { name: /Імпорт метрик/ })).toHaveAttribute("href", "/experiments");

    expect(fetchMock).toHaveBeenCalledWith(expect.stringContaining("/api/admin/jobs?limit=6"), expect.anything());
    expect(fetchMock).toHaveBeenCalledWith(expect.stringContaining("/api/admin/users?limit=50"), expect.anything());
    expect(container).not.toHaveTextContent("null");
    expect(container).not.toHaveTextContent("undefined");
    expect(container).not.toHaveTextContent("C:\\");
    expect(container).not.toHaveTextContent("/app/");
    expect(container).not.toHaveTextContent("/storage/");
  });

  it("blocks regular users from admin page and hides admin navigation", async () => {
    tokenStorage.set("jwt-token");
    mockFetch();

    render(<App authApi={authApi(regularUser)} initialEntries={["/admin"]} />);

    expect(await screen.findByRole("heading", { name: "Доступ заборонено" })).toBeInTheDocument();
    expect(screen.queryByRole("link", { name: "Адмін" })).not.toBeInTheDocument();
  });

  it("renders Ukrainian empty states for empty admin lists", async () => {
    tokenStorage.set("jwt-token");
    mockFetch({ empty: true });

    render(<App authApi={authApi()} initialEntries={["/admin"]} />);

    expect(await screen.findByText("Глобальних завдань ще немає")).toBeInTheDocument();
    expect(screen.getByText("Користувачів не знайдено")).toBeInTheDocument();
  });

  it("shows safe Ukrainian error and retry without backend details", async () => {
    tokenStorage.set("jwt-token");
    const fetchMock = mockFetch({ failAdmin: true });

    render(<App authApi={authApi()} initialEntries={["/admin"]} />);

    expect(await screen.findByText("Не вдалося завантажити адмін-дані")).toBeInTheDocument();
    expect(screen.queryByText(/database password leaked/i)).not.toBeInTheDocument();
    expect(screen.queryByText("/app/storage/private")).not.toBeInTheDocument();

    await userEvent.click(screen.getByRole("button", { name: "Повторити" }));
    await waitFor(() => expect(fetchMock.mock.calls.length).toBeGreaterThan(3));
  });

  it("previews cleanup before allowing confirmed cleanup", async () => {
    tokenStorage.set("jwt-token");
    const fetchMock = mockFetch();

    render(<App authApi={authApi()} initialEntries={["/admin"]} />);

    await screen.findByRole("heading", { name: "Адміністрування" });
    expect(screen.getByRole("button", { name: "Підтвердити очищення" })).toBeDisabled();

    await userEvent.click(screen.getByRole("button", { name: "Перевірити сховище" }));
    await screen.findByText("Можна видалити: 4");
    expect(cleanupPayloads(fetchMock)).toContainEqual({ dry_run: true });

    const cleanupPanel = screen.getByTestId("cleanup-panel");
    await userEvent.click(within(cleanupPanel).getByRole("checkbox", { name: "Підтверджую безпечне очищення" }));
    await userEvent.click(screen.getByRole("button", { name: "Підтвердити очищення" }));

    expect(await screen.findByText("Видалено файлів: 4")).toBeInTheDocument();
    expect(cleanupPayloads(fetchMock)).toContainEqual({ dry_run: false });
  });
});

function cleanupPayloads(fetchMock: ReturnType<typeof vi.fn>) {
  return fetchMock.mock.calls
    .filter(([url]) => String(url).includes("/api/admin/storage/cleanup"))
    .map(([, init]) => JSON.parse(String((init as RequestInit).body ?? "{}")));
}
