import { useState, type FormEvent } from "react";
import { Link, useNavigate } from "react-router-dom";
import { ReloadIcon } from "@radix-ui/react-icons";
import { ApiError } from "../api/auth";
import { useAuth } from "../auth/useAuth";
import { Alert } from "../components/Alert";
import { Button } from "../components/ui/button";
import { Input } from "../components/ui/input";
import { AuthLayout } from "./AuthLayout";

function registerErrorMessage(error: unknown) {
  if (error instanceof ApiError && error.status === 403) {
    return "Публічну реєстрацію вимкнено. Увійдіть через наданий обліковий запис.";
  }
  if (error instanceof ApiError && error.status === 409) {
    return "Обліковий запис з таким email вже існує.";
  }
  return "Не вдалося створити обліковий запис.";
}

export function RegisterPage() {
  const { authApi } = useAuth();
  const navigate = useNavigate();
  const [email, setEmail] = useState("");
  const [password, setPassword] = useState("");
  const [confirm, setConfirm] = useState("");
  const [error, setError] = useState("");
  const [loading, setLoading] = useState(false);

  const handleSubmit = async (event: FormEvent) => {
    event.preventDefault();
    setError("");
    if (!email) {
      setError("Email є обов'язковим.");
      return;
    }
    if (password.length < 8) {
      setError("Мінімум 8 символів.");
      return;
    }
    if (password !== confirm) {
      setError("Паролі не збігаються.");
      return;
    }
    setLoading(true);
    try {
      await authApi.register(email, password);
      navigate("/login", { replace: true });
    } catch (err) {
      setError(registerErrorMessage(err));
    } finally {
      setLoading(false);
    }
  };

  return (
    <AuthLayout subtitle="Створіть новий акаунт">
      <form className="flex flex-col gap-3.5" onSubmit={handleSubmit}>
        <div className="space-y-2">
          <label className="av-label" htmlFor="register-email">
            Email
          </label>
          <Input
            id="register-email"
            type="email"
            autoComplete="email"
            placeholder="email@example.com"
            value={email}
            onChange={(event) => setEmail(event.target.value)}
          />
        </div>
        <div className="space-y-2">
          <label className="av-label" htmlFor="register-password">
            Пароль
          </label>
          <Input
            id="register-password"
            type="password"
            autoComplete="new-password"
            placeholder="Мінімум 8 символів"
            value={password}
            onChange={(event) => setPassword(event.target.value)}
          />
          <p className="text-[11px] text-muted-foreground">Мінімальна довжина паролю - 8 символів</p>
        </div>
        <div className="space-y-2">
          <label className="av-label" htmlFor="confirm-password">
            Підтвердіть пароль
          </label>
          <Input
            id="confirm-password"
            type="password"
            autoComplete="new-password"
            placeholder="Повторіть пароль"
            value={confirm}
            onChange={(event) => setConfirm(event.target.value)}
          />
        </div>
        {error ? <Alert>{error}</Alert> : null}
        <Button className="mt-0.5 w-full" disabled={loading} type="submit">
          {loading ? <ReloadIcon className="h-4 w-4 animate-spin" /> : null}
          Зареєструватись
        </Button>
      </form>
      <p className="text-center text-xs text-muted-foreground">
        Вже є акаунт?{" "}
        <Link className="av-link" to="/login">
          Увійти
        </Link>
      </p>
    </AuthLayout>
  );
}
