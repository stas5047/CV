import { ApiError, apiRequest } from "./client";
import type { TokenResponse, User } from "./types";

export { ApiError };
export type { TokenResponse, User };

export interface AuthApi {
  login(email: string, password: string): Promise<TokenResponse>;
  register(email: string, password: string): Promise<User>;
  getCurrentUser(): Promise<User>;
}

export const authApi: AuthApi = {
  login(email, password) {
    return apiRequest<TokenResponse>("/auth/login", {
      method: "POST",
      body: { email, password },
    });
  },
  register(email, password) {
    return apiRequest<User>("/auth/register", {
      method: "POST",
      body: { email, password },
    });
  },
  getCurrentUser() {
    return apiRequest<User>("/auth/me");
  },
};
