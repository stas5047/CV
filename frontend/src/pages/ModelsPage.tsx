import { FormEvent, useState } from "react";
import { useMutation, useQuery, useQueryClient } from "@tanstack/react-query";
import { activateModel, listModels, registerModel } from "../api/models";
import { useAuth } from "../auth/useAuth";
import { Button } from "../components/ui/button";
import {
  EmptyState,
  ErrorState,
  Header,
  ModelForm,
  ModelList,
  ModelsSkeleton,
  SummaryStrip,
} from "./models/ModelPageParts";
import {
  EMPTY_VALUE,
  UNSAFE_PATH_ERROR,
  emptyModelForm,
  isUnsafeRelativePath,
  modelPayload,
  type ModelFormState,
} from "./models/modelPageUtils";

export function ModelsPage() {
  const { user } = useAuth();
  const queryClient = useQueryClient();
  const [showForm, setShowForm] = useState(false);
  const [form, setForm] = useState<ModelFormState>(emptyModelForm);
  const [formError, setFormError] = useState<string | null>(null);
  const [activationError, setActivationError] = useState<string | null>(null);
  const [activatingId, setActivatingId] = useState<string | null>(null);
  const isAdmin = user?.role === "admin";

  const modelsQuery = useQuery({
    queryKey: ["models"],
    queryFn: listModels,
  });

  const registerMutation = useMutation({
    mutationFn: registerModel,
    onSuccess: async () => {
      setForm(emptyModelForm);
      setShowForm(false);
      setFormError(null);
      await queryClient.invalidateQueries({ queryKey: ["models"] });
    },
    onError: () => {
      setFormError("Не вдалося зареєструвати модель. Перевірте поля та повторіть запит.");
    },
  });

  const activateMutation = useMutation({
    mutationFn: activateModel,
    onMutate: (modelId) => {
      setActivationError(null);
      setActivatingId(modelId);
    },
    onSuccess: async () => {
      await queryClient.invalidateQueries({ queryKey: ["models"] });
    },
    onError: () => {
      setActivationError("Не вдалося активувати модель. Перевірте права доступу та повторіть запит.");
    },
    onSettled: () => setActivatingId(null),
  });

  const handleSubmit = (event: FormEvent<HTMLFormElement>) => {
    event.preventDefault();
    setFormError(null);
    if (isUnsafeRelativePath(form.weights_path)) {
      setFormError(UNSAFE_PATH_ERROR);
      return;
    }
    registerMutation.mutate(modelPayload(form));
  };

  if (modelsQuery.isLoading) return <ModelsSkeleton />;
  if (modelsQuery.isError) return <ErrorState onRetry={() => void modelsQuery.refetch()} />;

  const models = modelsQuery.data?.items ?? [];

  return (
    <div className="space-y-5">
      <Header isAdmin={isAdmin} onToggleForm={() => setShowForm((value) => !value)} />

      {isAdmin && showForm ? (
        <ModelForm
          form={form}
          error={formError}
          isSubmitting={registerMutation.isPending}
          onChange={setForm}
          onClose={() => {
            setShowForm(false);
            setFormError(null);
          }}
          onSubmit={handleSubmit}
        />
      ) : null}

      {models.length === 0 ? (
        <EmptyState
          title="Моделі ще не зареєстровані"
          description="Після реєстрації тут з'явиться активна модель, fallback-версії та метрики."
          action={
            isAdmin ? (
              <Button onClick={() => setShowForm(true)}>Зареєструвати модель</Button>
            ) : undefined
          }
        />
      ) : (
        <>
          <SummaryStrip models={models} />
          {activationError ? (
            <p role="alert" className="rounded-md border border-destructive/25 bg-destructive/10 px-4 py-3 text-sm text-red-100">
              {activationError}
            </p>
          ) : null}
          <ModelList
            models={models}
            isAdmin={isAdmin}
            activatingId={activatingId}
            onActivate={(modelId) => activateMutation.mutate(modelId)}
          />
        </>
      )}

      <p className="sr-only">{EMPTY_VALUE}</p>
    </div>
  );
}
