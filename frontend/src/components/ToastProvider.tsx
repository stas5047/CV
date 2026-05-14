import { useCallback, useMemo, useState, type ReactNode } from "react";
import { CheckCircledIcon, Cross2Icon, ExclamationTriangleIcon, InfoCircledIcon } from "@radix-ui/react-icons";
import { cn } from "../lib/utils";
import { ToastContext, type ToastInput, type ToastVariant } from "./toast";

type ToastItem = ToastInput & {
  id: string;
  variant: ToastVariant;
};

const variantClasses: Record<ToastVariant, string> = {
  success: "border-primary/35 bg-primary/15 text-accent-foreground",
  error: "border-destructive/35 bg-destructive/15 text-red-100",
  info: "border-border bg-card text-foreground",
};

function ToastIcon({ variant }: { variant: ToastVariant }) {
  if (variant === "success") return <CheckCircledIcon className="mt-0.5 h-4 w-4 shrink-0" />;
  if (variant === "error") return <ExclamationTriangleIcon className="mt-0.5 h-4 w-4 shrink-0" />;
  return <InfoCircledIcon className="mt-0.5 h-4 w-4 shrink-0" />;
}

export function ToastProvider({ children }: { children: ReactNode }) {
  const [toasts, setToasts] = useState<ToastItem[]>([]);

  const dismissToast = useCallback((id: string) => {
    setToasts((items) => items.filter((item) => item.id !== id));
  }, []);

  const toast = useCallback(
    ({ title, description, variant = "info" }: ToastInput) => {
      const id = typeof crypto.randomUUID === "function" ? crypto.randomUUID() : `${Date.now()}-${Math.random()}`;
      setToasts((items) => [...items.slice(-3), { id, title, description, variant }]);
      window.setTimeout(() => dismissToast(id), 5000);
    },
    [dismissToast],
  );

  const value = useMemo(() => ({ toast, dismissToast }), [toast, dismissToast]);

  return (
    <ToastContext.Provider value={value}>
      {children}
      <div className="pointer-events-none fixed right-4 top-4 grid w-[min(360px,calc(100vw-2rem))] gap-3" aria-live="polite">
        {toasts.map((item) => (
          <div
            className={cn(
              "pointer-events-auto flex items-start gap-3 rounded-md border px-4 py-3 text-sm shadow-panel backdrop-blur animate-auth-slide-up",
              variantClasses[item.variant],
            )}
            key={item.id}
            role="status"
          >
            <ToastIcon variant={item.variant} />
            <div className="min-w-0 flex-1">
              <p className="font-semibold leading-5">{item.title}</p>
              {item.description ? <p className="mt-1 text-xs leading-5 opacity-80">{item.description}</p> : null}
            </div>
            <button
              type="button"
              className="rounded p-1 text-current opacity-70 transition hover:bg-white/10 hover:opacity-100 active:translate-y-px"
              onClick={() => dismissToast(item.id)}
              aria-label="Закрити сповіщення"
            >
              <Cross2Icon className="h-3.5 w-3.5" />
            </button>
          </div>
        ))}
      </div>
    </ToastContext.Provider>
  );
}
