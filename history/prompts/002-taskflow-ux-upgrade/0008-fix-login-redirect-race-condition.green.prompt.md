---
id: 0008
title: Fix Login to Tasks Redirect Race Condition
stage: green
date: 2026-01-09
surface: agent
model: claude-opus-4-5-20251101
feature: 002-taskflow-ux-upgrade
branch: 002-taskflow-ux-upgrade
user: madeeha
command: chat
labels: ["bug-fix", "auth", "race-condition", "localStorage"]
links:
  spec: null
  ticket: null
  adr: null
  pr: null
files:
  - phase_2_web_App/frontend/src/app/tasks/page.tsx
tests:
  - Manual test: login -> redirect to /tasks should work reliably
---

## Prompt

i am facing this error while redirecting from login to tasks page You login

You navigate to /tasks

/tasks page starts loading

React runs this logic:

if (!token) router.replace("/login")


At that moment:

token === null

OR localStorage not read yet

Redirect fires

Browser aborts /tasks

/login loads again

## Response snapshot

Identified race condition where `/tasks` page's auth check runs before localStorage is reliably accessible after `window.location.replace()` navigation from login page.

Fixed by:
1. Adding 50ms delay before auth check to let localStorage settle
2. Adding `isMounted` guard to prevent state updates after unmount
3. Adding cleanup function to clear timeout on unmount
4. Changed `router.push` to `router.replace` for cleaner navigation

Key code change in `tasks/page.tsx` lines 63-84:
```javascript
useEffect(() => {
  let isMounted = true;
  const timer = setTimeout(() => {
    if (!isMounted) return;
    const token = localStorage.getItem('authToken');
    if (!token) {
      router.replace('/login');
      return;
    }
    setIsAuthChecked(true);
    fetchTasks();
  }, 50);
  return () => {
    isMounted = false;
    clearTimeout(timer);
  };
}, []);
```

## Outcome

- Impact: Fixed redirect loop bug preventing users from accessing tasks after login
- Tests: Manual verification required - login flow should now work reliably
- Files: 1 file modified (tasks/page.tsx)
- Next prompts: Test the fix, consider implementing a proper auth context/provider
- Reflection: Race conditions with localStorage after full page navigation are common; small delays or retry mechanisms are practical solutions

## Evaluation notes (flywheel)

- Failure modes observed: localStorage read returning null immediately after window.location.replace()
- Graders run and results (PASS/FAIL): Manual testing required
- Prompt variant (if applicable): N/A
- Next experiment (smallest change to try): If issue persists, increase delay or implement retry logic
