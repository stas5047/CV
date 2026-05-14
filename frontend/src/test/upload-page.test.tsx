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

const model = {
  id: "model-1",
  name: "YOLO26s-v1.2",
  model_family: "YOLO26",
  variant: "s",
  weights_path: "models/yolo26s-v1.2.pt",
  dataset_name: "Seraphim",
  dataset_split_description: "train/val/test",
  metrics_json: { mAP50: 0.891 },
  is_active: true,
  created_by_user_id: null,
  created_at: "2026-05-14T00:00:00Z",
  updated_at: "2026-05-14T00:00:00Z",
};

const imageMedia = {
  id: "media-image-1",
  user_id: "user-1",
  original_filename: "drone_frame.jpg",
  media_type: "image",
  mime_type: "image/jpeg",
  file_size_bytes: 1048576,
  width: 1280,
  height: 720,
  frame_count: 1,
  fps: null,
  duration_seconds: null,
  created_at: "2026-05-14T10:00:00Z",
};

const videoMedia = {
  ...imageMedia,
  id: "media-video-1",
  original_filename: "patrol_clip.mp4",
  media_type: "video",
  mime_type: "video/mp4",
  frame_count: 180,
  fps: 30,
  duration_seconds: 6,
};

const queuedJob = {
  id: "job-1",
  user_id: "user-1",
  media_file_id: "media-image-1",
  model_version_id: "model-1",
  status: "queued",
  input_params_json: {},
  summary_json: null,
  error_message: null,
  progress_percent: 0,
  last_heartbeat_at: null,
  locked_by: null,
  locked_at: null,
  retry_count: 0,
  started_at: null,
  completed_at: null,
  created_at: "2026-05-14T10:01:00Z",
  updated_at: "2026-05-14T10:01:00Z",
  media: {
    id: "media-image-1",
    original_filename: "drone_frame.jpg",
    media_type: "image",
    width: 1280,
    height: 720,
    frame_count: 1,
    fps: null,
    duration_seconds: null,
  },
  model: {
    id: "model-1",
    name: "YOLO26s-v1.2",
    model_family: "YOLO26",
    variant: "s",
  },
};

const completedJob = {
  ...queuedJob,
  status: "completed",
  progress_percent: 100,
  completed_at: "2026-05-14T10:03:00Z",
  updated_at: "2026-05-14T10:03:00Z",
};

