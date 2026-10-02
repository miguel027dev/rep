# TYVON production release runbook

## Release principle

Ship small, reversible production changes. Product code uses one canonical TYVON experience; historical names are migration-only compatibility details and must not appear in the UI or public API contract.

## Architecture

- React/Vite frontend with deterministic workout rules shared with the Flask backend.
- Flask/Gunicorn API behind the Render proxy.
- PostgreSQL as source of truth for identity, profile, messages, workouts, sets, consent and rate limits.
- Server-side AI gateway; provider credentials never reach the browser.
- Versioned SQL migrations execute under a PostgreSQL advisory lock before Gunicorn serves traffic.
- Readiness: `/api/health/ready`. Liveness: `/api/health/live`.

## Release gate

1. `npm ci`
2. `npm run test:frontend`
3. `python -m pytest -q`
4. `npm run build`
5. CI green on the pull request
6. Merge to `main`
7. Render deploy succeeds
8. Smoke-test health, auth status, static app and API 404 behavior
9. Inspect application/request logs for 5xx or migration errors

## Product invariants

- Minimum account age: 14.
- Under-18 training remains conservative and excludes weight-loss goals.
- There is one public TYVON workout experience.
- Workout records use `engine=tyvon`.
- Email/password uses Argon2id; legacy PBKDF2 upgrades on successful login.
- Authenticated writes require CSRF and account snapshot writes use revision locking.

## Persistence roadmap

The current `/api/account` snapshot contract remains for compatibility in this release. The next persistence release should move workout and message writes to incremental endpoints while retaining the snapshot endpoint for hydration and migration. Keeping that migration separate reduces production risk.
