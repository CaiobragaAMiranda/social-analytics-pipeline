# Instagram Local Runbook

This runbook describes the safe local Instagram operator flow.

## Scope

Included:

- Local Instagram Graph API collection for an authorized professional account.
- Local JSON artifact loading.
- Instagram report JSON generation.
- Dashboard review from local report artifacts.

Deferred:

- TikTok integration.
- Instagram PostgreSQL loading.
- Instagram Airflow DAGs.
- Cloud deployment.
- Broad dashboard redesign.

## Local Settings

Copy the example environment file to a local `.env` file and fill only local values.

Required settings:

```text
INSTAGRAM_ACCESS_TOKEN=<local-instagram-access-token>
INSTAGRAM_USER_ID=<local-instagram-user-id>
```

Optional settings:

```text
INSTAGRAM_MAX_PAGES=1
INSTAGRAM_HTTP_MAX_ATTEMPTS=3
INSTAGRAM_HTTP_BACKOFF_SECONDS=1
INSTAGRAM_SMOKE_LOOKBACK_DAYS=30
INSTAGRAM_BACKFILL_START_AT=
INSTAGRAM_BACKFILL_END_AT=
INSTAGRAM_LOCAL_LOAD_TARGET=json
```

Do not commit `.env`, raw payloads, processed artifacts, run summaries or real account identifiers.

## Run Local Collection

Preview the local execution plan without credentials or API calls:

```powershell
$env:PYTHONPATH = "src"
python -m social_analytics_pipeline.cli.instagram_local_pipeline --dry-run
```

Preview a specific interval without editing `.env`:

```powershell
$env:PYTHONPATH = "src"
python -m social_analytics_pipeline.cli.instagram_local_pipeline --dry-run --start-at 2026-05-01T00:00:00Z --end-at 2026-05-31T00:00:00Z
```

Preview a lookback window without editing `.env`:

```powershell
$env:PYTHONPATH = "src"
python -m social_analytics_pipeline.cli.instagram_local_pipeline --dry-run --lookback-days 7
```

Success looks like:

- The command prints `Instagram local pipeline dry run`.
- The command shows whether local credentials are configured without printing them.
- Planned raw, processed and run-summary paths are project-relative.
- No API request is made and no artifact is written.

Run the local collection:

```powershell
$env:PYTHONPATH = "src"
python -m social_analytics_pipeline.cli.instagram_local_pipeline
```

Use `--fail-if-empty` when automation should fail a real local run that loads zero records.

Success looks like:

- The command prints `Instagram local pipeline summary`.
- `provider=instagram` is shown.
- `account_id=<configured>` is shown instead of the real account value.
- Raw, processed and run-summary paths are printed as project-relative artifact paths.
- Counts are printed for raw, valid, invalid and loaded records.

## Inspect Run Summaries

List local run-summary paths:

```powershell
$env:PYTHONPATH = "src"
python -m social_analytics_pipeline.cli.instagram_local_pipeline --list-run-summaries
```

Count local run summaries:

```powershell
$env:PYTHONPATH = "src"
python -m social_analytics_pipeline.cli.instagram_local_pipeline --count-run-summaries
```

Validate a selected run summary before relying on it:

```powershell
$env:PYTHONPATH = "src"
python -m social_analytics_pipeline.cli.instagram_local_pipeline --validate-run-summary data/runs/instagram/<run-summary-file>.json
```

Validate all local run summaries before relying on them:

```powershell
$env:PYTHONPATH = "src"
python -m social_analytics_pipeline.cli.instagram_local_pipeline --validate-run-summaries
```

Validate the latest run summary before relying on it:

```powershell
$env:PYTHONPATH = "src"
python -m social_analytics_pipeline.cli.instagram_local_pipeline --validate-latest-run-summary
```

Print compact status and counts from a selected run summary:

```powershell
$env:PYTHONPATH = "src"
python -m social_analytics_pipeline.cli.instagram_local_pipeline --show-run-summary data/runs/instagram/<run-summary-file>.json
```

Print the latest run-summary path:

```powershell
$env:PYTHONPATH = "src"
python -m social_analytics_pipeline.cli.instagram_local_pipeline --latest-run-summary
```

Print compact status and counts from the latest run summary:

```powershell
$env:PYTHONPATH = "src"
python -m social_analytics_pipeline.cli.instagram_local_pipeline --show-latest-run-summary
```

Use `--fail-if-missing` when automation should fail if no local run summary exists.

Success looks like:

- The command does not require credentials.
- The command does not call the Instagram API.
- Paths are project-relative.
- Validation status and counts come from the ignored local run-summary artifact.

Failure handling:

- Missing credentials fail before any API call.
- Unauthorized or forbidden responses fail fast with a credential/permission message.
- Transient API failures retry according to local retry settings.
- Error messages must not print tokens, raw request URLs or raw payloads.

## Check Artifacts

List processed artifacts:

```powershell
$env:PYTHONPATH = "src"
python -m social_analytics_pipeline.cli.instagram_report --list-artifacts --fail-if-missing
```

Print the latest processed artifact:

```powershell
$env:PYTHONPATH = "src"
python -m social_analytics_pipeline.cli.instagram_report --latest-artifact
```

Count processed artifacts:

```powershell
$env:PYTHONPATH = "src"
python -m social_analytics_pipeline.cli.instagram_report --count-artifacts --fail-if-missing
```

## Preview Report Generation

```powershell
$env:PYTHONPATH = "src"
python -m social_analytics_pipeline.cli.instagram_report --dry-run
```

Success looks like:

- The command prints `Instagram report dry run`.
- The selected artifact path is project-relative.
- Record count and sorting are visible.
- Planned JSON output path is visible.
- No report file is written.

## Generate Report JSON

```powershell
$env:PYTHONPATH = "src"
python -m social_analytics_pipeline.cli.instagram_report --fail-if-empty
```

Success looks like:

- The command prints `Instagram report summary`.
- Record, view and engagement counts are visible.
- The top content identifier may be shown, but real raw payloads are not printed.
- The report JSON is written under the ignored local report artifact directory.

## Review In Dashboard

```powershell
$env:PYTHONPATH = "src"
python -m social_analytics_pipeline.cli.dashboard --all-reports
```

Open the generated dashboard artifact locally or use the dashboard serving command when you want a temporary browser URL.

Success looks like:

- Instagram appears as a source inside the selected monitored channel.
- Channel names, content titles, thumbnails or fallback media, readable dates and links are preferred over technical identifiers.
- Missing sources show compact no-data messaging.
- No local paths, token labels, raw payloads, API keys or real account identifiers appear in the primary dashboard flow.
