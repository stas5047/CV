import { apiRequest } from "./client";
import type { AdminStatsResponse, JobListResponse, ModelListResponse } from "./types";

export function getUserDashboardJobs() {
  return apiRequest<JobListResponse>("/jobs?limit=100");
}

export function getAdminDashboardStats() {
  return apiRequest<AdminStatsResponse>("/admin/stats");
}

export function getAdminDashboardJobs() {
  return apiRequest<JobListResponse>("/admin/jobs?limit=5");
}

export function getActiveModels() {
  return apiRequest<ModelListResponse>("/models?is_active=true&limit=1");
}
