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

Simple local report from the latest processed artifact:

```powershell
$env:PYTHONPATH = "src"
python -m social_analytics_pipeline.cli.youtube_report
```

After installing the package locally, the same command is available as `youtube-report`.

The report command prints aggregate metrics and writes a markdown file under
`data/reports/youtube/`.

To report a specific processed artifact or choose a custom output path:

```powershell
$env:PYTHONPATH = "src"
python -m social_analytics_pipeline.cli.youtube_report --artifact data/processed/youtube/<artifact>.json --output data/reports/youtube/<report>.md
```

Use `--top <n>` to control how many rows are included in the top-content ranking.
Use `--sort-by views|likes|comments|shares` to choose the ranking metric.
Use `--output-dir <path>` to choose the markdown report directory while keeping the artifact-based file name.
Use `--json-output <path>` to also save a compact JSON summary for automation.
Use `--json-output-dir <path>` to choose the JSON report directory while keeping the artifact-based file name.
Use `--json-indent <n>` to control JSON indentation; use `0` for compact output.
Use `--print-json` to print the JSON summary payload to stdout.
Use `--no-markdown --json-output <path>` to write only the JSON summary.
Use `--no-markdown --print-json --quiet` to print only the JSON summary without writing report files.
Use `--quiet` to suppress report-generation summary output.
Use `--fail-if-empty` when automation should fail if the selected artifact has no records.
Use `--min-records <n>` when automation should require at least `n` records.
Use `--dry-run` to validate inputs and show planned report outputs without writing files.
Use `--list-artifacts` to list processed YouTube artifacts without writing reports.
Use `--latest-artifact` to print only the latest processed YouTube artifact.
Use `--count-artifacts` to print only the number of processed YouTube artifacts.
Use `--fail-if-missing` with list-only modes when automation should fail if no artifact exists.
Use only one list-only mode at a time: `--list-artifacts`, `--latest-artifact` or `--count-artifacts`.

Instagram dashboard JSON report:

See `docs/INSTAGRAM_LOCAL_RUNBOOK.md` for the compact end-to-end local Instagram operator flow.
Use `instagram-local-pipeline --dry-run` to preview the local collection interval and artifact paths without credentials or API calls.
Use `--start-at`, `--end-at` and `--lookback-days` with `instagram-local-pipeline` when you need a one-off local interval without editing `.env`.
Use `--fail-if-empty` with `instagram-local-pipeline` when automation should fail a real local run that loads zero records.

```powershell
$env:PYTHONPATH = "src"
python -m social_analytics_pipeline.cli.instagram_report
```

Use `--artifact data/processed/instagram/<artifact>.json` to report a specific processed Instagram artifact.
Use `--json-output data/reports/instagram-json/<report>.json` to choose the report path.
Use `--json-output-dir data/reports/instagram-json` to choose the report directory while keeping the artifact-based file name.
Use `--top <n>`, `--sort-by views|likes|comments|shares`, `--print-json`, `--quiet` and `--fail-if-empty` the same way as the YouTube report flow.
Use `--dry-run` to validate the selected artifact and show the planned JSON output path without writing files.
Use `--list-artifacts`, `--latest-artifact`, `--count-artifacts` and `--fail-if-missing` for list-only Instagram artifact checks.
Use `INSTAGRAM_HTTP_MAX_ATTEMPTS` and `INSTAGRAM_HTTP_BACKOFF_SECONDS` locally to tune transient API retry behavior.

Safe multi-provider dashboard smoke:

```powershell
$env:PYTHONPATH = "src"
python -m social_analytics_pipeline.cli.dashboard_smoke
```

This command uses committed fixture payloads only. It writes ignored smoke artifacts and a placeholder channel identity config under `data/temp/dashboard-smoke/`, then writes the static HTML output under `data/dashboard/`.

Serve the safe dashboard locally:

```powershell
$env:PYTHONPATH = "src"
python -m social_analytics_pipeline.cli.serve_dashboard
```

Open the local dashboard URL printed by the command while it is running.
Use `--no-smoke` to serve an existing `data/dashboard/smoke.html` without regenerating safe sample artifacts.

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
