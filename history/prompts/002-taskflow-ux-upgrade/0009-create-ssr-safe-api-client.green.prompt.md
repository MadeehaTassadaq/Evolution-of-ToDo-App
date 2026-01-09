---
id: "0009"
title: Create SSR-safe API client for 401 fix
stage: green
date: 2026-01-09
surface: agent
model: claude-opus-4-5-20251101
feature: 002-taskflow-ux-upgrade
branch: 002-taskflow-ux-upgrade
user: madeeha
command: direct-request
labels: ["api-client", "auth", "ssr-safety", "401-handling"]
links:
  spec: null
  ticket: null
  adr: null
  pr: null
files:
  - phase_2_web_App/frontend/src/lib/auth.ts
  - phase_2_web_App/frontend/src/lib/api-client.ts
  - phase_2_web_App/frontend/src/services/tasks.ts
tests:
  - N/A (manual verification)
---

## Prompt

You are a senior full-stack engineer.

I am getting 401 Unauthorized from my FastAPI backend when calling:
POST /api/tasks/ and GET /api/tasks/

Important context:

Authentication uses JWT stored in localStorage

Backend expects Authorization: Bearer <token>

Backend auth is correct and must NOT be changed

401 happens because frontend requests are sometimes sent without a valid token

This happens especially on:

Fresh page load

First task creation after login

Your task:

Create a single SSR-safe API client at src/lib/api-client.ts

Read token from localStorage safely (typeof window !== "undefined")

Automatically attach Authorization: Bearer <token> to all requests

Implement global 401 handling:

Clear localStorage

Redirect to /login

Create src/lib/auth.ts with:

getToken()

isAuthenticated()

SSR safety

Refactor src/services/tasks.ts to use the new API client

Ensure no API request fires if token is missing

Constraints:

Do NOT use cookies

Do NOT use middleware

Do NOT access localStorage outside client-only code

Use NEXT_PUBLIC_API_URL

Output format:

Provide only the final code for:

src/lib/auth.ts

src/lib/api-client.ts

src/services/tasks.ts

No explanations

## Response snapshot

Created three files:
1. `src/lib/auth.ts` - SSR-safe auth utilities: getToken(), getUserId(), isAuthenticated(), setToken(), clearAuth(), redirectToLogin() - all with typeof window checks
2. `src/lib/api-client.ts` - Authenticated API client with: pre-request auth check, auto Authorization header, global 401 handling (clear + redirect), AuthenticationError class
3. `src/services/tasks.ts` - Refactored to use new api.get/post/put/patch/delete methods with AuthenticationError handling

## Outcome

- Impact: Fixed 401 errors on fresh page load and first task creation by ensuring token is checked before requests fire
- Tests: Manual verification required
- Files: 3 files created/modified
- Next prompts: Test login flow end-to-end, verify 401 redirect works
- Reflection: Clean separation of auth utilities from API client improves maintainability

## Evaluation notes (flywheel)

- Failure modes observed: None
- Graders run and results (PASS/FAIL): N/A
- Prompt variant (if applicable): N/A
- Next experiment (smallest change to try): N/A
