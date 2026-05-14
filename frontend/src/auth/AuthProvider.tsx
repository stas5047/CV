import { useCallback, useEffect, useMemo, useState, type ReactNode } from "react";
import { useQuery, useQueryClient } from "@tanstack/react-query";
import { ApiError, type AuthApi, authApi as defaultAuthApi } from "../api/auth";
import { AuthContext, type AuthContextValue } from "./AuthContext";
import { tokenStorage } from "./tokenStorage";

export function AuthProvider({
  children,
  authApi = defaultAuthApi,
}: {
  children: ReactNode;
  authApi?: AuthApi;
}) {
  const queryClient = useQueryClient();
  const [token, setTokenState] = useState<string | null>(() => tokenStorage.get());

  const currentUser = useQuery({
    queryKey: ["auth", "me", token],
    queryFn: authApi.getCurrentUser,
    enabled: Boolean(token),
    retry: false,
  });

  useEffect(() => {
    const status = currentUser.error instanceof ApiError ? currentUser.error.status : null;
    if ((status === 401 || status === 403) && token) {
      tokenStorage.clear();
      setTokenState(null);
      queryClient.removeQueries({ queryKey: ["auth"] });
    }
  }, [currentUser.error, queryClient, token]);

  const setToken = useCallback(
    (nextToken: string) => {
      tokenStorage.set(nextToken);
      setTokenState(nextToken);
      void queryClient.invalidateQueries({ queryKey: ["auth"] });
    },
    [queryClient],
  );

  const logout = useCallback(() => {
    tokenStorage.clear();
    setTokenState(null);
    queryClient.removeQueries({ queryKey: ["auth"] });
  }, [queryClient]);

  const value = useMemo<AuthContextValue>(
    () => ({
      user: token ? (currentUser.data ?? null) : null,
      token,
      isLoading: Boolean(token) && currentUser.isLoading,
      authApi,
      setToken,
      logout,
    }),
    [authApi, currentUser.data, currentUser.isLoading, logout, setToken, token],
  );

  return <AuthContext.Provider value={value}>{children}</AuthContext.Provider>;
}
