# Progress

## Current Snapshot

Date: 2026-06-17

Current phase: Consumption layer

Current task: TASK-196 - Post-v1 delivery decision.

Overall status: the current YouTube v1 slice is closed, local reports are versioned, and the dashboard MVP can render explicit or discovered report JSON artifacts as a single-page channel analytics view. The dashboard contract now accepts platform source metrics inside a monitored channel, renders per-platform source cards inside the selected channel, can aggregate multiple local report JSON artifacts by channel identity and can apply a local channel identity configuration. Dashboard content display now prioritizes human-readable metadata such as titles, thumbnails, links and publish dates while keeping technical IDs secondary. Instagram now has a local report JSON command compatible with the dashboard contract. A safe multi-provider dashboard smoke command now proves YouTube and Instagram report artifacts can feed the same monitored channel dashboard option. Aggregated channel top content is now ranked globally across provider reports and shows platform metadata per row. Platform Sources now shows provider coverage, each platform's share of channel views and engagements, leading sources for views and engagements, provider-specific top content, top-content dates, top-content links, top-content thumbnails, top-content views and top-content type labels. The top-content table now shows rank badges, highlights the leading row and displays a ranked-item count for easier scanning. The dashboard can now be served locally through a dedicated command. The visual dashboard batch now adds a polished dark shell, stronger channel hero, graphic metric cards, a clearer production activity panel and a top-content card gallery.

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
- Local Airflow validation completed for the real YouTube DAG.
- YouTube provider resilience now includes retry/backoff and clearer credential failure handling.
- Invalid normalized metrics are now blocked before artifact or PostgreSQL loading.
- The next delivery direction is now explicit: controlled YouTube backfill before any new real provider expansion.
- Controlled YouTube backfill now supports explicit start/end timestamps for local and fallback DAG runs.
- Invalid normalized records now go to a local DLQ with a reason and raw file reference instead of stopping the full pipeline.

## Latest Notes

