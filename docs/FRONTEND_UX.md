# FRONTEND_UX.md

## Purpose

This document defines frontend routes, UX flows, visible UI language rules, UI states, and visual design expectations for the Drone Computer Vision Subsystem.

This document is canonical for:

- frontend language rules;
- routes and pages;
- page-level content requirements;
- user flows;
- loading, error, and empty states;
- visual design rules;
- admin UI visibility;
- frontend chart expectations.

This document is not canonical for API schemas, database fields, upload security internals, worker internals, or training procedure.

## Frontend Stack

Required frontend stack:

- React;
- TypeScript;
- Vite;
- Tailwind CSS;
- shadcn/ui;
- React Router;
- TanStack Query;
- Recharts.

The UI must look like a polished dashboard-style web application, not a raw debug panel.

## Language Rules

Visible frontend UI text must be Ukrainian.

This includes:

- page titles;
- navigation labels;
- button labels;
- form labels;
- validation messages;
- status messages;
- empty states;
- error messages;
- toast notifications;
- table headers when practical;
- helper text.

The following remain English:

- code identifiers;
- route names;
- API fields;
- database fields;
- internal types;
- log messages;
- developer comments;
- accepted technical labels such as `FPS`, `mAP`, `JWT`, `YOLO`, `CSV`, `JSON`.

## Navigation

Recommended navigation items:

| UI item | Route |
|---|---|
| Dashboard | `/dashboard` |
| Upload | `/upload` |
| Jobs | `/jobs` |
| Models | `/models` |
| Experiments | `/experiments` |
| Admin | `/admin` |

The `Admin` navigation item must be visible only to admin users.

Guests must not see authenticated dashboard navigation.

## Route Overview

Required routes:

| Route | Page |
|---|---|
| `/login` | Login page. |
| `/register` | Registration page. |
| `/dashboard` | Main dashboard. |
| `/upload` | Upload and processing page. |
| `/jobs` | Jobs/history page. |
| `/jobs/:jobId` | Job details page. |
| `/models` | Model registry page. |
| `/experiments` | Experiments and metrics page. |
| `/admin` | Admin page. |

Protected routes must redirect unauthenticated users to login.

Admin routes must reject or redirect non-admin users.

## Login Page

Route:

- `/login`

Required UI:

- email input;
- password input;
- login button;
- link to registration when public registration is enabled;
- error display;
- loading state.

Login errors must be displayed in Ukrainian.

## Registration Page

Route:

- `/register`

Required UI:

- email input;
- password input;
- confirm password input;
- registration button;
- link to login;
- validation messages;
- visible minimum password length rule.

Registration creates only `user` accounts.

When public registration is disabled, the page must redirect to `/login` or show a Ukrainian-language notice that registration is disabled.

## Main Dashboard

Route:

- `/dashboard`

Required content:

- total processed files;
- total detections;
- average confidence;
- average FPS;
- active model;
- recent processing jobs;
- quick upload action.

For regular users, show only their own statistics.

For admins, show global statistics where supported.

Dashboard cards must handle missing data gracefully.

## Upload and Processing Page

Route:

- `/upload`

Required content:

- drag-and-drop file upload;
- allowed file types message;
- selected file preview or metadata;
- model selector;
- confidence threshold control;
- IoU threshold control;
- tracker selector for videos;
- process button;
- job progress/status block after job creation.

The progress/status block must show:

- status badge;
- progress bar;
- percentage when available;
- last update time when available.

Default options must be preselected so a user can process a file without changing settings.

`frame_stride` must not appear as a user-facing control in the first implementation.

If processed video preview is unavailable in the browser, the UI must show a Ukrainian-language notice and keep the download action available.

## Jobs / History Page

Route:

- `/jobs`

Required content:

- processing jobs table;
- status badges;
- media type;
- original filename;
- model version;
- created date;
- processing duration;
- detections count;
- average confidence;
- filters;
- link to job details.

Recommended filters:

- status;
- media type;
- date;
- model.

Users see only their own jobs. Admin global job history belongs in admin routes/pages.

## Job Details Page

Route:

- `/jobs/:jobId`

Required content:

- job status;
- original media metadata;
- processed media preview;
- summary cards;
- detection table;
- track summary table for video;
- download annotated media button;
- download CSV button;
- download JSON button;
- error message area for failed jobs;
- progress bar for processing jobs;
- last heartbeat/update time for processing jobs when available.

Detection table must show at least:

- frame index;
- timestamp;
- class;
- confidence;
- bounding box;
- track ID.

If a completed job has no detections:

- show a Ukrainian-language empty state;
- do not treat it as an error;
- keep download buttons available for annotated media, CSV, and JSON when those outputs exist.

## Models Page

