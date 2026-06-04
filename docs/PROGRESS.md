# Progress

## Current Snapshot

Date: 2026-06-04

Current phase: Phase 3 - Resilience

Current task: TASK-034 - Add data validation before loading metrics.

Overall status: TASK-034 completed locally in code and tests. The pipeline now validates normalized metrics before JSON and PostgreSQL load paths.

## Completed Milestones

- Governance docs and review scripts were created.
- Python package skeleton, tests and quality gates were added.
- Mock providers for Instagram, YouTube and TikTok were created.
- A shared social metric schema and normalizers were implemented.
- PostgreSQL local loading was added with idempotent upsert behavior.
- Docker Compose now supports PostgreSQL and Airflow.
- Airflow has a mock pipeline DAG with 15-day schedule and catchup.
- YouTube Data API support was added behind local environment variables.
- Safe YouTube smoke and local pipeline commands were added.
- Real YouTube local JSON and PostgreSQL loads were validated without printing secrets or payloads.
- A real YouTube Airflow DAG was added and merged in PR #19.
- Local Airflow validation completed for the real YouTube DAG.
- YouTube provider resilience now includes retry/backoff and clearer credential failure handling.
- Invalid normalized metrics are now blocked before artifact or PostgreSQL loading.

## Latest Notes

- Windows reserved the previous local metrics PostgreSQL port; the local `.env` now uses a non-reserved port.
- Airflow 3.2.1 initialization now runs metadata migration without the incompatible user creation command.
- Celery workers now use the Airflow execution API URL and a shared JWT secret from local environment configuration.
- Automatic catchup is disabled for the real YouTube DAG to avoid unexpected YouTube API quota usage. Mock DAG catchup remains available for historical orchestration testing.
- The successful YouTube Airflow run loaded 50 records and masked the configured channel in logs.
- The YouTube HTTP client now retries transient statuses like `429` and `503`, but stops immediately on invalid credentials like `401` and `403`.
- Validation now rejects empty identifiers, negative counters, and `published_at` values later than `collected_at`.

## Current Constraints

- `.env`, raw data and processed data must remain local and ignored by Git.
- Do not commit real API keys, channel IDs, payloads, local paths, ports, IPs or expanded DSNs.
- Gemini CLI review may be unavailable when local auth is invalid; GitHub Actions and CodeRabbit remain required on PRs.

## Next Actions

- Decide whether the next work should expand provider coverage or deepen controlled backfill behavior for YouTube.
- Decide whether the next work should expand provider coverage or deepen controlled backfill behavior for YouTube.