const failedJob = {
  ...queuedJob,
  status: "failed",
  progress_percent: 44,
  error_message: "model path C:\\storage\\secret\\weights.pt missing",
  updated_at: "2026-05-14T10:02:00Z",
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

function setupUploadFetch(options: {
  media?: unknown;
  job?: unknown;
  jobDetail?: unknown;
  models?: unknown;
  failMedia?: boolean;
  failJob?: boolean;
} = {}) {
  const requests: { path: string; method: string; body?: BodyInit | null }[] = [];
  const fetchMock = vi.fn((input: RequestInfo | URL, init?: RequestInit) => {
    const url = new URL(String(input));
    const method = init?.method ?? "GET";
    requests.push({ path: `${url.pathname}${url.search}`, method, body: init?.body });

    if (url.pathname === "/api/models") {
      return json(options.models ?? { items: [model], total: 1, limit: 100, offset: 0 });
    }
    if (url.pathname === "/api/media" && method === "POST") {
      if (options.failMedia) {
        return json({ detail: "C:\\storage\\secret\\traceback.txt" }, 500);
      }
      return json(options.media ?? imageMedia);
    }
    if (url.pathname === "/api/jobs" && method === "POST") {
      if (options.failJob) {
        return json({ detail: "Traceback: C:\\storage\\secret\\job.log" }, 500);
      }
      return json(options.job ?? queuedJob);
    }
    if (url.pathname === "/api/jobs/job-1") {
      return json(options.jobDetail ?? completedJob);
    }
    return json({ detail: `unexpected ${url.pathname}${url.search}` }, 500);
  });
  vi.stubGlobal("fetch", fetchMock);
  return { fetchMock, requests };
}

async function renderUpload() {
  tokenStorage.set("jwt-token");
  render(<App authApi={authApi()} initialEntries={["/upload"]} />);
  expect(await screen.findByRole("heading", { name: "Завантаження" })).toBeInTheDocument();
}

describe("Phase 26 upload page", () => {
  beforeEach(() => {
    localStorage.clear();
    vi.restoreAllMocks();
  });

  it("renders protected upload guidance and model loading without exposing storage paths", async () => {
    const { fetchMock } = setupUploadFetch();

    await renderUpload();

    expect(screen.getByText(/JPG, JPEG, PNG, WEBP/)).toBeInTheDocument();
    expect(screen.getByText(/20 МБ/)).toBeInTheDocument();
    expect(screen.getByText(/500 МБ/)).toBeInTheDocument();
    const modelSelect = await screen.findByRole("combobox", { name: "Модель" });
    await waitFor(() => expect(modelSelect).toHaveValue("model-1"));
    expect(screen.queryByText("models/yolo26s-v1.2.pt")).not.toBeInTheDocument();
    expect(fetchMock).toHaveBeenCalled();
  });

  it("rejects unsupported file extensions before media upload", async () => {
    const { fetchMock } = setupUploadFetch();
    await renderUpload();

    fireEvent.change(screen.getByLabelText("Виберіть файл для обробки"), {
      target: { files: [new File(["bad"], "notes.txt", { type: "text/plain" })] },
    });

    expect(await screen.findByText("Формат файлу не підтримується.")).toBeInTheDocument();
    expect(fetchMock.mock.calls.some(([url]) => String(url).includes("/api/media"))).toBe(false);
  });

  it("uploads a valid image and creates a job without tracker_type or frame_stride", async () => {
    const { requests } = setupUploadFetch();
    await renderUpload();

    await userEvent.upload(
      screen.getByLabelText("Виберіть файл для обробки"),
      new File(["image"], "drone_frame.jpg", { type: "image/jpeg" }),
    );
    await userEvent.click(screen.getByRole("button", { name: "Запустити обробку" }));

    await screen.findByText("Обробку завершено успішно");
    const mediaRequest = requests.find((request) => request.path === "/api/media");
    const jobRequest = requests.find((request) => request.path === "/api/jobs");
    expect(mediaRequest?.body).toBeInstanceOf(FormData);
    expect((mediaRequest?.body as FormData).get("file")).toBeInstanceOf(File);
    expect(JSON.parse(String(jobRequest?.body))).toEqual({
      media_id: "media-image-1",
      model_version_id: "model-1",
      confidence_threshold: 0.25,
      iou_threshold: 0.45,
    });
    expect(screen.queryByText("frame_stride")).not.toBeInTheDocument();
  });

  it("shows tracker control only for video and sends lowercase tracker value", async () => {
    const { requests } = setupUploadFetch({ media: videoMedia, job: { ...queuedJob, media_file_id: "media-video-1" } });
    await renderUpload();

    await userEvent.upload(
      screen.getByLabelText("Виберіть файл для обробки"),
      new File(["video"], "patrol_clip.mp4", { type: "video/mp4" }),
    );
    await userEvent.selectOptions(await screen.findByLabelText("Трекер"), "botsort");
    await userEvent.click(screen.getByRole("button", { name: "Запустити обробку" }));

    await waitFor(() => expect(requests.some((request) => request.path === "/api/jobs")).toBe(true));
    const jobRequest = requests.find((request) => request.path === "/api/jobs");
    expect(JSON.parse(String(jobRequest?.body))).toMatchObject({ tracker_type: "botsort" });
  });

  it("maps backend internals to safe Ukrainian errors", async () => {
    setupUploadFetch({ failMedia: true });
    tokenStorage.set("jwt-token");
    const { container } = render(<App authApi={authApi()} initialEntries={["/upload"]} />);

    expect(await screen.findByRole("heading", { name: "Завантаження" })).toBeInTheDocument();
    await userEvent.upload(
      screen.getByLabelText("Виберіть файл для обробки"),
      new File(["image"], "drone_frame.jpg", { type: "image/jpeg" }),
    );
    await userEvent.click(screen.getByRole("button", { name: "Запустити обробку" }));

    expect(await screen.findByText("Не вдалося завантажити файл. Перевірте формат і розмір, потім повторіть.")).toBeInTheDocument();
    expect(container).not.toHaveTextContent("C:\\storage\\secret\\traceback.txt");
    expect(container).not.toHaveTextContent("null");
    expect(container).not.toHaveTextContent("undefined");
  });

  it("omits model_version_id when model list is empty", async () => {
    const { requests } = setupUploadFetch({ models: { items: [], total: 0, limit: 100, offset: 0 } });
    await renderUpload();

    expect(await screen.findByText("Модель не вибрано. Система застосує активну модель, якщо вона доступна.")).toBeInTheDocument();
    await userEvent.upload(
      screen.getByLabelText("Виберіть файл для обробки"),
      new File(["image"], "drone_frame.jpg", { type: "image/jpeg" }),
    );
    await userEvent.click(screen.getByRole("button", { name: "Запустити обробку" }));

    await waitFor(() => expect(requests.some((request) => request.path === "/api/jobs")).toBe(true));
    const jobRequest = requests.find((request) => request.path === "/api/jobs");
    expect(JSON.parse(String(jobRequest?.body))).not.toHaveProperty("model_version_id");
  });

  it("maps failed job creation to a safe Ukrainian error", async () => {
    setupUploadFetch({ failJob: true });
    tokenStorage.set("jwt-token");
    const { container } = render(<App authApi={authApi()} initialEntries={["/upload"]} />);

    expect(await screen.findByRole("heading", { name: "Завантаження" })).toBeInTheDocument();
    await userEvent.upload(
      screen.getByLabelText("Виберіть файл для обробки"),
      new File(["image"], "drone_frame.jpg", { type: "image/jpeg" }),
    );
    await userEvent.click(screen.getByRole("button", { name: "Запустити обробку" }));

    expect(await screen.findByText("Не вдалося створити завдання. Перевірте параметри й повторіть.")).toBeInTheDocument();
    expect(container).not.toHaveTextContent("Traceback");
    expect(container).not.toHaveTextContent("C:\\storage\\secret\\job.log");
  });

  it("renders queued status block and completed link after polling", async () => {
    setupUploadFetch();
    await renderUpload();

    await userEvent.upload(
      screen.getByLabelText("Виберіть файл для обробки"),
      new File(["image"], "drone_frame.jpg", { type: "image/jpeg" }),
    );
    await userEvent.click(screen.getByRole("button", { name: "Запустити обробку" }));

    const status = await screen.findByTestId("upload-job-status");
    expect(await within(status).findByText("Обробку завершено успішно")).toBeInTheDocument();
    expect(within(status).getByRole("link", { name: "Відкрити результати" })).toHaveAttribute("href", "/jobs/job-1");
  });

  it("renders failed job status with safe Ukrainian wording", async () => {
    setupUploadFetch({ jobDetail: failedJob });
    tokenStorage.set("jwt-token");
    const { container } = render(<App authApi={authApi()} initialEntries={["/upload"]} />);

    expect(await screen.findByRole("heading", { name: "Завантаження" })).toBeInTheDocument();
    await userEvent.upload(
      screen.getByLabelText("Виберіть файл для обробки"),
      new File(["image"], "drone_frame.jpg", { type: "image/jpeg" }),
    );
    await userEvent.click(screen.getByRole("button", { name: "Запустити обробку" }));

    const status = await screen.findByTestId("upload-job-status");
    expect(await within(status).findByText("Збій")).toBeInTheDocument();
    expect(within(status).getByText("Обробку зупинено. Перевірте деталі завдання.")).toBeInTheDocument();
    expect(container).not.toHaveTextContent("C:\\storage\\secret\\weights.pt");
  });
});
