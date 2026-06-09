# Tasks

## Status Legend

- Pending: not started.
- In Progress: currently being worked on.
- Review: waiting for reviewer or user decision.
- Done: completed and documented.

## Delivery Focus

- Keep the YouTube v1 cycle closed and continue with small functional slices.
- Keep the governance pattern, but prefer larger functional tasks over tiny infrastructure refinements.
- Defer extra observability, stronger alerting and broader orchestration work unless they directly unlock the next delivery.

## Current Task

### TASK-052 - Count processed YouTube report artifacts

Status: Done

Phase: Post-v1 direction

Goal: give local automation a small count-only artifact discovery mode before report generation.

Acceptance criteria:

- The report CLI supports `--count-artifacts`.
- Count-only mode prints only the number of processed YouTube artifacts.
- Count-only mode does not write markdown or JSON reports.
- `--count-artifacts --fail-if-missing` returns a failure code when no processed artifacts exist.
- Tests cover parser support, count output, failure behavior and conflicting list-only modes.

Evidence:

- `youtube_report.py` now supports `--count-artifacts`.
- Count-only mode uses the existing processed artifact discovery path.
- Tests cover successful count output, missing-artifact failure and parser exclusivity.
- `docs/BOOTSTRAP.md` documents the new option.

### TASK-051 - Prevent ambiguous YouTube report list-only modes

Status: Done

Phase: Post-v1 direction

Goal: keep artifact discovery commands predictable by rejecting conflicting list-only modes.

Acceptance criteria:

- `--list-artifacts` and `--latest-artifact` cannot be used together.
- Each list-only mode remains available on its own.
- `--fail-if-missing` remains compatible with list-only automation.
- Tests cover accepted and rejected parser combinations.

Evidence:

- `youtube_report.py` now uses an argparse mutually exclusive group for list-only modes.
- Tests cover `--latest-artifact` alone and conflicting list-only arguments.
- Existing list-only execution tests still pass.
- `docs/BOOTSTRAP.md` documents that only one list-only mode should be used at a time.

### TASK-050 - Fail list-only report automation when artifacts are missing

Status: Done

Phase: Post-v1 direction

Goal: let simple automation fail clearly when it expects processed YouTube artifacts but none are available.

Acceptance criteria:

- The report CLI supports `--fail-if-missing`.
- `--list-artifacts --fail-if-missing` returns a failure code when no processed artifacts exist.
- Existing list behavior remains successful when the flag is not used.
- Tests cover parser support and missing-artifact failure behavior.

Evidence:

- `youtube_report.py` now supports `--fail-if-missing`.
- List-only mode can return exit code 1 when no processed artifacts exist.
- Tests cover argument parsing and missing-artifact failure behavior.
- `docs/BOOTSTRAP.md` documents the new option.

### TASK-049 - Print the latest processed YouTube report artifact

Status: Done

Phase: Post-v1 direction

Goal: make automation and local operation simpler when only the latest processed artifact path is needed.

Acceptance criteria:

- The report CLI supports `--latest-artifact`.
- The command prints only the latest processed artifact path and exits.
- The command does not write markdown or JSON reports in this mode.
- Tests cover latest-artifact behavior and argument parsing.

Evidence:

- `youtube_report.py` now supports `--latest-artifact`.
- Latest artifact output reuses the existing processed artifact discovery path.
- Tests cover relative latest-artifact output and list-only execution.
- `docs/BOOTSTRAP.md` documents the new option.

### TASK-048 - List processed YouTube report artifacts

Status: Done

Phase: Post-v1 direction

Goal: make it easier to choose a processed YouTube artifact before generating a local report.

Acceptance criteria:

- The report CLI supports `--list-artifacts`.
- Listing artifacts exits without writing markdown or JSON reports.
- Listed paths are project-relative and safe for repository documentation.
- Tests cover listing behavior and argument parsing.

Evidence:

- `youtube_report.py` now supports `--list-artifacts`.
- Artifact listing reuses the existing processed artifact discovery path.
- Tests cover sorted relative artifact listing and list-only CLI execution.
- `docs/BOOTSTRAP.md` documents the new option.

### TASK-047 - Add optional JSON output to the YouTube report CLI

Status: Done

Phase: Post-v1 direction

Goal: make the local YouTube report easier to reuse in automation by saving a compact structured summary when requested.

Acceptance criteria:

