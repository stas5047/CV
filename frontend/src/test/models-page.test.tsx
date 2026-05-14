import { render, screen, waitFor, within } from "@testing-library/react";
import userEvent from "@testing-library/user-event";
import { beforeEach, describe, expect, it, vi } from "vitest";
import { App } from "../App";
import type { AuthApi } from "../api/auth";
import type { User } from "../api/types";
import { tokenStorage } from "../auth/tokenStorage";

const regularUser = {
  id: "user-1",
  email: "operator@example.com",
  role: "user" as const,
  is_active: true,
  created_at: "2026-05-14T00:00:00Z",
  updated_at: "2026-05-14T00:00:00Z",
};

const adminUser = {
  ...regularUser,
  id: "admin-1",
  email: "admin@example.com",
  role: "admin" as const,
};

const yolo26Model = {
  id: "model-1",
  name: "YOLO26s-seraphim-v1",
  model_family: "YOLO26",
  variant: "s",
  weights_path: "models/yolo26s-seraphim-v1/weights.pt",
  dataset_name: "Seraphim Drone Detection Dataset",
  dataset_split_description: "16 000 train / 2 000 val / 2 000 test",
  metrics_json: {
    precision: 0.912,
    recall: 0.876,
    map50: 0.891,
    map50_95: 0.734,
    model_size_mb: 22.4,
    fps: 47.2,
  },
  is_active: true,
  created_by_user_id: "admin-1",
  created_at: "2026-05-14T00:00:00Z",
  updated_at: "2026-05-14T00:00:00Z",
};

