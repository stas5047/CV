# API.md

## Purpose

This document defines the REST API contract for the Drone Computer Vision Subsystem.

This document is canonical for:

- route groups;
- endpoint responsibilities;
- access control matrix;
- common response behavior;
- ownership rules at API boundaries;
- download behavior;
- external output boundary.

This document is not canonical for database schema, upload validation internals, frontend layout, worker implementation, or training procedure.

## API Principles

All API routes must be prefixed with `/api`.

The API must:

- use JSON for structured request and response bodies unless returning file downloads;
- require JWT authentication for protected routes;
- enforce ownership checks for user-owned resources;
- enforce admin checks for admin-only routes;
- return clear errors for invalid requests;
- never expose passwords, password hashes, JWT secrets, raw tokens, or unsafe absolute filesystem paths;
- expose download URLs or file responses instead of internal storage paths;
- keep external outputs limited to CV data.

## Authentication Model

Protected routes require a valid JWT access token.

`GET /api/auth/me` returns the current authenticated user profile and role.

Frontend may implement logout by deleting the local token. A backend logout endpoint may exist for consistency, but token invalidation storage is not required in the MVP.

Detailed authentication and security rules are defined in `AUTH_SECURITY.md`.

## Common Response Rules

API responses should be consistent and predictable.

Recommended response principles:

- return resource objects for create/read operations;
- return paginated collections for list endpoints when lists can grow;
- include status, progress, and timestamps for processing jobs;
- include clear error messages suitable for frontend Ukrainian localization;
- include only relative/logical references or download URLs for files;
- hide soft-deleted media and jobs from normal user lists;
- allow admins to access broader/global lists through admin routes.

## Error Handling Rules

The API must handle:

- unauthorized access;
- forbidden role or ownership access;
- missing resources;
- unsupported file type;
- file too large;
- invalid processing parameters;
- missing model version;
- unavailable active model;
- failed job state;
- missing result file;
- database connectivity errors.

No-detection results are not errors and must be represented as completed jobs with empty detection data.

## Pagination and Filtering

List endpoints should support pagination when the dataset can grow.

Recommended filters:

| Resource | Filters |
|---|---|
| Media | media type, date, owner for admins. |
| Jobs | status, media type, date, model version, owner for admins. |
| Detections | frame index, confidence range, track ID. |
| Models | active status, model family, variant. |
| Experiments | experiment type, published status for admins. |

Filtering details may be refined during implementation, but access control must always be enforced before returning data.

## Mandatory Access Control Matrix

| Endpoint group | Guest | User | Admin | Notes |
|---|---:|---:|---:|---|
| `GET /api/health` | Yes | Yes | Yes | Public service health. |
| `GET /api/health/db` | Yes | Yes | Yes | Database connectivity check; must not leak secrets. |
| `POST /api/auth/register` | Conditional | No | No | Allowed only if public registration is enabled. Creates `user` role only. |
| `POST /api/auth/login` | Yes | No | No | Credentials-based guest endpoint. Authenticated clients should normally use `/api/auth/me`. |
| `GET /api/auth/me` | No | Yes | Yes | Returns current authenticated user. |
| `POST /api/auth/logout` | No | Yes | Yes | May be client-side token deletion only. |
| `POST /api/media` | No | Own | Own | Upload media as the authenticated account. Admin uploads are scoped to the admin account. |
| `GET /api/media` | No | Own only | All | User sees own media; admin may see all. |
| `GET /api/media/{media_id}` | No | Own only | All | Enforce ownership or admin. |
| `DELETE /api/media/{media_id}` | No | Own only | All | Soft deletion only. |
| `POST /api/jobs` | No | Own media only | Own media only | Creates queued job for media owned by the authenticated account. |
| `GET /api/jobs` | No | Own only | All through admin/global route or admin permission | User sees own jobs. |
| `GET /api/jobs/{job_id}` | No | Own only | All | Enforce ownership or admin. |
| `DELETE /api/jobs/{job_id}` | No | Own only | All | Soft deletion or cancellation behavior only. |
| Results endpoints | No | Own jobs only | All | Summary, detections, tracks, result references, downloads. |
| `GET /api/models` | No | Yes | Yes | Authenticated users can view models. |
| `GET /api/models/{model_id}` | No | Yes | Yes | Authenticated users can view registered models. |
| `POST /api/models` | No | No | Yes | Admin model registration only. |
| `PATCH /api/models/{model_id}/activate` | No | No | Yes | Admin active-model selection only. |
| `GET /api/experiments` | No | Published only | All | Regular users see published runs only. |
| `GET /api/experiments/{experiment_id}` | No | Published only | All | Admin can see unpublished/imported runs. |
| `POST /api/experiments/import` | No | No | Yes | Admin metric import only. |
| `GET /api/admin/*` | No | No | Yes | Admin-only routes. |
| `POST /api/admin/storage/cleanup` | No | No | Yes | Safe cleanup only. |