- The report CLI supports an optional `--json-output` path.
- Markdown output remains the default behavior.
- The JSON summary includes aggregate totals, ranking metadata and sanitized top rows.
- Tests cover JSON payload generation, persistence and CLI parsing.

Evidence:

- `youtube_report.py` now supports `--json-output`.
- JSON output is written only when explicitly requested.
- The JSON payload exports compact report fields instead of raw processed rows.
- Tests cover JSON persistence, argument parsing and explicit CLI execution.

### TASK-046 - Add configurable ranking metric to the YouTube report CLI

Status: Done

Phase: Post-v1 direction

Goal: let users choose which engagement metric drives the top-content ranking in the local YouTube markdown report.

Acceptance criteria:

- The report CLI supports a `--sort-by` option.
- The default ranking metric remains `views`.
- Supported metrics are `views`, `likes`, `comments` and `shares`.
- Tests cover custom ranking behavior and invalid metrics.

Evidence:

- `youtube_report.py` now supports `--sort-by`.
- Ranking generation now uses the selected metric while preserving the previous default.
- Tests cover `likes` ranking, invalid ranking metrics and CLI parsing.
- `docs/BOOTSTRAP.md` documents the new option.

### TASK-045 - Add configurable top-content size to the YouTube report CLI

Status: Done

Phase: Post-v1 direction

Goal: make local YouTube reports easier to tune by allowing users to choose how many ranked content rows appear in the markdown report.

Acceptance criteria:

- The report CLI supports a `--top` option.
- The default top-content ranking remains five rows.
- Invalid `--top` values fail clearly before report generation.
- Tests cover custom top limits and invalid values.

Evidence:

- `youtube_report.py` now supports `--top` with a positive integer validator.
- `build_youtube_report_summary_with_limit` controls the ranking size while preserving the existing default behavior.
- Tests cover explicit top limits, invalid top limits and CLI parsing.
- `docs/BOOTSTRAP.md` documents the new option.

### TASK-044 - Add explicit input and output options to the YouTube report CLI

Status: Done

Phase: Post-v1 direction

Goal: make local YouTube reporting easier to operate by allowing users to choose the processed artifact and markdown output path.

Acceptance criteria:

- The report CLI supports an explicit processed artifact path.
- The report CLI supports an explicit markdown output path.
- Default behavior still uses the latest processed artifact and default report location.
- Tests cover argument parsing and explicit path behavior.

Evidence:

- `youtube_report.py` now supports `--artifact` and `--output`.
- `write_youtube_report_markdown` accepts a custom output path while preserving the default path behavior.
- Tests cover argument parsing, custom output persistence, explicit-path CLI execution and output paths outside the project root.
- `docs/BOOTSTRAP.md` documents the optional arguments.

### TASK-043 - Add a shareable local YouTube markdown report

Status: Done

Phase: Post-v1 direction

Goal: make the existing YouTube data easier to consume by generating a small shareable markdown report instead of adding a dashboard or new infrastructure.

Acceptance criteria:

- The local report command generates a markdown file from the latest processed YouTube artifact.
- The markdown report includes compact aggregate metrics and a top-content ranking.
- The command still fails clearly when no processed artifact exists or the artifact is invalid.
- Tests cover summary aggregation and markdown persistence.

Evidence:

- `youtube_report.py` now writes a markdown report under `data/reports/youtube/`.
- The report includes totals plus a top-content table ranked by views.
- The command still reads the latest file from `data/processed/youtube/` by default.
- Tests cover latest-file selection, summary aggregation, markdown generation and invalid artifact handling.

### TASK-042 - Add a simple local YouTube report command for processed artifacts

Status: Done

Phase: Post-v1 direction

Goal: make the existing YouTube data immediately useful by adding a small local consumption command instead of more infrastructure.

Acceptance criteria:

- A local command can read the latest processed YouTube artifact.
- The command prints compact aggregated metrics from processed data.
- The command fails clearly when no processed artifact exists or the artifact is invalid.
- Tests cover artifact selection and summary aggregation.

Evidence:

- Added `src/social_analytics_pipeline/cli/youtube_report.py`.
- The command reads the latest file from `data/processed/youtube/` by default.
- The command prints totals for views, likes, comments, shares, followers and top content.
- Tests cover latest-file selection, summary aggregation and invalid artifact handling.

