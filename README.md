# Social Analytics Pipeline

Data engineering pipeline for collecting, storing, normalizing, validating and orchestrating social media metrics.

The repository is the source of truth. Work is split into small, reviewable tasks so the project can continue without relying on long chat history.

## Current Status

- Phase: Consumption layer
- Current task: TASK-207 - PR review for Instagram runbook parity batch
- Last completed delivery: TASK-206 - Package Instagram runbook parity batch

## Workflow

Before coding a task:

1. Review `docs/PLAN.md`, `docs/TASKS.md` and `docs/PROGRESS.md`.
2. Tell the user the proposed changes, scope, exclusions and validation plan.
3. Implement only after the user confirms or asks to continue.
4. Update documentation and progress.
5. Run local validation.
6. Batch up to five small tasks before committing and opening a PR.
7. Open a PR so GitHub Actions and CodeRabbit can review it.

Exceptions: commit and open a PR earlier when a task is large, risky, security-sensitive, blocks further work, or needs external review before continuing.

The detailed PR review rules are documented in `docs/REVIEW_POLICY.md`.

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

ADR-0003 chooses Instagram provider depth as the next post-v1 delivery direction. The next step is to review the current Instagram provider, report and dashboard compatibility before adding more implementation.

The Instagram gap review is recorded in `docs/INSTAGRAM_PROVIDER_GAP_REVIEW.md`.

Instagram API requests now retry transient failures with local retry tuning while keeping credential failures fail-fast.

`instagram-report` now supports list-only artifact checks for safer local operation.

`instagram-report` also supports dry-run planning so operators can preview the selected artifact and planned JSON output without writing files.

`instagram-report` can write JSON reports to a chosen directory while preserving artifact-based file names.

The first dashboard slice exposes a `social-dashboard` command that reads report JSON files and writes a static HTML file. When no report path is provided, it uses the latest JSON report from the local YouTube report directory. Automation can pass `--project-root` to discover reports outside the current directory. The command also accepts repeated `--report-json` values or `--all-reports` to aggregate multiple local artifacts by channel identity. A local `--channels-config` JSON file can map platform handles or IDs to a monitored channel display name and image URL; use `config/channels.example.json` as the safe placeholder template and keep `config/channels.local.json` uncommitted. The current static dashboard is a single-page channel analytics view with a channel selector, channel hero, responsive visual metric cards, per-record averages, engagement breakdown, readable generation time, report metadata with source artifact context, data quality status, platform source cards, an activity-style production panel, a top-content card gallery, a supporting top-content table and explicit empty states. The dashboard contract accepts platform source metrics inside each monitored channel.

The Instagram provider is available through the explicit `instagram-local-pipeline` command. It requires local `INSTAGRAM_ACCESS_TOKEN` and `INSTAGRAM_USER_ID` values, writes ignored local artifacts, and prints only compact masked execution summaries. Processed Instagram artifacts can be converted into dashboard-compatible JSON with `instagram-report`.

The compact local Instagram operator flow is documented in `docs/INSTAGRAM_LOCAL_RUNBOOK.md`.

The local `dashboard-smoke` command can generate safe sample YouTube and Instagram artifacts from fixtures and build a static multi-provider dashboard without API credentials. It also creates an ignored placeholder channel identity config so both providers render inside one monitored channel option.

The local `serve-dashboard` command can generate that safe smoke dashboard and print a local URL for browser review.

When multiple provider reports are grouped into one monitored channel, top content is ranked globally across providers by the configured ranking metric, with `views` as the fallback.

Aggregated top-content rows also show their provider platform before the secondary technical content ID.

The Platform Sources panel shows how many expected sources are available for the selected channel, such as `2/3 available`.

Platform cards also show each provider's share of total views and engagements for the selected channel.

The dashboard highlights which platform leads the selected channel in views and engagements.

Platform cards also show the leading content title for each available provider.

They also show the publication date for each provider's leading content item when available.

Provider-specific top content is linked directly when the report includes a content URL.

Platform cards also render the top content thumbnail when the report includes an image.

Platform cards also show the view count for each provider's leading content item.

Platform cards also show the content type for each provider's leading content item when available.

The top-content table now shows visual rank labels for easier scanning.

The top-ranked content row is highlighted in the dashboard table.

The Top Content section now shows how many ranked items are displayed.

The next visual dashboard cycle focuses on platform comparison charts for views, engagements and production volume inside the selected channel.

The dashboard now includes platform comparison charts for views, engagements and production counts.

The selected channel now has a visual preview with avatar, human channel name and source coverage next to the channel selector.

Top-content rows no longer show technical content IDs when a human title is already available.

The dashboard now includes visual channel option cards with avatar, human name and source summary while keeping the native selector available.

Report metadata now shows a safe report filename instead of exposing full artifact paths in the dashboard UI.

Data Quality labels now use user-facing analytics wording.

Report context labels now use user-facing wording instead of technical metadata labels.

Data Quality values now show readable status text such as `Ready`, `Available`, `Unknown` and `Missing`.

The next dashboard polish slice adds a short channel insights panel using existing metrics.

The dashboard now shows a Channel Insights panel with top content, views leader, engagement leader and publishing activity.

Channel Insights now uses readable empty states when top content or platform leaders are unavailable.

Channel Insights cards now have stronger visual hierarchy with compact markers and per-insight accents.

Channel Insights visual markers are now decorative for assistive text while keeping readable labels.

The next dashboard polish slice summarizes publishing cadence using existing production activity data.

The Production Calendar now includes compact cadence cards for total productions, active days and average productions per active day.

Publishing cadence cards now show `No dates` when publication dates are unavailable.

Publishing cadence cards now have compact markers and per-card visual accents.

Publishing cadence visual markers are decorative for assistive text while keeping readable labels.

A dashboard v1 gap review found that the remaining closure work is product-focused: demonstrate multiple monitored channels, stop relying on broken external placeholder images, simplify secondary diagnostics, render publication dates in a user-facing format and document the final v1 acceptance checklist.

The dashboard smoke now demonstrates three monitored channels with YouTube, Instagram and TikTok kept as internal source coverage, not as user-facing channel selector options.

The dashboard now treats placeholder image URLs as unavailable media and renders channel/content fallbacks instead of broken external images.

The dashboard now keeps secondary diagnostics and the detailed ranking table in collapsed supporting panels so the primary reading path stays focused on channel performance.

The dashboard now renders publication dates as readable labels, shows provider names as YouTube, TikTok and Instagram, and uses compact no-data messaging for missing platform sources.

Dashboard v1 closure is defined by the concise checklist in `docs/DASHBOARD_V1_ACCEPTANCE.md`.

The latest dashboard QA pass confirms desktop and narrow viewport rendering, channel switching, readable dates, safe visible text and no horizontal overflow.

## Useful Commands

```powershell
.\scripts\project_status.ps1
.\scripts\verify_docs.ps1
$env:PYTHONPATH = "src"; python -m unittest discover -s tests
ruff check .
bandit -c pyproject.toml -r src
serve-dashboard
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
