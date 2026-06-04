# Tasks

## Status Legend

- Pending: not started.
- In Progress: currently being worked on.
- Review: waiting for reviewer or user decision.
- Done: completed and documented.

## Current Task

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

## Review Rule

Every implementation PR should pass local validation where practical, GitHub Actions, secret scan and CodeRabbit. Gemini or ChatGPT review packets are used when available.