### TASK-041 - Record YouTube v1 closure and define the next delivery decision

Status: Done

Phase: Post-v1 direction

Goal: formally close the current YouTube v1 slice in repository context and make the next step explicit before new implementation work starts.

Acceptance criteria:

- The repository states that the YouTube v1 closure checkpoint has been met.
- The repository no longer presents the current cycle as still "closing".
- The next delivery decision is explicit and compact.
- The next options stay focused on product value instead of additional engineering polish.

Evidence:

- `README.md` now reflects the post-v1 decision phase.
- `docs/PLAN.md` now records the next delivery options after YouTube v1 closure.
- `docs/PROGRESS.md` now states that the YouTube v1 cycle is closed in repository context.
- The backlog now points to a deliberate next decision instead of more implicit closure work.

### TASK-040 - Create a concise YouTube v1 operator runbook and closure checkpoint

Status: Done

Phase: Phase 1 - MVP Core

Goal: make the existing real YouTube path easy to run, verify and hand off without adding new technical layers first.

Acceptance criteria:

- The repository documents the minimum steps to run the real YouTube path locally.
- The repository documents the minimum steps to run the YouTube Airflow DAG deliberately.
- The repository states what counts as "YouTube v1 closed" for the current cycle.
- The guidance stays compact and does not expose secrets, local paths or raw payloads.

Notes:

- This task is intentionally operational, not architectural.
- Its purpose is to close the current delivery cycle before expanding scope again.

Evidence:

- `README.md` now states the YouTube v1 closure target in compact form.
- `docs/BOOTSTRAP.md` now includes a minimal local and Airflow operator runbook.
- The repository now records a concrete closure checkpoint for the current YouTube cycle.
- The guidance stays compact and avoids secrets, local paths and raw payload details.

### TASK-039 - Persist a structured run summary for the real YouTube pipeline

Status: Done

Phase: Phase 3 - Resilience

Goal: keep a compact execution summary artifact for each real YouTube run so troubleshooting does not depend on terminal output or Airflow task logs alone.

Acceptance criteria:

- Each local YouTube run writes a structured JSON run summary artifact.
- The summary captures interval, status, execution counts and artifact locations.
- The local CLI output shows the run summary path.
- The YouTube Airflow DAG result includes the run summary path.
- Tests prove the summary file is created for both healthy and warning runs.

Evidence:

- Added run summary artifact helpers in `pipeline/artifacts.py`.
- `run_youtube_local_pipeline` now writes a run summary under `data/runs/youtube/`.
- The local CLI output now prints `run_summary_path`.
- The YouTube Airflow DAG return payload now includes `run_summary_path`.
- Tests confirm summary creation and warning status behavior when invalid records are diverted to the DLQ.

### TASK-037 - Add a local DLQ for invalid records without breaking the main load

Status: Done

Phase: Phase 3 - Resilience

Goal: isolate invalid normalized records into a local dead letter queue so valid metrics can still load.

Acceptance criteria:

- Invalid records do not stop valid records from loading.
- Invalid records are persisted in a local DLQ area with a reason and raw file reference.
- The pipeline result reports invalid record counts.
- Tests prove that invalid records are diverted while valid load behavior remains intact.

Evidence:

- Added `storage/dlq.py` with local dead letter storage for invalid records.
- `run_provider_pipeline` now diverts invalid records to `data/dlq/` and continues loading valid metrics.
- `LocalPipelineResult` now reports `invalid_records`.
- YouTube local and Airflow summaries now include invalid record counts.
- Tests confirm invalid records are persisted to the DLQ while the main load path remains usable.

### TASK-038 - Add runtime metrics and simple invalid-record alerting

Status: Done

Phase: Phase 3 - Resilience

Goal: expose execution counts more clearly and allow deliberate failure when invalid records are detected.

Acceptance criteria:

- Pipeline results expose valid record counts.
- YouTube local and Airflow summaries include a simple execution status.
- A local environment flag can fail the run when invalid records were sent to the DLQ.
- Tests cover the invalid-record alert policy.

Evidence:

- `LocalPipelineResult` now exposes `valid_records`.
- YouTube local output now reports `valid_records` and can fail when `YOUTUBE_FAIL_ON_INVALID_RECORDS=true`.
- The YouTube Airflow DAG now reports `status`, `valid_records`, `invalid_records`, and `loaded_records`.
- Tests cover warning-only behavior and fail-on-invalid behavior.

