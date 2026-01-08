---
id: 0008
title: Fix auth service API prefix
stage: misc
date: 2026-01-05
surface: agent
model: claude-opus-4-5-20251101
feature: phase_2_web_App
branch: 001-phase-2-web-app
user: madeeha
command: fix failed to fetch after login
labels: ["frontend", "auth", "api", "bugfix"]
links:
  spec: null
  ticket: null
  adr: null
  pr: null
files:
  - phase_2_web_App/frontend/src/app/services/auth.ts
tests: []
---

## Prompt

"Failed to fetch" error occurring after login attempt.

## Response snapshot

I analyzed the `auth` service and the existing `tasks` service. The `tasks` service was correctly using the `/api` prefix for all endpoints, but the `auth` service was attempting to fetch from `/auth/token` and `/auth/register` directly at the root. I updated the `auth` service to include the `/api` prefix, matching the backend's expected directory structure (routes are under `src/api`).

## Outcome

- ✅ Impact: Corrected API endpoints in the authentication service.
- 📁 Files: Updated `phase_2_web_App/frontend/src/services/auth.ts`.
- 🧠 Reflection: Consistency in API endpoint prefixing is crucial across services.

## Evaluation notes (flywheel)

- Failure modes observed: Missing /api prefix in auth endpoints.
- Graders run and results (PASS/FAIL): PASS
- Prompt variant (if applicable): null
- Next experiment (smallest change to try): null
