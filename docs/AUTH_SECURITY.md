# AUTH_SECURITY.md

## Purpose

This document defines authentication, authorization, account activity checks, upload validation, and baseline security rules for the Drone Computer Vision Subsystem.

This document is canonical for:

- authentication model;
- account activity behavior;
- roles and permissions;
- public registration behavior;
- seeded admin behavior;
- ownership checks;
- upload validation;
- path traversal prevention;
- CORS;
- secret handling;
- logging safety.

This document is not canonical for endpoint lists, database field definitions, UI layout, CV processing, or training workflows.

## Authentication Model

The application must support normal user registration and login using email and password.

Authentication uses JWT access tokens.

Passwords must be hashed securely with bcrypt or Argon2. Plain-text passwords must never be stored.

Email confirmation is not required in the MVP. A user can register and then log in immediately when public registration is enabled.

## Account Activity

The `users.is_active` field controls whether an account may authenticate and use protected API routes.

Authentication must reject users where `is_active = false`. No JWT access token should be issued for inactive accounts.

Inactive users must not be allowed to upload media, create jobs, view results, download exports, or access authenticated API endpoints.

## Password Policy

Minimum password length:

- 8 characters.

No additional password complexity rules are required for the MVP.

Stricter rules may be added later, but they are not required unless explicitly approved.

## Public Registration Toggle

Public registration is controlled by `ALLOW_PUBLIC_REGISTRATION`.

Behavior:

| Value | Behavior |
|---|---|
| `true` | Public users can register through the registration endpoint and UI. |
| `false` | Public registration endpoint returns HTTP 403 and the UI should redirect or show a Ukrainian notice. |

Public registration always creates accounts with role `user`.

Public registration must never create admin accounts.

Admin-created user accounts are out of scope for the first implementation unless explicitly added later.

## Seeded Admin

The initial admin account must be created through setup/seed flow using environment variables:

| Variable | Purpose |
|---|---|
| `ADMIN_EMAIL` | Initial admin email. |
| `ADMIN_PASSWORD` | Initial admin password. |

The seed flow must hash the admin password before storing it.

The admin account must not be created through public registration.

## Roles

The system has exactly two roles:

| Role | Meaning |
|---|---|
| `user` | Regular authenticated user. |
| `admin` | Administrator with global visibility and management permissions. |

No additional roles are part of the MVP.

## Guest Permissions

A guest is an unauthenticated visitor.

Guests may only:

- open the login page;
- open the registration page when public registration is enabled;
- view minimal public landing information if such a page exists;
- call public health endpoints if implemented as public.

Guests must not:

- upload media;
- create processing jobs;
- view results;
- download exports;
- access dashboards;
- access admin pages.

## User Permissions

A regular user may:

- register when public registration is enabled;
- log in;
- upload images and videos;
- create processing jobs for own uploaded media;
- choose allowed processing parameters;
- view own media;
- view own jobs;
- view own job details;
- view own processed results;
- download own annotated media;
- download own CSV and JSON exports;
- view own processing statistics.

A regular user must not:

- view another user's media;
- view another user's jobs;
- download another user's results;
- activate or delete model versions;
- register model versions;
- manage global experiments;
- import experiment results;
- run storage cleanup;
- access admin pages.

## Admin Permissions

An admin inherits all regular user capabilities.

Additionally, an admin may:

- view all jobs from all users;
- view all media metadata;
- view global dashboard statistics;
- register model versions;
- activate default model versions;
- import experiment results;
- view all experiment metrics;
- run safe storage cleanup;
- view a basic list of users.

Admin routes must enforce admin role explicitly.

## Ownership Checks

Ownership checks are mandatory for user-owned resources.

A regular user may access a resource only when:

- the resource belongs to the user; or
- the resource belongs to a job/media record owned by the user.

Ownership checks must apply to:

- media metadata;
- media deletion;
- job creation;
- job details;
- job deletion/cancellation;
- summaries;
- detections;
- tracks;
- annotated media downloads;
- CSV downloads;
- JSON downloads.

Admin users may access global resources through admin-authorized routes and admin permissions.

## Upload Validation

Upload validation is canonical in this document.

The backend must validate uploaded files before storing them as accepted media.

Required image formats:

- `.jpg`
- `.jpeg`
- `.png`
- `.webp`

Required video formats:

- `.mp4`
- `.avi`
- `.mov`
- `.mkv`

The MVP must not support:

- webcam streams;
- RTSP streams;
- live camera processing.

