import { fireEvent, render, screen, waitFor, within } from "@testing-library/react";
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

const resultRefs = {
  media: { available: true, download_url: "/api/jobs/job-1/download/media" },
  csv: { available: true, download_url: "/api/jobs/job-1/download/csv" },
  json: { available: true, download_url: "/api/jobs/job-1/download/json" },
};

interface MockJob {
  id: string;
  status: string;
  input_params_json: Record<string, unknown>;
  summary_json: Record<string, unknown> | null;
  error_message: string | null;
  progress_percent: number;
  completed_at: string | null;
  media: {
    original_filename: string;
    media_type: string;
    fps: number | null;
    duration_seconds: number | null;
    [key: string]: unknown;
  };
  result: typeof resultRefs;
  [key: string]: unknown;
}

const completedVideoJob: MockJob = {
  id: "job-1",
  user_id: "user-1",
  media_file_id: "media-1",
  model_version_id: "model-1",
  status: "completed",
  input_params_json: { confidence_threshold: 0.25, iou_threshold: 0.45, tracker_type: "bytetrack", frame_stride: 1 },
  summary_json: {
    total_detections: 2,
    average_confidence: 0.884,
    average_fps: 28.4,
    processing_duration_seconds: 31,
  },
  error_message: null,
  progress_percent: 100,
  last_heartbeat_at: "2026-05-14T09:00:30Z",
  locked_by: null,
  locked_at: null,
  retry_count: 0,
  started_at: "2026-05-14T09:00:00Z",
  completed_at: "2026-05-14T09:00:31Z",
  created_at: "2026-05-14T08:58:00Z",
  updated_at: "2026-05-14T09:00:31Z",
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
  result: resultRefs,
};

const detections = {
  items: [
    {
      id: "det-1",
      job_id: "job-1",
      media_file_id: "media-1",
      frame_index: 12,
      timestamp_ms: 400,
      class_id: 0,
      class_name: "drone",
      confidence: 0.91,
      bbox_x1: 124,
      bbox_y1: 87,
      bbox_x2: 312,
      bbox_y2: 198,
      center_x: 218,
      center_y: 142,
      bbox_width: 188,
      bbox_height: 111,
      frame_width: 1920,
      frame_height: 1080,
      track_id: 7,
      created_at: "2026-05-14T09:00:10Z",
    },
  ],
  total: 1,
  limit: 100,
  offset: 0,
};

