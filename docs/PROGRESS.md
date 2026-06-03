# Progress

## Current Snapshot

Date: 2026-06-03

Current phase: Phase 2 - Orchestration and history

Current task: TASK-031 - Condense documentation in English.

Overall status: TASK-031 completed locally. Main documentation is now compact, English-first and still preserves current project state, workflow and safety rules.

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

## Current Constraints

- `.env`, raw data and processed data must remain local and ignored by Git.
- Do not commit real API keys, channel IDs, payloads, local paths, ports, IPs or expanded DSNs.
- Gemini CLI review may be unavailable when local auth is invalid; GitHub Actions and CodeRabbit remain required on PRs.

## Next Actions

- Validate the real YouTube DAG inside local Airflow.
- Add targeted resilience around API failures and invalid configuration.
