import { createContext } from "react";
import type { AuthApi } from "../api/auth";
import type { User } from "../api/types";

export interface AuthContextValue {
  user: User | null;
  token: string | null;
  isLoading: boolean;
  authApi: AuthApi;
  setToken(token: string): void;
  logout(): void;
}

export const AuthContext = createContext<AuthContextValue | null>(null);