const tracks = {
  items: [
    {
      id: "track-1",
      job_id: "job-1",
      track_id: 7,
      class_name: "drone",
      first_frame_index: 12,
      last_frame_index: 24,
      frames_count: 9,
      average_confidence: 0.86,
      max_confidence: 0.94,
      created_at: "2026-05-14T09:00:10Z",
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

function setupFetch(job: MockJob, detectionData = detections, trackData = tracks) {
  const fetchMock = vi.fn((input: RequestInfo | URL) => {
    const url = new URL(String(input));
    if (url.pathname === "/api/jobs/job-1") return json(job);
    if (url.pathname === "/api/jobs/job-1/result") return json({ job_id: "job-1", status: job.status, summary: job.summary_json, ...job.result });
    if (url.pathname === "/api/jobs/job-1/detections") return json(detectionData);
    if (url.pathname === "/api/jobs/job-1/tracks") return json(trackData);
    if (url.pathname.startsWith("/api/jobs/job-1/download/")) {
      const isMedia = url.pathname.endsWith("/download/media");
      return Promise.resolve(
        new Response(new Blob(["file"], { type: isMedia ? "video/mp4" : "text/plain" }), {
          status: 200,
          headers: isMedia ? { "Content-Type": "video/mp4" } : undefined,
        }),
      );
    }
    return json({ detail: "unexpected route" }, 500);
  });
  vi.stubGlobal("fetch", fetchMock);
  return fetchMock;
}

describe("Phase 27 job details page", () => {
  beforeEach(() => {
    localStorage.clear();
    vi.restoreAllMocks();
    if (!("createObjectURL" in URL)) {
      Object.defineProperty(URL, "createObjectURL", { value: vi.fn(), configurable: true });
    }
    if (!("revokeObjectURL" in URL)) {
      Object.defineProperty(URL, "revokeObjectURL", { value: vi.fn(), configurable: true });
    }
    vi.spyOn(URL, "createObjectURL").mockReturnValue("blob:preview");
    vi.spyOn(URL, "revokeObjectURL").mockImplementation(() => undefined);
    vi.spyOn(HTMLAnchorElement.prototype, "click").mockImplementation(() => undefined);
  });

  it("redirects guests from job details to login", async () => {
    render(<App authApi={authApi()} initialEntries={["/jobs/job-1"]} />);

    expect(await screen.findByRole("heading", { name: /AeroVision/ })).toBeInTheDocument();
  });

  it("renders completed video details, detections, tracks, and safe downloads", async () => {
    tokenStorage.set("jwt-token");
    const fetchMock = setupFetch(completedVideoJob);
    const { container } = render(<App authApi={authApi()} initialEntries={["/jobs/job-1"]} />);

    expect(await screen.findByRole("heading", { name: "Деталі завдання" })).toBeInTheDocument();
    expect(screen.getAllByText("patrol_footage_01.mp4").length).toBeGreaterThan(0);
    expect(screen.getByText("Завершено")).toBeInTheDocument();
    expect(screen.getAllByText("drone").length).toBeGreaterThan(0);
    expect(screen.getByText("[124, 87, 312, 198]")).toBeInTheDocument();
    expect(screen.getByRole("columnheader", { name: "Координати рамки" })).toBeInTheDocument();
    expect(screen.getAllByRole("columnheader", { name: "ID треку" })).toHaveLength(2);
    expect(screen.queryByRole("columnheader", { name: "Bounding box" })).not.toBeInTheDocument();
    expect(screen.queryByRole("columnheader", { name: "Track ID" })).not.toBeInTheDocument();
    expect(screen.getByRole("heading", { name: "Треки об'єктів" })).toBeInTheDocument();
    await waitFor(() =>
      expect(screen.getByLabelText("processed-video-preview")).toHaveAttribute("src", "blob:preview"),
    );
    expect(
      vi.mocked(URL.createObjectURL).mock.calls.some(([blob]) => blob instanceof Blob && blob.type === "video/mp4"),
    ).toBe(true);
    expect(container).not.toHaveTextContent("frame_stride");
    expect(container).not.toHaveTextContent("C:\\");
    expect(container).not.toHaveTextContent("/app/storage");
    expect(container).not.toHaveTextContent("null");
    expect(container).not.toHaveTextContent("undefined");

    await userEvent.click(screen.getByRole("button", { name: /CSV-звіт/ }));
    await waitFor(() => expect(fetchMock.mock.calls.some(([url]) => String(url).includes("/api/jobs/job-1/download/csv"))).toBe(true));
  });

  it("shows no-detection empty state as successful result", async () => {
    tokenStorage.set("jwt-token");
    setupFetch(
      { ...completedVideoJob, summary_json: { total_detections: 0, average_confidence: null } },
      { items: [], total: 0, limit: 100, offset: 0 },
      { items: [], total: 0, limit: 100, offset: 0 },
    );

    render(<App authApi={authApi()} initialEntries={["/jobs/job-1"]} />);

    expect(await screen.findByText("Виявлень не знайдено")).toBeInTheDocument();
    expect(screen.getByText("Модель не виявила об'єктів drone у цьому файлі. Це успішний результат, не помилка.")).toBeInTheDocument();
    expect(screen.getByRole("button", { name: /CSV-звіт/ })).toBeEnabled();
  });

  it("shows queued progress with polling state", async () => {
    tokenStorage.set("jwt-token");
    setupFetch({ ...completedVideoJob, status: "processing", progress_percent: 63, completed_at: null });

    render(<App authApi={authApi()} initialEntries={["/jobs/job-1"]} />);

    const section = await screen.findByText("Завдання обробляється");
    expect(section).toBeInTheDocument();
    expect(screen.getByText("63%")).toBeInTheDocument();
  });

  it("hides raw failed-job internals", async () => {
    tokenStorage.set("jwt-token");
    const failed = {
      ...completedVideoJob,
      status: "failed",
      progress_percent: 44,
      error_message: "Traceback C:\\storage\\secret\\weights.pt",
      completed_at: null,
      result: {
        media: { available: false, download_url: "/api/jobs/job-1/download/media" },
        csv: { available: false, download_url: "/api/jobs/job-1/download/csv" },
        json: { available: false, download_url: "/api/jobs/job-1/download/json" },
      },
    };
    setupFetch(failed);
    const { container } = render(<App authApi={authApi()} initialEntries={["/jobs/job-1"]} />);

    expect(await screen.findByText("Помилка обробки")).toBeInTheDocument();
    expect(screen.getByText("Обробку зупинено. Перевірте файл або параметри та створіть нове завдання.")).toBeInTheDocument();
    expect(container).not.toHaveTextContent("Traceback");
    expect(container).not.toHaveTextContent("weights.pt");
  });

  it("does not show track summary table for completed image jobs", async () => {
    tokenStorage.set("jwt-token");
    setupFetch(
      {
        ...completedVideoJob,
        media: { ...completedVideoJob.media, media_type: "image", original_filename: "frame_capture.webp", fps: null, duration_seconds: null },
        input_params_json: { confidence_threshold: 0.25, iou_threshold: 0.45, frame_stride: 1 },
      },
      detections,
      { items: [], total: 0, limit: 100, offset: 0 },
    );

    render(<App authApi={authApi()} initialEntries={["/jobs/job-1"]} />);

    expect((await screen.findAllByText("frame_capture.webp")).length).toBeGreaterThan(0);
    expect(screen.queryByRole("heading", { name: "Треки об'єктів" })).not.toBeInTheDocument();
    expect(within(screen.getByText("Параметри").closest("div") as HTMLElement).queryByText("Трекер")).not.toBeInTheDocument();
  });

  it("does not send bearer token to external download URLs", async () => {
    tokenStorage.set("jwt-token");
    const unsafeJob = {
      ...completedVideoJob,
      result: {
        media: { available: true, download_url: "https://example.invalid/api/jobs/job-1/download/media" },
        csv: { available: true, download_url: "https://example.invalid/api/jobs/job-1/download/csv" },
        json: { available: true, download_url: "https://example.invalid/api/jobs/job-1/download/json" },
      },
    };
    const fetchMock = setupFetch(unsafeJob);

    render(<App authApi={authApi()} initialEntries={["/jobs/job-1"]} />);

    await screen.findByRole("heading", { name: "Деталі завдання" });
    await userEvent.click(screen.getByRole("button", { name: /CSV-звіт/ }));

    await waitFor(() => expect(screen.getByText("Не вдалося підготувати завантаження.")).toBeInTheDocument());
    expect(fetchMock.mock.calls.some(([url]) => String(url).includes("example.invalid"))).toBe(false);
  });
  it("shows the documented notice when processed video playback fails", async () => {
    tokenStorage.set("jwt-token");
    setupFetch(completedVideoJob);

    render(<App authApi={authApi()} initialEntries={["/jobs/job-1"]} />);

    const video = await screen.findByLabelText("processed-video-preview");
    fireEvent.error(video);

    const notice = await screen.findByTestId("preview-unavailable-notice");
    expect(notice).toBeInTheDocument();
    expect(screen.getByRole("button", { name: /Анотоване відео/ })).toBeEnabled();
  });
});