- Windows reserved the previous local metrics PostgreSQL port; the local `.env` now uses a non-reserved port.
- Airflow 3.2.1 initialization now runs metadata migration without the incompatible user creation command.
- Celery workers now use the Airflow execution API URL and a shared JWT secret from local environment configuration.
- Automatic catchup is disabled for the real YouTube DAG to avoid unexpected YouTube API quota usage. Mock DAG catchup remains available for historical orchestration testing.
- The successful YouTube Airflow run loaded 50 records and masked the configured channel in logs.
- The YouTube HTTP client now retries transient statuses like `429` and `503`, but stops immediately on invalid credentials like `401` and `403`.
- Validation now rejects empty identifiers, negative counters, and `published_at` values later than `collected_at`.
- New provider breadth was intentionally deferred because only YouTube currently has a real end-to-end path.
- Automatic YouTube DAG catchup is still disabled; historical recovery now happens only through explicit backfill settings.
- Pipeline summaries now expose invalid record counts for local and Airflow-backed YouTube runs.
- Real YouTube executions now persist a structured run summary with interval, status, counts and artifact locations.
- The delivery strategy was simplified: keep governance, but prioritize cycle closure over new engineering layers.
- The repository now documents what must be true to consider the current YouTube v1 delivery closed.
- The repository now treats the YouTube v1 cycle as closed and shifts attention to the next functional slice.
- The repository now includes a small local reporting step for processed YouTube artifacts.
- The local YouTube reporting step now also writes a markdown report with ranked content.
- The report CLI now accepts explicit processed artifact and markdown output paths.
- The report CLI now accepts `--top` to control the top-content ranking size.
- The report CLI now accepts `--sort-by` to choose the ranking metric.
- The report CLI now accepts `--json-output` to save a compact structured summary.
- The report CLI now accepts `--list-artifacts` to show available processed artifacts.
- The report CLI now accepts `--latest-artifact` to print only the latest processed artifact.
- The report CLI now accepts `--fail-if-missing` so list-only automation can fail when no processed artifact exists.
- The report CLI now rejects using `--list-artifacts` and `--latest-artifact` together.
- The report CLI now accepts `--count-artifacts` to print only the processed artifact count.
- The report CLI now accepts `--no-markdown` with `--json-output` for JSON-only report generation.
- The report CLI now accepts `--quiet` to suppress report-generation summary output.
- The report CLI now accepts `--output-dir` to choose the markdown report directory while preserving artifact-based file names.
- The report CLI now accepts `--json-output-dir` to choose the JSON report directory while preserving artifact-based file names.
- The report CLI now accepts `--json-indent` to choose pretty or compact JSON output.
- The report CLI now accepts `--print-json` to print the JSON summary payload to stdout.
- The report CLI now accepts `--fail-if-empty` to fail before report writing when the selected artifact has no records.
- The report CLI now accepts `--min-records` to fail before report writing when the selected artifact is too small.
- The report CLI now accepts `--dry-run` to validate selected inputs and show planned report paths without writing files.
- The report CLI now accepts `--no-markdown --print-json` to emit JSON without writing report files.
- The package now exposes a `youtube-report` console script for the local report command.
- YouTube reports now expose the selected top-ranking metric value alongside top views.
- YouTube reports now expose total engagements as likes plus comments plus shares.
- YouTube reports now expose engagement rate as total engagements divided by total views.
- YouTube report JSON now exposes engagement rate as a numeric percentage.
- YouTube reports now expose average views per processed record.
- YouTube reports now expose average engagements per processed record.
- YouTube reports now expose average likes, comments and shares per processed record.
- YouTube report JSON now exposes engagement breakdown percentages for likes, comments and shares.
- YouTube report JSON now includes `report_schema_version`.
- YouTube report JSON now includes a UTC `generated_at` timestamp.
- YouTube report JSON now includes provider and source artifact metadata.
- YouTube report JSON now includes ranking metric and limit metadata.
- YouTube report JSON now includes simple data quality metadata.
- YouTube report JSON data quality now indicates whether top content exists.
- YouTube report JSON data quality now exposes a compact status.
- YouTube report JSON data quality now marks current summaries as non-partial.
- YouTube report JSON data quality now indicates whether engagement metrics exist.
- YouTube markdown reports now include a compact data quality status.
- YouTube markdown reports now indicate whether engagement metrics exist.
- YouTube markdown reports now include the displayed top rows count.
- YouTube markdown reports now include the report schema version.
- The next delivery direction is now dashboard MVP first, then second real provider.
- The dashboard MVP now has a local static HTML generator command.
- The dashboard CLI now defaults to the latest local YouTube report JSON.
- The dashboard CLI now accepts a project root for latest-report discovery.
- The dashboard now renders channel images when report source metadata provides an image URL.
- The dashboard now uses a cleaner responsive layout for metrics, data quality and top content.
- The dashboard now renders clear empty states when top content rows are missing.
- The dashboard now shows report schema and ranking metadata from report JSON.
- The dashboard now shows likes, comments and shares as engagement breakdown percentages.
- The dashboard now shows per-record averages from report JSON totals.
- The dashboard now shows the source artifact used to produce the report view.
- The dashboard now formats valid generated timestamps for easier reading.
- The dashboard now uses a single-page channel selector layout inspired by the provided reference.
- The roadmap now prioritizes consolidated channel analytics over platform-first selection.
- The dashboard channel contract now accepts platform source metrics and consolidates platform totals.
- The dashboard now shows per-platform source cards for YouTube, TikTok and Instagram.
- The dashboard can now aggregate multiple report JSON artifacts into channel options with platform source breakdowns.
- The dashboard can now apply a local channel identity config for monitored channel names and images.
- The second real provider decision now selects Instagram and defers TikTok.
- The Instagram provider skeleton now supports authorized account/media collection with fake-HTTP test coverage.
- The Instagram provider can now run through `instagram-local-pipeline` and write ignored local raw, processed and run-summary artifacts.
- The metric schema and local artifact loader now preserve optional channel and content display metadata.
- The real YouTube provider now fetches channel snippet/statistics metadata for human channel names, images and follower counts.
- YouTube report JSON now preserves optional human channel and content metadata for dashboard consumers.
- The dashboard top-content view now prioritizes title, thumbnail/fallback, link and publish date before technical IDs.
- Instagram report JSON now exposes dashboard-compatible totals, ranking, data quality, production dates and top content.
- Instagram normalization now preserves caption, permalink, media image, username and profile image metadata when available.
- The dashboard report discovery now includes Instagram JSON report artifacts.
- `dashboard-smoke` now generates safe sample YouTube and Instagram artifacts from fixtures in an isolated ignored smoke workspace and builds a local static dashboard through all-report discovery.
- The current dashboard/provider batch passed local validation and is ready for PR #33 review follow-up.
- PR #33 was squash-merged after GitHub Actions, secret scan and CodeRabbit passed.
- `dashboard-smoke` now creates an ignored placeholder channel config so sample YouTube and Instagram reports render inside one monitored channel option.
- Aggregated channel dashboards now sort combined top-content rows by ranking metric instead of provider file order.
- Aggregated top-content rows now show their provider platform before the secondary content ID.
- The current three-task dashboard batch passed local validation and is ready for PR review.
- PR #34 was squash-merged after GitHub Actions, secret scan and CodeRabbit passed.
- Platform Sources now shows a coverage pill such as `2/3 available`.
- Platform cards now show each provider's share of total views and engagements.
- The dashboard now shows which platform leads in views and engagements for the selected channel.
- The current platform source batch passed local validation and is ready for PR review.
- PR #35 was squash-merged after GitHub Actions, secret scan and CodeRabbit passed.
- Platform cards now show the leading content title for each available provider.
- Platform cards now show the leading content publication date when available.
- Platform cards now link provider-specific top content when a content URL is available.
- The current platform top-content batch passed local validation and is ready for PR review.
- PR #36 was squash-merged after GitHub Actions, secret scan and CodeRabbit passed.
- Platform cards now render provider-specific top-content thumbnails when available.
- Platform cards now show provider-specific top-content view counts when available.
- Platform cards now show provider-specific top-content type labels when available.
- The current visual platform content batch passed local validation and is ready for PR review.
- PR #37 was squash-merged after GitHub Actions, secret scan and CodeRabbit passed.
- The next dashboard slice was selected as top-content table readability.
- Top-content rows now show visual rank labels.
- The leading top-content row now renders with a distinct winner highlight.
- The Top Content section now shows how many ranked items are displayed.
- PR #38 was squash-merged after GitHub Actions, secret scan and CodeRabbit passed.
- `serve-dashboard` now generates the safe dashboard smoke artifact and serves it through a localhost URL.
- Local dashboard serving is now documented in README and bootstrap notes.
- Local dashboard serving now reports a clear host and port message when binding fails.
- PR #39 was squash-merged after GitHub Actions, secret scan and CodeRabbit passed.
- The task batch rule is now five small tasks before commit and PR.
- The next visual batch targets shell refresh, channel hero, metric cards, production heatmap and top-content cards.
- The dashboard shell now has a stronger dark analytics panel treatment.
- The channel identity now appears as a first-viewport hero.
- Main metrics now render as stronger visual cards with compact spark accents.
- The production activity panel now has a more contribution-chart-like treatment.
- Top content now appears as a visual card gallery before the supporting table.
- The current visual dashboard batch passed local validation and browser QA.
- PR #40 was squash-merged after GitHub Actions, secret scan and CodeRabbit passed.
- The next visual dashboard cycle targets platform comparison charts for views, engagements and production counts.
- Platform comparison charts now show views, engagements and production counts in provider order.
- The current platform comparison chart batch passed full local validation, sensitive-pattern scan, dashboard smoke regeneration and browser QA.
- PR #41 was squash-merged after GitHub Actions, secret scan and CodeRabbit passed.
- The next dashboard polish batch targets clearer selected-channel identity and fewer visible technical IDs.
- The selected channel now has a visual preview with avatar, human channel name and source coverage beside the channel selector.
- Top-content rows no longer show technical content IDs when a human title is already available.
- Visual channel option cards now let users choose monitored channels by avatar, human name and source summary while preserving the native select.
- The current channel identity polish batch passed full validation, sensitive-pattern scan, dashboard smoke regeneration and browser QA.
- PR #42 was squash-merged after GitHub Actions, secret scan and CodeRabbit passed.
- The next dashboard polish slice targets human-readable metadata and data-quality labels.
- Report metadata now shows a safe report filename instead of full artifact paths.
- Data Quality labels now use user-facing analytics wording.
- Report context labels now use user-facing wording instead of technical metadata labels.
- Data Quality values now show readable status text such as `Ready`, `Available`, `Unknown` and `Missing`.
- The current metadata readability polish batch passed full validation, sensitive-pattern scan, dashboard smoke regeneration and browser QA.
- PR #43 was squash-merged after GitHub Actions, secret scan and CodeRabbit passed.
- The next dashboard polish slice targets a short channel insights panel using existing metrics.
- The dashboard now shows a Channel Insights panel with top content, views leader, engagement leader and publishing activity.
- Channel Insights now uses readable empty states when top content or platform leaders are unavailable.
- Channel Insights cards now have stronger visual hierarchy with compact markers and per-insight accents.
- Channel Insights visual markers are now decorative for assistive text while keeping readable labels.
- The current Channel Insights polish batch passed full validation, sensitive-pattern scan, dashboard smoke regeneration and browser QA.
- PR #44 was squash-merged after GitHub Actions, secret scan and CodeRabbit passed.
- The next dashboard polish slice targets publishing cadence summaries using existing production activity data.
- The Production Calendar now includes compact cadence cards for total productions, active days and average productions per active day.
- Publishing cadence cards now show `No dates` when publication dates are unavailable.
- Publishing cadence cards now have compact markers and per-card visual accents.
- Publishing cadence visual markers are decorative for assistive text while keeping readable labels.
- The current publishing cadence polish batch passed full validation, sensitive-pattern scan, dashboard smoke regeneration and browser QA.
- PR #45 was squash-merged after GitHub Actions, secret scan and CodeRabbit passed.
- Dashboard v1 gap review inspected the local smoke dashboard as a product surface: it has the channel-first structure, metrics, platform sources, production calendar and top-content names, but it still needs multiple monitored sample channels, offline-safe imagery, simpler primary flow, readable dates and a final acceptance checklist before the dashboard v1 cycle is closed.
- `dashboard-smoke` now renders three monitored channel options from safe fixture variants: Growth Lab, Creator Studio and Launch Room.
- The smoke workspace is cleared before regeneration so stale local report artifacts cannot create extra dashboard channels.
- Dashboard image rendering now falls back for placeholder image URLs instead of loading broken external images.
- Browser QA confirmed the local smoke dashboard has no broken images, no placeholder image loads, no console errors and no horizontal overflow.
- The dashboard now keeps Report Context, Data Quality and the detailed top-content table inside collapsed supporting panels.
- Browser QA confirmed the simplified flow keeps channel switching, top-content counters and detailed rows synchronized.
- The dashboard now renders top-content dates as readable labels, shows provider labels as YouTube, TikTok and Instagram, and uses compact no-data messaging for missing platform sources.
- Browser QA confirmed readable dates, no raw ISO timestamps in visible text, no visible `unavailable` text, no console errors and no horizontal overflow.
- Dashboard v1 closure is now defined by a concise acceptance checklist covering smoke generation, local serving, channel-first selection, channel identity, production cadence, core metrics, safe output and explicit v1 exclusions.
- README and bootstrap docs now avoid publishing a fixed local IP and port for dashboard review instructions.
- CodeRabbit review policy is now explicit: automatic review is disabled, manual review uses `@coderabbitai review`, and GitHub Actions plus secret scan remain required PR checks.
- The work plan now matches the current five-task batch rule.
- Final dashboard browser QA passed on desktop and narrow viewport.
- Desktop QA confirmed three monitored channel options, readable dates, no visible raw ISO timestamps, no sensitive visible text, no console errors and no horizontal overflow.
- Narrow viewport QA confirmed channel switching updates primary dashboard sections and no page or element overflow remains after compacting the production heatmap.
- The dashboard v1 closure batch is prepared for PR packaging with review policy documentation, final browser QA evidence and responsive dashboard fixes.
- PR #47 passed GitHub Actions quality/security, secret scan and CodeRabbit, then was squash-merged into `master`.
- The dashboard v1 closure path is now complete in repository history.

## Current Constraints

- `.env`, raw data and processed data must remain local and ignored by Git.
- Do not commit real API keys, channel IDs, payloads, local paths, ports, IPs or expanded DSNs.
- Gemini CLI review may be unavailable when local auth is invalid; GitHub Actions and CodeRabbit remain required on PRs.
- Instagram real-provider work must use official Meta APIs and authorized professional accounts only.

## Next Actions

- Choose the post-v1 delivery path before implementing more work.
- Compare second real provider depth, dashboard product polish and operational quality before starting the next slice.
- Keep TikTok mocked until an official analytics path fits this project.