const yolo11FallbackModel = {
  id: "model-2",
  name: "YOLO11s-fallback-seraphim",
  model_family: "YOLO11",
  variant: "s",
  weights_path: "models/yolo11s-fallback/weights.pt",
  dataset_name: "Seraphim fallback",
  dataset_split_description: null,
  metrics_json: {},
  is_active: false,
  created_by_user_id: "admin-1",
  created_at: "2026-05-13T00:00:00Z",
  updated_at: "2026-05-13T00:00:00Z",
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

describe("Phase 28 models page", () => {
  beforeEach(() => {
    localStorage.clear();
    vi.restoreAllMocks();
  });

  it("redirects guests from models registry to login", async () => {
    render(<App authApi={authApi()} initialEntries={["/models"]} />);

    expect(await screen.findByRole("heading", { name: /AeroVision/ })).toBeInTheDocument();
  });

  it("renders model registry for regular users without admin controls or unsafe values", async () => {
    tokenStorage.set("jwt-token");
    const fetchMock = vi.fn((input: RequestInfo | URL) => {
      const url = new URL(String(input));
      if (url.pathname === "/api/models") {
        return json({ items: [yolo26Model, yolo11FallbackModel], total: 2, limit: 100, offset: 0 });
      }
      return json({ detail: `unexpected ${url.pathname}` }, 500);
    });
    vi.stubGlobal("fetch", fetchMock);

    const { container } = render(<App authApi={authApi()} initialEntries={["/models"]} />);

    expect(await screen.findByRole("heading", { name: "Реєстр моделей" })).toBeInTheDocument();
    expect(screen.getAllByText("YOLO26s-seraphim-v1").length).toBeGreaterThan(0);
    expect(screen.getByText("YOLO26 · s")).toBeInTheDocument();
    expect(screen.getByText("Seraphim Drone Detection Dataset")).toBeInTheDocument();
    expect(screen.getByText("16 000 train / 2 000 val / 2 000 test")).toBeInTheDocument();
    expect(screen.getByText(/22,4 МБ/)).toBeInTheDocument();
    expect(screen.getByText(/47,2 FPS/)).toBeInTheDocument();
    expect(screen.getByText("YOLO11 · s")).toBeInTheDocument();
    expect(screen.getByText("Документований fallback")).toBeInTheDocument();
    expect(screen.getAllByText("Немає даних").length).toBeGreaterThan(0);
    expect(screen.queryByRole("button", { name: /Зареєструвати модель/ })).not.toBeInTheDocument();
    expect(screen.queryByRole("button", { name: /Активувати/ })).not.toBeInTheDocument();
    expect(fetchMock.mock.calls.some(([url]) => String(url).includes("/activate"))).toBe(false);
    expect(container).not.toHaveTextContent("weights_path");
    expect(container).not.toHaveTextContent("models/yolo26s-seraphim-v1/weights.pt");
    expect(container).not.toHaveTextContent("null");
    expect(container).not.toHaveTextContent("undefined");
    expect(container).not.toHaveTextContent("frame_stride");
    expect(container).not.toHaveTextContent("/app/storage");
    expect(container).not.toHaveTextContent("C:\\");
  });

  it("lets admins register a relative-path model and activate another model", async () => {
    tokenStorage.set("jwt-token");
    let activeId = "model-1";
    const fetchMock = vi.fn((input: RequestInfo | URL, init?: RequestInit) => {
      const url = new URL(String(input));
      if (url.pathname === "/api/models" && init?.method === "POST") {
        return json(
          {
            id: "model-3",
            name: "YOLO26n-smoke",
            model_family: "YOLO26",
            variant: "n",
            weights_path: "models/yolo26n-smoke/weights.pt",
            dataset_name: "Seraphim smoke",
            dataset_split_description: "tiny smoke split",
            metrics_json: {},
            is_active: false,
            created_by_user_id: "admin-1",
            created_at: "2026-05-15T00:00:00Z",
            updated_at: "2026-05-15T00:00:00Z",
          },
          201,
        );
      }
      if (url.pathname === "/api/models/model-2/activate" && init?.method === "PATCH") {
        activeId = "model-2";
        return json({ ...yolo11FallbackModel, is_active: true });
      }
      if (url.pathname === "/api/models") {
        return json({
          items: [
            { ...yolo26Model, is_active: activeId === "model-1" },
            { ...yolo11FallbackModel, is_active: activeId === "model-2" },
          ],
          total: 2,
          limit: 100,
          offset: 0,
        });
      }
      return json({ detail: `unexpected ${url.pathname}` }, 500);
    });
    vi.stubGlobal("fetch", fetchMock);

    render(<App authApi={authApi(adminUser)} initialEntries={["/models"]} />);

    await screen.findByRole("heading", { name: "Реєстр моделей" });
    await userEvent.click(screen.getByRole("button", { name: /Зареєструвати модель/ }));
    await userEvent.type(screen.getByLabelText("Назва моделі"), "YOLO26n-smoke");
    await userEvent.selectOptions(screen.getByLabelText("Сімейство"), "YOLO26");
    await userEvent.type(screen.getByLabelText("Варіант"), "n");
    await userEvent.type(screen.getByLabelText(/Відносний шлях до ваг/), "models/yolo26n-smoke/weights.pt");
    await userEvent.type(screen.getByLabelText("Датасет"), "Seraphim smoke");
    await userEvent.type(screen.getByLabelText("Опис split"), "tiny smoke split");
    await userEvent.click(screen.getByRole("button", { name: "Зберегти модель" }));

    await waitFor(() => {
      const postCall = fetchMock.mock.calls.find(
        ([url, init]) => String(url).includes("/api/models") && init?.method === "POST",
      );
      expect(postCall).toBeTruthy();
      expect(JSON.parse(String(postCall?.[1]?.body))).toMatchObject({
        name: "YOLO26n-smoke",
        model_family: "YOLO26",
        variant: "n",
        weights_path: "models/yolo26n-smoke/weights.pt",
        dataset_name: "Seraphim smoke",
        dataset_split_description: "tiny smoke split",
        is_active: false,
      });
    });

    const fallbackCard = screen.getByTestId("model-card-model-2");
    await userEvent.click(within(fallbackCard).getByRole("button", { name: "Активувати" }));

    await waitFor(() => {
      expect(fetchMock.mock.calls.some(([url, init]) => String(url).includes("/api/models/model-2/activate") && init?.method === "PATCH")).toBe(true);
    });
    await waitFor(() => {
      expect(within(screen.getByTestId("model-card-model-2")).getByText("Активна")).toBeInTheDocument();
      expect(within(screen.getByTestId("model-card-model-1")).queryByText("Активна")).not.toBeInTheDocument();
    });
  });

  it("shows a safe Ukrainian error when model activation fails", async () => {
    tokenStorage.set("jwt-token");
    const fetchMock = vi.fn((input: RequestInfo | URL, init?: RequestInit) => {
      const url = new URL(String(input));
      if (url.pathname === "/api/models/model-2/activate" && init?.method === "PATCH") {
        return json({ detail: "forbidden" }, 403);
      }
      if (url.pathname === "/api/models") {
        return json({ items: [yolo26Model, yolo11FallbackModel], total: 2, limit: 100, offset: 0 });
      }
      return json({ detail: `unexpected ${url.pathname}` }, 500);
    });
    vi.stubGlobal("fetch", fetchMock);

    render(<App authApi={authApi(adminUser)} initialEntries={["/models"]} />);

    await screen.findByRole("heading", { name: "Реєстр моделей" });
    const fallbackCard = screen.getByTestId("model-card-model-2");
    await userEvent.click(within(fallbackCard).getByRole("button", { name: "Активувати" }));

    expect(await screen.findByRole("alert")).toHaveTextContent(
      "Не вдалося активувати модель. Перевірте права доступу та повторіть запит.",
    );
    expect(screen.getByRole("alert")).not.toHaveTextContent("forbidden");
  });

  it("blocks unsafe admin weights paths before submit", async () => {
    tokenStorage.set("jwt-token");
    const fetchMock = vi.fn((input: RequestInfo | URL, init?: RequestInit) => {
      const url = new URL(String(input));
      if (url.pathname === "/api/models") {
        return json({ items: [yolo26Model], total: 1, limit: 100, offset: 0 });
      }
      void init;
      return json({ detail: "unexpected route" }, 500);
    });
    vi.stubGlobal("fetch", fetchMock);

    render(<App authApi={authApi(adminUser)} initialEntries={["/models"]} />);

    await screen.findByRole("heading", { name: "Реєстр моделей" });
    await userEvent.click(screen.getByRole("button", { name: /Зареєструвати модель/ }));
    await userEvent.type(screen.getByLabelText("Назва моделі"), "YOLO26s-bad");
    await userEvent.type(screen.getByLabelText("Варіант"), "s");
    await userEvent.type(screen.getByLabelText(/Відносний шлях до ваг/), "/app/storage/models/bad.pt");
    await userEvent.click(screen.getByRole("button", { name: "Зберегти модель" }));

    expect(await screen.findByText("Вкажіть шлях відносно сховища без абсолютних сегментів або ..")).toBeInTheDocument();
    expect(fetchMock.mock.calls.some(([, init]) => init?.method === "POST")).toBe(false);
  });

  it("renders loading, error, and empty states in Ukrainian", async () => {
    tokenStorage.set("jwt-token");
    let resolveModels: (value: Response) => void = () => undefined;
    vi.stubGlobal(
      "fetch",
      vi.fn((input: RequestInfo | URL) => {
        const url = new URL(String(input));
        if (url.pathname === "/api/models") {
          return new Promise<Response>((resolve) => {
            resolveModels = resolve;
          });
        }
        return json({ detail: "unexpected route" }, 500);
      }),
    );

    render(<App authApi={authApi()} initialEntries={["/models"]} />);

    expect((await screen.findAllByTestId("model-skeleton")).length).toBeGreaterThan(0);
    resolveModels(new Response(JSON.stringify({ detail: "boom" }), { status: 500, headers: { "Content-Type": "application/json" } }));
    expect(await screen.findByText("Не вдалося завантажити моделі")).toBeInTheDocument();
  });

  it("renders empty model registry state", async () => {
    tokenStorage.set("jwt-token");
    vi.stubGlobal(
      "fetch",
      vi.fn((input: RequestInfo | URL) => {
        const url = new URL(String(input));
        if (url.pathname === "/api/models") {
          return json({ items: [], total: 0, limit: 100, offset: 0 });
        }
        return json({ detail: "unexpected route" }, 500);
      }),
    );

    render(<App authApi={authApi()} initialEntries={["/models"]} />);

    expect(await screen.findByText("Моделі ще не зареєстровані")).toBeInTheDocument();
    expect(screen.getByText("Після реєстрації тут з'явиться активна модель, fallback-версії та метрики.")).toBeInTheDocument();
  });
});
