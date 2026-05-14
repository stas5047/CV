# Code Review Resolution - Phase 27

## Verdict: FIXED

OpenAI review verdict was `APPROVED_WITH_CHANGES`. No Claude code review file exists in this checkout. All review items are doc-consistent and accepted. No item needs user decision.

## Resolution table

| ID | Priority | Review item | Resolution | Reason | Fix target |
|---|---|---|---|---|---|
| OAI-I1 | important | Diff whitespace gate fails on `docs/phase.md:3`. | accepted | Whitespace cleanup is low-risk and unblocks review hygiene. | Remove trailing whitespace. |
| OAI-I2 | important | Jobs page omits model filter despite existing `model_version_id` API support. | accepted | Phase 27 says model filter where practical; backend and model list API support it. | Add model selector backed by `/api/models` and pass `model_version_id`. |
| OAI-I3 | important | Jobs page API error contains English visible copy `backend API`. | accepted | Visible errors must be Ukrainian except accepted technical labels. | Replace with Ukrainian wording. |
| OAI-I4 | important | `apiBlobRequest` can send bearer token to arbitrary absolute URL. | accepted | Security/privacy issue; downloads/previews must stay on backend API. | Restrict blob URLs to API-relative or same API origin/path before attaching token. |

## Accepted critical fixes

- None.

## Accepted important fixes

- Remove trailing whitespace in `docs/phase.md`.
- Add backend-backed model filter to `/jobs`.
- Replace English-facing jobs error wording.
- Guard authenticated blob fetches against external absolute URLs.

## Accepted optional fixes

- None.

## Rejected items

- None.

## Duplicate items

- None.

## Items needing user decision

- None.

## Fixes applied

- Removed trailing whitespace from `docs/phase.md`.
- Added `listJobFilterModels()` and `/jobs` model selector backed by `/api/models?limit=100`.
- Wired selected model to `model_version_id` query param and reset pagination on model changes.
- Replaced visible English jobs-list error copy with Ukrainian server wording.
- Restricted `apiBlobRequest()` to API-relative or same API origin/path URLs before applying bearer auth.
- Added frontend tests for model filter query params and external download URL blocking.

## Final verification

- `cd frontend; npm run lint`: PASS.
- `cd frontend; npm test`: PASS, 33 tests passed.
- `cd frontend; npm run build`: PASS.
- `git diff --check`: PASS.
- Manual browser smoke: not available; same tooling blocker remains from implementation status.
