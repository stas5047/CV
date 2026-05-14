import { render, screen, within } from "@testing-library/react";
import userEvent from "@testing-library/user-event";
import { beforeEach, describe, expect, it, vi } from "vitest";
import { App } from "../App";
import type { AuthApi } from "../api/auth";
import type { ExperimentRun, User } from "../api/types";
import { tokenStorage } from "../auth/tokenStorage";

const DOCS_REQUIRED_EXPERIMENT_EMPTY_TEXT = "Дані експерименту ще не завантажено";

const regularUser = {
  id: "user-1",
  email: "operator@example.com",
  role: "user" as const,
  is_active: true,
  created_at: "2026-05-14T00:00:00Z",
  updated_at: "2026-05-14T00:00:00Z",
};

const metricBase = {
  experiment_run_id: "exp",
  created_at: "2026-05-15T00:00:00Z",
};

function authApi(user: User = regularUser): AuthApi {
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

function metric(name: string, value: number | null, unit: string | null = null, metadata: Record<string, unknown> = {}) {
  return {
    ...metricBase,
    id: `metric-${name}-${Math.random()}`,
    metric_name: name,
    metric_value: value,
    metric_unit: unit,
    metadata_json: metadata,
  };
}

function run(overrides: Partial<ExperimentRun>): ExperimentRun {
  return {
    id: overrides.id ?? "exp-1",
    name: overrides.name ?? "YOLO26s-seraphim-v1",
    experiment_type: overrides.experiment_type ?? "model_comparison",
    description: overrides.description ?? null,
    model_version_id: overrides.model_version_id ?? null,
    dataset_name: overrides.dataset_name ?? "Seraphim",
    config_json: overrides.config_json ?? {},
    artifacts_path: overrides.artifacts_path ?? null,
    is_published: overrides.is_published ?? true,
    created_by_user_id: overrides.created_by_user_id ?? "admin-1",
    created_at: overrides.created_at ?? "2026-05-15T00:00:00Z",
    metrics: overrides.metrics ?? [],
  };
}

const experimentItems: ExperimentRun[] = [
  run({
    id: "model-n",
    name: "YOLO26n-seraphim-v1",
    metrics: [
      metric("precision", 0.867),
      metric("recall", 0.821),
      metric("map50", 0.843),
      metric("map50_95", 0.681),
      metric("fps", 42.6),
      metric("latency_ms", 23.4),
    ],
  }),
  run({
    id: "model-s",
    name: "YOLO26s-seraphim-v1",
    metrics: [
      metric("precision", 0.912),
      metric("recall", 0.876),
      metric("map50", 0.891),
      metric("map50_95", 0.734),
      metric("fps", 31.8),
      metric("latency_ms", 31.5),
    ],
  }),
  run({
    id: "threshold-25",
    name: "confidence 0.25",
    experiment_type: "threshold_analysis",
    config_json: { confidence_threshold: 0.25 },
    metrics: [metric("precision", 0.781), metric("recall", 0.932), metric("f1", 0.85), metric("false_positive_rate", 0.092)],
  }),
  run({
    id: "threshold-70",
    name: "confidence 0.70",
    experiment_type: "threshold_analysis",
    config_json: { confidence_threshold: 0.7 },
    metrics: [metric("precision", 0.934), metric("recall", 0.701), metric("f1", 0.801), metric("false_positive_rate", 0.021)],
  }),
  run({
    id: "tracker-bt",
    name: "ByteTrack behavior",
    experiment_type: "tracker_comparison",
    config_json: { tracker_type: "bytetrack" },
    metrics: [
      metric("video_fps", 34.2, "FPS"),
      metric("unique_track_ids", 18),
      metric("frames_with_detections", 420),
      metric("average_confidence", 0.81),
      metric("track_fragmentation_proxy", 0.17),
      metric("visual_stability", null, null, { label: "Стабільна" }),
      metric("mota", 0.99),
    ],
  }),
  run({
    id: "tracker-bs",
    name: "BoT-SORT behavior",
    experiment_type: "tracker_comparison",
    config_json: { tracker_type: "botsort" },
    metrics: [
      metric("video_fps", 28.1, "FPS"),
      metric("unique_track_ids", 21),
      metric("frames_with_detections", 416),
      metric("average_confidence", 0.8),
      metric("track_fragmentation_proxy", 0.22),
      metric("visual_stability", null, null, { label: "Помірна" }),
      metric("idf1", 0.98),
    ],
  }),
  run({
    id: "fp",
    name: "Bird vs Drone review",
    experiment_type: "false_positive_analysis",
    metrics: [
      metric("false_positive_rate", 0.032),
      metric("bird_false_detections", 18),
      metric("reviewed_images", 562),
      metric("true_positive_rate", 0.968),
    ],
  }),
];

describe("Phase 29 experiments page", () => {
  beforeEach(() => {
    localStorage.clear();
    vi.restoreAllMocks();
  });

  it("redirects guests from experiments to login", async () => {
    render(<App authApi={authApi()} initialEntries={["/experiments"]} />);

    expect(await screen.findByRole("heading", { name: /AeroVision/ })).toBeInTheDocument();
  });

  it("renders experiment metrics with Recharts sections and no unsafe raw values", async () => {
    tokenStorage.set("jwt-token");
    const fetchMock = vi.fn((input: RequestInfo | URL) => {
      const url = new URL(String(input));
      if (url.pathname === "/api/experiments") {
        return json({ items: experimentItems, total: experimentItems.length, limit: 100, offset: 0 });
      }
      return json({ detail: `unexpected ${url.pathname}` }, 500);
    });
    vi.stubGlobal("fetch", fetchMock);

    const { container } = render(<App authApi={authApi()} initialEntries={["/experiments"]} />);

    expect(await screen.findByRole("heading", { name: "Досліди та метрики" })).toBeInTheDocument();
    expect(screen.getAllByText("YOLO26n-seraphim-v1").length).toBeGreaterThan(0);
    expect(screen.getAllByText("YOLO26s-seraphim-v1").length).toBeGreaterThan(0);
    expect(screen.getAllByText("Recharts").length).toBeGreaterThan(0);
    expect(screen.getAllByText("FPS / latency").length).toBeGreaterThan(0);
    expect(screen.getAllByText(DOCS_REQUIRED_EXPERIMENT_EMPTY_TEXT).length).toBeGreaterThan(0);

    await userEvent.click(screen.getByRole("button", { name: "Поріг впевненості" }));
    expect(screen.getByText("0.25")).toBeInTheDocument();
    expect(screen.getByText("0.70")).toBeInTheDocument();

    await userEvent.click(screen.getByRole("button", { name: "tracker behavior comparison" }));
    expect(screen.getByRole("heading", { name: "tracker behavior comparison" })).toBeInTheDocument();
    expect(screen.getByText("Video FPS")).toBeInTheDocument();
    expect(screen.getByText("Проксі фрагментації треку")).toBeInTheDocument();
    expect(screen.queryByText(/mota/i)).not.toBeInTheDocument();
    expect(screen.queryByText(/idf1/i)).not.toBeInTheDocument();
    expect(screen.queryByText(/hota/i)).not.toBeInTheDocument();

    await userEvent.click(screen.getByRole("button", { name: "Хибнопозитивні" }));
    expect(screen.getByText("Частка хибнопозитивних")).toBeInTheDocument();
    expect(screen.getByText("Хибні виявлення птахів")).toBeInTheDocument();

    expect(container).not.toHaveTextContent("null");
    expect(container).not.toHaveTextContent("undefined");
    expect(container).not.toHaveTextContent("frame_stride");
    expect(container).not.toHaveTextContent("artifacts_path");
    expect(container).not.toHaveTextContent("/app/storage");
    expect(container).not.toHaveTextContent("storage/");
    expect(container).not.toHaveTextContent("C:\\");
    expect(fetchMock.mock.calls.some(([url]) => String(url).includes("is_published"))).toBe(false);
    expect(fetchMock.mock.calls.some(([url]) => String(url).includes("limit=100"))).toBe(true);
  });

  it("shows required empty state for missing experiment sections and null metrics", async () => {
    tokenStorage.set("jwt-token");
    const items = [
      run({
        id: "empty-model",
        artifacts_path: "reports/unsafe/confusion.png",
        metrics: [metric("precision", null), metric("recall", null)],
      }),
    ];
    vi.stubGlobal(
      "fetch",
      vi.fn((input: RequestInfo | URL) => {
        const url = new URL(String(input));
        if (url.pathname === "/api/experiments") {
          return json({ items, total: 1, limit: 100, offset: 0 });
        }
        return json({ detail: "unexpected route" }, 500);
      }),
    );

    const { container } = render(<App authApi={authApi()} initialEntries={["/experiments"]} />);

    expect(await screen.findByRole("heading", { name: "Досліди та метрики" })).toBeInTheDocument();
    expect(screen.getAllByText(DOCS_REQUIRED_EXPERIMENT_EMPTY_TEXT).length).toBeGreaterThan(0);
    expect(screen.queryByRole("img", { name: "Матриця помилок" })).not.toBeInTheDocument();
    expect(container).not.toHaveTextContent("reports/unsafe/confusion.png");
    expect(container).not.toHaveTextContent("null");
    expect(container).not.toHaveTextContent("undefined");
  });

  it("renders loading and safe Ukrainian error states", async () => {
    tokenStorage.set("jwt-token");
    let resolveExperiments: (value: Response) => void = () => undefined;
    vi.stubGlobal(
      "fetch",
      vi.fn((input: RequestInfo | URL) => {
        const url = new URL(String(input));
        if (url.pathname === "/api/experiments") {
          return new Promise<Response>((resolve) => {
            resolveExperiments = resolve;
          });
        }
        return json({ detail: "unexpected route" }, 500);
      }),
    );

    render(<App authApi={authApi()} initialEntries={["/experiments"]} />);

    expect((await screen.findAllByTestId("experiment-skeleton")).length).toBeGreaterThan(0);
    resolveExperiments(new Response(JSON.stringify({ detail: "database down" }), { status: 500, headers: { "Content-Type": "application/json" } }));
    expect(await screen.findByText("Не вдалося завантажити досліди")).toBeInTheDocument();
    expect(screen.getByText("Повторити")).toBeInTheDocument();
    expect(screen.queryByText("database down")).not.toBeInTheDocument();
  });

  it("renders all-section empty state when no experiments are returned", async () => {
    tokenStorage.set("jwt-token");
    vi.stubGlobal(
      "fetch",
      vi.fn((input: RequestInfo | URL) => {
        const url = new URL(String(input));
        if (url.pathname === "/api/experiments") {
          return json({ items: [], total: 0, limit: 100, offset: 0 });
        }
        return json({ detail: "unexpected route" }, 500);
      }),
    );

    const { container } = render(<App authApi={authApi()} initialEntries={["/experiments"]} />);

    const page = await screen.findByRole("heading", { name: "Досліди та метрики" });
    expect(page).toBeInTheDocument();
    expect(screen.getAllByText(DOCS_REQUIRED_EXPERIMENT_EMPTY_TEXT).length).toBeGreaterThan(0);
    expect(within(container).queryByText("Matplotlib")).not.toBeInTheDocument();
  });
});
