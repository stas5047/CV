# Phase 5 Planning Review - Claude

## Verdict: APPROVED_WITH_CHANGES

## Summary

Plan matches Phase 5 scope: backend auth/account activity only. It follows relevant docs on bcrypt, JWT access tokens, `ALLOW_PUBLIC_REGISTRATION`, `role = user` on public registration, inactive-account rejection, safe user responses, and focused backend tests.

No blocker found. Two important issues should be fixed in implementation/tests before source work is considered complete.

## Blocking issues

None.

## Important issues

1. Guest-only auth endpoints are not test-pinned.
   - Evidence: `docs/API.md` Mandatory Access Control Matrix marks `POST /api/auth/register` as Guest conditional, User No, Admin No, and `POST /api/auth/login` as Guest Yes, User No, Admin No.
   - Evidence: `.context/design.md` says register/login are guest endpoints, but `.context/plan.md` ordered test list does not require rejection when an authenticated user/admin calls register or login.
   - Risk: implementation may ignore an existing bearer token and allow authenticated clients to create accounts or log in through guest endpoints, drifting from API access matrix.
   - Required change: add Phase 5 tests or implementation acceptance criteria proving authenticated user/admin requests to register/login are rejected or explicitly documented as outside enforcement with user decision.

2. Registration token response is ambiguous and can drift from documented API contract.
   - Evidence: `docs/API.md` defines `POST /api/auth/login` as the endpoint that returns a JWT access token; `POST /api/auth/register` registers a new user account when public registration is enabled.
   - Evidence: `docs/AUTH_SECURITY.md` says a user can register and then log in immediately, not that registration auto-authenticates.
   - Evidence: `.context/design.md` allows "token plus user" on registration if implementation chooses.
   - Risk: returning a JWT from registration expands token exposure beyond the documented login path and changes frontend/auth behavior without product-doc backing.
   - Required change: implementation should make registration return safe user data only, then login issues token. If auto-login on registration is desired, get explicit user approval or doc update first.

## Optional improvements

- Add one explicit test that a registration payload containing `role = admin` or any extra role-like field still creates `role = user` or is rejected. Plan already says public registration cannot create admin; this makes the smuggling case concrete.
- Add one response-shape test for `/api/auth/me` confirming no `password_hash` and no token field appears.

## Questions for resolution

- Should authenticated clients be rejected from `POST /api/auth/register` and `POST /api/auth/login` with `403`, `409`, or another consistent error? Docs require "No" access but do not specify status code.
- Should registration ever return a JWT access token? Current docs point to no; approve only if product behavior is intentionally changed.

## Files consulted

- `CLAUDE.md`
- `AGENTS.md`
- `docs/index.md`
- `docs/ROADMAP.md`
- `docs/phase.md`
- `.context/research.md`
- `.context/design.md`
- `.context/plan.md`
- `docs/AUTH_SECURITY.md`
- `docs/API.md`
- `docs/DATA_MODEL.md`
- `docs/TESTING_QA.md`
- `C:/Users/Kotletka/.codex/skills/caveman/SKILL.md`
