import { apiRequest } from "./client";
import type {
  AdminJobListResponse,
  AdminStatsResponse,
  AdminUserListResponse,
  StorageCleanupRequest,
  StorageCleanupResponse,
} from "./types";

export function getAdminStats() {
  return apiRequest<AdminStatsResponse>("/admin/stats");
}

export function listAdminJobs(limit = 6) {
  return apiRequest<AdminJobListResponse>(`/admin/jobs?limit=${limit}`);
}

export function listAdminUsers(limit = 50) {
  return apiRequest<AdminUserListResponse>(`/admin/users?limit=${limit}`);
}

export function cleanupStorage(payload: StorageCleanupRequest) {
  return apiRequest<StorageCleanupResponse>("/admin/storage/cleanup", {
    method: "POST",
    body: payload,
  });
}