Admin users can view all media and jobs through admin/global views, but creation of media and processing jobs remains scoped to the authenticated admin account unless a future delegated-processing feature is explicitly added.

## Health API

Required endpoints:

| Method | Route | Purpose |
|---|---|---|
| GET | `/api/health` | Basic backend health status. |
| GET | `/api/health/db` | Database connectivity check for service health. |

Health endpoints must not expose secrets or internal configuration values.

## Auth API

Required endpoints:

| Method | Route | Purpose |
|---|---|---|
| POST | `/api/auth/register` | Register a new user account when public registration is enabled. |
| POST | `/api/auth/login` | Authenticate with email/password and return JWT access token. |
| GET | `/api/auth/me` | Return the current authenticated user profile. |
| POST | `/api/auth/logout` | Optional consistency endpoint; client token deletion is acceptable. |

Registration rules:

- public registration can be disabled;
- disabled registration returns HTTP 403;
- public registration always creates `user` role;
- admin accounts are seeded, not publicly registered.

## Media API

Required endpoints:

| Method | Route | Purpose |
|---|---|---|
| POST | `/api/media` | Upload and register an image or video. |
| GET | `/api/media` | List media visible to the current user. |
| GET | `/api/media/{media_id}` | Get media metadata. |
| DELETE | `/api/media/{media_id}` | Soft-delete media metadata. |

Rules:

- users can access only their own media;
- admins can access all media;
- media deletion must not break existing job records;
- deletion is soft deletion through `deleted_at`;
- physical file removal is only through safe admin cleanup;
- upload validation is canonical in `AUTH_SECURITY.md`.

## Jobs API

Required endpoints:

| Method | Route | Purpose |
|---|---|---|
| POST | `/api/jobs` | Create a queued processing job for an uploaded media file. |
| GET | `/api/jobs` | List jobs visible to the current user. |
| GET | `/api/jobs/{job_id}` | Get job details, status, progress, and references. |
| DELETE | `/api/jobs/{job_id}` | Soft-delete or cancel a job according to status. |

Rules:

- users can create jobs only for their own media;
- users can view only their own jobs;
- admins can view all jobs;
- long media processing must not happen in this API request;
- job creation creates a `queued` job for the worker;
- jobs in `queued` state may be cancelled or soft-deleted;
- jobs in `processing` state do not require hard interruption in the MVP.

## Results API

Required endpoints:

| Method | Route | Purpose |
|---|---|---|
| GET | `/api/jobs/{job_id}/summary` | Return processing summary. |
| GET | `/api/jobs/{job_id}/detections` | Return detection rows for the job. |
| GET | `/api/jobs/{job_id}/tracks` | Return track summaries for video jobs. |
| GET | `/api/jobs/{job_id}/result` | Return result metadata and preview references. |
| GET | `/api/jobs/{job_id}/download/media` | Download annotated output media. |
| GET | `/api/jobs/{job_id}/download/csv` | Download detection CSV export. |
| GET | `/api/jobs/{job_id}/download/json` | Download structured JSON export. |

Rules:

- user access is limited to own jobs;
- admins can access all job results;
- completed no-detection jobs must still provide CSV and JSON downloads;
- missing result files must produce clear errors without exposing internal paths.

## Models API

Required endpoints:

| Method | Route | Purpose |
|---|---|---|
| GET | `/api/models` | List available model versions. |
| GET | `/api/models/{model_id}` | Get one model version. |
| POST | `/api/models` | Register a model version. |
| PATCH | `/api/models/{model_id}/activate` | Activate a model version as default. |

