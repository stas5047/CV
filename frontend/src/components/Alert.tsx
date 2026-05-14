import { ExclamationTriangleIcon } from "@radix-ui/react-icons";

export function Alert({ children }: { children: React.ReactNode }) {
  return (
    <div className="flex items-start gap-3 rounded-md border border-destructive/30 bg-destructive/10 p-3 text-sm text-red-200">
      <ExclamationTriangleIcon className="mt-0.5 h-4 w-4 shrink-0" />
      <div>{children}</div>
    </div>
  );
}
