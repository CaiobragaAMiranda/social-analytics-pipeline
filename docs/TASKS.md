# Tasks

## Status Legend

- Pending: not started.
- In Progress: currently being worked on.
- Review: waiting for reviewer or user decision.
- Done: completed and documented.

## Current Task

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

## Backlog

| ID | Task | Status |
| --- | --- | --- |
| TASK-033 | Add retry/backoff and clearer failure alerts for API/configuration errors. | Pending |
| TASK-034 | Add data validation before loading metrics. | Pending |
| TASK-035 | Decide whether to expand to another provider or harden YouTube first. | Pending |

## Review Rule

Every implementation PR should pass local validation where practical, GitHub Actions, secret scan and CodeRabbit. Gemini or ChatGPT review packets are used when available.
