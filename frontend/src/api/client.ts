import { tokenStorage } from "../auth/tokenStorage";

export class ApiError extends Error {
  constructor(
    readonly status: number,
    message: string,
    readonly data?: unknown,
  ) {
    super(message);
    this.name = "ApiError";
  }
}

const API_BASE_URL = import.meta.env.VITE_API_BASE_URL ?? "http://localhost:8000/api";

type RequestOptions = Omit<RequestInit, "body"> & {
  body?: unknown;
  token?: string | null;
};

async function parseResponse(response: Response) {
  const contentType = response.headers.get("content-type") ?? "";
  if (response.status === 204) return null;
  if (contentType.includes("application/json")) return response.json();
  return response.text();
}

export async function apiRequest<T>(path: string, options: RequestOptions = {}): Promise<T> {
  const token = options.token ?? tokenStorage.get();
  const headers = new Headers(options.headers);
  headers.set("Accept", "application/json");

  if (options.body !== undefined && !(options.body instanceof FormData)) {
    headers.set("Content-Type", "application/json");
  }

  if (token) {
    headers.set("Authorization", `Bearer ${token}`);
  }

  const response = await fetch(`${API_BASE_URL}${path}`, {
    ...options,
    headers,
    body: options.body instanceof FormData ? options.body : JSON.stringify(options.body),
  });
  const data = await parseResponse(response);

  if (!response.ok) {
    const message =
      typeof data === "object" && data !== null && "detail" in data
        ? String((data as { detail: unknown }).detail)
        : response.statusText;
    throw new ApiError(response.status, message, data);
  }

  return data as T;
}

export async function apiBlobRequest(path: string, options: RequestOptions = {}): Promise<Blob> {
  const token = options.token ?? tokenStorage.get();
  const fetchOptions = { ...options } as Record<string, unknown>;
  delete fetchOptions.body;
  delete fetchOptions.token;
  const headers = new Headers(options.headers);
  const locationOrigin = globalThis.location?.origin ?? "http://localhost";
  const apiBase = new URL(API_BASE_URL, locationOrigin);
  const url = path.startsWith("http")
    ? new URL(path)
    : new URL(`${API_BASE_URL}${path.startsWith("/api/") ? path.slice(4) : path}`, locationOrigin);

  const apiPath = apiBase.pathname.replace(/\/$/, "");
  const isApiPath = url.pathname === apiPath || url.pathname.startsWith(`${apiPath}/`);
  if (url.origin !== apiBase.origin || !isApiPath) {
    throw new ApiError(400, "Unsafe download URL");
  }

  if (token) {
    headers.set("Authorization", `Bearer ${token}`);
  }

  const response = await fetch(url.toString(), {
    ...(fetchOptions as RequestInit),
    headers,
  });

  if (!response.ok) {
    const data = await parseResponse(response);
    const message =
      typeof data === "object" && data !== null && "detail" in data
        ? String((data as { detail: unknown }).detail)
        : response.statusText;
    throw new ApiError(response.status, message, data);
  }

  return response.blob();
}
