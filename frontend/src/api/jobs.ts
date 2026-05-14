import { apiBlobRequest, apiRequest } from "./client";
import type {
  DetectionListParams,
  DetectionListResponse,
  JobDetail,
  JobListParams,
  JobListResponse,
  JobResultResponse,
  JobSummaryResponse,
  ModelListResponse,
  TrackListResponse,
} from "./types";

function query(params: object) {
  const search = new URLSearchParams();
  Object.entries(params as Record<string, string | number | undefined>).forEach(([key, value]) => {
    if (value !== undefined && value !== "") search.set(key, String(value));
  });
  const suffix = search.toString();
  return suffix ? `?${suffix}` : "";
}

export function listJobs(params: JobListParams = {}) {
  return apiRequest<JobListResponse>(`/jobs${query(params)}`);
}

export function listJobFilterModels() {
  return apiRequest<ModelListResponse>("/models?limit=100");
}

export function getJob(jobId: string) {
  return apiRequest<JobDetail>(`/jobs/${jobId}`);
}

export function getJobSummary(jobId: string) {
  return apiRequest<JobSummaryResponse>(`/jobs/${jobId}/summary`);
}

export function getJobResult(jobId: string) {
  return apiRequest<JobResultResponse>(`/jobs/${jobId}/result`);
}

export function listJobDetections(jobId: string, params: DetectionListParams = {}) {
  return apiRequest<DetectionListResponse>(`/jobs/${jobId}/detections${query(params)}`);
}

export function listJobTracks(jobId: string, params: { limit?: number; offset?: number } = {}) {
  return apiRequest<TrackListResponse>(`/jobs/${jobId}/tracks${query(params)}`);
}

export function downloadJobFile(downloadUrl: string) {
  return apiBlobRequest(downloadUrl);
}

export function saveBlob(blob: Blob, filename: string) {
  const url = URL.createObjectURL(blob);
  const anchor = document.createElement("a");
  anchor.href = url;
  anchor.download = filename;
  document.body.append(anchor);
  anchor.click();
  anchor.remove();
  URL.revokeObjectURL(url);
}
