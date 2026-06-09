# Social Analytics Pipeline

Data engineering pipeline for collecting, storing, normalizing, validating and orchestrating social media metrics.

The repository is the source of truth. Work is split into small, reviewable tasks so the project can continue without relying on long chat history.

## Current Status

- Phase: Post-v1 direction
- Current task: TASK-044 - Add explicit input and output options to the YouTube report CLI
- Last completed delivery: TASK-043 - Shareable local YouTube markdown report

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

The repository now treats this YouTube v1 slice as closed. The next decision should favor product value, such as another real provider or a simple layer to consume the metrics already being collected.

The repository now includes that simple consumption layer in local CLI form: a YouTube report command that reads the latest processed artifact, prints compact aggregate metrics and writes a markdown report.

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
