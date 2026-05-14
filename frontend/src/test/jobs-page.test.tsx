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

const baseJob = {
  id: "job-1",
  user_id: "user-1",
  media_file_id: "media-1",
  model_version_id: "model-1",
  status: "completed",
  input_params_json: { confidence_threshold: 0.25, iou_threshold: 0.45, frame_stride: 1 },
  summary_json: { total_detections: 7, average_confidence: 0.873, processing_duration_seconds: 41 },
  error_message: null,
  progress_percent: 100,
  last_heartbeat_at: null,
  locked_by: null,
  locked_at: null,
  retry_count: 0,
  started_at: "2026-05-14T09:00:00Z",
  completed_at: "2026-05-14T09:00:41Z",
  created_at: "2026-05-14T08:58:00Z",
  updated_at: "2026-05-14T09:00:41Z",
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
  result: {
    media: { available: true, download_url: "/jobs/job-1/download/media" },
    csv: { available: true, download_url: "/jobs/job-1/download/csv" },
    json: { available: true, download_url: "/jobs/job-1/download/json" },
  },
};

const modelList = {
  items: [
    {
      id: "model-1",
      name: "YOLO26s-v1.2",
      model_family: "YOLO26",
      variant: "s",
      weights_path: "models/yolo26s.pt",
      dataset_name: "Seraphim",
      dataset_split_description: null,
      metrics_json: {},
      is_active: true,
      created_by_user_id: "admin-1",
      created_at: "2026-05-14T00:00:00Z",
      updated_at: "2026-05-14T00:00:00Z",
    },
  ],
  total: 1,
  limit: 100,
  offset: 0,
};

function authApi(): AuthApi {
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

describe("Phase 27 jobs page", () => {
  beforeEach(() => {
    localStorage.clear();
    vi.restoreAllMocks();
  });

  it("redirects guests from jobs history to login", async () => {
    render(<App authApi={authApi()} initialEntries={["/jobs"]} />);

    expect(await screen.findByRole("heading", { name: /AeroVision/ })).toBeInTheDocument();
  });

  it("renders user jobs without admin routes or unsafe values", async () => {
    tokenStorage.set("jwt-token");
    const fetchMock = vi.fn((input: RequestInfo | URL) => {
      const url = new URL(String(input));
      if (url.pathname === "/api/jobs") {
        return json({ items: [baseJob], total: 1, limit: 10, offset: 0 });
      }
      if (url.pathname === "/api/models") {
        return json(modelList);
      }
      return json({ detail: `unexpected ${url.pathname}` }, 500);
    });
    vi.stubGlobal("fetch", fetchMock);

    const { container } = render(<App authApi={authApi()} initialEntries={["/jobs"]} />);

    expect(await screen.findByRole("heading", { name: "Черга завдань" })).toBeInTheDocument();
    expect(screen.getByText("patrol_footage_01.mp4")).toBeInTheDocument();
    expect(within(screen.getByRole("table")).getByText("Завершено")).toBeInTheDocument();
    expect(screen.getByText("87,3%")).toBeInTheDocument();
    expect(within(screen.getByRole("table")).getByRole("link", { name: /Відкрити/ })).toHaveAttribute("href", "/jobs/job-1");
    expect(fetchMock.mock.calls.some(([url]) => String(url).includes("/api/admin"))).toBe(false);
    expect(container).not.toHaveTextContent("frame_stride");
    expect(container).not.toHaveTextContent("null");
    expect(container).not.toHaveTextContent("undefined");
    expect(container).not.toHaveTextContent("/app/storage");
  });

  it("sends documented filter query params and shows filtered empty state", async () => {
    tokenStorage.set("jwt-token");
    const fetchMock = vi.fn((input: RequestInfo | URL) => {
      const url = new URL(String(input));
      if (url.pathname === "/api/jobs" && url.search.includes("status=failed")) {
        return json({ items: [], total: 0, limit: 10, offset: 0 });
      }
      if (url.pathname === "/api/jobs" && url.search.includes("model_version_id=model-1")) {
        return json({ items: [baseJob], total: 1, limit: 10, offset: 0 });
      }
      if (url.pathname === "/api/jobs") {
        return json({ items: [baseJob], total: 1, limit: 10, offset: 0 });
      }
      if (url.pathname === "/api/models") {
        return json(modelList);
      }
      return json({ detail: "unexpected route" }, 500);
    });
    vi.stubGlobal("fetch", fetchMock);

    render(<App authApi={authApi()} initialEntries={["/jobs"]} />);

    await screen.findByText("patrol_footage_01.mp4");
    await userEvent.selectOptions(screen.getByLabelText("Статус"), "failed");

    await screen.findByText("Завдань ще немає");
    await waitFor(() => {
      expect(fetchMock.mock.calls.some(([url]) => String(url).includes("status=failed"))).toBe(true);
    });

    await userEvent.selectOptions(screen.getByLabelText("Модель"), "model-1");

    await waitFor(() => {
      expect(fetchMock.mock.calls.some(([url]) => String(url).includes("model_version_id=model-1"))).toBe(true);
    });
  });

  it("searches only current page and explains no local matches", async () => {
    tokenStorage.set("jwt-token");
    vi.stubGlobal(
      "fetch",
      vi.fn((input: RequestInfo | URL) => {
        const url = new URL(String(input));
        if (url.pathname === "/api/jobs") {
          return json({ items: [baseJob], total: 1, limit: 10, offset: 0 });
        }
        if (url.pathname === "/api/models") {
          return json(modelList);
        }
        return json({ detail: "unexpected route" }, 500);
      }),
    );

    render(<App authApi={authApi()} initialEntries={["/jobs"]} />);

    await screen.findByText("patrol_footage_01.mp4");
    await userEvent.type(screen.getByLabelText("Пошук на цій сторінці"), "missing");

    expect(await screen.findByText("Нічого не знайдено")).toBeInTheDocument();
    expect(screen.getByText("Пошук працює тільки в межах поточної сторінки результатів.")).toBeInTheDocument();
  });
});
