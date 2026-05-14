import { apiRequest } from "./client";
import type { ExperimentListResponse } from "./types";

export function listExperiments() {
  return apiRequest<ExperimentListResponse>("/experiments?limit=100");
}
