# Progress

## Current Snapshot

Date: 2026-06-09

Current phase: Post-v1 direction

Current task: TASK-052 - Count processed YouTube report artifacts.

Overall status: the current YouTube v1 slice is closed, and the local reporting flow now has explicit controls to list, identify or count processed artifacts before report generation.

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
- The next delivery direction is now explicit: controlled YouTube backfill before any new real provider expansion.
- Controlled YouTube backfill now supports explicit start/end timestamps for local and fallback DAG runs.
- Invalid normalized records now go to a local DLQ with a reason and raw file reference instead of stopping the full pipeline.

## Latest Notes

- Windows reserved the previous local metrics PostgreSQL port; the local `.env` now uses a non-reserved port.
- Airflow 3.2.1 initialization now runs metadata migration without the incompatible user creation command.
- Celery workers now use the Airflow execution API URL and a shared JWT secret from local environment configuration.
- Automatic catchup is disabled for the real YouTube DAG to avoid unexpected YouTube API quota usage. Mock DAG catchup remains available for historical orchestration testing.
- The successful YouTube Airflow run loaded 50 records and masked the configured channel in logs.
- The YouTube HTTP client now retries transient statuses like `429` and `503`, but stops immediately on invalid credentials like `401` and `403`.
- Validation now rejects empty identifiers, negative counters, and `published_at` values later than `collected_at`.
- New provider breadth was intentionally deferred because only YouTube currently has a real end-to-end path.
- Automatic YouTube DAG catchup is still disabled; historical recovery now happens only through explicit backfill settings.
- Pipeline summaries now expose invalid record counts for local and Airflow-backed YouTube runs.
- Real YouTube executions now persist a structured run summary with interval, status, counts and artifact locations.
- The delivery strategy was simplified: keep governance, but prioritize cycle closure over new engineering layers.
- The repository now documents what must be true to consider the current YouTube v1 delivery closed.
- The repository now treats the YouTube v1 cycle as closed and shifts attention to the next functional slice.
- The repository now includes a small local reporting step for processed YouTube artifacts.
- The local YouTube reporting step now also writes a markdown report with ranked content.
- The report CLI now accepts explicit processed artifact and markdown output paths.
- The report CLI now accepts `--top` to control the top-content ranking size.
- The report CLI now accepts `--sort-by` to choose the ranking metric.
- The report CLI now accepts `--json-output` to save a compact structured summary.
- The report CLI now accepts `--list-artifacts` to show available processed artifacts.
- The report CLI now accepts `--latest-artifact` to print only the latest processed artifact.
- The report CLI now accepts `--fail-if-missing` so list-only automation can fail when no processed artifact exists.
- The report CLI now rejects using `--list-artifacts` and `--latest-artifact` together.
- The report CLI now accepts `--count-artifacts` to print only the processed artifact count.

## Current Constraints

- `.env`, raw data and processed data must remain local and ignored by Git.
- Do not commit real API keys, channel IDs, payloads, local paths, ports, IPs or expanded DSNs.
- Gemini CLI review may be unavailable when local auth is invalid; GitHub Actions and CodeRabbit remain required on PRs.
- New work should prefer functional closure tasks over further sophistication unless the user explicitly asks for it.

## Next Actions

- Decide whether the next slice should be another real provider or a simple consumption/reporting layer.
- Keep additional infrastructure polish deferred unless it clearly unlocks the next slice.
- Decide whether to deepen the simple consumption layer or open a second real provider.
