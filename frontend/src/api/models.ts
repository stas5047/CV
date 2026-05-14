import { apiRequest } from "./client";
import type { ModelCreateRequest, ModelListResponse, ModelVersion } from "./types";

export function listModels() {
  return apiRequest<ModelListResponse>("/models?limit=100");
}

export function registerModel(payload: ModelCreateRequest) {
  return apiRequest<ModelVersion>("/models", {
    method: "POST",
    body: payload,
  });
}

export function activateModel(modelId: string) {
  return apiRequest<ModelVersion>(`/models/${modelId}/activate`, {
    method: "PATCH",
  });
}
