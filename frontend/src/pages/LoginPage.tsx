import { useState, type FormEvent } from "react";
import { Link, Navigate, useLocation, useNavigate } from "react-router-dom";
import { ReloadIcon } from "@radix-ui/react-icons";
import { ApiError } from "../api/auth";
import { useAuth } from "../auth/useAuth";
import { Alert } from "../components/Alert";
import { useToast } from "../components/toast";
import { Button } from "../components/ui/button";
import { Input } from "../components/ui/input";
import { AuthLayout } from "./AuthLayout";

function loginErrorMessage(error: unknown) {
  if (error instanceof ApiError && (error.status === 401 || error.status === 400)) {
    return "Невірний email або пароль.";
  }
  return "Не вдалося увійти. Перевірте дані й спробуйте ще раз.";
}

export function LoginPage() {
  const { authApi, setToken, token } = useAuth();
  const navigate = useNavigate();
  const location = useLocation();
  const { toast } = useToast();
  const [email, setEmail] = useState("");
  const [password, setPassword] = useState("");
  const [error, setError] = useState("");
  const [loading, setLoading] = useState(false);

  if (token) {
    return <Navigate to="/dashboard" replace />;
  }

  const handleSubmit = async (event: FormEvent) => {
    event.preventDefault();
    setError("");
    if (!email || !password) {
      const message = "Заповніть email і пароль.";
      setError(message);
      toast({ variant: "error", title: "Форма неповна" });
      return;
    }
    setLoading(true);
    try {
      const response = await authApi.login(email, password);
      setToken(response.access_token);
      toast({ variant: "success", title: "Вхід виконано", description: "Переходимо до робочої панелі." });
      const from = (location.state as { from?: { pathname?: string } } | null)?.from?.pathname ?? "/dashboard";
      navigate(from, { replace: true });
    } catch (err) {
      const message = loginErrorMessage(err);
      setError(message);
      toast({ variant: "error", title: "Не вдалося увійти", description: "Перевірте поля форми." });
    } finally {
      setLoading(false);
    }
  };

  return (
    <AuthLayout subtitle="Система комп'ютерного зору для аналізу медіафайлів">
      <form className="flex flex-col gap-3.5" onSubmit={handleSubmit}>
        <div className="space-y-2">
          <label className="av-label" htmlFor="email">
            Email
          </label>
          <Input
            id="email"
            type="email"
            autoComplete="email"
            placeholder="email@example.com"
            value={email}
            onChange={(event) => setEmail(event.target.value)}
          />
        </div>
        <div className="space-y-2">
          <label className="av-label" htmlFor="password">
            Пароль
          </label>
          <Input
            id="password"
            type="password"
            autoComplete="current-password"
            placeholder="••••••••"
            value={password}
            onChange={(event) => setPassword(event.target.value)}
          />
        </div>
        {error ? <Alert>{error}</Alert> : null}
        <Button className="mt-0.5 w-full" disabled={loading} type="submit">
          {loading ? <ReloadIcon className="h-4 w-4 animate-spin" /> : null}
          Увійти
        </Button>
      </form>
      <p className="text-center text-xs text-muted-foreground">
        Немає акаунту?{" "}
        <Link className="av-link" to="/register">
          Зареєструватись
        </Link>
      </p>
    </AuthLayout>
  );
}
