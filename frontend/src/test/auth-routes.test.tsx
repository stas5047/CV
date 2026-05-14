import { render, screen, waitFor } from "@testing-library/react";
import userEvent from "@testing-library/user-event";
import { beforeEach, describe, expect, it, vi } from "vitest";
import { App } from "../App";
import { ApiError, type AuthApi } from "../api/auth";
import { tokenStorage } from "../auth/tokenStorage";

const baseUser = {
  id: "user-1",
  email: "pilot@example.com",
  role: "user" as const,
  is_active: true,
  created_at: "2026-05-14T00:00:00Z",
  updated_at: "2026-05-14T00:00:00Z",
};

function authApi(overrides: Partial<AuthApi> = {}): AuthApi {
  return {
    login: vi.fn().mockResolvedValue({ access_token: "jwt-token", token_type: "bearer" }),
    register: vi.fn().mockResolvedValue({ ...baseUser, id: "user-2" }),
    getCurrentUser: vi.fn().mockResolvedValue(baseUser),
    ...overrides,
  };
}

describe("Phase 24 auth routes", () => {
  beforeEach(() => {
    localStorage.clear();
  });

  it("renders login page in Ukrainian and shows Ukrainian failed-login error", async () => {
    const api = authApi({
      login: vi.fn().mockRejectedValue(new ApiError(401, "invalid credentials")),
    });

    render(<App authApi={api} initialEntries={["/login"]} />);

    expect(screen.getByRole("heading", { name: /AeroVision/ })).toBeInTheDocument();
    await userEvent.type(screen.getByLabelText("Email"), "bad@example.com");
    await userEvent.type(screen.getByLabelText("Пароль"), "wrongpass");
    await userEvent.click(screen.getByRole("button", { name: "Увійти" }));

    expect(await screen.findByText("Невірний email або пароль.")).toBeInTheDocument();
  });

  it("validates registration password length and maps disabled registration to Ukrainian notice", async () => {
    const api = authApi({
      register: vi.fn().mockRejectedValue(new ApiError(403, "registration disabled")),
    });

    render(<App authApi={api} initialEntries={["/register"]} />);

    await userEvent.type(screen.getByLabelText("Email"), "new@example.com");
    await userEvent.type(screen.getByLabelText("Пароль"), "short");
    await userEvent.type(screen.getByLabelText("Підтвердіть пароль"), "short");
    await userEvent.click(screen.getByRole("button", { name: /Зареєструват/ }));
    expect(screen.getByText("Мінімум 8 символів.")).toBeInTheDocument();

    await userEvent.clear(screen.getByLabelText("Пароль"));
    await userEvent.type(screen.getByLabelText("Пароль"), "longpass1");
    await userEvent.clear(screen.getByLabelText("Підтвердіть пароль"));
    await userEvent.type(screen.getByLabelText("Підтвердіть пароль"), "longpass1");
    await userEvent.click(screen.getByRole("button", { name: /Зареєструват/ }));

    expect(await screen.findByText("Публічну реєстрацію вимкнено. Увійдіть через наданий обліковий запис.")).toBeInTheDocument();
  });

  it("redirects guests from protected routes to login", async () => {
    render(<App authApi={authApi()} initialEntries={["/dashboard"]} />);

    expect(await screen.findByRole("heading", { name: /AeroVision/ })).toBeInTheDocument();
  });

  it("clears token and redirects when current-user request is unauthorized", async () => {
    tokenStorage.set("expired-token");
    const api = authApi({
      getCurrentUser: vi.fn().mockRejectedValue(new ApiError(401, "unauthorized")),
    });

    render(<App authApi={api} initialEntries={["/dashboard"]} />);

    await waitFor(() => expect(tokenStorage.get()).toBeNull());
    expect(await screen.findByRole("heading", { name: /AeroVision/ })).toBeInTheDocument();
  });

  it("clears token and redirects when current user is inactive", async () => {
    tokenStorage.set("inactive-token");
    const api = authApi({
      getCurrentUser: vi.fn().mockResolvedValue({ ...baseUser, is_active: false }),
    });

    render(<App authApi={api} initialEntries={["/dashboard"]} />);

    await waitFor(() => expect(tokenStorage.get()).toBeNull());
    expect(await screen.findByRole("heading", { name: /AeroVision/ })).toBeInTheDocument();
  });

  it("hides admin navigation from regular users and rejects admin route", async () => {
    tokenStorage.set("jwt-token");

    render(<App authApi={authApi()} initialEntries={["/admin"]} />);

    expect(await screen.findByRole("heading", { name: "Доступ заборонено" })).toBeInTheDocument();
    expect(screen.queryByRole("link", { name: "Адмін" })).not.toBeInTheDocument();
  });

  it("shows admin navigation to admins", async () => {
    tokenStorage.set("jwt-token");
    const api = authApi({
      getCurrentUser: vi.fn().mockResolvedValue({ ...baseUser, role: "admin" }),
    });

    render(<App authApi={api} initialEntries={["/dashboard"]} />);

    expect(await screen.findByRole("link", { name: "Адмін" })).toBeInTheDocument();
    expect(screen.getByRole("heading", { name: "Огляд" })).toBeInTheDocument();
  });

  it("clears token on logout", async () => {
    tokenStorage.set("jwt-token");

    render(<App authApi={authApi()} initialEntries={["/dashboard"]} />);

    await screen.findByRole("heading", { name: "Огляд" });
    await userEvent.click(screen.getByRole("button", { name: "Вийти" }));

    await waitFor(() => expect(tokenStorage.get()).toBeNull());
    expect(await screen.findByRole("heading", { name: /AeroVision/ })).toBeInTheDocument();
  });
});
