# Tasks

## Status Legend

- Pending: not started.
- In Progress: currently being worked on.
- Review: waiting for reviewer or user decision.
- Done: completed and documented.

## Current Task

### TASK-031 - Condense documentation in English

Status: Done

Phase: Phase 0 - Governance

Goal: replace long Portuguese documentation with concise English documentation while keeping the project state, workflow, safety rules and validation commands easy to resume.

Acceptance criteria:

- Main documentation files are in English.
- `README.md`, `docs/PLAN.md`, `docs/TASKS.md`, `docs/PROGRESS.md`, `docs/BOOTSTRAP.md`, `docs/ARCHITECTURE.md`, `docs/AGENT_CONTRACTS.md` and ADR-0001 remain present.
- Historical task detail is summarized instead of repeated in full.
- Safety rules about secrets, local paths, payloads and expanded DSNs remain explicit.
- `scripts/project_status.ps1` and `scripts/verify_docs.ps1` still work.

Evidence:

- `.\scripts\verify_docs.ps1` passed.
- `.\scripts\project_status.ps1` passed.
- Documentation was reduced from long historical logs to compact English summaries.

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

## Backlog

| ID | Task | Status |
| --- | --- | --- |
| TASK-032 | Validate `social_analytics_youtube_pipeline` inside local Airflow. | Pending |
| TASK-033 | Add retry/backoff and clearer failure alerts for API/configuration errors. | Pending |
| TASK-034 | Add data validation before loading metrics. | Pending |
| TASK-035 | Decide whether to expand to another provider or harden YouTube first. | Pending |

## Review Rule

Every implementation PR should pass local validation where practical, GitHub Actions, secret scan and CodeRabbit. Gemini or ChatGPT review packets are used when available.
