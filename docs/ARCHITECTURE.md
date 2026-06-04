# Architecture

## Pipeline Shape

```text
Provider -> Raw Storage -> Normalization -> Load/Validation -> Orchestration
```

## Main Components

- Providers collect raw payloads. Current providers include mock sources and a real YouTube Data API provider.
- Raw storage writes original payloads under `data/raw/` for audit and reprocessing.
- Normalizers convert provider-specific payloads into `SocialMetric`.
- Loaders write normalized metrics to JSON artifacts or PostgreSQL.
- Airflow DAGs orchestrate scheduled runs with 15-day intervals and catchup.

## Normalized Metric

Core fields:

```text
provider
account_id
content_id
content_type
collected_at
published_at
likes
comments
shares
views
followers
raw_path
```

PostgreSQL uses an idempotent natural key:

```text
provider + account_id + content_id + collected_at
```

## Current DAGs

- `social_analytics_mock_pipeline`: runs mock providers through raw storage, normalization and configurable JSON/PostgreSQL loading.
- `social_analytics_youtube_pipeline`: runs the real YouTube provider with settings from environment variables only.

Current scheduling behavior:

```text
social_analytics_mock_pipeline:
  schedule = 15 days
  catchup = True
  start_date = 2026-01-01 UTC

social_analytics_youtube_pipeline:
  schedule = 15 days
  catchup = False
  start_date = 2026-01-01 UTC
```

## Configuration Safety

- API keys, channel IDs, DSNs and passwords come from local environment variables or `.env`.
- `.env`, `data/raw/`, `data/processed/` and review logs are ignored by Git.
- Terminal output should show counts and placeholders, not raw payloads or sensitive values.

## Quality Gates

- Unit tests with fake clients for API behavior.
- Ruff for lint.
- Bandit for Python security lint.
- pip-audit for dependency audit.
- Gitleaks and GitHub Actions for secret scanning.
- CodeRabbit for PR review.

## Later Architecture Work

- Controlled backfill for the real YouTube path.
- Dead Letter Queue for invalid records.
- Runtime metrics and alerting.
- Async or Celery scaling only when real volume justifies it.
