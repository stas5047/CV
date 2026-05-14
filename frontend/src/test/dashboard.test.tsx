import { render, screen, waitFor, within } from "@testing-library/react";
import userEvent from "@testing-library/user-event";
import { beforeEach, describe, expect, it, vi } from "vitest";
import { App } from "../App";
import type { AuthApi } from "../api/auth";
import { tokenStorage } from "../auth/tokenStorage";

const user = {
  id: "user-1",
  email: "operator@example.com",
  role: "user" as const,
  is_active: true,
  created_at: "2026-05-14T00:00:00Z",
  updated_at: "2026-05-14T00:00:00Z",
};

const activeModel = {
  id: "model-1",
  name: "YOLO26s-v1.2",
  model_family: "YOLO26",
  variant: "s",
  weights_path: "models/yolo26s-v1.2.pt",
  dataset_name: "Seraphim",
  dataset_split_description: "train/val/test",
  metrics_json: { mAP50: 0.891, precision: 0.912, recall: 0.876 },
  is_active: true,
  created_by_user_id: null,
  created_at: "2026-05-14T00:00:00Z",
  updated_at: "2026-05-14T00:00:00Z",
};

const completedJob = {
  id: "job-1",
  user_id: "user-1",
  media_file_id: "media-1",
  model_version_id: "model-1",
  status: "completed",
  input_params_json: {},
  summary_json: {
    total_detections: 12,
    average_confidence: 0.812,
    average_fps: 23.7,
    processing_duration_seconds: 42,
  },
  error_message: null,
  progress_percent: 100,
  last_heartbeat_at: null,
  locked_by: null,
  locked_at: null,
  retry_count: 0,
  started_at: "2026-05-14T09:00:00Z",
  completed_at: "2026-05-14T09:00:42Z",
  created_at: "2026-05-14T08:58:00Z",
  updated_at: "2026-05-14T09:00:42Z",
  media: {
    id: "media-1",
    original_filename: "patrol_footage_01.mp4",
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

function authApi(role: "user" | "admin" = "user"): AuthApi {
  return {
    login: vi.fn(),
    register: vi.fn(),
    getCurrentUser: vi.fn().mockResolvedValue({ ...user, role }),
  };
}

function json(data: unknown) {
  return Promise.resolve(new Response(JSON.stringify(data), { status: 200, headers: { "Content-Type": "application/json" } }));
}

function mockFetch(routes: Record<string, unknown>) {
  const fetchMock = vi.fn((input: RequestInfo | URL) => {
    const url = new URL(String(input));
    const key = `${url.pathname}${url.search}`;
    if (!(key in routes)) {
      return Promise.resolve(new Response(JSON.stringify({ detail: `unexpected ${key}` }), { status: 500 }));
    }
    return json(routes[key]);
  });
  vi.stubGlobal("fetch", fetchMock);
  return fetchMock;
}

describe("Phase 25 dashboard", () => {
  beforeEach(() => {
    localStorage.clear();
    vi.restoreAllMocks();
  });

  it("renders regular user dashboard from user-scoped APIs and does not call admin endpoints", async () => {
    tokenStorage.set("jwt-token");
    const fetchMock = mockFetch({
      "/api/jobs?limit=100": { items: [completedJob], total: 1, limit: 100, offset: 0 },
      "/api/models?is_active=true&limit=1": { items: [activeModel], total: 1, limit: 1, offset: 0 },
    });

    render(<App authApi={authApi()} initialEntries={["/dashboard"]} />);

    expect(await screen.findByRole("heading", { name: "Огляд" })).toBeInTheDocument();
    expect(screen.getAllByText("12").length).toBeGreaterThan(0);
    expect(screen.getByText("81,2%")).toBeInTheDocument();
    expect(screen.getAllByText("YOLO26s-v1.2").length).toBeGreaterThan(0);
    expect(screen.getByText("patrol_footage_01.mp4")).toBeInTheDocument();
    expect(screen.queryByText("models/yolo26s-v1.2.pt")).not.toBeInTheDocument();
    expect(fetchMock.mock.calls.some(([url]) => String(url).includes("/api/admin/"))).toBe(false);
  });

  it("renders admin nav and global dashboard counts from admin APIs", async () => {
    tokenStorage.set("jwt-token");
    mockFetch({
      "/api/admin/stats": {
        users: { total: 4, active: 3, admins: 1 },
        media: { total: 8, images: 5, videos: 3 },
        jobs: { total: 6, by_status: { completed: 4, processing: 1, queued: 1 } },
        detections: { total: 127 },
        tracks: { total: 18 },
        models: { total: 2, active: 1 },
        experiments: { total: 1, published: 1 },
      },
      "/api/admin/jobs?limit=5": { items: [completedJob], total: 1, limit: 5, offset: 0 },
      "/api/models?is_active=true&limit=1": { items: [activeModel], total: 1, limit: 1, offset: 0 },
    });

    render(<App authApi={authApi("admin")} initialEntries={["/dashboard"]} />);

    expect(await screen.findByRole("link", { name: "Адмін" })).toBeInTheDocument();
    expect(await screen.findByText("Глобальна статистика системи")).toBeInTheDocument();
    expect(screen.getByText("127")).toBeInTheDocument();
    expect(screen.getAllByText("Немає даних").length).toBeGreaterThanOrEqual(2);
    expect(screen.queryByText("81,2%")).not.toBeInTheDocument();
  });

  it("renders Ukrainian empty placeholders without raw null values", async () => {
    tokenStorage.set("jwt-token");
    mockFetch({
      "/api/jobs?limit=100": { items: [], total: 0, limit: 100, offset: 0 },
      "/api/models?is_active=true&limit=1": { items: [], total: 0, limit: 1, offset: 0 },
    });

    const { container } = render(<App authApi={authApi()} initialEntries={["/dashboard"]} />);

    expect(await screen.findByText("Завдань ще немає")).toBeInTheDocument();
    expect(screen.getAllByText("Немає даних").length).toBeGreaterThan(0);
    expect(container).not.toHaveTextContent("null");
    expect(container).not.toHaveTextContent("undefined");
  });

  it("shows safe Ukrainian error state and retry action when dashboard API fails", async () => {
    tokenStorage.set("jwt-token");
    const fetchMock = vi.fn((input: RequestInfo | URL) => {
      const url = new URL(String(input));
      if (url.pathname === "/api/models") {
        return json({ items: [], total: 0, limit: 1, offset: 0 });
      }
      return Promise.resolve(new Response(JSON.stringify({ detail: "database password leaked?" }), { status: 500, headers: { "Content-Type": "application/json" } }));
    });
    vi.stubGlobal("fetch", fetchMock);

    render(<App authApi={authApi()} initialEntries={["/dashboard"]} />);

    const error = await screen.findByRole("heading", { name: "Не вдалося завантажити огляд" });
    expect(error).toBeInTheDocument();
    expect(screen.queryByText("database password leaked?")).not.toBeInTheDocument();
    await userEvent.click(screen.getByRole("button", { name: "Повторити" }));
    await waitFor(() => expect(fetchMock).toHaveBeenCalled());
  });

  it("keeps recent job details links available", async () => {
    tokenStorage.set("jwt-token");
    mockFetch({
      "/api/jobs?limit=100": { items: [completedJob], total: 1, limit: 100, offset: 0 },
      "/api/models?is_active=true&limit=1": { items: [activeModel], total: 1, limit: 1, offset: 0 },
    });

    render(<App authApi={authApi()} initialEntries={["/dashboard"]} />);

    const table = await screen.findByRole("table");
    expect(within(table).getByRole("link", { name: "Відкрити" })).toHaveAttribute("href", "/jobs/job-1");
  });
});
