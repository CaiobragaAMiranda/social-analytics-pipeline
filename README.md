# Social Analytics Pipeline

Data engineering pipeline for collecting, storing, normalizing, validating and orchestrating social media metrics.

The repository is the source of truth. Work is split into small, reviewable tasks so the project can continue without relying on long chat history.

## Current Status

- Phase: Delivery simplification and YouTube v1 closure
- Current task: TASK-040 - Create a concise YouTube v1 operator runbook and closure checkpoint
- Last completed delivery: TASK-039 - Real YouTube run summary artifact

## Workflow

Before coding a task:

1. Review `docs/PLAN.md`, `docs/TASKS.md` and `docs/PROGRESS.md`.
2. Tell the user the proposed changes, scope, exclusions and validation plan.
3. Implement only after the user confirms or asks to continue.
4. Update documentation and progress.
5. Run local validation.
6. Open a PR so GitHub Actions and CodeRabbit can review it.

## YouTube v1 Closure

The current delivery goal is to close one usable real-provider slice before adding more engineering depth.

YouTube v1 is considered closed when all of the following are true:

1. The local YouTube command runs with local `.env` settings only.
2. The pipeline preserves raw payloads, normalizes metrics and loads them to JSON or PostgreSQL.
3. The local run exposes a compact execution summary without leaking secrets.
4. The Airflow YouTube DAG can be triggered deliberately and complete successfully.
5. The repository documents the minimum safe operator steps to run and verify the flow.

## Useful Commands

```powershell
.\scripts\project_status.ps1
.\scripts\verify_docs.ps1
$env:PYTHONPATH = "src"; python -m unittest discover -s tests
ruff check .
bandit -c pyproject.toml -r src
docker compose --env-file .env.example config --quiet
```

## Project Layout

```text
src/social_analytics_pipeline/  Python package
dags/                           Airflow DAGs
db/init/                        PostgreSQL schema
data/fixtures/                  safe mock payloads
tests/                          automated tests
docs/                           compact project context
SKILLS.md                       engineering standards and daily checklist
scripts/                        status, docs and review helpers
```
