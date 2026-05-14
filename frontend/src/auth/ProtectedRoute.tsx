import { Navigate, Outlet, useLocation } from "react-router-dom";
import { useEffect } from "react";
import { useAuth } from "./useAuth";
import { SkeletonPage } from "../components/SkeletonPage";

export function ProtectedRoute() {
  const location = useLocation();
  const { token, user, isLoading, logout } = useAuth();
  const shouldLogout = Boolean(token) && !isLoading && (!user || !user.is_active);

  useEffect(() => {
    if (shouldLogout) {
      logout();
    }
  }, [logout, shouldLogout]);

  if (!token) {
    return <Navigate to="/login" replace state={{ from: location }} />;
  }

  if (isLoading) {
    return <SkeletonPage />;
  }

  if (shouldLogout) {
    return <Navigate to="/login" replace />;
  }

  return <Outlet />;
}
