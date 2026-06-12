# Progress

## Current Snapshot

Date: 2026-06-12

Current phase: Post-v1 direction

Current task: TASK-080 - YouTube report JSON engagement data quality flag.

Overall status: the current YouTube v1 slice is closed, and the local reporting JSON now records generation, source, ranking and engagement-aware data quality metadata.

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
- The report CLI now accepts `--no-markdown` with `--json-output` for JSON-only report generation.
- The report CLI now accepts `--quiet` to suppress report-generation summary output.
- The report CLI now accepts `--output-dir` to choose the markdown report directory while preserving artifact-based file names.
- The report CLI now accepts `--json-output-dir` to choose the JSON report directory while preserving artifact-based file names.
- The report CLI now accepts `--json-indent` to choose pretty or compact JSON output.
- The report CLI now accepts `--print-json` to print the JSON summary payload to stdout.
- The report CLI now accepts `--fail-if-empty` to fail before report writing when the selected artifact has no records.
- The report CLI now accepts `--min-records` to fail before report writing when the selected artifact is too small.
- The report CLI now accepts `--dry-run` to validate selected inputs and show planned report paths without writing files.
- The report CLI now accepts `--no-markdown --print-json` to emit JSON without writing report files.
- The package now exposes a `youtube-report` console script for the local report command.
- YouTube reports now expose the selected top-ranking metric value alongside top views.
- YouTube reports now expose total engagements as likes plus comments plus shares.
- YouTube reports now expose engagement rate as total engagements divided by total views.
- YouTube report JSON now exposes engagement rate as a numeric percentage.
- YouTube reports now expose average views per processed record.
- YouTube reports now expose average engagements per processed record.
- YouTube reports now expose average likes, comments and shares per processed record.
- YouTube report JSON now exposes engagement breakdown percentages for likes, comments and shares.
- YouTube report JSON now includes `report_schema_version`.
- YouTube report JSON now includes a UTC `generated_at` timestamp.
- YouTube report JSON now includes provider and source artifact metadata.
- YouTube report JSON now includes ranking metric and limit metadata.
- YouTube report JSON now includes simple data quality metadata.
- YouTube report JSON data quality now indicates whether top content exists.
- YouTube report JSON data quality now exposes a compact status.
- YouTube report JSON data quality now marks current summaries as non-partial.
- YouTube report JSON data quality now indicates whether engagement metrics exist.

## Current Constraints

- `.env`, raw data and processed data must remain local and ignored by Git.
- Do not commit real API keys, channel IDs, payloads, local paths, ports, IPs or expanded DSNs.
- Gemini CLI review may be unavailable when local auth is invalid; GitHub Actions and CodeRabbit remain required on PRs.
- New work should prefer functional closure tasks over further sophistication unless the user explicitly asks for it.

## Next Actions

- Decide whether the next slice should be another real provider or a simple consumption/reporting layer.
- Keep additional infrastructure polish deferred unless it clearly unlocks the next slice.
- Decide whether to deepen the simple consumption layer or open a second real provider.