Rules:

- all authenticated users can view registered models;
- only admins can register model versions;
- only admins can activate a model;
- first implementation registers existing relative paths under model storage;
- large `.pt` upload through the UI is optional and not required.

## Experiments API

Required endpoints:

| Method | Route | Purpose |
|---|---|---|
| GET | `/api/experiments` | List experiment runs visible to the current user. |
| GET | `/api/experiments/{experiment_id}` | Get experiment details and metrics. |
| POST | `/api/experiments/import` | Import experiment results and artifacts. |

Rules:

- regular users can view only `is_published=true` experiments;
- admins can view all experiment runs;
- only admins can import experiment metrics;
- the web UI and API must not launch training.

## Admin API

Required endpoints:

| Method | Route | Purpose |
|---|---|---|
| GET | `/api/admin/stats` | Global processing and system statistics. |
| GET | `/api/admin/jobs` | Global job history. |
| GET | `/api/admin/users` | Basic user list. |
| POST | `/api/admin/storage/cleanup` | Safe old-file cleanup. |

Rules:

- admin endpoints require admin role;
- cleanup must not delete active model weights;
- cleanup must not delete recent user results accidentally;
- cleanup must respect database references and soft-deletion rules.

## Processing Parameter Rules

The job creation API must validate processing parameters.

Allowed user-facing parameters:

| Parameter | Notes |
|---|---|
| `model_version_id` | Optional; if omitted, backend resolves active model. |
| `confidence_threshold` | User-configurable threshold. |
| `iou_threshold` | User-configurable threshold. |
| `tracker_type` | User-configurable for video. |

Internal parameter:

| Parameter | Notes |
|---|---|
| `frame_stride` | Default `1`; must not be exposed in standard UI. |

Model selection priority is defined in `CV_PIPELINE.md`.

## Download and File Serving Rules

The API must serve files through safe download endpoints.

Rules:

- do not expose absolute host paths;
- do not expose absolute container paths;
- validate job ownership or admin role before serving files;
- ensure the requested file belongs to the requested job/resource;
- handle missing files gracefully;
- set appropriate file names and media types for downloads;
- keep downloads available for completed no-detection jobs.

## CSV Export Contract

The CSV export must contain one row per detection.

Required columns:

| Column |
|---|
| `job_id` |
| `media_id` |
| `frame_index` |
| `timestamp_ms` |
| `class_id` |
| `class_name` |
| `confidence` |
| `bbox_x1` |
| `bbox_y1` |
| `bbox_x2` |
| `bbox_y2` |
| `center_x` |
| `center_y` |
| `bbox_width` |
| `bbox_height` |
| `frame_width` |
| `frame_height` |
| `track_id` |
| `model_version` |
| `tracker_type` |

No-detection jobs must still produce a CSV file with headers only.

## JSON Export Contract

The JSON export must contain the following top-level objects/arrays:

| Key | Meaning |
|---|---|
| `job` | Job metadata and status. |
| `media` | Source media metadata. |
| `model` | Model version metadata. |
| `parameters` | Processing parameters. |
| `summary` | Processing summary metrics. |
| `detections` | Detection array. |
| `tracks` | Track summary array. |

No-detection jobs must use an empty `detections` array.

## External Module Interface Boundary

The API and JSON exports may expose only computer vision data.

Allowed external output fields:

- detection status;
- frame index;
- timestamp;
- bounding box;
- center point in image coordinates;
- confidence;
- class label;
- track ID;
- FPS;
- model version.

Forbidden external output fields:

- interception course;
- flight control commands;
- motor commands;
- aiming commands;
- weapon or payload commands;
- geospatial targeting data;
- autonomous engagement decisions.

All coordinates are image-space coordinates only.

## API Invariants

The API must always preserve these rules:

- All protected endpoints enforce authentication.
- All user-owned resources enforce ownership or admin role.
- All admin routes enforce admin role.
- Public registration never creates admins.
- Training is not launched from the API.
- Long video processing is not performed synchronously by the API.
- File downloads never reveal unsafe internal paths.
- No-detection jobs are successful completed jobs.
- API/export outputs remain inside the CV-only boundary.
