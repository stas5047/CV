import { useAuth } from "./useAuth";
import { ForbiddenPage } from "../pages/ForbiddenPage";

export function AdminRoute({ children }: { children: React.ReactNode }) {
  const { user } = useAuth();
  if (user?.role !== "admin") {
    return <ForbiddenPage />;
  }
  return <>{children}</>;
}