### TASK-036 - Add controlled YouTube backfill support without re-enabling automatic DAG catchup

Status: Done

Phase: Phase 3 - Resilience

Goal: support deliberate historical YouTube intervals without restoring automatic catchup behavior in Airflow.

Acceptance criteria:

- Explicit backfill start and end settings are supported for local YouTube runs.
- The real YouTube DAG can use explicit backfill settings only when Airflow interval context is absent.
- Invalid or partial backfill configuration fails early with clear errors.
- Automatic DAG catchup remains disabled.
- Tests cover explicit backfill interval parsing and validation.

Evidence:

- Added `YOUTUBE_BACKFILL_START_AT` and `YOUTUBE_BACKFILL_END_AT` parsing in `youtube_smoke.py`.
- Local YouTube commands now reuse the explicit backfill interval when both values are present.
- The real YouTube DAG uses the explicit backfill interval only as a controlled fallback when no Airflow data interval is provided.
- Tests cover missing pair behavior, timezone validation, reversed ranges, and explicit UTC parsing.
- `.env.example` and `docs/BOOTSTRAP.md` document the new backfill variables.

### TASK-035 - Decide whether to expand to another provider or harden YouTube first

Status: Done

Phase: Phase 4 - Quality and scale

Goal: choose the next implementation direction based on the real maturity of the repository, not on mock coverage alone.

Acceptance criteria:

- The decision is documented in repository context.
- The decision explains why the chosen path is lower risk and higher value.
- A concrete follow-up task is created for the chosen direction.

Evidence:

- The repository currently has one real provider path end to end: YouTube.
- Instagram and TikTok are still represented by mock providers only.
- The real YouTube path already includes local CLI execution, raw storage, normalization, validation, PostgreSQL loading, Airflow orchestration, resilience, and tests.
- The next implementation direction is to harden YouTube further with controlled backfill before expanding to another real provider.

Decision:

- Choose depth before breadth.
- Continue with YouTube first.
- Defer new real provider expansion until the YouTube path supports deliberate historical recovery behavior.

### TASK-034 - Add data validation before loading metrics

Status: Done

Phase: Phase 4 - Quality and scale

Goal: block impossible normalized metrics before they reach JSON artifacts or PostgreSQL loads.

Acceptance criteria:

- Normalized metrics are validated before the load step.
- Empty required identifiers are rejected.
- Negative metric counters are rejected.
- `published_at` after `collected_at` is rejected.
- Tests prove invalid metrics stop the load path.

Evidence:

- Added `transform/validation.py` with targeted metric validation.
- `run_provider_pipeline` now validates metrics before calling the loader.
- Tests cover invalid counters, invalid timestamps, empty identifiers, and pipeline load blocking.

### TASK-033 - Add retry/backoff and clearer failure alerts for API/configuration errors

Status: Done

Phase: Phase 3 - Resilience

Goal: make the real YouTube provider fail more safely by retrying transient API/network errors, stopping early on invalid credentials/configuration, and preserving sanitized error messages.

Acceptance criteria:

- Retryable YouTube API failures use bounded retry/backoff behavior.
- Invalid credentials or configuration errors fail without useless retries.
- Error messages remain sanitized and do not expose API keys, local paths, or raw request URLs.
- Automated tests cover retry success, retry exhaustion, and credential/configuration failures.

Evidence:

- `HttpJsonClient` now retries transient request failures and stops early on `401` and `403`.
- `YouTubeApiConfig.from_env` validates retry/backoff environment settings.
- `tests/test_youtube_provider.py` covers retryable status handling, retry exhaustion, and credential failure behavior.

### TASK-032 - Validate `social_analytics_youtube_pipeline` inside local Airflow

Status: Done

Phase: Phase 2 - Orchestration and history

Goal: prove the real YouTube DAG can be parsed, triggered and completed in the local Airflow Docker environment without exposing secrets, channel IDs or payloads.

Acceptance criteria:

- Airflow metadata initialization succeeds.
- Airflow API server, scheduler, DAG processor, worker, triggerer, Redis and PostgreSQL containers are healthy.
- `social_analytics_youtube_pipeline` is listed by Airflow.
- A manual DAG run finishes successfully.
- Logs mask the configured channel and do not print API keys or payloads.
- The real YouTube DAG does not automatically backfill historical intervals.

