# Bootstrap

## Requirements

- Windows PowerShell.
- Git.
- Python 3.12+.
- Docker Desktop for PostgreSQL and Airflow.
- Node.js only when using Gemini CLI through npm.

## Setup

```powershell
cd <project-root>
Copy-Item .env.example .env
python -m pip install --upgrade pip
python -m pip install -r requirements-dev.txt
```

Fill local `.env` values only on your machine. Never commit `.env`, raw API payloads, generated data, real channel IDs, expanded DSNs or local paths.

For Airflow with CeleryExecutor, set `AIRFLOW_API_AUTH_JWT_SECRET` locally to the same non-empty random value for all containers. The Compose file passes it to `AIRFLOW__API_AUTH__JWT_SECRET` so workers can authenticate with the Airflow execution API.

## Local Checks

```powershell
.\scripts\project_status.ps1
.\scripts\verify_docs.ps1
$env:PYTHONPATH = "src"; python -m unittest discover -s tests
ruff check .
bandit -c pyproject.toml -r src
docker compose --env-file .env.example config --quiet
```

Optional dependency/security checks:

```powershell
pip-audit .
gitleaks detect --source . --config .gitleaks.toml
```

## PostgreSQL

Start the metrics database:

```powershell
docker compose up -d postgres
docker compose ps
```

The schema is initialized from `db/init/001_create_social_metrics.sql`.

Reset local volumes only when you intentionally want a clean database:

```powershell
docker compose down -v
docker compose up -d postgres
```

## YouTube Local Commands

Required local settings:

```text
YOUTUBE_API_KEY=<local-api-key>
YOUTUBE_CHANNEL_ID=<public-channel-id>
YOUTUBE_CHANNEL_HANDLE=<optional-public-handle>
YOUTUBE_MAX_PAGES=1
YOUTUBE_SMOKE_LOOKBACK_DAYS=30
YOUTUBE_BACKFILL_START_AT=<optional-iso-8601-start>
YOUTUBE_BACKFILL_END_AT=<optional-iso-8601-end>
YOUTUBE_LOCAL_LOAD_TARGET=json
```

Use `YOUTUBE_CHANNEL_ID` when available. Otherwise use `YOUTUBE_CHANNEL_HANDLE`; the code resolves it without printing the resolved channel ID.
Use `YOUTUBE_BACKFILL_START_AT` and `YOUTUBE_BACKFILL_END_AT` together only when you want a deliberate historical interval. Keep them empty for normal lookback-based runs.

Safe smoke run:

```powershell
$env:PYTHONPATH = "src"
python -m social_analytics_pipeline.cli.youtube_smoke
```

Safe local load:

```powershell
$env:PYTHONPATH = "src"
python -m social_analytics_pipeline.cli.youtube_local_pipeline
```

Controlled backfill example:

```powershell
$env:PYTHONPATH = "src"
$env:YOUTUBE_BACKFILL_START_AT = "2026-05-01T00:00:00Z"
$env:YOUTUBE_BACKFILL_END_AT = "2026-05-15T00:00:00Z"
python -m social_analytics_pipeline.cli.youtube_local_pipeline
```

Clear the backfill variables after the run if you want to return to normal lookback behavior.

For PostgreSQL loading, set these locally:

```text
YOUTUBE_LOCAL_LOAD_TARGET=postgres
SOCIAL_ANALYTICS_POSTGRES_DSN=<local-dsn>
```

The command may write to `data/raw/` and `data/processed/`; both are ignored by Git.

## YouTube v1 Runbook

Minimum local operator flow:

1. Copy `.env.example` to `.env` and fill only local values.
2. Set `YOUTUBE_API_KEY` and either `YOUTUBE_CHANNEL_ID` or `YOUTUBE_CHANNEL_HANDLE`.
3. Run `python -m social_analytics_pipeline.cli.youtube_local_pipeline`.
4. Confirm the terminal reports counts and `run_summary_path` without exposing secrets.
5. If `YOUTUBE_LOCAL_LOAD_TARGET=postgres`, confirm records were loaded into PostgreSQL.

Minimum Airflow operator flow:

1. Start `postgres` plus the required Airflow services.
2. Trigger `social_analytics_youtube_pipeline` deliberately.
3. Confirm the run finishes successfully.
4. Confirm logs and task results show counts and placeholders instead of secrets.

Current closure checkpoint for YouTube v1:

- Local YouTube execution works from `.env` only.
- Raw payload persistence, normalization and load all complete in one run.
- Invalid records are handled safely without exposing payloads.
- The run generates a compact summary artifact.
- The Airflow DAG remains manually triggerable without automatic catchup.

## Airflow

Initialize Airflow metadata:

```powershell
docker compose up airflow-init
```

Start Airflow:

```powershell
docker compose up -d airflow-api-server airflow-scheduler airflow-dag-processor airflow-worker airflow-triggerer
```

Useful Airflow commands:

```powershell
docker compose exec airflow-api-server airflow dags list
docker compose exec airflow-api-server airflow dags trigger social_analytics_mock_pipeline
docker compose exec airflow-api-server airflow dags trigger social_analytics_youtube_pipeline
docker compose exec airflow-api-server airflow dags unpause social_analytics_mock_pipeline
docker compose exec airflow-api-server airflow dags unpause social_analytics_youtube_pipeline
```

The Airflow UI runs at `http://localhost:<AIRFLOW_API_PORT>`.

## Review Helpers

```powershell
.\scripts\gemini_packet.ps1
.\scripts\gemini_review.ps1
.\scripts\chatgpt_review.ps1
```

Review packets must not repeat secrets or local-only values. Files under `docs/REVIEWS/*.md` are ignored by default; commit them only after manual sensitivity review.
