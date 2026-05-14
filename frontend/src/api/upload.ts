import { apiRequest } from "./client";
import type { JobCreateRequest, JobDetail, MediaResponse, ModelListResponse } from "./types";

export function uploadMedia(file: File) {
  const body = new FormData();
  body.set("file", file);
  return apiRequest<MediaResponse>("/media", {
    method: "POST",
    body,
  });
}

export function listModelsForUpload() {
  return apiRequest<ModelListResponse>("/models?limit=100");
}

export function createProcessingJob(payload: JobCreateRequest) {
  return apiRequest<JobDetail>("/jobs", {
    method: "POST",
    body: payload,
  });
}

export function getProcessingJob(jobId: string) {
  return apiRequest<JobDetail>(`/jobs/${jobId}`);
}