Route:

- `/models`

Required content:

- list of registered model versions;
- model name;
- family, such as YOLO26 or documented fallback YOLO11;
- variant;
- active status;
- dataset description;
- key metrics;
- model size if known.

Admin-only actions:

- register model;
- activate model.

Regular users may view available models but must not see admin-only mutation actions.

## Experiments and Metrics Page

Route:

- `/experiments`

Required content:

- model comparison table;
- threshold analysis chart;
- tracker behavior comparison table;
- false-positive analysis summary;
- precision/recall/mAP cards;
- FPS/latency chart;
- confusion matrix image if available.

Charts must use Recharts.

Matplotlib must not be used in the web UI.

Tracker comparison must be described as tracker behavior comparison, not absolute tracking accuracy.

## Experiment Empty State

Experiment data may not exist on first application launch. Metric values may be `null` until experiments are imported.

The page must not:

- crash;
- render blank sections;
- display raw `null` values;
- show an empty chart canvas without explanation.

For each experiment section with no data, show this exact Ukrainian text:

```text
Дані експерименту ще не завантажено
```

Charts with no data must show the same empty state instead of an empty chart.

## Admin Page

Route:

- `/admin`

Admin-only page.

Required content:

- global processing statistics;
- recent jobs from all users;
- model management shortcuts;
- storage cleanup action;
- basic users table.

Do not implement complex user management unless explicitly required later.

## Status Badges

The UI must use visual status badges for job statuses:

| Status | Meaning |
|---|---|
| `queued` | Waiting for worker. |
| `processing` | Worker is processing. |
| `completed` | Finished successfully. |
| `failed` | Finished with error. |
| `cancelled` | Cancelled or marked as cancelled. |

Badge text must be Ukrainian in visible UI.

## Loading States

Use clear loading states for:

- page loading;
- login/register requests;
- upload submission;
- job creation;
- job status polling;
- table loading;
- model list loading;
- experiment metric loading;
- download preparation when needed.

Loading states may use skeletons, spinners, disabled buttons, or progress indicators depending on context.

## Error States

Error states must be clear and user-facing in Ukrainian.

Required error handling UI:

- login failure;
- registration failure;
- upload validation failure;
- file too large;
- unsupported file type;
- job creation failure;
- job processing failure;
- missing result file;
- unauthorized/forbidden access;
- failed API request;
- unavailable experiment data.

API errors should be translated or mapped into useful Ukrainian UI messages.

## Empty States

Empty states must be implemented for:

- no jobs yet;
- no uploaded media yet;
- completed job with no detections;
- no track data for image jobs or video jobs with no tracks;
- no registered model metrics yet;
- no experiment data yet;
- empty admin lists.

Do not show raw empty tables without explanation.

## Data Display Rules

The UI must not display raw `null` values.

Recommended mappings:

| Data case | UI behavior |
|---|---|
| Missing metric | Empty state or Ukrainian placeholder. |
| No detections | Empty state, not error. |
| No track ID | Ukrainian equivalent of not available. |
| Missing video preview | Notice plus download button. |
| Failed job | Error block with safe error message. |

Bounding boxes should be displayed in a readable compact format.

Confidence values should be formatted consistently.

Dates and durations should be user-friendly.

## Design Requirements

The UI must:

- use shadcn/ui components;
- use Tailwind CSS;
- use consistent spacing;
- use cards for metrics;
- use tables for detections, jobs, and models;
- use status badges;
- use loading skeletons or clear loading indicators;
- use toast notifications for success and errors;
- be responsive for desktop and laptop screens;
- avoid raw debug-panel appearance.

## Auth and Admin Visibility

Frontend route protection must match backend authorization.

Rules:

- guests are redirected away from protected pages;
- users cannot see admin navigation;
- users cannot access `/admin`;
- admin-only buttons are hidden or disabled for non-admin users;
- backend authorization remains the source of truth even if frontend hides controls.

## Job Polling UX

When a job is queued or processing, the frontend should poll job status.

Processing UI should show:

- current status;
- progress percent when available;
- last update/heartbeat time when available;
- clear transition to completed or failed state.

The UI must not imply real-time processing guarantees. CPU video processing may be slow.

## Frontend Invariants

The frontend must always preserve these rules:

- Visible UI text is Ukrainian.
- Code identifiers remain English.
- `frame_stride` is not exposed in standard UI.
- Recharts are used for frontend charts.
- Admin navigation is visible only to admins.
- Users see only their own media/jobs/results.
- No-detection completed jobs show empty states, not errors.
- Experiment sections with no data show the required Ukrainian empty-state text.
- The UI does not expose absolute filesystem paths.
- The UI does not present CV results as targeting, navigation, or interception instructions.
