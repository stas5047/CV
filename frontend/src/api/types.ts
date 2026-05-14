export type UserRole = "user" | "admin";

export interface User {
  id: string;
  email: string;
  role: UserRole;
  is_active: boolean;
  created_at: string;
  updated_at: string;
}

export interface TokenResponse {
  access_token: string;
  token_type: string;
}

export type JobStatus = "queued" | "processing" | "completed" | "failed" | "cancelled";

export interface JobMediaReference {
  id: string;
  original_filename: string;
  media_type: "image" | "video" | string;
  width: number | null;
  height: number | null;
  frame_count: number | null;
  fps: number | null;
  duration_seconds: number | null;
}

export interface JobModelReference {
  id: string;
  name: string;
  model_family: string;
  variant: string;
}

export interface JobDetail {
  id: string;
  user_id: string;
  media_file_id: string;
  model_version_id: string | null;
  status: JobStatus | string;
  input_params_json: Record<string, unknown>;
  summary_json: Record<string, unknown> | null;
  error_message: string | null;
  progress_percent: number;
  last_heartbeat_at: string | null;
  locked_by: string | null;
  locked_at: string | null;
  retry_count: number;
  started_at: string | null;
  completed_at: string | null;
  created_at: string;
  updated_at: string;
  media: JobMediaReference;
  model: JobModelReference | null;
}

export interface JobListResponse {
  items: JobDetail[];
  total: number;
  limit: number;
  offset: number;
}

export interface ModelVersion {
  id: string;
  name: string;
  model_family: string;
  variant: string;
  weights_path: string;
  dataset_name: string | null;
  dataset_split_description: string | null;
  metrics_json: Record<string, unknown>;
  is_active: boolean;
  created_by_user_id: string | null;
  created_at: string;
  updated_at: string;
}

export interface ModelListResponse {
  items: ModelVersion[];
  total: number;
  limit: number;
  offset: number;
}

export interface AdminStatsResponse {
  users: {
    total: number;
    active: number;
    admins: number;
  };
  media: {
    total: number;
    images: number;
    videos: number;
  };
  jobs: {
    total: number;
    by_status: Record<string, number>;
  };
  detections: {
    total: number;
  };
  tracks: {
    total: number;
  };
  models: {
    total: number;
    active: number;
  };
  experiments: {
    total: number;
    published: number;
  };
}