Evidence:

- `docker compose --env-file .env config --quiet` passed.
- `docker compose --env-file .env up airflow-init` completed successfully.
- Airflow services started and reported healthy where applicable.
- `airflow dags list` showed `social_analytics_youtube_pipeline`.
- Manual run `manual__2026-06-03T14:58:41.282474+00:00` completed with `success`.
- Successful task log returned `raw_records=50` and `loaded_records=50` with `channel_id=<configured>`.
- Local DAG was paused after validation to avoid accidental YouTube API quota usage.

## Completed Task Summary

| Task range | Summary | Status |
| --- | --- | --- |
| TASK-001 to TASK-007 | Governance foundation, Python skeleton, mock providers, shared schema, PostgreSQL loader and local mock pipeline. | Done |
| TASK-008 to TASK-010 | Airflow Docker environment, mock pipeline DAG, 15-day schedule and catchup. | Done |
| TASK-011 to TASK-017 | Change proposal governance, security gates, sensitive-data checks, Airflow/Postgres readiness and loader configuration. | Done |
| TASK-018 to TASK-021 | Initial real YouTube provider and safe smoke command with `.env` support. | Done |
| TASK-022 to TASK-023 | Multi-agent governance and review packet improvements. | Done |
| TASK-024 to TASK-026 | Safer YouTube configuration validation, sanitized HTTP errors and handle resolution. | Done |
| TASK-027 to TASK-029 | Real YouTube local raw/processed pipeline and PostgreSQL load validation. | Done |
| TASK-030 | Real YouTube Airflow DAG, environment wiring and CI/CodeRabbit validation in PR #19. | Done |
| TASK-031 | Main documentation condensed into compact English project context. | Done |
| TASK-032 | Real YouTube Airflow DAG validated locally with a successful manual run. | Done |
| TASK-033 | Retry/backoff and clearer YouTube failure handling with targeted tests. | Done |
| TASK-034 | Metric validation now blocks impossible data before JSON/PostgreSQL load. | Done |
| TASK-035 | Decision recorded: harden the real YouTube path before expanding to another real provider. | Done |
| TASK-036 | Controlled YouTube backfill now supports explicit intervals without re-enabling DAG catchup. | Done |
| TASK-037 | Invalid records now go to a local DLQ without blocking valid loads. | Done |
| TASK-038 | Runtime metrics and simple invalid-record alerting were added to the YouTube path. | Done |
| TASK-039 | Real YouTube runs now persist a compact structured run summary artifact. | Done |
| TASK-040 | The repository now includes a concise YouTube v1 runbook and closure checkpoint. | Done |
| TASK-041 | The repository now treats the YouTube v1 slice as closed and sets up the next decision. | Done |
| TASK-042 | A simple local YouTube report command now consumes processed artifacts. | Done |
| TASK-043 | The local YouTube report command now generates a shareable markdown report. | Done |
| TASK-044 | The local YouTube report command now accepts explicit input and output paths. | Done |
| TASK-045 | The local YouTube report command now supports configurable top-content ranking size. | Done |
| TASK-046 | The local YouTube report command now supports configurable ranking metrics. | Done |
| TASK-047 | The local YouTube report command now supports optional compact JSON summaries. | Done |
| TASK-048 | The local YouTube report command can list processed artifacts before reporting. | Done |
| TASK-049 | The local YouTube report command can print only the latest processed artifact. | Done |
| TASK-050 | The local YouTube report command can fail list-only automation when artifacts are missing. | Done |
| TASK-051 | The local YouTube report command rejects ambiguous list-only mode combinations. | Done |
| TASK-052 | The local YouTube report command can print only the processed artifact count. | Done |

## Deferred Until After v1 Closure

- Broaden run summaries beyond the real YouTube path.
- Add stronger alert delivery beyond the current local fail-on-invalid mode.
- Revisit broader Airflow/observability refinements.
- Expand to additional real providers only after the current YouTube cycle is clearly closed.

## Next Candidate Deliveries

- Add a second real provider path only if a public and stable source is practical.
- Add a simple consumption layer for the existing YouTube metrics before deepening infrastructure again.
- Keep extra architecture refinement deferred unless it directly unlocks the next delivery.

## Review Rule

Every implementation PR should pass local validation where practical, GitHub Actions, secret scan and CodeRabbit. Gemini or ChatGPT review packets are used when available.
