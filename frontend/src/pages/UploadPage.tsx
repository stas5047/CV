import { useEffect, useMemo, useRef, useState } from "react";
import { useMutation, useQuery } from "@tanstack/react-query";
import { FileIcon, ReloadIcon, RocketIcon, UploadIcon } from "@radix-ui/react-icons";
import { createProcessingJob, getProcessingJob, listModelsForUpload, uploadMedia } from "../api/upload";
import type { JobCreateRequest, JobDetail, MediaResponse, TrackerType } from "../api/types";
import { Button } from "../components/ui/button";
import { cn } from "../lib/utils";
import { FilePreview, JobStatusPanel, ModelSelector, SliderField } from "./upload/UploadPageParts";
import {
  ALL_EXTENSIONS,
  DEFAULT_CONFIDENCE,
  DEFAULT_IOU,
  extensionOf,
  mediaKind,
  safeSubmitError,
  selectDefaultModel,
} from "./upload/uploadUtils";

export function UploadPage() {
  const [file, setFile] = useState<File | null>(null);
  const [dragOver, setDragOver] = useState(false);
  const [validationError, setValidationError] = useState<string | null>(null);
  const [submitError, setSubmitError] = useState<string | null>(null);
  const [uploadedMedia, setUploadedMedia] = useState<MediaResponse | null>(null);
  const [createdJob, setCreatedJob] = useState<JobDetail | null>(null);
  const [selectedModelId, setSelectedModelId] = useState("");
  const [confidence, setConfidence] = useState(DEFAULT_CONFIDENCE);
  const [iou, setIou] = useState(DEFAULT_IOU);
  const [tracker, setTracker] = useState<TrackerType>("bytetrack");
  const inputRef = useRef<HTMLInputElement | null>(null);

  const modelsQuery = useQuery({
    queryKey: ["upload", "models"],
    queryFn: listModelsForUpload,
  });
  const models = useMemo(() => modelsQuery.data?.items ?? [], [modelsQuery.data?.items]);
  const kind = mediaKind(file);
  const isBusy = createdJob?.status === "queued" || createdJob?.status === "processing";

  const jobQuery = useQuery({
    queryKey: ["upload", "job", createdJob?.id],
    queryFn: () => getProcessingJob(createdJob?.id ?? ""),
    enabled: Boolean(createdJob?.id),
    refetchInterval: (query) => {
      const status = (query.state.data as JobDetail | undefined)?.status ?? createdJob?.status;
      return status === "queued" || status === "processing" ? 1200 : false;
    },
  });

  useEffect(() => {
    if (models.length > 0 && !models.some((model) => model.id === selectedModelId)) {
      setSelectedModelId(selectDefaultModel(models));
    }
    if (models.length === 0 && selectedModelId) setSelectedModelId("");
  }, [models, selectedModelId]);

  const mutation = useMutation({
    mutationFn: async () => {
      if (!file) throw new Error("missing file");
      setSubmitError(null);
      const media = await uploadMedia(file).catch((error) => {
        throw Object.assign(error instanceof Error ? error : new Error("upload failed"), { step: "media" });
      });
      setUploadedMedia(media);

      const payload: JobCreateRequest = {
        media_id: media.id,
        confidence_threshold: confidence,
        iou_threshold: iou,
      };
      if (selectedModelId) payload.model_version_id = selectedModelId;
      if (media.media_type === "video" || kind === "video") payload.tracker_type = tracker;

      return createProcessingJob(payload).catch((error) => {
        throw Object.assign(error instanceof Error ? error : new Error("job failed"), { step: "job" });
      });
    },
    onSuccess: setCreatedJob,
    onError: (error) => {
      const step = (error as Error & { step?: "media" | "job" }).step ?? "job";
      setSubmitError(safeSubmitError(step));
    },
  });

  const acceptFile = (candidate: File | undefined) => {
    if (!candidate) return;
    if (!ALL_EXTENSIONS.includes(extensionOf(candidate.name))) {
      setValidationError("Формат файлу не підтримується.");
      setFile(null);
      setUploadedMedia(null);
      setCreatedJob(null);
      return;
    }
    setValidationError(null);
    setSubmitError(null);
    setFile(candidate);
    setUploadedMedia(null);
    setCreatedJob(null);
  };

  const clearFile = () => {
    setFile(null);
    setUploadedMedia(null);
    setCreatedJob(null);
    setSubmitError(null);
    setValidationError(null);
    if (inputRef.current) inputRef.current.value = "";
  };

  const visibleJob = jobQuery.data ?? createdJob;

  return (
    <div className="space-y-5">
      <header className="flex flex-col gap-2">
        <h1 className="font-display text-2xl font-bold tracking-tight">Завантаження</h1>
        <p className="max-w-2xl text-sm leading-6 text-muted-foreground">
          Завантажте зображення або відео, виберіть параметри й створіть завдання обробки.
        </p>
      </header>

      <section className="grid gap-5 lg:grid-cols-[minmax(0,1fr)_340px]">
        <div className="space-y-4">
          {!file ? (
            <button
              type="button"
              className={cn(
                "av-card flex min-h-72 w-full flex-col items-center justify-center gap-4 border-dashed p-8 text-center transition duration-300 hover:border-primary/70 hover:bg-secondary/40 active:translate-y-px",
                dragOver && "border-primary/70 bg-primary/5",
              )}
              onClick={() => inputRef.current?.click()}
              onDragOver={(event) => {
                event.preventDefault();
                setDragOver(true);
              }}
              onDragLeave={() => setDragOver(false)}
              onDrop={(event) => {
                event.preventDefault();
                setDragOver(false);
                acceptFile(event.dataTransfer.files[0]);
              }}
            >
              <span className="grid h-14 w-14 place-items-center rounded-md bg-primary/10 text-accent-foreground">
                <UploadIcon className="h-7 w-7" />
              </span>
              <span className="text-base font-medium text-foreground">Перетягніть файл сюди або натисніть для вибору</span>
              <span className="max-w-lg text-sm leading-6 text-muted-foreground">
                JPG, JPEG, PNG, WEBP — рекомендовано до 20 МБ. MP4, AVI, MOV, MKV — рекомендовано до 500 МБ.
              </span>
            </button>
          ) : (
            <FilePreview file={file} uploadedMedia={uploadedMedia} onClear={clearFile} />
          )}

          <input
            ref={inputRef}
            className="sr-only"
            type="file"
            aria-label="Виберіть файл для обробки"
            accept=".jpg,.jpeg,.png,.webp,.mp4,.avi,.mov,.mkv"
            onChange={(event) => acceptFile(event.target.files?.[0])}
          />

          {validationError ? <InlineError>{validationError}</InlineError> : null}
          {submitError ? <InlineError>{submitError}</InlineError> : null}
          {visibleJob ? <JobStatusPanel job={visibleJob} /> : null}
        </div>

        <aside className="av-card p-5">
          <div className="mb-5 flex items-center gap-3 border-b border-border pb-4">
            <div className="grid h-9 w-9 place-items-center rounded-md bg-secondary text-accent-foreground">
              <RocketIcon className="h-4 w-4" />
            </div>
            <div>
              <h2 className="font-display text-base font-semibold">Параметри обробки</h2>
              <p className="text-xs text-muted-foreground">Типові значення вже вибрано</p>
            </div>
          </div>

          <div className="space-y-5">
            <ModelSelector
              models={models}
              selectedModelId={selectedModelId}
              setSelectedModelId={setSelectedModelId}
              loading={modelsQuery.isLoading}
              error={modelsQuery.isError}
            />
            <SliderField label="Поріг впевненості" value={confidence} onChange={setConfidence} />
            <SliderField label="Поріг IoU" value={iou} onChange={setIou} />

            {kind === "video" ? (
              <div className="space-y-2">
                <label className="av-label" htmlFor="upload-tracker">
                  Трекер
                </label>
                <select
                  id="upload-tracker"
                  className="av-input"
                  value={tracker}
                  onChange={(event) => setTracker(event.target.value as TrackerType)}
                >
                  <option value="bytetrack">ByteTrack (типово)</option>
                  <option value="botsort">BoT-SORT</option>
                </select>
              </div>
            ) : null}

            <div className="border-t border-border pt-4">
              <Button
                className="w-full"
                disabled={!file || Boolean(validationError) || mutation.isPending || isBusy}
                onClick={() => mutation.mutate()}
              >
                {mutation.isPending ? <ReloadIcon className="h-4 w-4 animate-spin" /> : <FileIcon className="h-4 w-4" />}
                {mutation.isPending ? "Створення завдання" : "Запустити обробку"}
              </Button>
              {!file ? <p className="mt-3 text-center text-xs text-muted-foreground">Спочатку виберіть файл</p> : null}
            </div>
          </div>
        </aside>
      </section>
    </div>
  );
}

function InlineError({ children }: { children: string }) {
  return (
    <div className="rounded-md border border-destructive/25 bg-destructive/10 p-3 text-sm text-red-100/85">
      {children}
    </div>
  );
}
