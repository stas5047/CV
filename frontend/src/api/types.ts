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

export interface JobDownloadReference {
  available: boolean;
  download_url: string;
}

export interface JobResultReferences {
  media: JobDownloadReference;
  csv: JobDownloadReference;
  json: JobDownloadReference;
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
  result?: JobResultReferences;
}

export interface JobListResponse {
  items: JobDetail[];
  total: number;
  limit: number;
  offset: number;
}

export interface MediaResponse {
  id: string;
  user_id: string;
  original_filename: string;
  media_type: "image" | "video" | string;
  mime_type: string;
  file_size_bytes: number;
  width: number | null;
  height: number | null;
  frame_count: number | null;
  fps: number | null;
  duration_seconds: number | null;
  created_at: string;
}

export interface MediaListResponse {
  items: MediaResponse[];
  total: number;
  limit: number;
  offset: number;
}

export type TrackerType = "bytetrack" | "botsort";

export interface JobCreateRequest {
  media_id: string;
  model_version_id?: string;
  confidence_threshold?: number;
  iou_threshold?: number;
  tracker_type?: TrackerType;
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

export interface JobSummaryResponse {
  job_id: string;
  status: JobStatus | string;
  summary: Record<string, unknown> | null;
}

export interface JobResultResponse {
  job_id: string;
  status: JobStatus | string;
  summary: Record<string, unknown> | null;
  media: JobDownloadReference;
  csv: JobDownloadReference;
  json: JobDownloadReference;
}

export interface DetectionResponse {
  id: string;
  job_id: string;
  media_file_id: string;
  frame_index: number;
  timestamp_ms: number;
  class_id: number;
  class_name: string;
  confidence: number;
  bbox_x1: number;
  bbox_y1: number;
  bbox_x2: number;
  bbox_y2: number;
  center_x: number;
  center_y: number;
  bbox_width: number;
  bbox_height: number;
  frame_width: number;
  frame_height: number;
  track_id: number | null;
  created_at: string;
}

export interface DetectionListResponse {
  items: DetectionResponse[];
  total: number;
  limit: number;
  offset: number;
}

export interface TrackResponse {
  id: string;
  job_id: string;
  track_id: number;
  class_name: string;
  first_frame_index: number;
  last_frame_index: number;
  frames_count: number;
  average_confidence: number | null;
  max_confidence: number | null;
  created_at: string;
}

export interface TrackListResponse {
  items: TrackResponse[];
  total: number;
  limit: number;
  offset: number;
}

export interface JobListParams {
  limit?: number;
  offset?: number;
  status?: string;
  media_type?: string;
  model_version_id?: string;
  created_from?: string;
  created_to?: string;
}

export interface DetectionListParams {
  limit?: number;
  offset?: number;
  frame_index?: number;
  min_confidence?: number;
  max_confidence?: number;
  track_id?: number;
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
