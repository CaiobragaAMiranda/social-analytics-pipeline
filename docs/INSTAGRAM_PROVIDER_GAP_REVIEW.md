# Instagram Provider Gap Review

## Purpose

This review defines the smallest useful post-v1 Instagram provider depth slice.

## Current Strengths

- `instagram-local-pipeline` exists and fails closed when local credentials are missing.
- `InstagramGraphApiProvider` uses an injectable HTTP client, which keeps tests safe and avoids real API calls in automation.
- Account metadata and media payloads are collected through the official Graph API shape used by the provider.
- Pagination is supported through `INSTAGRAM_MAX_PAGES`.
- Raw, processed and run-summary artifacts are written under ignored local data directories.
- Console output masks the configured account and does not print tokens or raw payloads.
- Instagram normalization preserves caption, permalink, media image, username and profile image metadata.
- `instagram-report` writes dashboard-compatible JSON.
- `social-dashboard --all-reports` can discover Instagram report JSON artifacts.
- `dashboard-smoke` proves safe sample YouTube and Instagram reports can feed the same channel-first dashboard.

## Current Gaps

- The Instagram HTTP client does not yet have retry/backoff behavior for transient statuses such as rate limits or server errors.
- The Instagram local pipeline is JSON-only; PostgreSQL and Airflow paths are intentionally deferred.
- `instagram-report` has fewer operator conveniences than `youtube-report`, such as list/count/latest artifact modes and dry-run planning.
- Bootstrap guidance mentions Instagram report generation but does not yet provide a compact end-to-end local Instagram operator flow.
- The project has not recorded a real local Instagram run result with authorized professional account credentials.

## Next Slice

The next implementation slice should add Instagram provider resilience before expanding storage or orchestration.

Included:

- Add retry/backoff behavior for transient Instagram HTTP failures.
- Keep credential failures fail-fast for unauthorized or forbidden responses.
- Keep error messages sanitized so tokens, raw URLs and local paths are not printed.
- Add tests for transient retry, fail-fast credential errors and sanitized messages.

Deferred:

- Real TikTok integration.
- Instagram PostgreSQL loading.
- Instagram Airflow DAGs.
- Cloud deployment.
- Large-scale async fetching.
- Dashboard redesign unrelated to provider compatibility.

## Validation Baseline

Focused Instagram and dashboard-smoke tests passed locally before this review was recorded.