### Extension and MIME Validation

The backend must validate:

- file extension;
- MIME type;
- file size;
- file category: image or video.

Both extension validation and MIME/type validation are required.

Unsupported file types must be rejected before job creation.

### Upload Size Limits

Recommended limits:

| Media type | Default limit |
|---|---:|
| Image | 20 MB |
| Video | 500 MB |

Limits must be configurable through environment variables:

| Variable | Purpose |
|---|---|
| `MAX_IMAGE_SIZE_MB` | Maximum accepted image upload size. |
| `MAX_VIDEO_SIZE_MB` | Maximum accepted video upload size. |

Files exceeding configured limits must be rejected with a clear error.

### Filename Safety

Uploaded filenames must be sanitized.

Internal storage must use generated IDs, not raw user filenames.

The original filename may be stored for display after sanitization, but it must not control filesystem paths.

### Path Traversal Prevention

The backend must prevent path traversal.

Disallowed behavior:

- using raw user filename as a path;
- accepting paths from the client as storage paths;
- allowing `../` or equivalent traversal to affect storage location;
- exposing absolute host or container paths in API responses;
- serving files without verifying ownership and resource association.

Stored file references in the database must be relative to `STORAGE_ROOT`.

## Generated Internal Paths

The backend must generate internal paths for uploaded media.

Recommended path strategy:

- include user ID and media ID;
- use a normalized original extension after validation;
- avoid raw user-controlled path components;
- keep all paths relative to `STORAGE_ROOT`.

Result files are created by the worker under generated job-specific paths.

## File Execution Policy

The system must not execute uploaded files.

Uploaded media are treated only as data for image/video decoding and CV inference.

## Processing Parameter Validation

The backend must validate processing parameters before creating a job.

Validation must cover:

- model version exists and is visible/allowed;
- confidence threshold is within an accepted numeric range;
- IoU threshold is within an accepted numeric range;
- tracker type is allowed for the media type;
- image size is valid if configurable internally;
- `frame_stride` remains internal and is not exposed in standard UI.

Invalid parameters must not create jobs.

## CORS

CORS must allow only configured frontend origins from `BACKEND_CORS_ORIGINS`.

Wildcard `*` must not be used in non-local configurations.

In local development, an explicit list such as local frontend origins is acceptable.

## Secrets

Secrets must not be committed to Git.

Sensitive values include:

- `JWT_SECRET_KEY`;
- database passwords;
- admin password;
- real `.env` file content;
- access tokens;
- any service credentials added later.

A `.env.example` file must contain safe placeholders only.

## Logging Safety

Backend and worker logs may include:

- login/register events without passwords;
- media upload events;
- job creation events;
- job status transitions;
- worker job claim events;
- stale job recovery events;
- model loading events;
- selected CV device;
- processing start/end and duration;
- processing errors in worker logs;
- export generation events.

Logs must not include:

- plain-text passwords;
- password hashes;
- JWT tokens;
- JWT secret keys;
- database passwords;
- unsafe absolute host paths in user-facing logs;
- sensitive environment variable values.

API responses must not expose stack traces.

## Error Response Safety

Failed jobs must store:

- failed status;
- error message;
- updated timestamp.

The frontend must show a clear Ukrainian-language error message.

Worker logs may include detailed stack traces for debugging, but API responses should contain safe summarized errors.

No-detection results must not be treated as failures.

## Admin Storage Cleanup Safety

Admin storage cleanup must be conservative.

Cleanup must not remove:

- active model weights;
- model cards for active models;
- files referenced by non-deleted records;
- recent user results accidentally;
- files needed by completed jobs that remain visible.

Cleanup behavior should be auditable through logs.

## Out-of-Scope Security Features

The MVP does not require:

- email verification;
- email-based password reset;
- CAPTCHA;
- registration rate limiting;
- account lockout;
- OAuth or social login;
- two-factor authentication;
- enterprise RBAC beyond `user` and `admin`;
- admin-created user accounts, unless explicitly added later.

## Security Invariants

The implementation must always preserve these rules:

- Passwords are hashed.
- Authentication uses JWT.
- Public registration never creates admins.
- Users can access only their own resources.
- Admin routes require admin role.
- Uploads are validated before storage and processing.
- Filenames are sanitized.
- Internal storage paths are generated.
- Path traversal is prevented.
- Absolute filesystem paths are not exposed in API responses.
- User-uploaded files are not executed.
- CORS does not use wildcard origins in non-local configurations.
- Secrets and tokens are not logged.
