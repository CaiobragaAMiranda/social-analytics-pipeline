# Social Analytics Pipeline

Data engineering pipeline for collecting, storing, normalizing, validating and orchestrating social media metrics.

The repository is the source of truth. Work is split into small, reviewable tasks so the project can continue without relying on long chat history.

## Current Status

- Phase: Consumption layer
- Current task: TASK-126 - PR review for platform top-content batch
- Last completed delivery: TASK-125 - Package three-task platform top-content batch

## Workflow

Before coding a task:

1. Review `docs/PLAN.md`, `docs/TASKS.md` and `docs/PROGRESS.md`.
2. Tell the user the proposed changes, scope, exclusions and validation plan.
3. Implement only after the user confirms or asks to continue.
4. Update documentation and progress.
5. Run local validation.
6. Batch up to three small tasks before committing and opening a PR.
7. Open a PR so GitHub Actions and CodeRabbit can review it.

Exceptions: commit and open a PR earlier when a task is large, risky, security-sensitive, blocks further work, or needs external review before continuing.

## YouTube v1 Closure

The current delivery goal is to close one usable real-provider slice before adding more engineering depth.

YouTube v1 is considered closed when all of the following are true:

1. The local YouTube command runs with local `.env` settings only.
2. The pipeline preserves raw payloads, normalizes metrics and loads them to JSON or PostgreSQL.
3. The local run exposes a compact execution summary without leaking secrets.
4. The Airflow YouTube DAG can be triggered deliberately and complete successfully.
5. The repository documents the minimum safe operator steps to run and verify the flow.

The repository now treats this YouTube v1 slice as closed. The next decision should favor product value, such as another real provider or a simple layer to consume the metrics already being collected.

The repository now includes that simple consumption layer in local CLI form: a YouTube report command that reads the latest processed artifact, prints compact aggregate metrics and writes markdown and JSON reports.

## Next Delivery

The next cycle is a local channel-first dashboard MVP before adding another real provider. The dashboard should read generated report JSON files, render a static HTML view and avoid new secrets, servers or cloud dependencies.

The user-facing dashboard selector should choose monitored channels/accounts, not platforms. YouTube, TikTok and Instagram should appear as data sources inside the selected channel, with consolidated totals and per-platform breakdowns. Dashboard labels should prefer human channel names, channel images, content titles, thumbnails, publish dates and links; technical IDs are secondary metadata or fallbacks.

After the channel contract is useful, the next provider cycle can start. ADR-0002 selects Instagram as the next real provider, limited to authorized Instagram professional accounts through official Meta APIs. TikTok remains deferred until a better official analytics path fits the monitored-channel use case.

The first dashboard slice exposes a `social-dashboard` command that reads report JSON files and writes a static HTML file. When no report path is provided, it uses the latest JSON report from the local YouTube report directory. Automation can pass `--project-root` to discover reports outside the current directory. The command also accepts repeated `--report-json` values or `--all-reports` to aggregate multiple local artifacts by channel identity. A local `--channels-config` JSON file can map platform handles or IDs to a monitored channel display name and image URL; use `config/channels.example.json` as the safe placeholder template and keep `config/channels.local.json` uncommitted. The current static dashboard is a single-page channel analytics view with a channel selector, channel avatar, responsive metric cards, per-record averages, engagement breakdown, readable generation time, report metadata with source artifact context, data quality status, platform source cards, a top-content table and explicit empty states. The dashboard contract accepts platform source metrics inside each monitored channel.

The Instagram provider is available through the explicit `instagram-local-pipeline` command. It requires local `INSTAGRAM_ACCESS_TOKEN` and `INSTAGRAM_USER_ID` values, writes ignored local artifacts, and prints only compact masked execution summaries. Processed Instagram artifacts can be converted into dashboard-compatible JSON with `instagram-report`.

The local `dashboard-smoke` command can generate safe sample YouTube and Instagram artifacts from fixtures and build a static multi-provider dashboard without API credentials. It also creates an ignored placeholder channel identity config so both providers render inside one monitored channel option.

When multiple provider reports are grouped into one monitored channel, top content is ranked globally across providers by the configured ranking metric, with `views` as the fallback.

Aggregated top-content rows also show their provider platform before the secondary technical content ID.

The Platform Sources panel shows how many expected sources are available for the selected channel, such as `2/3 available`.

Platform cards also show each provider's share of total views and engagements for the selected channel.

The dashboard highlights which platform leads the selected channel in views and engagements.

Platform cards also show the leading content title for each available provider.

They also show the publication date for each provider's leading content item when available.

Provider-specific top content is linked directly when the report includes a content URL.

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
