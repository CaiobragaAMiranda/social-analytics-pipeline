# Tasks

## Status Legend

- Pending: not started.
- In Progress: currently being worked on.
- Review: waiting for reviewer or user decision.
- Done: completed and documented.

## Delivery Focus

- Keep the YouTube v1 cycle closed and move into a channel-first dashboard slice.
- Keep the governance pattern, but prefer larger functional tasks over tiny infrastructure refinements.
- The user-facing selector must be a monitored channel/account, not a platform selector.
- YouTube, TikTok and Instagram are data sources inside a selected channel.
- Defer real TikTok and Instagram API work until the consolidated channel contract is useful.
- Defer extra observability, stronger alerting and broader orchestration work unless they directly unlock the channel dashboard or provider slice.

## Current Task

### TASK-203 - Instagram provider next slice decision

Status: Pending

Phase: Governance

Goal: choose the next small Instagram provider-depth task after retry and report operator parity.

Acceptance criteria:

- The next Instagram slice is chosen before implementation.
- The decision considers report parity, local runbook clarity and real-run readiness.
- TikTok, PostgreSQL loading, Airflow DAGs and broad dashboard redesign remain explicitly deferred unless selected.
- Public documentation avoids secrets, local paths, raw payloads, ports, IPs and expanded DSNs.

### TASK-100 - Dashboard platform breakdown inside selected channel

Status: Done

Phase: Consumption layer

Goal: show platform-specific metrics inside the selected channel view.

Acceptance criteria:

- Dashboard still selects by channel, not by platform.
- The selected channel shows consolidated top cards.
- The selected channel shows platform cards for YouTube, TikTok and Instagram when present.
- Missing platform data renders as unavailable instead of zeroing silently.
- Tests cover mixed platform availability.

Evidence:

- Dashboard now renders a `Platform Sources` section inside the selected channel view.
- Platform cards show productions, views, engagements and performance.
- Missing platform sources render as `unavailable`.
- Tests cover complete and partial platform availability.

### TASK-099 - Cross-platform channel dashboard contract

Status: Done

Phase: Consumption layer

Goal: define and support the report JSON shape for one monitored channel with multiple platform sources.

Acceptance criteria:

- A channel object has a stable display identity.
- A channel object can include a `platforms` list for YouTube, TikTok and Instagram source metrics.
- Platform source metrics include provider, records, views, engagements and engagement rate.
- Dashboard channel totals can be consolidated from platform sources.
- Existing single-report behavior remains supported.
- Tests cover the contract with YouTube, TikTok and Instagram platform sources.

Evidence:

- Dashboard channel modeling now accepts a `platforms` list.
- Platform totals are consolidated into selected-channel cards.
- Tests cover a channel with YouTube, TikTok and Instagram platform metrics.

### TASK-098 - Channel-oriented roadmap refactor

Status: Done

Phase: Consumption layer

Goal: realign the backlog so the dashboard is organized around monitored channels rather than individual platforms.

Acceptance criteria:

- Documentation states that the dashboard selector is channel/account-first.
- Documentation states that platforms are sources inside a selected channel.
- Near-term tasks prioritize the consolidated channel contract before new real providers.
- TikTok and Instagram real integrations remain deferred until official access and the dashboard contract are ready.
- Public documentation avoids secrets, local paths, raw payloads and expanded DSNs.

Evidence:

- Delivery focus now states the channel-first dashboard direction.
- Next tasks now define a cross-platform channel contract before provider expansion.
- README, plan and progress docs now describe the consolidated channel objective.

### TASK-097 - Channel selector dashboard redesign

Status: Done

Phase: Consumption layer

Goal: redesign the static dashboard as a single-page channel analytics view with channel selection.

Acceptance criteria:

- Dashboard uses a darker single-page layout with a teal sidebar and compact cards.
- Dashboard renders a channel selector.
- Dashboard shows the selected channel name, provider and image/fallback avatar.
- Dashboard shows productions, total views, total engagements and semiannual performance.
- Dashboard can render multiple channel options when the payload contains a `channels` list.
- Existing values remain safely escaped or serialized.
- Tests cover the redesigned layout and multiple channel options.

Evidence:

- Dashboard HTML now renders a sidebar, channel selector and channel-focused card layout.
- Channel data is embedded as safe JSON and updated client-side when a channel is selected.
- Tests cover the redesigned shell, escaped values and multi-channel options.

### TASK-096 - Dashboard generated date formatting

Status: Done

Phase: Consumption layer

Goal: make the dashboard generation timestamp easier to read while preserving safe fallback behavior.

Acceptance criteria:

- ISO `generated_at` values render in a compact date/time format.
- UTC timestamps render with a clear `UTC` suffix.
- Non-ISO values remain visible as escaped text.
- Existing dashboard sections remain unchanged.
- Tests cover formatted and fallback timestamp behavior.

Evidence:

- Dashboard rendering now formats valid ISO `generated_at` values.
- Non-ISO timestamps still render safely through HTML escaping.
- Tests cover UTC formatting and escaped fallback values.

### TASK-095 - Dashboard source artifact metadata

Status: Done

Phase: Consumption layer

Goal: make the dashboard show which local report artifact produced the view.

Acceptance criteria:

- Dashboard shows `source.artifact` when present.
- Dashboard falls back to top-level `artifact` when source metadata is missing.
- Missing artifact metadata renders as `unknown`.
- Artifact values are HTML-escaped.
- Existing dashboard sections remain unchanged.
- Tests cover source artifact, fallback artifact and escaping.

Evidence:

- Dashboard rendering now includes `Source artifact` in the report metadata section.
- The value prefers `source.artifact` and falls back to top-level `artifact`.
- Tests cover the preferred value, fallback value and escaped artifact text.

### TASK-094 - Dashboard averages panel

Status: Done

Phase: Consumption layer

Goal: make the dashboard show per-record averages already present in report JSON.

Acceptance criteria:

- Dashboard shows average views per record.
- Dashboard shows average engagements per record.
- Dashboard shows average likes, comments and shares per record.
- Missing averages render as `0.00`.
- Existing dashboard sections remain unchanged.
- Tests cover populated and missing average metadata.

Evidence:

- Dashboard rendering now includes a `Per-Record Averages` section.
- The section reads average fields from the existing `totals` report JSON object.
- Tests cover populated averages and backward-compatible missing averages.

### TASK-093 - Dashboard engagement breakdown

Status: Done

Phase: Consumption layer

Goal: make the dashboard explain the composition of total engagement.

Acceptance criteria:

- Dashboard shows likes, comments and shares engagement percentages.
- The values come from the existing `engagement_breakdown` report JSON object.
- Missing breakdown metadata renders as `0.00%`.
- Existing dashboard sections remain unchanged.
- Tests cover populated and missing breakdown metadata.

Evidence:

- Dashboard rendering now includes an `Engagement Breakdown` section.
- The section reads `likes_percent`, `comments_percent` and `shares_percent`.
- Tests cover populated percentages and backward-compatible missing metadata.

### TASK-092 - Dashboard report metadata panel

Status: Done

Phase: Consumption layer

Goal: make the dashboard show the report contract metadata already present in JSON reports.

Acceptance criteria:

- Dashboard shows the report schema version.
- Dashboard shows the ranking metric when present.
- Dashboard shows the ranking limit when present.
- Missing metadata renders as `unknown`.
- Metadata values are HTML-escaped.
- Tests cover populated and missing metadata.

Evidence:

- Dashboard rendering now includes a `Report Metadata` section.
- The section reads `report_schema_version` and `ranking` from the existing report JSON.
- Tests cover normal metadata, missing metadata and escaped ranking text.

### TASK-091 - Dashboard empty state

Status: Done

Phase: Consumption layer

Goal: make empty report output clear in the static dashboard.

Acceptance criteria:

- Empty top-content reports do not render fake zero rows.
- The quality area shows a clear top-content empty label.
- The top-content table shows a clear empty-state row.
- Existing populated report rendering remains unchanged.
- Tests cover the empty-state rendering.

Evidence:

- Dashboard rendering now uses an explicit empty row when `top_rows` is empty.
- Missing or empty top content now renders as `No top content available`.
- Tests cover the empty table state and ensure fake placeholder rows are not emitted.

### TASK-090 - Dashboard visual polish

Status: Done

Phase: Consumption layer

Goal: make the static dashboard easier to read without adding frontend dependencies or a server.

Acceptance criteria:

- Dashboard uses a cleaner responsive layout.
- Summary cards, data quality and top content are visually separated.
- Channel image fallback remains available.
- Existing dashboard data contract remains unchanged.
- Tests cover the rendered dashboard shell.

Evidence:

- Dashboard HTML now includes a responsive shell, metric cards, quality panel and table wrapper.
- The generator still writes one static HTML file from the same report JSON contract.
- Tests cover the new dashboard shell while preserving content and escaping checks.

### TASK-089 - Dashboard channel image rendering

Status: Done

Phase: Consumption layer

Goal: let the dashboard display channel imagery when report metadata provides it.

Acceptance criteria:

- Dashboard renders `source.image_url` as a channel image.
- Dashboard also accepts `source.channel_image_url`.
- Dashboard shows a safe fallback avatar when no image URL exists.
- Image and provider text values are HTML-escaped.
- Tests cover image rendering and fallback behavior.

Evidence:

- Dashboard HTML now includes a channel image area in the header.
- `source.image_url` and `source.channel_image_url` are supported.
- Tests cover rendered image URLs and fallback output.

### TASK-088 - Dashboard project root option

Status: Done

Phase: Consumption layer

Goal: let automation discover dashboard inputs from an explicit project root.

Acceptance criteria:

- Dashboard CLI accepts `--project-root`.
- The option is used for latest-report discovery.
- Explicit `--report-json` behavior remains unchanged.
- Tests cover argument parsing for the project root option.

Evidence:

- `parse_args` now supports `--project-root`.
- `cli_entrypoint` passes the project root to `main`.
- Dashboard parser tests cover the new option.

### TASK-087 - Dashboard defaults to latest report JSON

Status: Done

Phase: Consumption layer

Goal: make the dashboard command easier to run in the normal local reporting flow.

Acceptance criteria:

- Dashboard CLI can run without `--report-json`.
- Default behavior selects the latest local YouTube report JSON.
- Missing report JSON artifacts fail with a clear error.
- Explicit `--report-json` behavior still works.
- Tests cover latest-report discovery and missing-artifact failure.

Evidence:

- `find_latest_report_json` locates the latest JSON report artifact.
- `social-dashboard` treats `--report-json` as optional.
- Tests cover default discovery, explicit input and missing reports.

### TASK-086 - Static dashboard MVP skeleton

Status: Done

Phase: Consumption layer

Goal: create the first local static dashboard generator without adding servers or external dependencies.

Acceptance criteria:

- A dashboard CLI can read one report JSON file.
- The CLI writes a static HTML dashboard file.
- The dashboard shows core totals, data quality and top content.
- Text values are escaped before rendering.
- Tests cover rendering, writing, argument parsing and invalid JSON shape.

Evidence:

- `social_analytics_pipeline.cli.dashboard` now generates static dashboard HTML.
- `pyproject.toml` now exposes `social-dashboard`.
- `tests/test_dashboard.py` covers the first dashboard behavior.

### TASK-085 - Record dashboard-first next delivery direction

Status: Done

Phase: Consumption layer

Goal: make the next delivery sequence explicit before implementing dashboard or provider work.

Acceptance criteria:

- Documentation states that the dashboard MVP comes before the second provider.
- Documentation states that the dashboard reads local report JSON files.
- Documentation states that the second provider starts after the dashboard contract is useful.
- Public documentation avoids secrets, local paths, raw payloads and expanded DSNs.

Evidence:

- `docs/PLAN.md` now defines the dashboard-first delivery sequence.
- `README.md` now explains the next dashboard and provider cycles.
- `docs/PROGRESS.md` now records dashboard MVP as the next action.

### TASK-084 - YouTube markdown report schema version

Status: Done

Phase: Post-v1 direction

Goal: make the human-readable YouTube report identify the report schema version.

Acceptance criteria:

- Markdown report output includes the report schema version.
- The value uses the same schema version constant as JSON output.
- Existing Markdown fields remain unchanged.
- Tests cover the Markdown schema version.

Evidence:

- Markdown payloads now include `Report schema version`.
- The value comes from `YOUTUBE_REPORT_SCHEMA_VERSION`.
- Tests cover the Markdown schema version line.

### TASK-083 - YouTube markdown report top rows count

Status: Done

Phase: Post-v1 direction

Goal: make the human-readable YouTube report show how many ranked rows are displayed.

Acceptance criteria:

- Markdown report output includes the top rows count.
- Populated reports show the actual displayed row count.
- Empty reports show `0`.
- Existing Markdown fields remain unchanged.
- Tests cover populated and empty Markdown reports.

Evidence:

- Markdown payloads now include `Top rows`.
- Populated reports show the displayed ranking count.
- Empty reports show `0`.

### TASK-082 - YouTube markdown report engagement flag

Status: Done

Phase: Post-v1 direction

Goal: make the human-readable YouTube report show whether engagement metrics exist.

Acceptance criteria:

- Markdown report output includes an engagement presence flag.
- Reports with engagements show `yes`.
- Reports without engagements show `no`.
- Existing Markdown fields remain unchanged.
- Tests cover populated and empty Markdown reports.

Evidence:

- Markdown payloads now include `Has engagements`.
- Engagement-bearing reports show `yes`.
- Empty reports show `no`.

### TASK-081 - YouTube markdown report data quality status

Status: Done

Phase: Post-v1 direction

Goal: make the human-readable YouTube report show the same compact quality status used by JSON consumers.

Acceptance criteria:

- Markdown report output includes a data quality status.
- Populated reports show `ok`.
- Empty reports show `empty`.
- JSON status keeps using the same rule.
- Tests cover populated and empty Markdown reports.

Evidence:

- Markdown payloads now include `Data quality`.
- JSON status uses a shared helper for the same rule.
- Tests cover `ok` and `empty` Markdown output.

### TASK-080 - YouTube report JSON engagement data quality flag

Status: Done

Phase: Post-v1 direction

Goal: let report consumers quickly identify whether engagement metrics exist in the summary.

Acceptance criteria:

- JSON `data_quality` includes `has_engagements`.
- The flag is true when likes, comments or shares exist.
- The flag is false when total engagements are zero.
- Existing report fields remain unchanged.
- Tests cover populated, zero-engagement and empty artifacts.

Evidence:

- JSON payloads now include `data_quality.has_engagements`.
- Engagement-bearing artifacts produce `true`.
- Zero-engagement and empty artifacts produce `false`.

### TASK-079 - YouTube report JSON partial data quality flag

Status: Done

Phase: Post-v1 direction

Goal: reserve explicit JSON metadata for future partial report handling without changing current behavior.

Acceptance criteria:

- JSON `data_quality` includes `is_partial`.
- Current report payloads set `is_partial` to `false`.
- Existing report fields remain unchanged.
- Tests cover the flag for populated and empty artifacts.

Evidence:

- JSON payloads now include `data_quality.is_partial`.
- Current complete artifact reports mark `is_partial` as `false`.
- Tests cover the flag in populated and empty report payloads.

### TASK-078 - YouTube report JSON data quality status

Status: Done

Phase: Post-v1 direction

Goal: let report consumers classify the summary quality without combining multiple fields.

Acceptance criteria:

- JSON `data_quality` includes `status`.
- The status is `ok` when records exist.
- The status is `empty` when no records exist.
- Existing report fields remain unchanged.
- Tests cover both statuses.

Evidence:

- JSON payloads now include `data_quality.status`.
- Populated artifacts produce `ok`.
- Empty artifacts produce `empty`.

### TASK-077 - YouTube report JSON top-content data quality flag

Status: Done

Phase: Post-v1 direction

Goal: let report consumers quickly identify whether a JSON summary has a ranked top content item.

Acceptance criteria:

- JSON `data_quality` includes `has_top_content`.
- The flag is true when a top content item exists.
- The flag is false for empty artifacts.
- Existing report fields remain unchanged.
- Tests cover the flag for populated and empty artifacts.

Evidence:

- JSON payloads now include `data_quality.has_top_content`.
- Existing data quality fields remain present.
- Tests cover the flag in populated and empty report payloads.

### TASK-076 - YouTube report JSON data quality metadata

Status: Done

Phase: Post-v1 direction

Goal: let report consumers quickly identify whether a JSON summary contains usable rows.

Acceptance criteria:

- JSON output includes `data_quality`.
- Data quality metadata includes whether the artifact has records.
- Data quality metadata includes the actual top rows count.
- Existing report fields remain unchanged.
- Tests cover the data quality metadata.

Evidence:

- JSON payloads now include `data_quality.has_records`.
- JSON payloads now include `data_quality.top_rows_count`.
- Tests cover data quality metadata in saved and in-memory JSON payloads.

### TASK-075 - YouTube report JSON ranking metadata

Status: Done

Phase: Post-v1 direction

Goal: make report JSON explicit about how `top_rows` was ranked.

Acceptance criteria:

- JSON output includes `ranking`.
- Ranking metadata includes the selected metric.
- Ranking metadata includes the requested top limit.
- Existing `sort_by` and `top_rows` fields remain unchanged.
- Tests cover the ranking metadata.

Evidence:

- `YouTubeReportSummary` now stores the requested top limit.
- JSON payloads now include `ranking.metric` and `ranking.limit`.
- Tests cover the summary top limit and JSON ranking metadata.

### TASK-074 - YouTube report JSON source metadata

Status: Done

Phase: Post-v1 direction

Goal: make report JSON self-describing about the provider and source artifact.

Acceptance criteria:

- JSON output includes `source`.
- Source metadata includes provider `youtube`.
- Source metadata includes the normalized artifact path.
- Existing top-level `artifact` remains unchanged.
- Tests cover the source metadata.

Evidence:

- JSON payloads now include `source.provider` and `source.artifact`.
- The existing `artifact` field remains present.
- Tests cover source metadata in the compact JSON payload.

### TASK-073 - YouTube report JSON generation timestamp

Status: Done

Phase: Post-v1 direction

Goal: let external consumers know when a report JSON summary was generated.

Acceptance criteria:

- JSON output includes `generated_at`.
- The timestamp uses UTC.
- Tests can inject a deterministic timestamp.
- Existing JSON fields remain unchanged.

Evidence:

- JSON payloads now include `generated_at`.
- JSON rendering and writing accept an optional generated timestamp for tests.
- Tests cover deterministic timestamp output.

### TASK-072 - YouTube report JSON schema version

Status: Done

Phase: Post-v1 direction

Goal: make report JSON safer for external consumers as the payload evolves.

Acceptance criteria:

- JSON output includes `report_schema_version`.
- The schema version is controlled by a named constant.
- Existing JSON fields remain unchanged.
- Tests cover the schema version field.

Evidence:

- `youtube_report.py` now defines `YOUTUBE_REPORT_SCHEMA_VERSION`.
- JSON payloads now include `report_schema_version`.
- Tests cover the schema version in the compact JSON payload.

### TASK-071 - YouTube report engagement breakdown

Status: Done

Phase: Post-v1 direction

Goal: make JSON report consumption easier by exposing engagement composition percentages.

Acceptance criteria:

- JSON output includes engagement breakdown percentages for likes, comments and shares.
- The existing totals remain unchanged.
- Zero-engagement artifacts use `0.0` percentages instead of failing.
- Tests cover normal and zero-engagement cases.

Evidence:

- JSON payloads now include `engagement_breakdown`.
- The breakdown exposes numeric percentages for likes, comments and shares.
- Tests cover regular and zero-engagement breakdown behavior.

### TASK-070 - YouTube report engagement averages

Status: Done

Phase: Post-v1 direction

Goal: expose per-record averages for individual engagement types in local YouTube report outputs.

Acceptance criteria:

- Report summaries include average likes, comments and shares per record.
- Empty artifacts use `0.0` instead of failing.
- Markdown, JSON and terminal summary outputs include the averages.
- Tests cover normal and empty-artifact cases.

Evidence:

- `YouTubeReportSummary` now includes average likes, comments and shares per record.
- Markdown output includes the three new averages.
- JSON totals include the three new averages.
- Tests cover regular and empty-artifact behavior.

### TASK-069 - YouTube report average engagements

Status: Done

Phase: Post-v1 direction

Goal: expose average engagement volume per processed YouTube record.

Acceptance criteria:

- Report summaries include average engagements per record.
- Average engagements are calculated as total engagements divided by record count.
- Empty artifacts use `0.0` instead of failing.
- Markdown, JSON and terminal summary outputs include the aggregate.
- Tests cover normal and empty-artifact cases.

Evidence:

- `YouTubeReportSummary` now includes `average_engagements_per_record`.
- Markdown output includes average engagements per record.
- JSON totals include `average_engagements_per_record`.
- Tests cover regular and empty-artifact average behavior.

### TASK-068 - YouTube report average views

Status: Done

Phase: Post-v1 direction

Goal: expose a simple average views aggregate in local YouTube report outputs.

Acceptance criteria:

- Report summaries include average views per record.
- Average views are calculated as total views divided by record count.
- Empty artifacts use `0.0` instead of failing.
- Markdown, JSON and terminal summary outputs include the aggregate.
- Tests cover normal and empty-artifact cases.

Evidence:

- `YouTubeReportSummary` now includes `average_views_per_record`.
- Markdown output includes average views per record.
- JSON totals include `average_views_per_record`.
- Tests cover regular and empty-artifact average behavior.

### TASK-067 - YouTube report engagement rate percent

Status: Done

Phase: Post-v1 direction

Goal: make JSON report consumption easier for spreadsheets and simple automations.

Acceptance criteria:

- JSON totals keep the decimal `engagement_rate` field.
- JSON totals also include numeric `engagement_rate_percent`.
- Markdown and terminal output remain unchanged.
- Tests cover the new JSON field.

Evidence:

- JSON totals now include `engagement_rate_percent`.
- The value is numeric and derived from `engagement_rate * 100`.
- Tests cover the field in the compact JSON report payload.

### TASK-066 - YouTube report engagement rate

Status: Done

Phase: Post-v1 direction

Goal: expose a simple engagement-rate aggregate in local YouTube report outputs.

Acceptance criteria:

- Report summaries include engagement rate.
- Engagement rate is calculated as total engagements divided by total views.
- Zero-view artifacts use `0.0` instead of failing.
- Markdown, JSON and terminal summary outputs include engagement rate.
- Tests cover normal and zero-view cases.

Evidence:

- `YouTubeReportSummary` now includes `engagement_rate`.
- Markdown output includes a formatted engagement-rate percentage.
- JSON totals include `engagement_rate`.
- Tests cover regular engagement rate and zero-view handling.

### TASK-065 - YouTube report total engagements

Status: Done

Phase: Post-v1 direction

Goal: expose a simple engagement aggregate in local YouTube report outputs.

Acceptance criteria:

- Report summaries include total engagements.
- Total engagements are calculated as likes plus comments plus shares.
- Markdown, JSON and terminal summary outputs include total engagements.
- Tests cover the aggregate in summary, markdown and JSON outputs.

Evidence:

- `YouTubeReportSummary` now includes `total_engagements`.
- Markdown output includes total engagements.
- JSON totals include `engagements`.
- Tests cover the aggregate without changing existing totals.

### TASK-064 - Explicit YouTube report top metric value

Status: Done

Phase: Post-v1 direction

Goal: make report summaries clear when top content is ranked by a metric other than views.

Acceptance criteria:

- Report summaries keep `top_views` for compatibility.
- Report summaries expose the selected top-ranking metric value.
- Markdown, JSON and terminal summary outputs include the selected metric value.
- Tests cover ranking by a non-default metric.

Evidence:

- `YouTubeReportSummary` now includes `top_metric_value`.
- Markdown output includes the selected top metric value.
- JSON output includes `top_content.metric` and `top_content.metric_value`.
- Tests cover `likes` ranking in summary, markdown and JSON outputs.

### TASK-063 - YouTube report console script

Status: Done

Phase: Post-v1 direction

Goal: make the local YouTube report easier to run after package installation.

Acceptance criteria:

- The package exposes a `youtube-report` console script.
- The console script uses the same parser and behavior as `python -m social_analytics_pipeline.cli.youtube_report`.
- The module entrypoint and console script share one implementation.
- Tests cover the entrypoint path.

Evidence:

- `pyproject.toml` now declares `youtube-report`.
- `youtube_report.py` now has a shared `cli_entrypoint`.
- Tests cover invoking the entrypoint with CLI-style arguments.
- `docs/BOOTSTRAP.md` documents the shortcut.

### TASK-062 - Stdout-only JSON YouTube reports

Status: Done

Phase: Post-v1 direction

Goal: let automation consume a JSON report from stdout without writing markdown or JSON files.

Acceptance criteria:

- The report CLI accepts `--no-markdown --print-json`.
- The parser still rejects `--no-markdown` when no JSON destination exists.
- Stdout-only JSON mode does not create report files.
- Tests cover parser support and file-free JSON execution.

Evidence:

- `youtube_report.py` now treats `--print-json` as a valid JSON destination for `--no-markdown`.
- Tests cover stdout-only JSON output without creating `data/reports`.
- `docs/BOOTSTRAP.md` documents the new usage.

### TASK-061 - Dry-run YouTube report generation

Status: Done

Phase: Post-v1 direction

Goal: let operators validate report inputs and planned outputs without writing markdown or JSON files.

Acceptance criteria:

- The report CLI supports `--dry-run`.
- Dry runs load and validate the selected artifact.
- Dry runs respect `--fail-if-empty` and `--min-records`.
- Dry runs print planned markdown and JSON output paths when not quiet.
- Dry runs do not create report output files.
- Tests cover parser support, dry-run output and minimum-record failure behavior.

Evidence:

- `youtube_report.py` now supports `--dry-run`.
- Planned markdown and JSON output paths are resolved before writing.
- Dry-run mode returns before report files are created.
- `docs/BOOTSTRAP.md` documents the new option.

### TASK-060 - Require a minimum YouTube report record count

Status: Done

Phase: Post-v1 direction

Goal: let automation require a minimum number of records before report output is written.

Acceptance criteria:

- The report CLI supports `--min-records`.
- Negative values fail during argument parsing.
- Report generation fails before writing outputs when the selected artifact has fewer records than required.
- `--fail-if-empty` remains supported as a convenience for requiring at least one record.
- Tests cover parser support, invalid values, failure behavior and successful minimum checks.

Evidence:

- `youtube_report.py` now supports `--min-records`.
- Minimum-record checks happen after loading the selected artifact and before report writing.
- Tests cover below-minimum failure and successful report output when the minimum is met.
- `docs/BOOTSTRAP.md` documents the new option.

### TASK-059 - Fail YouTube report generation for empty artifacts

Status: Done

Phase: Post-v1 direction

Goal: let automation fail clearly when the selected processed artifact has no records.

Acceptance criteria:

- The report CLI supports `--fail-if-empty`.
- Empty selected artifacts return a failure code before writing markdown or JSON reports.
- Non-empty report generation remains unchanged.
- Quiet mode suppresses the empty-artifact message.
- Tests cover parser support, empty-artifact failure and quiet failure behavior.

Evidence:

- `youtube_report.py` now supports `--fail-if-empty`.
- Empty-artifact failure happens after loading the selected artifact and before report writing.
- Tests cover failing empty artifacts without creating report output.
- `docs/BOOTSTRAP.md` documents the new option.

### TASK-058 - Print YouTube report JSON to stdout

Status: Done

Phase: Post-v1 direction

Goal: let automation consume the compact JSON report directly from stdout without requiring a file.

Acceptance criteria:

- The report CLI supports `--print-json`.
- Printed JSON uses the same payload as JSON file output.
- `--print-json` respects `--json-indent`.
- `--quiet --print-json` prints only the JSON payload.
- Tests cover JSON rendering and quiet stdout JSON behavior.

Evidence:

- `youtube_report.py` now supports `--print-json`.
- JSON rendering is shared between file writing and stdout printing.
- Tests cover compact JSON text rendering and quiet JSON stdout execution.
- `docs/BOOTSTRAP.md` documents the new option.

### TASK-057 - Configure YouTube report JSON indentation

Status: Done

Phase: Post-v1 direction

Goal: let automation choose between pretty and compact JSON report output.

Acceptance criteria:

- The report CLI supports `--json-indent`.
- The default JSON indentation remains `2`.
- `--json-indent 0` writes compact JSON output.
- Negative indentation values fail during argument parsing.
- Tests cover parser support, invalid values and compact JSON writing.

Evidence:

- `youtube_report.py` now supports `--json-indent`.
- JSON writing accepts an indentation setting while preserving the previous default.
- Tests cover compact JSON output and invalid indentation values.
- `docs/BOOTSTRAP.md` documents the new option.

### TASK-056 - Allow YouTube report JSON output directory

Status: Done

Phase: Post-v1 direction

Goal: let operators choose a JSON report directory without manually composing the output file name.

Acceptance criteria:

- The report CLI supports `--json-output-dir`.
- `--json-output-dir` writes JSON using the processed artifact stem as the file name.
- `--json-output` and `--json-output-dir` cannot be used together.
- `--no-markdown` accepts either `--json-output` or `--json-output-dir`.
- Tests cover path construction, parser validation and JSON output-dir execution.

Evidence:

- `youtube_report.py` now supports `--json-output-dir`.
- JSON output-dir mode keeps artifact-based JSON file names.
- Parser and direct `main` calls reject conflicting JSON output arguments.
- Tests cover JSON output-dir path generation and execution.
- `docs/BOOTSTRAP.md` documents the new option.

### TASK-055 - Allow YouTube report markdown output directory

Status: Done

Phase: Post-v1 direction

Goal: let operators choose a markdown report directory without manually composing the output file name.

Acceptance criteria:

- The report CLI supports `--output-dir`.
- `--output-dir` writes markdown using the processed artifact stem as the file name.
- `--output` and `--output-dir` cannot be used together.
- Existing explicit `--output` behavior remains supported.
- Tests cover path construction, parser validation and output-dir execution.

Evidence:

- `youtube_report.py` now supports `--output-dir`.
- Output-dir mode keeps artifact-based markdown file names.
- Parser and direct `main` calls reject conflicting output arguments.
- Tests cover output-dir path generation and execution.
- `docs/BOOTSTRAP.md` documents the new option.

### TASK-054 - Suppress YouTube report summary output

Status: Done

Phase: Post-v1 direction

Goal: let automation generate report files without printing the human-readable summary.

Acceptance criteria:

- The report CLI supports `--quiet`.
- Quiet mode still writes the requested report files.
- Quiet mode suppresses report-generation summary output.
- List-only modes keep their required output.
- Tests cover parser support and quiet report execution.

Evidence:

- `youtube_report.py` now supports `--quiet`.
- Quiet mode skips summary printing after report generation.
- Tests cover quiet execution while still writing markdown output.
- `docs/BOOTSTRAP.md` documents the new option.

### TASK-053 - Allow JSON-only YouTube report output

Status: Done

Phase: Post-v1 direction

Goal: let automation generate a compact JSON report without also writing a markdown report.

Acceptance criteria:

- The report CLI supports `--no-markdown`.
- `--no-markdown` requires `--json-output`.
- JSON-only mode writes the JSON summary and skips markdown output.
- Default behavior still writes markdown.
- Tests cover parser validation and JSON-only execution.

Evidence:

- `youtube_report.py` now supports `--no-markdown`.
- Parser and direct `main` calls reject `--no-markdown` without JSON output.
- Tests cover JSON-only execution and invalid no-output usage.
- `docs/BOOTSTRAP.md` documents the new option.

### TASK-052 - Count processed YouTube report artifacts

Status: Done

Phase: Post-v1 direction

Goal: give local automation a small count-only artifact discovery mode before report generation.

Acceptance criteria:

- The report CLI supports `--count-artifacts`.
- Count-only mode prints only the number of processed YouTube artifacts.
- Count-only mode does not write markdown or JSON reports.
- `--count-artifacts --fail-if-missing` returns a failure code when no processed artifacts exist.
- Tests cover parser support, count output, failure behavior and conflicting list-only modes.

Evidence:

- `youtube_report.py` now supports `--count-artifacts`.
- Count-only mode uses the existing processed artifact discovery path.
- Tests cover successful count output, missing-artifact failure and parser exclusivity.
- `docs/BOOTSTRAP.md` documents the new option.

### TASK-051 - Prevent ambiguous YouTube report list-only modes

Status: Done

Phase: Post-v1 direction

Goal: keep artifact discovery commands predictable by rejecting conflicting list-only modes.

Acceptance criteria:

- `--list-artifacts` and `--latest-artifact` cannot be used together.
- Each list-only mode remains available on its own.
- `--fail-if-missing` remains compatible with list-only automation.
- Tests cover accepted and rejected parser combinations.

Evidence:

- `youtube_report.py` now uses an argparse mutually exclusive group for list-only modes.
- Tests cover `--latest-artifact` alone and conflicting list-only arguments.
- Existing list-only execution tests still pass.
- `docs/BOOTSTRAP.md` documents that only one list-only mode should be used at a time.

### TASK-050 - Fail list-only report automation when artifacts are missing

Status: Done

Phase: Post-v1 direction

Goal: let simple automation fail clearly when it expects processed YouTube artifacts but none are available.

Acceptance criteria:

- The report CLI supports `--fail-if-missing`.
- `--list-artifacts --fail-if-missing` returns a failure code when no processed artifacts exist.
- Existing list behavior remains successful when the flag is not used.
- Tests cover parser support and missing-artifact failure behavior.

Evidence:

- `youtube_report.py` now supports `--fail-if-missing`.
- List-only mode can return exit code 1 when no processed artifacts exist.
- Tests cover argument parsing and missing-artifact failure behavior.
- `docs/BOOTSTRAP.md` documents the new option.

### TASK-049 - Print the latest processed YouTube report artifact

Status: Done

Phase: Post-v1 direction

Goal: make automation and local operation simpler when only the latest processed artifact path is needed.

Acceptance criteria:

- The report CLI supports `--latest-artifact`.
- The command prints only the latest processed artifact path and exits.
- The command does not write markdown or JSON reports in this mode.
- Tests cover latest-artifact behavior and argument parsing.

Evidence:

- `youtube_report.py` now supports `--latest-artifact`.
- Latest artifact output reuses the existing processed artifact discovery path.
- Tests cover relative latest-artifact output and list-only execution.
- `docs/BOOTSTRAP.md` documents the new option.

### TASK-048 - List processed YouTube report artifacts

Status: Done

Phase: Post-v1 direction

Goal: make it easier to choose a processed YouTube artifact before generating a local report.

Acceptance criteria:

- The report CLI supports `--list-artifacts`.
- Listing artifacts exits without writing markdown or JSON reports.
- Listed paths are project-relative and safe for repository documentation.
- Tests cover listing behavior and argument parsing.

Evidence:

- `youtube_report.py` now supports `--list-artifacts`.
- Artifact listing reuses the existing processed artifact discovery path.
- Tests cover sorted relative artifact listing and list-only CLI execution.
- `docs/BOOTSTRAP.md` documents the new option.

### TASK-047 - Add optional JSON output to the YouTube report CLI

Status: Done

Phase: Post-v1 direction

Goal: make the local YouTube report easier to reuse in automation by saving a compact structured summary when requested.

Acceptance criteria:

- The report CLI supports an optional `--json-output` path.
- Markdown output remains the default behavior.
- The JSON summary includes aggregate totals, ranking metadata and sanitized top rows.
- Tests cover JSON payload generation, persistence and CLI parsing.

Evidence:

- `youtube_report.py` now supports `--json-output`.
- JSON output is written only when explicitly requested.
- The JSON payload exports compact report fields instead of raw processed rows.
- Tests cover JSON persistence, argument parsing and explicit CLI execution.

### TASK-046 - Add configurable ranking metric to the YouTube report CLI

Status: Done

Phase: Post-v1 direction

Goal: let users choose which engagement metric drives the top-content ranking in the local YouTube markdown report.

Acceptance criteria:

- The report CLI supports a `--sort-by` option.
- The default ranking metric remains `views`.
- Supported metrics are `views`, `likes`, `comments` and `shares`.
- Tests cover custom ranking behavior and invalid metrics.

Evidence:

- `youtube_report.py` now supports `--sort-by`.
- Ranking generation now uses the selected metric while preserving the previous default.
- Tests cover `likes` ranking, invalid ranking metrics and CLI parsing.
- `docs/BOOTSTRAP.md` documents the new option.

### TASK-045 - Add configurable top-content size to the YouTube report CLI

Status: Done

Phase: Post-v1 direction

Goal: make local YouTube reports easier to tune by allowing users to choose how many ranked content rows appear in the markdown report.

Acceptance criteria:

- The report CLI supports a `--top` option.
- The default top-content ranking remains five rows.
- Invalid `--top` values fail clearly before report generation.
- Tests cover custom top limits and invalid values.

Evidence:

- `youtube_report.py` now supports `--top` with a positive integer validator.
- `build_youtube_report_summary_with_limit` controls the ranking size while preserving the existing default behavior.
- Tests cover explicit top limits, invalid top limits and CLI parsing.
- `docs/BOOTSTRAP.md` documents the new option.

### TASK-044 - Add explicit input and output options to the YouTube report CLI

Status: Done

Phase: Post-v1 direction

Goal: make local YouTube reporting easier to operate by allowing users to choose the processed artifact and markdown output path.

Acceptance criteria:

- The report CLI supports an explicit processed artifact path.
- The report CLI supports an explicit markdown output path.
- Default behavior still uses the latest processed artifact and default report location.
- Tests cover argument parsing and explicit path behavior.

Evidence:

- `youtube_report.py` now supports `--artifact` and `--output`.
- `write_youtube_report_markdown` accepts a custom output path while preserving the default path behavior.
- Tests cover argument parsing, custom output persistence, explicit-path CLI execution and output paths outside the project root.
- `docs/BOOTSTRAP.md` documents the optional arguments.

### TASK-043 - Add a shareable local YouTube markdown report

Status: Done

Phase: Post-v1 direction

Goal: make the existing YouTube data easier to consume by generating a small shareable markdown report instead of adding a dashboard or new infrastructure.

Acceptance criteria:

- The local report command generates a markdown file from the latest processed YouTube artifact.
- The markdown report includes compact aggregate metrics and a top-content ranking.
- The command still fails clearly when no processed artifact exists or the artifact is invalid.
- Tests cover summary aggregation and markdown persistence.

Evidence:

- `youtube_report.py` now writes a markdown report under `data/reports/youtube/`.
- The report includes totals plus a top-content table ranked by views.
- The command still reads the latest file from `data/processed/youtube/` by default.
- Tests cover latest-file selection, summary aggregation, markdown generation and invalid artifact handling.

### TASK-042 - Add a simple local YouTube report command for processed artifacts

Status: Done

Phase: Post-v1 direction

Goal: make the existing YouTube data immediately useful by adding a small local consumption command instead of more infrastructure.

Acceptance criteria:

- A local command can read the latest processed YouTube artifact.
- The command prints compact aggregated metrics from processed data.
- The command fails clearly when no processed artifact exists or the artifact is invalid.
- Tests cover artifact selection and summary aggregation.

Evidence:

- Added `src/social_analytics_pipeline/cli/youtube_report.py`.
- The command reads the latest file from `data/processed/youtube/` by default.
- The command prints totals for views, likes, comments, shares, followers and top content.
- Tests cover latest-file selection, summary aggregation and invalid artifact handling.

### TASK-041 - Record YouTube v1 closure and define the next delivery decision

Status: Done

Phase: Post-v1 direction

Goal: formally close the current YouTube v1 slice in repository context and make the next step explicit before new implementation work starts.

Acceptance criteria:

- The repository states that the YouTube v1 closure checkpoint has been met.
- The repository no longer presents the current cycle as still "closing".
- The next delivery decision is explicit and compact.
- The next options stay focused on product value instead of additional engineering polish.

Evidence:

- `README.md` now reflects the post-v1 decision phase.
- `docs/PLAN.md` now records the next delivery options after YouTube v1 closure.
- `docs/PROGRESS.md` now states that the YouTube v1 cycle is closed in repository context.
- The backlog now points to a deliberate next decision instead of more implicit closure work.

### TASK-040 - Create a concise YouTube v1 operator runbook and closure checkpoint

Status: Done

Phase: Phase 1 - MVP Core

Goal: make the existing real YouTube path easy to run, verify and hand off without adding new technical layers first.

Acceptance criteria:

- The repository documents the minimum steps to run the real YouTube path locally.
- The repository documents the minimum steps to run the YouTube Airflow DAG deliberately.
- The repository states what counts as "YouTube v1 closed" for the current cycle.
- The guidance stays compact and does not expose secrets, local paths or raw payloads.

Notes:

- This task is intentionally operational, not architectural.
- Its purpose is to close the current delivery cycle before expanding scope again.

Evidence:

- `README.md` now states the YouTube v1 closure target in compact form.
- `docs/BOOTSTRAP.md` now includes a minimal local and Airflow operator runbook.
- The repository now records a concrete closure checkpoint for the current YouTube cycle.
- The guidance stays compact and avoids secrets, local paths and raw payload details.

### TASK-039 - Persist a structured run summary for the real YouTube pipeline

Status: Done

Phase: Phase 3 - Resilience

Goal: keep a compact execution summary artifact for each real YouTube run so troubleshooting does not depend on terminal output or Airflow task logs alone.

Acceptance criteria:

- Each local YouTube run writes a structured JSON run summary artifact.
- The summary captures interval, status, execution counts and artifact locations.
- The local CLI output shows the run summary path.
- The YouTube Airflow DAG result includes the run summary path.
- Tests prove the summary file is created for both healthy and warning runs.

Evidence:

- Added run summary artifact helpers in `pipeline/artifacts.py`.
- `run_youtube_local_pipeline` now writes a run summary under `data/runs/youtube/`.
- The local CLI output now prints `run_summary_path`.
- The YouTube Airflow DAG return payload now includes `run_summary_path`.
- Tests confirm summary creation and warning status behavior when invalid records are diverted to the DLQ.

### TASK-037 - Add a local DLQ for invalid records without breaking the main load

Status: Done

Phase: Phase 3 - Resilience

Goal: isolate invalid normalized records into a local dead letter queue so valid metrics can still load.

Acceptance criteria:

- Invalid records do not stop valid records from loading.
- Invalid records are persisted in a local DLQ area with a reason and raw file reference.
- The pipeline result reports invalid record counts.
- Tests prove that invalid records are diverted while valid load behavior remains intact.

Evidence:

- Added `storage/dlq.py` with local dead letter storage for invalid records.
- `run_provider_pipeline` now diverts invalid records to `data/dlq/` and continues loading valid metrics.
- `LocalPipelineResult` now reports `invalid_records`.
- YouTube local and Airflow summaries now include invalid record counts.
- Tests confirm invalid records are persisted to the DLQ while the main load path remains usable.

### TASK-038 - Add runtime metrics and simple invalid-record alerting

Status: Done

Phase: Phase 3 - Resilience

Goal: expose execution counts more clearly and allow deliberate failure when invalid records are detected.

Acceptance criteria:

- Pipeline results expose valid record counts.
- YouTube local and Airflow summaries include a simple execution status.
- A local environment flag can fail the run when invalid records were sent to the DLQ.
- Tests cover the invalid-record alert policy.

Evidence:

- `LocalPipelineResult` now exposes `valid_records`.
- YouTube local output now reports `valid_records` and can fail when `YOUTUBE_FAIL_ON_INVALID_RECORDS=true`.
- The YouTube Airflow DAG now reports `status`, `valid_records`, `invalid_records`, and `loaded_records`.
- Tests cover warning-only behavior and fail-on-invalid behavior.

### TASK-036 - Add controlled YouTube backfill support without re-enabling automatic DAG catchup

Status: Done

Phase: Phase 3 - Resilience

Goal: support deliberate historical YouTube intervals without restoring automatic catchup behavior in Airflow.

Acceptance criteria:

- Explicit backfill start and end settings are supported for local YouTube runs.
- The real YouTube DAG can use explicit backfill settings only when Airflow interval context is absent.
- Invalid or partial backfill configuration fails early with clear errors.
- Automatic DAG catchup remains disabled.
- Tests cover explicit backfill interval parsing and validation.

Evidence:

- Added `YOUTUBE_BACKFILL_START_AT` and `YOUTUBE_BACKFILL_END_AT` parsing in `youtube_smoke.py`.
- Local YouTube commands now reuse the explicit backfill interval when both values are present.
- The real YouTube DAG uses the explicit backfill interval only as a controlled fallback when no Airflow data interval is provided.
- Tests cover missing pair behavior, timezone validation, reversed ranges, and explicit UTC parsing.
- `.env.example` and `docs/BOOTSTRAP.md` document the new backfill variables.

### TASK-035 - Decide whether to expand to another provider or harden YouTube first

Status: Done

Phase: Phase 4 - Quality and scale

Goal: choose the next implementation direction based on the real maturity of the repository, not on mock coverage alone.

Acceptance criteria:

- The decision is documented in repository context.
- The decision explains why the chosen path is lower risk and higher value.
- A concrete follow-up task is created for the chosen direction.

Evidence:

- The repository currently has one real provider path end to end: YouTube.
- Instagram and TikTok are still represented by mock providers only.
- The real YouTube path already includes local CLI execution, raw storage, normalization, validation, PostgreSQL loading, Airflow orchestration, resilience, and tests.
- The next implementation direction is to harden YouTube further with controlled backfill before expanding to another real provider.

Decision:

- Choose depth before breadth.
- Continue with YouTube first.
- Defer new real provider expansion until the YouTube path supports deliberate historical recovery behavior.

### TASK-034 - Add data validation before loading metrics

Status: Done

Phase: Phase 4 - Quality and scale

Goal: block impossible normalized metrics before they reach JSON artifacts or PostgreSQL loads.

Acceptance criteria:

- Normalized metrics are validated before the load step.
- Empty required identifiers are rejected.
- Negative metric counters are rejected.
- `published_at` after `collected_at` is rejected.
- Tests prove invalid metrics stop the load path.

Evidence:

- Added `transform/validation.py` with targeted metric validation.
- `run_provider_pipeline` now validates metrics before calling the loader.
- Tests cover invalid counters, invalid timestamps, empty identifiers, and pipeline load blocking.

### TASK-033 - Add retry/backoff and clearer failure alerts for API/configuration errors

Status: Done

Phase: Phase 3 - Resilience

Goal: make the real YouTube provider fail more safely by retrying transient API/network errors, stopping early on invalid credentials/configuration, and preserving sanitized error messages.

Acceptance criteria:

- Retryable YouTube API failures use bounded retry/backoff behavior.
- Invalid credentials or configuration errors fail without useless retries.
- Error messages remain sanitized and do not expose API keys, local paths, or raw request URLs.
- Automated tests cover retry success, retry exhaustion, and credential/configuration failures.

Evidence:

- `HttpJsonClient` now retries transient request failures and stops early on `401` and `403`.
- `YouTubeApiConfig.from_env` validates retry/backoff environment settings.
- `tests/test_youtube_provider.py` covers retryable status handling, retry exhaustion, and credential failure behavior.

### TASK-032 - Validate `social_analytics_youtube_pipeline` inside local Airflow

Status: Done

Phase: Phase 2 - Orchestration and history

Goal: prove the real YouTube DAG can be parsed, triggered and completed in the local Airflow Docker environment without exposing secrets, channel IDs or payloads.

Acceptance criteria:

- Airflow metadata initialization succeeds.
- Airflow API server, scheduler, DAG processor, worker, triggerer, Redis and PostgreSQL containers are healthy.
- `social_analytics_youtube_pipeline` is listed by Airflow.
- A manual DAG run finishes successfully.
- Logs mask the configured channel and do not print API keys or payloads.
- The real YouTube DAG does not automatically backfill historical intervals.

Evidence:

- `docker compose --env-file .env config --quiet` passed.
- `docker compose --env-file .env up airflow-init` completed successfully.
- Airflow services started and reported healthy where applicable.
- `airflow dags list` showed `social_analytics_youtube_pipeline`.
- Manual run `manual__2026-06-03T14:58:41.282474+00:00` completed with `success`.
- Successful task log returned `raw_records=50` and `loaded_records=50` with `channel_id=<configured>`.
- Local DAG was paused after validation to avoid accidental YouTube API quota usage.

## Completed Task Summary

| Task range | Summary | Status |
| --- | --- | --- |
| TASK-001 to TASK-007 | Governance foundation, Python skeleton, mock providers, shared schema, PostgreSQL loader and local mock pipeline. | Done |
| TASK-008 to TASK-010 | Airflow Docker environment, mock pipeline DAG, 15-day schedule and catchup. | Done |
| TASK-011 to TASK-017 | Change proposal governance, security gates, sensitive-data checks, Airflow/Postgres readiness and loader configuration. | Done |
| TASK-018 to TASK-021 | Initial real YouTube provider and safe smoke command with `.env` support. | Done |
| TASK-022 to TASK-023 | Multi-agent governance and review packet improvements. | Done |
| TASK-024 to TASK-026 | Safer YouTube configuration validation, sanitized HTTP errors and handle resolution. | Done |
| TASK-027 to TASK-029 | Real YouTube local raw/processed pipeline and PostgreSQL load validation. | Done |
| TASK-030 | Real YouTube Airflow DAG, environment wiring and CI/CodeRabbit validation in PR #19. | Done |
| TASK-031 | Main documentation condensed into compact English project context. | Done |
| TASK-032 | Real YouTube Airflow DAG validated locally with a successful manual run. | Done |
| TASK-033 | Retry/backoff and clearer YouTube failure handling with targeted tests. | Done |
| TASK-034 | Metric validation now blocks impossible data before JSON/PostgreSQL load. | Done |
| TASK-035 | Decision recorded: harden the real YouTube path before expanding to another real provider. | Done |
| TASK-036 | Controlled YouTube backfill now supports explicit intervals without re-enabling DAG catchup. | Done |
| TASK-037 | Invalid records now go to a local DLQ without blocking valid loads. | Done |
| TASK-038 | Runtime metrics and simple invalid-record alerting were added to the YouTube path. | Done |
| TASK-039 | Real YouTube runs now persist a compact structured run summary artifact. | Done |
| TASK-040 | The repository now includes a concise YouTube v1 runbook and closure checkpoint. | Done |
| TASK-041 | The repository now treats the YouTube v1 slice as closed and sets up the next decision. | Done |
| TASK-042 | A simple local YouTube report command now consumes processed artifacts. | Done |
| TASK-043 | The local YouTube report command now generates a shareable markdown report. | Done |
| TASK-044 | The local YouTube report command now accepts explicit input and output paths. | Done |
| TASK-045 | The local YouTube report command now supports configurable top-content ranking size. | Done |
| TASK-046 | The local YouTube report command now supports configurable ranking metrics. | Done |
| TASK-047 | The local YouTube report command now supports optional compact JSON summaries. | Done |
| TASK-048 | The local YouTube report command can list processed artifacts before reporting. | Done |
| TASK-049 | The local YouTube report command can print only the latest processed artifact. | Done |
| TASK-050 | The local YouTube report command can fail list-only automation when artifacts are missing. | Done |
| TASK-051 | The local YouTube report command rejects ambiguous list-only mode combinations. | Done |
| TASK-052 | The local YouTube report command can print only the processed artifact count. | Done |
| TASK-053 | The local YouTube report command can write JSON output without markdown. | Done |
| TASK-054 | The local YouTube report command can suppress report-generation summary output. | Done |
| TASK-055 | The local YouTube report command can write markdown into a chosen output directory. | Done |
| TASK-056 | The local YouTube report command can write JSON into a chosen output directory. | Done |
| TASK-057 | The local YouTube report command can configure JSON indentation. | Done |
| TASK-058 | The local YouTube report command can print the JSON summary payload to stdout. | Done |
| TASK-059 | The local YouTube report command can fail before writing reports for empty artifacts. | Done |
| TASK-060 | The local YouTube report command can require a minimum record count before writing reports. | Done |
| TASK-061 | The local YouTube report command can dry-run planned report outputs without writing files. | Done |
| TASK-062 | The local YouTube report command can print JSON without writing report files. | Done |
| TASK-063 | The package exposes the local YouTube report command as `youtube-report`. | Done |
| TASK-064 | YouTube reports expose the selected top-ranking metric value. | Done |
| TASK-065 | YouTube reports expose total engagements. | Done |
| TASK-066 | YouTube reports expose engagement rate. | Done |
| TASK-067 | YouTube report JSON exposes engagement rate as a numeric percentage. | Done |
| TASK-068 | YouTube reports expose average views per record. | Done |
| TASK-069 | YouTube reports expose average engagements per record. | Done |
| TASK-070 | YouTube reports expose average likes, comments and shares per record. | Done |
| TASK-071 | YouTube report JSON exposes engagement breakdown percentages. | Done |
| TASK-072 | YouTube report JSON exposes an explicit schema version. | Done |
| TASK-073 | YouTube report JSON exposes a UTC generation timestamp. | Done |
| TASK-074 | YouTube report JSON exposes provider and source artifact metadata. | Done |
| TASK-075 | YouTube report JSON exposes ranking metric and limit metadata. | Done |
| TASK-076 | YouTube report JSON exposes simple data quality metadata. | Done |
| TASK-077 | YouTube report JSON indicates whether top content exists. | Done |
| TASK-078 | YouTube report JSON exposes compact data quality status. | Done |
| TASK-079 | YouTube report JSON marks current summaries as non-partial. | Done |
| TASK-080 | YouTube report JSON indicates whether engagement metrics exist. | Done |
| TASK-081 | YouTube markdown reports expose compact data quality status. | Done |
| TASK-082 | YouTube markdown reports indicate whether engagement metrics exist. | Done |
| TASK-083 | YouTube markdown reports expose the displayed top rows count. | Done |
| TASK-084 | YouTube markdown reports expose the report schema version. | Done |
| TASK-085 | Documentation records dashboard MVP before the second real provider. | Done |
| TASK-086 | Static dashboard MVP can render one report JSON file to HTML. | Done |
| TASK-087 | Dashboard CLI defaults to the latest local report JSON. | Done |
| TASK-088 | Dashboard CLI accepts an explicit project root for report discovery. | Done |
| TASK-089 | Dashboard renders channel imagery from report source metadata. | Done |
| TASK-090 | Dashboard static HTML received responsive visual polish. | Done |
| TASK-091 | Dashboard renders explicit empty states for missing top content. | Done |
| TASK-092 | Dashboard shows report schema and ranking metadata. | Done |
| TASK-093 | Dashboard shows engagement composition percentages. | Done |
| TASK-094 | Dashboard shows per-record average metrics. | Done |
| TASK-095 | Dashboard shows the source artifact used for the report. | Done |
| TASK-096 | Dashboard formats generated timestamps for readability. | Done |
| TASK-097 | Dashboard was redesigned as a single-page channel selector view. | Done |
| TASK-098 | Roadmap was realigned around channel-first multi-platform analytics. | Done |
| TASK-099 | Dashboard channel contract now supports platform source metrics. | Done |
| TASK-100 | Dashboard shows per-platform source cards inside selected channels. | Done |
| TASK-101 | Dashboard aggregates multiple report JSON artifacts by channel identity. | Done |
| TASK-102 | Dashboard can apply local monitored channel identity configuration. | Done |
| TASK-103 | Instagram was selected as the next real provider. | Done |
| TASK-104 | Instagram provider skeleton was added behind local credentials. | Done |
| TASK-105 | Instagram provider can run through an explicit local pipeline command. | Done |
| TASK-106 | Dashboard content display now prioritizes human metadata over technical IDs. | Done |
| TASK-107 | Instagram report JSON can feed the channel-first dashboard contract. | Done |

## Next Channel-Oriented Tasks

### TASK-101 - Multi-report channel aggregation

Status: Done

Phase: Consumption layer

Goal: let the dashboard build a channel list from multiple report JSON artifacts.

Acceptance criteria:

- Dashboard can accept or discover multiple report JSON files.
- Reports with the same channel identity are grouped into one channel option.
- Reports from different providers become platform sources inside the channel.
- Existing single-report behavior remains supported.
- Tests cover single-report and multi-report aggregation.

Implementation notes:

- `social-dashboard` now accepts repeated `--report-json` values.
- `social-dashboard --all-reports` discovers every local JSON report in the default report directory.
- Reports with matching channel identity are grouped into one dashboard channel.
- Each grouped report becomes a platform source for the selected channel.
- Existing single-report and latest-report behavior remains supported.

### TASK-102 - Channel identity configuration

Status: Done

Phase: Consumption layer

Goal: map platform-specific accounts to a single monitored channel identity.

Acceptance criteria:

- Local configuration can map one channel to YouTube, TikTok and Instagram handles/IDs.
- Configuration examples use placeholders only.
- The dashboard/report layer can use the configured display name and image URL.
- Missing platform handles are allowed.
- Tests cover complete and partial channel mappings.

Implementation notes:

- `config/channels.example.json` documents a safe placeholder mapping for YouTube, TikTok and Instagram.
- `config/channels.local.json` is ignored and can hold local real handles or IDs.
- `social-dashboard --channels-config` can apply monitored channel display names and image URLs.
- Matching is provider-aware, so the same handle string on the wrong provider is not treated as a match.
- Missing platform entries are allowed for partial monitoring.

### TASK-103 - Second real provider decision

Status: Done

Phase: Second real provider

Goal: choose the next real provider only after the channel contract can absorb it.

Acceptance criteria:

- The decision compares TikTok and Instagram official API availability.
- The selected provider has local credential requirements documented with placeholders only.
- The implementation plan avoids scraping and non-official access.
- The provider must produce metrics compatible with the channel dashboard contract.

Implementation notes:

- ADR-0002 selects Instagram as the next real provider.
- The decision is limited to authorized Instagram professional accounts.
- TikTok remains deferred because the official public-data path is research-oriented and constrained.
- Public docs use placeholder credential names only.
- The next implementation step is a small Instagram provider skeleton.

### TASK-104 - Instagram provider skeleton

Status: Done

Phase: Second real provider

Goal: add the smallest official-API Instagram provider shape without making automatic real calls.

Acceptance criteria:

- Provider requires explicit local credentials and fails closed when missing.
- Public configuration examples use placeholders only.
- Provider methods map account/media metrics toward the existing `SocialMetric` schema.
- Tests use fake HTTP responses only.
- No scraping, browser automation or non-official access is introduced.

Implementation notes:

- `InstagramApiConfig` reads placeholder local variables for token, account ID and pagination.
- `InstagramGraphApiProvider` collects account metadata and paginated media payloads through an injectable HTTP client.
- Provider payloads include existing collection metadata and normalize through the current Instagram schema path.
- Tests use fake HTTP responses and verify sanitized HTTP errors.
- No CLI, Airflow DAG or automatic real Instagram run was added in this task.

### TASK-105 - Instagram local pipeline command

Status: Done

Phase: Second real provider

Goal: make the Instagram provider runnable through an explicit local command.

Acceptance criteria:

- Command fails closed when Instagram credentials are missing.
- Command writes local raw and processed artifacts without committing generated data.
- Command output is compact and does not print tokens or raw payloads.
- Tests cover dry-run or fake-provider execution only.
- Documentation explains local operator steps with placeholders.

Implementation notes:

- `instagram-local-pipeline` runs the Instagram provider only when explicit local credentials exist.
- The command writes raw, processed and run-summary JSON artifacts under ignored local data directories.
- The command prints compact masked output and never prints tokens, account IDs or raw payloads.
- Tests cover fake-provider execution, interval resolution, loader behavior and missing credentials.
- The first Instagram local load target is intentionally JSON-only.

### TASK-107 - Instagram local report artifact

Status: Done

Phase: Second real provider

Goal: generate a dashboard-compatible report JSON from processed Instagram metrics.

Acceptance criteria:

- Report command reads the latest or explicit processed Instagram artifact.
- Report JSON uses the same dashboard contract shape as YouTube reports.
- Source metadata uses placeholder-safe fields and local relative paths only.
- Tests cover totals, top content and empty inputs.
- No real Instagram credentials or raw payloads are printed.

Evidence:

- `instagram-report` can read the latest or explicit processed Instagram artifact.
- Instagram report JSON writes the same dashboard contract sections used by YouTube reports.
- Instagram normalizer now preserves caption, permalink, media image, username and profile image when available.
- `social-dashboard --all-reports` now discovers Instagram report JSON artifacts alongside YouTube report JSON artifacts.
- Tests cover Instagram totals, top content, empty artifacts, CLI output, metadata propagation and dashboard discovery.

### TASK-108 - Multi-provider dashboard smoke

Status: Done

Phase: Consumption layer

Goal: validate a local dashboard run with more than one provider report artifact.

Acceptance criteria:

- A local smoke path can generate or use safe sample YouTube and Instagram report JSON artifacts.
- `social-dashboard --all-reports` renders both providers into the channel-first dashboard contract.
- The smoke path uses placeholders or generated fake data only.
- Documentation records the command sequence without local secrets, real IDs or absolute paths.

Evidence:

- `dashboard-smoke` generates safe sample YouTube and Instagram processed artifacts from committed fixtures.
- The smoke command writes dashboard-compatible YouTube and Instagram report JSON artifacts under an ignored isolated smoke workspace.
- The smoke command builds a static dashboard through all-report discovery from both provider reports.
- Tests cover direct smoke execution, CLI execution and relative output handling.

### TASK-109 - Review and package current task batch

Status: Done

Phase: Governance

Goal: prepare the accumulated dashboard/provider changes for commit and PR review.

Acceptance criteria:

- Local validation results are current.
- Sensitive information scan is clean.
- Gemini review is retried or explicitly recorded as unavailable.
- Commit groups are clear and avoid generated local data.
- PR notes summarize completed tasks and remaining tradeoffs.

Evidence:

- Local validation passed with lint, docs verification, security scan and the full test suite.
- Sensitive information scan found no committed secrets, local paths, raw payloads, expanded DSNs, ports or IPs in versionable files.
- Gemini review was retried and timed out without producing a new review artifact, so it is recorded as unavailable for this batch.
- Generated smoke artifacts remain ignored under local data directories.
- PR #33 is the review target for the current dashboard/provider batch.

### TASK-110 - PR review follow-up and next slice decision

Status: Done

Phase: Governance

Goal: use GitHub Actions and CodeRabbit feedback to decide whether to merge the current batch or fix review findings first.

Acceptance criteria:

- GitHub Actions status is checked after the branch update.
- CodeRabbit review is checked for actionable findings.
- Any necessary fixes are applied before merge.
- If no blockers exist, the PR can be merged and the next implementation slice can be selected.

Evidence:

- PR #33 passed GitHub Actions, secret scan and CodeRabbit.
- A Linux-only smoke test output issue was fixed before merge.
- PR #33 was squash-merged into `master`.
- The next implementation slice was selected to strengthen channel identity grouping in the multi-provider smoke path.

### TASK-111 - Channel identity smoke consolidation

Status: Done

Phase: Consumption layer

Goal: make the safe multi-provider smoke prove that YouTube and Instagram reports can render as sources inside one monitored channel.

Acceptance criteria:

- `dashboard-smoke` creates an ignored local channel identity config using placeholders only.
- The smoke config maps sample YouTube and Instagram fixture reports to one monitored channel.
- The generated dashboard has one monitored channel option instead of one option per provider report.
- Tests verify the generated config and consolidated dashboard output.

Evidence:

- `dashboard-smoke` now writes `data/temp/dashboard-smoke/config/channels.local.json`.
- The smoke dashboard renders `Sample Monitored Channel` as the single channel selector option.
- YouTube and Instagram remain visible as platform sources inside that selected channel.
- Tests cover the smoke config path, generated channel identity and single-option selector.

### TASK-112 - Next implementation slice decision

Status: Done

Phase: Governance

Goal: choose the next small implementation slice after the channel-first dashboard smoke proves provider grouping.

Acceptance criteria:

- The next slice is tied to the channel-first dashboard or real-provider usefulness.
- The scope stays small enough for one focused PR.
- Public documentation continues to avoid secrets, local paths, raw payloads and real identifiers.

Evidence:

- The next slice was selected as global top-content ranking for aggregated channel dashboards.
- The slice stays inside the dashboard consumption layer and uses existing report JSON data.
- No new provider credentials, real identifiers, raw payloads or external services are introduced.

### TASK-113 - Aggregated channel top-content ranking

Status: Done

Phase: Consumption layer

Goal: make consolidated channel dashboards rank top content across providers instead of preserving provider file order.

Acceptance criteria:

- Aggregated channel `top_rows` are sorted by the configured ranking metric.
- The fallback ranking metric is `views`.
- Aggregated channel `top_content` reflects the first sorted top row.
- Tests cover mixed-provider reports where the later provider has the stronger top content.

Evidence:

- Multi-report dashboard aggregation now sorts combined `top_rows` by ranking metric descending.
- Aggregated `top_content` now follows the sorted rows.
- Dashboard tests cover cross-provider top row ordering.

### TASK-114 - Top-content platform metadata

Status: Done

Phase: Consumption layer

Goal: make each aggregated top-content row show which platform produced it.

Acceptance criteria:

- Aggregated top-content rows preserve their provider source.
- Dashboard row metadata shows the provider when available.
- Content IDs remain secondary metadata.
- Tests cover provider metadata in aggregated payloads and rendered HTML.

Evidence:

- Aggregated top rows are now annotated with their report provider.
- Top-content metadata now renders platform and ID together when both are available.
- Dashboard tests cover provider metadata propagation and display.

### TASK-115 - Package three-task dashboard batch

Status: Done

Phase: Governance

Goal: commit and open a PR for TASK-111, TASK-113 and TASK-114 as the current three-task batch.

Acceptance criteria:

- Full local validation passes.
- Sensitive information scan is clean.
- The batch is committed on the current feature branch.
- A PR is opened for GitHub Actions and CodeRabbit review.

Evidence:

- Local validation passed with lint, documentation verification, security scan and the full test suite.
- Sensitive information scan found no committed secrets, local paths, raw payloads, expanded DSNs, ports or IPs in versionable files.
- The local smoke dashboard was regenerated from safe fixtures and shows platform metadata in top-content rows.
- The batch is ready for commit and PR review.

### TASK-116 - PR review for three-task dashboard batch

Status: Done

Phase: Governance

Goal: review GitHub Actions and CodeRabbit feedback for the current dashboard batch.

Acceptance criteria:

- GitHub Actions status is checked after the PR opens.
- CodeRabbit review is checked for actionable findings.
- Any blocker is fixed before merge.
- If checks are green and no blocker exists, the PR can be merged.

Evidence:

- PR #34 passed GitHub Actions, secret scan and CodeRabbit.
- PR #34 was squash-merged into `master`.
- The next three-task batch started from a clean `master`.

### TASK-117 - Platform coverage summary

Status: Done

Phase: Consumption layer

Goal: show how many expected platform sources are available for the selected monitored channel.

Acceptance criteria:

- The dashboard shows platform coverage near the Platform Sources header.
- Full YouTube, TikTok and Instagram data renders as `3/3 available`.
- Partial provider data renders the available count, such as `1/3 available`.
- The value updates when the selected channel changes.
- Tests cover full and partial coverage rendering.

Evidence:

- Dashboard channel models now include `platform_coverage`.
- Platform Sources renders a coverage pill for the active channel.
- The client-side channel switch updates the coverage pill.
- Dashboard tests cover full and partial platform coverage.

### TASK-118 - Platform share metrics

Status: Done

Phase: Consumption layer

Goal: show each available platform source's share of the selected channel totals.

Acceptance criteria:

- Platform cards show view share for each available platform.
- Platform cards show engagement share for each available platform.
- Share values are calculated from consolidated channel totals.
- Zero-total channels render `0.00%` instead of failing.
- Tests cover platform share values in the dashboard payload.

Evidence:

- Dashboard channel models now calculate `views_share` and `engagements_share` for platform sources.
- Platform cards render View share and Engagement share rows.
- Dashboard tests cover expected cross-platform share percentages.

### TASK-119 - Leading platform summary

Status: Done

Phase: Consumption layer

Goal: show which platform leads the selected channel in views and engagements.

Acceptance criteria:

- Dashboard channel models identify the top views source.
- Dashboard channel models identify the top engagement source.
- The summary renders in a compact dashboard panel.
- The value updates when the selected channel changes.
- Tests cover the leader labels for mixed platform data.

Evidence:

- Dashboard channel models now include `top_views_source` and `top_engagement_source`.
- The Data Quality panel shows the leading platform for views and engagements.
- The client-side channel switch updates both values.
- Dashboard tests cover the leading platform labels.

### TASK-120 - Package three-task platform source batch

Status: Done

Phase: Governance

Goal: commit and open a PR for TASK-117, TASK-118 and TASK-119 as the current three-task batch.

Acceptance criteria:

- Full local validation passes.
- Sensitive information scan is clean.
- The batch is committed on the current feature branch.
- A PR is opened for GitHub Actions and CodeRabbit review.

Evidence:

- Local validation passed with lint, documentation verification, security scan and the full test suite.
- Sensitive information scan found no committed secrets, local paths, raw payloads, expanded DSNs, ports or IPs in versionable files.
- The local smoke dashboard was regenerated from safe fixtures and shows provider coverage, share metrics and leading platform summaries.
- The batch is ready for commit and PR review.

### TASK-121 - PR review for platform source batch

Status: Done

Phase: Governance

Goal: review GitHub Actions and CodeRabbit feedback for the current platform source batch.

Acceptance criteria:

- GitHub Actions status is checked after the PR opens.
- CodeRabbit review is checked for actionable findings.
- Any blocker is fixed before merge.
- If checks are green and no blocker exists, the PR can be merged.

Evidence:

- PR #35 passed GitHub Actions, secret scan and CodeRabbit.
- PR #35 was squash-merged into `master`.
- The next three-task batch started from a clean `master`.

### TASK-122 - Platform top-content summary

Status: Done

Phase: Consumption layer

Goal: show the leading content item inside each available platform source card.

Acceptance criteria:

- Platform cards show the top content title for that provider when available.
- Missing platform top content renders as unavailable.
- The value is derived from the selected channel top rows.
- The value updates when the selected channel changes.
- Tests cover provider-specific top content in platform cards.

Evidence:

- Platform source models now include `top_content` derived from channel top rows.
- Platform cards render a Top content row.
- Dashboard tests cover provider-specific top content labels.

### TASK-123 - Platform top-content date

Status: Done

Phase: Consumption layer

Goal: show the publication date for each platform's leading content item.

Acceptance criteria:

- Platform cards show the top content publication date when available.
- Missing dates render as unavailable.
- The value is derived from the selected channel top rows.
- The value updates when the selected channel changes.
- Tests cover provider-specific top content dates.

Evidence:

- Platform source models now include `top_content_published_at`.
- Platform cards render a Top content date row.
- Dashboard tests cover provider-specific top content date labels.

### TASK-124 - Platform top-content links

Status: Done

Phase: Consumption layer

Goal: make provider-specific top content clickable when a content URL is available.

Acceptance criteria:

- Platform source models preserve the top content URL when available.
- Platform cards link the top content title when a URL exists.
- Missing URLs render as plain text without failing.
- The link uses safe external-link attributes.
- Tests cover linked provider-specific top content.

Evidence:

- Platform source models now include `top_content_url`.
- Platform cards render top content as an external link when a URL exists.
- Dashboard tests cover provider-specific top content URLs and rendered links.

### TASK-125 - Package three-task platform top-content batch

Status: Done

Phase: Governance

Goal: commit and open a PR for TASK-122, TASK-123 and TASK-124 as the current three-task batch.

Acceptance criteria:

- Full local validation passes.
- Sensitive information scan is clean.
- The batch is committed on the current feature branch.
- A PR is opened for GitHub Actions and CodeRabbit review.

Evidence:

- Local validation passed with lint, documentation verification, security scan and the full test suite.
- Sensitive information scan found no new secrets, local paths, raw payloads, expanded DSNs, ports or IPs in the files changed by this batch.
- The local smoke dashboard was regenerated from safe fixtures and shows provider-specific top-content titles, dates and links.
- The batch is ready for commit and PR review.

### TASK-126 - PR review for platform top-content batch

Status: Done

Phase: Governance

Goal: review GitHub Actions and CodeRabbit feedback for the current platform top-content batch.

Acceptance criteria:

- GitHub Actions status is checked after the PR opens.
- CodeRabbit review is checked for actionable findings.
- Any blocker is fixed before merge.
- If checks are green and no blocker exists, the PR can be merged.

Evidence:

- PR #36 passed GitHub Actions, secret scan and CodeRabbit.
- PR #36 was squash-merged into `master`.
- The next visual dashboard batch started from a clean `master`.

### TASK-127 - Platform top-content thumbnails

Status: Done

Phase: Consumption layer

Goal: show a visual thumbnail for each provider's leading content item inside platform source cards.

Acceptance criteria:

- Platform source models preserve the top content thumbnail or image URL when available.
- Platform cards render the thumbnail when a provider-specific top content image exists.
- Missing thumbnails keep the existing text-only card behavior.
- Existing top-content links and dates remain unchanged.
- Tests cover thumbnail propagation and rendered HTML.

Evidence:

- Platform source models now include `top_content_thumbnail_url`.
- Platform cards render a compact preview image for provider-specific top content when available.
- Dashboard tests cover thumbnail propagation from `thumbnail_url` and `image_url`.
- Focused dashboard tests and lint passed.

### TASK-128 - Platform top-content metric summary

Status: Done

Phase: Consumption layer

Goal: show the leading content item's main metric inside each platform source card.

Acceptance criteria:

- Platform source models preserve the top content views when available.
- Platform cards show a compact top-content views row.
- Missing metric values render as unavailable.
- The value updates when the selected channel changes.
- Tests cover provider-specific top-content metrics.

Evidence:

- Platform source models now include `top_content_views`.
- Platform cards render a Top content views row for each provider when available.
- Missing views render as unavailable through the existing unavailable card behavior.
- Dashboard tests cover provider-specific top-content metric propagation and rendering.
- Focused dashboard tests and lint passed.

### TASK-129 - Platform top-content type label

Status: Done

Phase: Consumption layer

Goal: show the leading content item's human content type inside each platform source card.

Acceptance criteria:

- Platform source models preserve the top content type when available.
- Platform cards show a compact top-content type row.
- Missing content types render as unavailable.
- Existing top-content title, thumbnail, link, views and date behavior remains unchanged.
- Tests cover provider-specific top-content type labels.

Evidence:

- Platform source models now include `top_content_type`.
- Platform cards render a Top content type row when the provider row includes `content_type` or `media_type`.
- Missing content types render as unavailable through the existing unavailable behavior.
- Dashboard tests cover provider-specific type labels for short, video and reel examples.
- Focused dashboard tests and lint passed.

### TASK-130 - Package three-task visual platform content batch

Status: Done

Phase: Governance

Goal: commit and open a PR for TASK-127, TASK-128 and TASK-129 as the current three-task batch.

Acceptance criteria:

- Full local validation passes.
- Sensitive information scan is clean for changed files.
- The batch is committed on the current feature branch.
- A PR is opened for GitHub Actions and CodeRabbit review.

Evidence:

- Local validation passed with lint, documentation verification, security scan and the full test suite.
- Sensitive information scan found no new secrets, local paths, raw payloads, expanded DSNs, ports or IPs in the files changed by this batch.
- Platform cards now render provider-specific thumbnails, view counts and type labels for leading content.
- The batch is ready for commit and PR review.

### TASK-131 - PR review for visual platform content batch

Status: Done

Phase: Governance

Goal: review GitHub Actions and CodeRabbit feedback for the current visual platform content batch.

Acceptance criteria:

- GitHub Actions status is checked after the PR opens.
- CodeRabbit review is checked for actionable findings.
- Any blocker is fixed before merge.
- If checks are green and no blocker exists, the PR can be merged.

Evidence:

- PR #37 passed GitHub Actions, secret scan and CodeRabbit.
- PR #37 was squash-merged into `master`.
- The next implementation cycle started from the merged visual platform content batch.

### TASK-132 - Next dashboard slice decision

Status: Done

Phase: Governance

Goal: choose the next small dashboard implementation slice after improving platform top-content cards.

Acceptance criteria:

- The next task improves channel readability or dashboard usefulness.
- The scope is small enough to fit the three-task batch rule.
- Public documentation remains free of secrets, local paths, raw payloads, expanded DSNs, ports and IPs.
- The proposed change is explained before implementation.

Evidence:

- The next slice was selected as a top-content table readability improvement.
- The slice stays inside the static dashboard and does not add providers, API calls, servers or credentials.
- The first implementation task adds visual ranking labels to top-content rows.
- The change keeps technical IDs secondary and improves dashboard scanning.

### TASK-133 - Top-content visual rank labels

Status: Done

Phase: Consumption layer

Goal: make top-content rows easier to scan by showing a clear visual rank label for each row.

Acceptance criteria:

- Top-content rows include rank labels such as `#1`, `#2` and `#3`.
- The rank labels render in the static HTML table.
- Empty top-content state remains unchanged.
- Existing content title, thumbnail, provider, ID, publish date and link behavior remains unchanged.
- Tests cover rendered rank labels.

Evidence:

- Top-content table rows now render visual rank badges such as `#1`.
- Client-side channel switching renders rank badges for the selected channel rows.
- Empty table state keeps a valid colspan after the new rank column.
- Dashboard tests cover the rank header, rank badge and empty-state colspan.
- Focused dashboard tests and lint passed.

### TASK-134 - Top-content winner row highlight

Status: Done

Phase: Consumption layer

Goal: make the leading top-content row visually stand out in the dashboard table.

Acceptance criteria:

- The first top-content row has a distinct winner class.
- The winner class renders in static HTML and client-side channel switching.
- Empty top-content state remains unchanged.
- Existing rank, content title, thumbnail, provider, ID, publish date and link behavior remains unchanged.
- Tests cover the winner row class.

Evidence:

- The first top-content row now renders with a `winner-row` class.
- Client-side channel switching applies the same winner class to the first visible row.
- Empty table state remains unchanged.
- Dashboard tests cover the rendered winner row class.
- Focused dashboard tests and lint passed.

### TASK-135 - Top-content table count summary

Status: Done

Phase: Consumption layer

Goal: make the top-content table state clearer by showing how many ranked items are displayed.

Acceptance criteria:

- The Top Content section shows a compact ranked-item count.
- Populated tables show the number of visible ranked rows.
- Empty tables show `0 ranked items`.
- The value updates when the selected channel changes.
- Tests cover populated and empty count summaries.

Evidence:

- The Top Content section now renders a ranked-item count pill.
- Client-side channel switching updates the count label.
- Empty tables show `0 ranked items`.
- Dashboard tests cover populated and empty count summaries.
- Focused dashboard tests and lint passed.

### TASK-136 - Package three-task top-content table readability batch

Status: Done

Phase: Governance

Goal: commit and open a PR for TASK-133, TASK-134 and TASK-135 as the current three-task batch.

Acceptance criteria:

- Full local validation passes.
- Sensitive information scan is clean for changed files.
- The batch is committed on the current feature branch.
- A PR is opened for GitHub Actions and CodeRabbit review.

Evidence:

- Local validation passed with lint, documentation verification, security scan and the full test suite.
- Sensitive information scan found no new secrets, local paths, raw payloads, expanded DSNs, ports or IPs in the files changed by this batch.
- Top-content rows now show rank badges, highlight the first row and expose a ranked-item count.
- The batch is ready for commit and PR review.

### TASK-137 - PR review for top-content table readability batch

Status: Done

Phase: Governance

Goal: review GitHub Actions and CodeRabbit feedback for the current top-content table readability batch.

Acceptance criteria:

- GitHub Actions status is checked after the PR opens.
- CodeRabbit review is checked for actionable findings.
- Any blocker is fixed before merge.
- If checks are green and no blocker exists, the PR can be merged.

Evidence:

- PR #38 passed GitHub Actions, secret scan and CodeRabbit.
- PR #38 was squash-merged into `master`.
- The next implementation cycle started from the merged top-content table readability batch.

### TASK-138 - Local dashboard serve command

Status: Done

Phase: Consumption layer

Goal: make the static dashboard easier to open locally through one command.

Acceptance criteria:

- A local command can generate the safe dashboard smoke artifact and serve it on localhost.
- The command prints the dashboard URL.
- The command can serve an existing dashboard without regenerating smoke data.
- Tests avoid opening a real blocking server.
- Public docs avoid real local paths, secrets, raw payloads, expanded DSNs, ports beyond the documented local default and IPs beyond localhost binding.

Evidence:

- `serve-dashboard` is now exposed as a console script.
- The command generates the safe smoke dashboard by default and prints a localhost URL.
- `--no-smoke` allows serving an existing dashboard output.
- Tests cover URL generation, parser behavior and non-blocking main execution.
- Focused tests and lint passed.

### TASK-139 - Document local dashboard serving

Status: Done

Phase: Consumption layer

Goal: document the safest local steps to open the dashboard in a browser.

Acceptance criteria:

- README mentions the local serve command.
- Bootstrap docs include the command sequence with placeholders only.
- Documentation explains the static dashboard output path without absolute local paths.
- Documentation does not introduce secrets, raw payloads or environment-specific values.

Evidence:

- README now mentions `serve-dashboard` and the local smoke dashboard URL.
- Bootstrap docs now show the local command and the static dashboard path.
- Docs explain `--no-smoke` for serving an existing generated dashboard.
- Documentation uses only safe local placeholders and localhost binding.

### TASK-140 - Dashboard server port error message

Status: Done

Phase: Consumption layer

Goal: make local dashboard serving fail with a clearer message when the selected port is unavailable.

Acceptance criteria:

- The serve command reports when the local port cannot be bound.
- The error message includes the requested host and port.
- The command exits non-zero on bind failure.
- Tests cover the failure path without opening a real server.

Evidence:

- `serve-dashboard` now reports the requested host and port when binding fails.
- Bind failures return exit code 1.
- Tests cover the failure path through a mocked server call.
- Focused tests and lint passed.

### TASK-141 - Package three-task local dashboard serving batch

Status: Done

Phase: Governance

Goal: commit and open a PR for TASK-138, TASK-139 and TASK-140 as the current three-task batch.

Acceptance criteria:

- Full local validation passes.
- Sensitive information scan is clean for changed files.
- The batch is committed on the current feature branch.
- A PR is opened for GitHub Actions and CodeRabbit review.

Evidence:

- Local validation passed with lint, documentation verification, security scan and the full test suite.
- Sensitive information scan found no real secrets, local paths, raw payloads or expanded DSNs in the files changed by this batch.
- The only matched credential-like value was an existing documented placeholder, not a real secret.
- The batch is ready for commit and PR review.

### TASK-142 - PR review for local dashboard serving batch

Status: Done

Phase: Governance

Goal: review GitHub Actions and CodeRabbit feedback for the current local dashboard serving batch.

Acceptance criteria:

- GitHub Actions status is checked after the PR opens.
- CodeRabbit review is checked for actionable findings.
- Any blocker is fixed before merge.
- If checks are green and no blocker exists, the PR can be merged.

Evidence:

- PR #39 passed GitHub Actions, secret scan and CodeRabbit.
- PR #39 was squash-merged into `master`.
- The next implementation cycle started from the merged local dashboard serving batch.

### TASK-143 - Next dashboard usability slice decision

Status: Done

Phase: Governance

Goal: choose the next small dashboard usability improvement after making local serving easier.

Acceptance criteria:

- The next task improves the user's ability to inspect or operate the dashboard locally.
- The scope is small enough to fit the three-task batch rule.
- Public documentation remains free of real secrets, local paths, raw payloads and expanded DSNs.
- The proposed change is explained before implementation.

Evidence:

- The next slice was redirected to the user's requested visual dashboard improvements.
- The batch size rule changed from three small tasks to five small tasks before commit and PR.
- The next batch prioritizes a polished dark analytics panel, stronger channel identity, graphic metric cards, production visual polish and card-based top content.
- Provider/API expansion remains deferred while the dashboard presentation catches up to the requested design direction.

### TASK-144 - Dashboard visual direction refresh

Status: Done

Phase: Consumption layer

Goal: make the dashboard shell visually closer to a polished dark analytics panel with teal and blue accents.

Acceptance criteria:

- The dashboard uses a stronger dark panel composition.
- The palette emphasizes teal, cyan, blue and green highlights without becoming a single-hue page.
- Existing dashboard data contract remains unchanged.
- Text remains readable on desktop and mobile.
- Tests cover the refreshed shell markers.

Evidence:

- The dashboard shell now uses a stronger dark panel composition with teal, blue and green accents.
- The refreshed shell exposes a visual dashboard marker for tests.
- Existing dashboard data contract remains unchanged.
- Focused dashboard tests and lint passed.

### TASK-145 - Channel hero identity panel

Status: Done

Phase: Consumption layer

Goal: make the selected channel identity more prominent at the top of the dashboard.

Acceptance criteria:

- The selected channel image or fallback appears as a larger visual anchor.
- The selected channel name is the strongest first-viewport label.
- Provider/source summary remains visible but secondary.
- The channel selector still chooses monitored channels, not platforms.
- Tests cover the hero identity markup.

Evidence:

- The dashboard now opens with a channel hero panel anchored by the selected channel image or fallback.
- The selected channel name is the strongest first-viewport label.
- The channel selector remains channel-first and not platform-first.
- Focused dashboard tests and lint passed.

### TASK-146 - Visual metric cards

Status: Done

Phase: Consumption layer

Goal: make the main metrics feel more like dashboard widgets and less like plain text cards.

Acceptance criteria:

- Production, views, engagements and performance cards get stronger visual treatments.
- Cards include compact graphic accents using existing values.
- Existing numeric values remain unchanged.
- Tests cover the metric card shell.

Evidence:

- Main metric cards now render as visual dashboard widgets with accent bars and compact spark graphics.
- Existing metric values and selectors remain unchanged.
- Focused dashboard tests and lint passed.

### TASK-147 - Production heatmap polish

Status: Done

Phase: Consumption layer

Goal: make the production calendar visually closer to a contribution-style activity chart.

Acceptance criteria:

- The production heatmap has clearer month labels, legend and activity levels.
- The visual treatment matches the dashboard palette.
- Empty production states remain clear.
- Existing production counts remain unchanged.
- Tests cover the production panel shell.

Evidence:

- The production panel now has a stronger activity-chart container and palette treatment.
- Existing production counts, months, days and empty states remain unchanged.
- Focused dashboard tests and lint passed.

### TASK-148 - Top-content card gallery

Status: Done

Phase: Consumption layer

Goal: replace the table-first top-content presentation with a more visual card gallery while preserving the table data contract.

Acceptance criteria:

- Top content renders as visual cards with thumbnail/fallback, rank, title, platform, date and views.
- The current table can remain as supporting detail or be visually secondary.
- Technical IDs remain secondary metadata.
- Empty top content shows a clear card-gallery empty state.
- Tests cover the rendered gallery.

Evidence:

- Top content now renders as a visual card gallery before the supporting table.
- Cards show thumbnail or fallback, rank, title, platform/date context and views.
- The gallery updates when the selected channel changes.
- Empty top content shows a clear gallery empty state.
- Focused dashboard tests and lint passed.

### TASK-149 - Package five-task visual dashboard batch

Status: Done

Phase: Governance

Goal: commit and open a PR for TASK-144 through TASK-148 as the current five-task visual dashboard batch.

Acceptance criteria:

- Full local validation passes.
- Sensitive information scan is clean for changed files.
- The dashboard smoke output is regenerated for local visual QA.
- The batch is committed on the current feature branch.
- A PR is opened for GitHub Actions and CodeRabbit review.

Evidence:

- Local validation passed with lint, documentation verification, security scan and the full test suite.
- Sensitive information scan found no new secrets, local paths, raw payloads, expanded DSNs or ports in the files changed by this batch.
- Dashboard smoke output was regenerated from safe fixtures.
- Browser QA confirmed the channel hero, metric cards, top-content gallery, production heatmap and page width.
- The batch is ready for commit and PR review.

### TASK-150 - PR review for visual dashboard batch

Status: Done

Phase: Governance

Goal: review GitHub Actions and CodeRabbit feedback for the current visual dashboard batch.

Acceptance criteria:

- GitHub Actions status is checked after the PR opens.
- CodeRabbit review is checked for actionable findings.
- Any blocker is fixed before merge.
- If checks are green and no blocker exists, the PR can be merged.

Evidence:

- PR #40 passed GitHub Actions, secret scan and CodeRabbit.
- PR #40 was squash-merged into `master`.
- The next visual dashboard cycle started from the merged shell, hero, metric card, production and top-content gallery improvements.

### TASK-151 - Next visual chart slice decision

Status: Done

Phase: Governance

Goal: choose the next dashboard visual slice after the first visual refresh batch.

Acceptance criteria:

- The next slice directly improves chart readability and visual impact.
- The scope fits the five-task batch rule.
- Existing dashboard data contract remains unchanged.
- The proposed direction is explained before implementation.

Evidence:

- The next slice is platform comparison charts inside the selected channel view.
- The slice targets visual comparison of YouTube, TikTok and Instagram by views, engagement and production volume.
- The task stays in the static dashboard layer and does not add providers, API calls or credentials.

### TASK-152 - Platform comparison chart panel

Status: Done

Phase: Consumption layer

Goal: add a visual chart panel comparing available platform sources inside the selected channel.

Acceptance criteria:

- The selected channel shows a platform comparison chart panel.
- The chart compares YouTube, TikTok and Instagram when available.
- Missing platform data renders as unavailable or empty chart state.
- The chart updates when the selected channel changes.
- Tests cover the chart panel shell.

Evidence:

- The dashboard now renders a `data-platform-comparison` panel under Platform Sources.
- The panel contains chart cards for views, engagements and productions.
- The panel updates when the selected channel changes.
- Focused dashboard tests and lint passed.

### TASK-153 - Platform views bar chart

Status: Done

Phase: Consumption layer

Goal: make platform view totals easy to compare with a horizontal bar chart.

Acceptance criteria:

- Platform views render as bars using the existing platform source metrics.
- Bars use the dashboard teal, blue and green palette.
- Zero-view or missing values do not break rendering.
- The chart updates when the selected channel changes.
- Tests cover rendered platform view bars.

Evidence:

- Platform view totals now render as horizontal bars in provider order.
- Missing providers render as unavailable without breaking the chart.
- Focused dashboard tests and lint passed.

### TASK-154 - Platform engagement bar chart

Status: Done

Phase: Consumption layer

Goal: make platform engagement totals easy to compare with a second visual bar group.

Acceptance criteria:

- Platform engagements render as bars using the existing platform source metrics.
- Bars align with the same provider order as the platform cards.
- Zero-engagement or missing values do not break rendering.
- The chart updates when the selected channel changes.
- Tests cover rendered platform engagement bars.

Evidence:

- Platform engagement totals now render as a second horizontal bar chart.
- The chart uses the same provider order as the platform cards.
- Focused dashboard tests and lint passed.

### TASK-155 - Platform production mini chart

Status: Done

Phase: Consumption layer

Goal: show production count by platform in a compact visual chart.

Acceptance criteria:

- Platform production counts render as compact visual bars or chips.
- Missing platform data remains clearly unavailable.
- The chart uses the same provider order as other platform sections.
- The chart updates when the selected channel changes.
- Tests cover rendered production comparison.

Evidence:

- Platform production counts now render as a compact comparison chart.
- Missing platform data remains explicitly unavailable.
- Focused dashboard tests and lint passed.

### TASK-156 - Platform chart empty state

Status: Done

Phase: Consumption layer

Goal: make platform comparison charts clear when no platform metrics are available.

Acceptance criteria:

- Empty platform comparison charts show a clear empty-state message.
- Partial platform data still renders available providers.
- Empty state does not remove the platform cards.
- Tests cover empty and partial platform comparison states.

Evidence:

- Empty platform comparison charts render a clear empty-state message.
- Partial platform data keeps available providers while missing providers render unavailable.
- Existing platform cards remain unchanged.
- Focused dashboard tests and lint passed.

### TASK-157 - Package five-task platform comparison chart batch

Status: Done

Phase: Governance

Goal: commit and open a PR for TASK-152 through TASK-156 as the current five-task platform comparison chart batch.

Acceptance criteria:

- Full local validation passes.
- Sensitive information scan is clean for changed files.
- Dashboard smoke output is regenerated for local visual QA.
- The batch is committed on the current feature branch.
- A PR is opened for GitHub Actions and CodeRabbit review.

Evidence:

- Full local validation passed with ruff, unit tests, documentation verification and Bandit.
- Sensitive-pattern scan on changed files returned no findings.
- Dashboard smoke output was regenerated.
- Browser QA confirmed the platform comparison panel, three chart cards, rendered chart fills, no horizontal overflow and no console errors.

### TASK-158 - PR review for platform comparison chart batch

Status: Done

Phase: Governance

Goal: review GitHub Actions and CodeRabbit feedback for the platform comparison chart batch.

Acceptance criteria:

- The PR is open with the five-task platform comparison chart batch.
- GitHub Actions checks are reviewed.
- CodeRabbit feedback is reviewed.
- Any blocker is fixed before merge.
- If checks are green and no blocker exists, the PR can be merged.

Evidence:

- PR #41 passed GitHub Actions quality checks and secret scan.
- CodeRabbit returned a passing skipped review status with no blocking feedback.
- PR #41 was squash-merged into `master`.

### TASK-159 - Channel identity polish batch decision

Status: Done

Phase: Governance

Goal: choose the next simplified dashboard polish batch after the platform comparison PR.

Acceptance criteria:

- The next batch directly addresses channel-first dashboard clarity.
- The scope fits the five-task batch rule.
- The batch does not add new providers, API calls or credentials.
- Proposed changes are explained before implementation.

Evidence:

- The next batch focuses on making the selected channel obvious with human name, avatar and source coverage.
- The next batch also targets reducing visible technical IDs where human titles or names are available.
- The scope stays inside the static dashboard layer.

### TASK-160 - Selected channel visual preview

Status: Done

Phase: Consumption layer

Goal: make the selected monitored channel obvious beside the channel selector.

Acceptance criteria:

- The channel selector area shows the selected channel avatar or fallback.
- The selector area shows the human channel name.
- The selector area shows a source summary instead of looking like a platform selector.
- The preview updates when a different channel is selected.
- Tests cover the rendered preview and source summary.

Evidence:

- The dashboard now renders a `data-channel-preview` block beside the channel selector.
- The preview shows channel avatar/fallback, human channel name and source coverage.
- The hero subtitle now uses the same source summary for consolidated channel views.
- Focused dashboard lint and tests passed.

### TASK-161 - Reduce technical IDs in visible dashboard metadata

Status: Done

Phase: Consumption layer

Goal: reduce visible technical IDs in dashboard metadata when human-readable content labels are available.

Acceptance criteria:

- Top-content metadata keeps provider context without making content IDs primary.
- Content IDs remain available only as secondary fallback metadata.
- Existing title, thumbnail, link and date display behavior remains unchanged.
- Tests cover rows with and without human-readable titles.

Evidence:

- Top-content row metadata now keeps provider context without adding `ID: ...` beside human titles.
- Dynamic channel switching uses the same reduced visible metadata rule.
- Focused dashboard lint and tests passed.

### TASK-162 - Visual channel option cards

Status: Done

Phase: Consumption layer

Goal: let users choose monitored channels through visual channel cards instead of relying only on the native select.

Acceptance criteria:

- The dashboard renders visual channel option cards with avatar or fallback, human name and source summary.
- Selecting a card updates the same selected channel view as the native select.
- The active channel card is visually distinguishable.
- The native select remains available for accessibility and simple keyboard use.
- Tests cover the rendered channel option card shell.

Evidence:

- The dashboard now renders `data-channel-options` visual cards with avatar/fallback, human name and source summary.
- The first channel card renders active by default.
- Clicking a visual card updates the same selected channel view as the native select.
- Focused dashboard lint and tests passed.

### TASK-163 - Package channel identity polish batch

Status: Done

Phase: Governance

Goal: commit and open a PR for TASK-159 through TASK-162 as the current channel identity polish batch.

Acceptance criteria:

- Full local validation passes.
- Sensitive information scan is clean for changed files.
- Dashboard smoke output is regenerated for local visual QA.
- Browser QA confirms channel preview and visual channel option cards.
- The batch is committed and opened as a PR for GitHub Actions and CodeRabbit.

Evidence:

- Full validation passed with ruff, unit tests, documentation verification and Bandit.
- Sensitive-pattern scan on changed files returned no findings.
- Dashboard smoke output was regenerated.
- Browser QA confirmed the channel preview, active visual channel card, reduced visible ID labels, no horizontal overflow and no console errors.

### TASK-164 - PR review for channel identity polish batch

Status: Done

Phase: Governance

Goal: review GitHub Actions and CodeRabbit feedback for the channel identity polish batch.

Acceptance criteria:

- The PR is open with the channel identity polish batch.
- GitHub Actions checks are reviewed.
- CodeRabbit feedback is reviewed.
- Any blocker is fixed before merge.
- If checks are green and no blocker exists, the PR can be merged.

Evidence:

- PR #42 passed GitHub Actions quality checks and secret scan.
- CodeRabbit returned a passing skipped review status with no blocking feedback.
- PR #42 was squash-merged into `master`.

### TASK-165 - Next dashboard polish decision

Status: Done

Phase: Governance

Goal: choose the next dashboard polish slice after the channel identity batch.

Acceptance criteria:

- The next slice is explained before implementation.
- The scope fits the five-task batch rule.
- The change improves dashboard clarity for channel analytics.
- The change does not add new providers, credentials or external API calls.

Evidence:

- The next slice is dashboard metadata readability.
- The slice starts by replacing technical artifact paths with safe report filenames.
- The slice continues with user-facing data-quality labels.

### TASK-166 - Safe report file metadata label

Status: Done

Phase: Consumption layer

Goal: avoid exposing technical artifact paths in the visible dashboard metadata.

Acceptance criteria:

- The report metadata section shows a user-facing file label.
- Full artifact paths are reduced to safe filenames in the visible UI.
- Top-level artifact fallback uses the same safe filename rule.
- Existing dashboard data binding remains compatible.
- Tests cover source-level and top-level artifact values.

Evidence:

- The dashboard metadata label now reads `Report file`.
- Source and top-level artifact values are rendered as safe filenames.
- Focused dashboard lint and tests passed.

### TASK-167 - Human-readable data quality labels

Status: Done

Phase: Consumption layer

Goal: make the Data Quality section read like dashboard context instead of internal pipeline flags.

Acceptance criteria:

- Data Quality labels use user-facing wording.
- The section keeps the same underlying values and bindings.
- Existing tests are updated for the new labels.
- No new provider, API or credential behavior is introduced.

Evidence:

- Data Quality now shows `Engagement data`, `Top content`, `Views leader` and `Engagement leader`.
- Underlying data bindings and values remain unchanged.
- Focused dashboard lint and tests passed.

### TASK-168 - Human-readable report context labels

Status: Done

Phase: Consumption layer

Goal: make the report metadata section read as user-facing report context.

Acceptance criteria:

- The report metadata section title is user-facing.
- Schema and ranking labels are clearer to non-technical dashboard users.
- The safe report filename behavior remains unchanged.
- Tests cover the new labels.

Evidence:

- The section title now reads `Report Context`.
- Report labels now read `Report schema`, `Ranking by`, `Top items limit` and `Report file`.
- Focused dashboard lint and tests passed.

### TASK-169 - Human-readable data quality values

Status: Done

Phase: Consumption layer

Goal: make data-quality values read as user-facing status text instead of internal flags.

Acceptance criteria:

- Quality status values are mapped to readable labels.
- Engagement availability values are mapped to readable labels.
- Existing dashboard bindings remain unchanged.
- Tests cover the readable values.

Evidence:

- Quality status values now render as readable labels such as `Ready`, `No records` and `Unknown`.
- Engagement availability now renders as `Available` or `Missing`.
- Focused dashboard lint and tests passed.

### TASK-170 - Package metadata readability polish batch

Status: Done

Phase: Governance

Goal: commit and open a PR for TASK-165 through TASK-169 as the metadata readability polish batch.

Acceptance criteria:

- Full local validation passes.
- Sensitive information scan is clean for changed files.
- Dashboard smoke output is regenerated for local visual QA.
- Browser QA confirms readable report context and data-quality labels.
- The batch is committed and opened as a PR for GitHub Actions and CodeRabbit.

Evidence:

- Full validation passed with ruff, unit tests, documentation verification and Bandit.
- Sensitive-pattern scan on changed files returned no findings.
- Dashboard smoke output was regenerated.
- Browser QA confirmed readable report context labels, readable data-quality values, no artifact path exposure, no horizontal overflow and no console errors.

### TASK-171 - PR review for metadata readability polish batch

Status: Done

Phase: Governance

Goal: review GitHub Actions and CodeRabbit feedback for the metadata readability polish batch.

Acceptance criteria:

- The PR is open with the metadata readability polish batch.
- GitHub Actions checks are reviewed.
- CodeRabbit feedback is reviewed.
- Any blocker is fixed before merge.
- If checks are green and no blocker exists, the PR can be merged.

Evidence:

- PR #43 passed GitHub Actions quality checks and secret scan.
- CodeRabbit returned a passing skipped review status with no blocking feedback.
- PR #43 was squash-merged into `master`.

### TASK-172 - Channel insights polish decision

Status: Done

Phase: Governance

Goal: choose the next dashboard polish slice after the metadata readability batch.

Acceptance criteria:

- The next slice is explained before implementation.
- The scope fits the five-task batch rule.
- The change improves dashboard clarity for channel analytics.
- The change does not add new providers, credentials or external API calls.

Evidence:

- The next slice is a Channel Insights panel.
- The panel will summarize top content, views leader, engagement leader and production activity.
- The slice uses only existing dashboard fields.

### TASK-173 - Channel insights summary panel

Status: Done

Phase: Consumption layer

Goal: add a short channel insights panel that answers the selected channel's most important questions quickly.

Acceptance criteria:

- The dashboard renders a Channel Insights panel near the top of the page.
- The panel shows top content, views leader, engagement leader and publishing activity.
- The panel updates when the selected channel changes.
- The panel uses existing dashboard fields only.
- Tests cover the rendered panel and data bindings.

Evidence:

- The dashboard now renders `data-channel-insights` near the top of the page.
- The panel shows top content, views leader, engagement leader and publishing activity.
- The panel updates through the existing channel switching flow.
- Focused dashboard lint and tests passed.

### TASK-174 - Channel insights empty states

Status: Done

Phase: Consumption layer

Goal: make Channel Insights read naturally when content or platform leader data is unavailable.

Acceptance criteria:

- Missing top-content insight text uses a user-facing empty state.
- Missing platform leader insight text uses a user-facing empty state.
- Existing Data Quality values remain unchanged.
- Tests cover unavailable insight states.

Evidence:

- Channel Insights now shows `No top content yet`, `No views leader yet` and `No engagement leader yet` where appropriate.
- Data Quality values remain unchanged.
- Focused dashboard lint and tests passed.

### TASK-175 - Channel insights visual polish

Status: Done

Phase: Consumption layer

Goal: make Channel Insights more visually scannable while keeping the panel compact.

Acceptance criteria:

- Insight cards have stronger visual hierarchy than ordinary metadata items.
- The layout remains responsive across existing breakpoints.
- Text remains inside its card for long values.
- Tests or browser QA cover the rendered panel.

Evidence:

- Channel Insights cards now have compact markers and per-insight accent variants.
- Existing responsive breakpoints remain unchanged.
- Focused dashboard lint and tests passed.

### TASK-176 - Channel insights accessible labels

Status: Done

Phase: Consumption layer

Goal: keep Channel Insights markers accessible and understandable without relying only on single-letter visual markers.

Acceptance criteria:

- Visual markers are hidden from assistive text when they are decorative.
- Insight labels remain readable as text.
- Tests cover the accessible marker treatment.

Evidence:

- Channel Insights markers now render with `aria-hidden="true"`.
- Insight labels remain visible text beside the decorative markers.
- Focused dashboard lint and tests passed.

### TASK-177 - Package channel insights polish batch

Status: Done

Phase: Governance

Goal: commit and open a PR for TASK-172 through TASK-176 as the Channel Insights polish batch.

Acceptance criteria:

- Full local validation passes.
- Sensitive information scan is clean for changed files.
- Dashboard smoke output is regenerated for local visual QA.
- Browser QA confirms Channel Insights panel, visual cards, readable empty states and no layout overflow.
- The batch is committed and opened as a PR for GitHub Actions and CodeRabbit.

Evidence:

- Full validation passed with ruff, unit tests, documentation verification and Bandit.
- Sensitive-pattern scan on changed files returned no findings.
- Dashboard smoke output was regenerated.
- Browser QA confirmed the Channel Insights panel, four visual cards, decorative markers, no horizontal overflow and no console errors.

### TASK-178 - PR review for channel insights polish batch

Status: Done

Phase: Governance

Goal: review GitHub Actions and CodeRabbit feedback for the Channel Insights polish batch.

Acceptance criteria:

- The PR is open with the Channel Insights polish batch.
- GitHub Actions checks are reviewed.
- CodeRabbit feedback is reviewed.
- Any blocker is fixed before merge.
- If checks are green and no blocker exists, the PR can be merged.

Evidence:

- PR #44 passed GitHub Actions quality checks and secret scan.
- CodeRabbit returned a passing skipped review status with no blocking feedback.
- PR #44 was squash-merged into `master`.

### TASK-179 - Publishing cadence polish decision

Status: Done

Phase: Governance

Goal: choose the next dashboard polish slice after the Channel Insights batch.

Acceptance criteria:

- The next slice is explained before implementation.
- The scope fits the five-task batch rule.
- The change improves dashboard clarity for channel analytics.
- The change does not add new providers, credentials or external API calls.

Evidence:

- The next slice is publishing cadence summaries.
- The slice uses existing production activity data.
- The slice stays inside the static dashboard layer.

### TASK-180 - Publishing cadence summary cards

Status: Done

Phase: Consumption layer

Goal: add compact publishing cadence summary cards near the Production Calendar.

Acceptance criteria:

- The dashboard shows a compact cadence summary near the production calendar.
- The summary includes total productions, active publishing days and average production per active day.
- The summary updates when the selected channel changes.
- The summary uses existing production activity data only.
- Tests cover the rendered cadence values.

Evidence:

- Production Calendar now renders `data-cadence-summary`.
- Cadence cards show total productions, active publishing days and average productions per active day.
- Cadence values update through the existing channel switching flow.
- Focused dashboard lint and tests passed.

### TASK-181 - Publishing cadence empty state labels

Status: Done

Phase: Consumption layer

Goal: make publishing cadence cards read naturally when publication dates are unavailable.

Acceptance criteria:

- Empty cadence values use user-facing labels instead of only zeros where useful.
- The production heatmap empty state remains unchanged.
- Tests cover unavailable publication-date cadence values.

Evidence:

- Cadence cards now show `No dates` when publication dates are unavailable.
- The production heatmap empty state remains unchanged.
- Focused dashboard lint and tests passed.

### TASK-182 - Publishing cadence visual polish

Status: Done

Phase: Consumption layer

Goal: make publishing cadence cards visually scannable while keeping the production section compact.

Acceptance criteria:

- Cadence cards have visual hierarchy distinct from ordinary metadata items.
- The layout remains responsive across existing breakpoints.
- Text remains inside each cadence card.
- Tests or browser QA cover the rendered cadence cards.

Evidence:

- Cadence cards now have compact markers and per-card accent variants.
- Existing responsive breakpoints remain unchanged.
- Focused dashboard lint and tests passed.

### TASK-183 - Publishing cadence accessible markers

Status: Done

Phase: Consumption layer

Goal: keep publishing cadence markers decorative for assistive text while preserving readable labels.

Acceptance criteria:

- Visual markers are hidden from assistive text.
- Cadence labels remain visible text.
- Tests cover the accessible marker treatment.

Evidence:

- Cadence markers render with `aria-hidden="true"`.
- Cadence labels remain visible text beside the decorative markers.
- Focused dashboard lint and tests passed.

### TASK-184 - Package publishing cadence polish batch

Status: Done

Phase: Governance

Goal: commit and open a PR for TASK-179 through TASK-183 as the publishing cadence polish batch.

Acceptance criteria:

- Full local validation passes.
- Sensitive information scan is clean for changed files.
- Dashboard smoke output is regenerated for local visual QA.
- Browser QA confirms publishing cadence cards, readable empty states and no layout overflow.
- The batch is committed and opened as a PR for GitHub Actions and CodeRabbit.

Evidence:

- Full validation passed with ruff, unit tests, documentation verification and Bandit.
- Sensitive-pattern scan on changed files returned no findings.
- Dashboard smoke output was regenerated.
- Browser QA confirmed publishing cadence cards, three visual variants, decorative markers, no horizontal overflow and no console errors.

### TASK-185 - PR review for publishing cadence polish batch

Status: Done

Phase: Governance

Goal: review GitHub Actions and CodeRabbit feedback for the publishing cadence polish batch.

Acceptance criteria:

- The PR is open with the publishing cadence polish batch.
- GitHub Actions checks are reviewed.
- CodeRabbit feedback is reviewed.
- Any blocker is fixed before merge.
- If checks are green and no blocker exists, the PR can be merged.

Evidence:

- PR #45 passed GitHub Actions quality checks and secret scan.
- CodeRabbit returned a passing skipped review status with no blocking feedback.
- PR #45 was squash-merged into `master`.

### TASK-186 - Dashboard v1 gap review

Status: Done

Phase: Governance

Goal: inspect the current local dashboard against the requested channel-first product goals and define the shortest closure path.

Acceptance criteria:

- The local dashboard smoke page is opened and inspected as a user-facing product.
- The review checks whether the dashboard is channel-first, not platform-first.
- The review checks whether visible labels avoid technical IDs, local paths, ports, tokens and raw secrets.
- The review checks whether channel images, content names, production dates, production volume, views and engagement metrics are understandable.
- The review produces the remaining tasks needed to close the dashboard v1 cycle.

Evidence:

- The dashboard smoke page returned `200` at the local smoke URL.
- Browser QA found no console errors and no horizontal overflow at the inspected desktop viewport.
- Visible text did not expose local paths, API key labels, token labels, channel IDs or video IDs.
- The dashboard already shows a channel selector, channel hero, consolidated metrics, platform source cards, platform comparison charts, production calendar, cadence cards and top-content names.
- Remaining product gaps are broken placeholder images, only one sample monitored channel in the smoke data, too many unavailable platform values in the main flow, ISO timestamps visible to users and secondary technical sections competing with primary dashboard content.

### TASK-187 - Dashboard sample channel set

Status: Done

Phase: Consumption layer

Goal: make the smoke dashboard demonstrate multiple monitored channels so the channel selector can be evaluated like the final product.

Acceptance criteria:

- The smoke dashboard renders at least three monitored channel options.
- Each monitored channel has a human display name and channel image or generated fallback avatar.
- YouTube, Instagram and TikTok remain data sources inside each selected channel instead of becoming selectable platforms.
- At least one channel has mixed provider availability and one channel has fuller sample coverage.
- Tests cover multi-channel smoke rendering without requiring real API credentials.

Evidence:

- `dashboard-smoke` now generates safe report variants for three monitored channels: Growth Lab, Creator Studio and Launch Room.
- Growth Lab renders YouTube and Instagram as available sources, while Creator Studio and Launch Room demonstrate mixed provider availability.
- TikTok remains an expected source inside each monitored channel config without adding real TikTok API work.
- The smoke workspace is cleared before regeneration so stale report artifacts cannot create extra channel options.
- Focused dashboard smoke, serve-dashboard and dashboard tests passed.

### TASK-188 - Dashboard local image fallbacks

Status: Done

Phase: Consumption layer

Goal: avoid broken external placeholder images in the dashboard and keep channel/content imagery useful offline.

Acceptance criteria:

- Smoke dashboard images render without depending on `example.com` or external network access.
- Broken or missing channel images fall back to a polished local/avatar treatment.
- Broken or missing content thumbnails fall back to a content-card visual that still shows title, platform and content type.
- The UI never exposes raw image URLs as a primary label.
- Tests cover image fallback behavior for channels and top-content cards.

Evidence:

- Dashboard image rendering now treats `example.com` and `example.test` image URLs as placeholders and renders visual fallbacks instead of broken `<img>` tags.
- Channel hero, channel preview and channel option cards use fallback avatars when placeholder images are present.
- Top-content cards and top-content table rows use content-type fallback media when placeholder thumbnails are present.
- Dynamic channel switching uses the same image fallback rule in browser-side rendering.
- Browser QA on the local smoke dashboard found zero image tags, zero broken images, zero placeholder image loads, no console errors and no horizontal overflow.
- Focused dashboard, dashboard-smoke and serve-dashboard tests passed.

### TASK-189 - Dashboard primary flow simplification

Status: Done

Phase: Consumption layer

Goal: make the first dashboard reading path simpler by pushing secondary diagnostics below the primary analytics flow.

Acceptance criteria:

- The first screen prioritizes selected channel identity, source coverage, semestral performance, productions, total views, total engagements and top insights.
- Report Context, Data Quality and supporting table details are visually secondary or collapsible.
- Unavailable provider values do not dominate the main reading path.
- No existing report data is removed from the HTML output.
- Tests cover the presence of primary sections and secondary diagnostic sections.

Evidence:

- Report Context and Data Quality now live inside a collapsed Supporting Details panel.
- The detailed top-content table now lives inside a collapsed Detailed ranking table panel while the visual top-content gallery remains primary.
- Existing data bindings remain in the HTML and update when the selected channel changes.
- Browser QA confirmed the details are collapsed by default, channel switching updates both top-content counters, no console errors occur and no horizontal overflow is present.
- Focused dashboard, dashboard-smoke and serve-dashboard tests passed.

### TASK-190 - Dashboard user-facing dates and labels

Status: Done

Phase: Consumption layer

Goal: make publication dates and source labels easier to understand for dashboard users.

Acceptance criteria:

- Top-content and platform top-content dates render as readable dates instead of raw ISO timestamps.
- Provider names keep clear source context such as YouTube, Instagram and TikTok.
- Unavailable values use short user-facing labels and avoid repeating `unavailable` across every metric in a card.
- Existing safe escaping behavior remains unchanged.
- Tests cover readable dates and unavailable source labels.

Evidence:

- Top-content and platform top-content dates now render as readable dates such as `May 21, 2026`.
- Provider labels now render as user-facing source names such as YouTube, TikTok and Instagram while preserving source context.
- Missing provider cards now show a compact `No data` status and one short explanatory note instead of repeating `unavailable` across every metric.
- Browser QA confirmed readable dates, no raw ISO timestamps in visible text, no visible `unavailable` text, no console errors and no horizontal overflow.
- Focused dashboard, dashboard-smoke and serve-dashboard tests passed.

### TASK-191 - Dashboard v1 acceptance checklist

Status: Done

Phase: Governance

Goal: document the exact criteria for closing the dashboard v1 cycle without adding more scope.

Acceptance criteria:

- Documentation lists the dashboard v1 acceptance checks in concise English.
- The checklist covers local smoke generation, local serving, channel-first selection, multiple monitored channels, channel images, content names, production cadence, views, engagements and safe public output.
- The checklist explicitly excludes new real TikTok work, cloud deployment and advanced observability from v1 closure.
- Public documentation avoids secrets, local paths, raw payloads, local ports, IPs and expanded DSNs.

Evidence:

- `docs/DASHBOARD_V1_ACCEPTANCE.md` now defines the concise dashboard v1 closure checklist.
- The checklist covers smoke generation, local serving, channel-first selection, multiple monitored channels, channel images, content names, production cadence, core metrics and safe public output.
- The checklist explicitly excludes real TikTok integration, cloud deployment, advanced observability, new Airflow changes and new credential-management features from v1.
- README and bootstrap docs now avoid a fixed local IP and port for dashboard review instructions.

### TASK-192 - CodeRabbit review policy cleanup

Status: Done

Phase: Governance

Goal: align the project documentation with how CodeRabbit should review PRs before dashboard v1 is closed.

Acceptance criteria:

- The repository documents whether CodeRabbit should run automatically or be triggered manually for implementation PRs.
- If repository configuration skips automatic review, the manual trigger command is documented.
- The policy keeps GitHub Actions and secret scan as required checks.
- No secrets, local paths or private operational details are added to public documentation.

Evidence:

- `docs/REVIEW_POLICY.md` now documents that CodeRabbit automatic review is disabled in repository configuration.
- The policy documents `@coderabbitai review` as the manual review trigger for PRs that need CodeRabbit.
- The policy keeps GitHub Actions, Python quality/security and secret scan as required checks.
- README, agent contracts and the work plan now point to the review policy or match the five-task batch rule.

### TASK-193 - Dashboard v1 browser QA pass

Status: Done

Phase: Governance

Goal: run a final browser QA pass over the dashboard after the closure fixes.

Acceptance criteria:

- Desktop QA confirms no console errors and no horizontal overflow.
- Mobile or narrow viewport QA confirms the dashboard remains readable.
- QA confirms channel selection updates the hero, metric cards, insights, platform sources, production calendar and top content.
- QA confirms no visible local paths, token labels, API key labels, raw channel IDs or raw video IDs appear in the dashboard.
- The QA result is recorded in progress documentation.

Evidence:

- Desktop browser QA confirmed three monitored channel options, readable dates, no visible raw ISO timestamps, no sensitive visible text, no console errors and no horizontal overflow.
- Desktop channel switching to Launch Room updated the hero, metric cards, insights, platform sources, production calendar and top-content gallery.
- Narrow viewport QA confirmed Creator Studio selection updates the same primary dashboard sections.
- Narrow viewport QA confirmed no page overflow, no problematic element overflow, no console errors, readable dates and no sensitive visible text.
- Mobile production heatmap CSS now compacts cells and month labels so it fits the narrow dashboard layout.

### TASK-194 - Package dashboard v1 closure batch

Status: Done

Phase: Governance

Goal: commit and open a PR for the dashboard v1 closure tasks.

Acceptance criteria:

- The closure batch passes local validation.
- Sensitive-pattern scan is clean for changed files.
- Dashboard smoke output is regenerated for local visual QA.
- Browser QA evidence is recorded.
- The batch is committed and opened as a PR for GitHub Actions and CodeRabbit.

Evidence:

- Local validation for documentation, lint, focused dashboard tests and dashboard smoke regeneration passed before packaging.
- Sensitive-pattern scan for changed files returned no findings.
- Browser QA evidence from TASK-193 is recorded in this document and progress notes.
- The branch is prepared for commit and PR review through GitHub Actions and CodeRabbit.

### TASK-195 - PR review for dashboard v1 closure batch

Status: Done

Phase: Governance

Goal: review GitHub Actions and CodeRabbit feedback for the dashboard v1 closure batch.

Acceptance criteria:

- The PR is open with the dashboard v1 closure batch.
- GitHub Actions checks are reviewed.
- CodeRabbit feedback is reviewed according to the documented policy.
- Any blocker is fixed before merge.
- If checks are green and no blocker exists, the PR can be merged.

Evidence:

- PR #47 was opened for the dashboard v1 closure review policy and QA batch.
- GitHub Actions `Python quality and security` completed successfully.
- GitHub Actions `Secret scan` completed successfully.
- CodeRabbit status completed successfully.
- PR #47 was squash-merged into `master` with no blocking findings.

### TASK-196 - Post-v1 delivery decision

Status: Done

Phase: Governance

Goal: choose the next delivery direction after the dashboard v1 closure.

Acceptance criteria:

- The next slice is chosen before implementation starts.
- The decision compares at least provider expansion, dashboard product polish and operational quality.
- The decision states what is included and explicitly deferred.
- The decision keeps public documentation free of secrets, local paths, raw payloads, ports, IPs and expanded DSNs.

Evidence:

- ADR-0003 compares provider expansion, dashboard product polish and operational quality.
- ADR-0003 chooses Instagram provider depth as the next delivery direction.
- The decision includes current Instagram provider/report/dashboard compatibility review before implementation.
- TikTok, cloud deployment, advanced observability, large-scale async fetching and broad dashboard redesign remain deferred.

### TASK-197 - Instagram provider depth gap review

Status: Done

Phase: Governance

Goal: inspect the current Instagram provider path and define the smallest useful real-provider depth slice.

Acceptance criteria:

- Current Instagram provider, report and dashboard compatibility are reviewed.
- The review identifies what already works and what blocks a useful local Instagram real-provider flow.
- The next implementation tasks are scoped without adding TikTok, cloud deployment or broad orchestration changes.
- Public documentation avoids secrets, local paths, raw payloads, ports, IPs and expanded DSNs.

Evidence:

- `docs/INSTAGRAM_PROVIDER_GAP_REVIEW.md` records current Instagram strengths and gaps.
- The review confirms the provider, local pipeline, report command and dashboard smoke path already exist.
- Focused Instagram provider, local pipeline, report and dashboard smoke tests passed locally.
- The next slice is provider resilience for transient Instagram HTTP failures.
- TikTok, PostgreSQL loading, Airflow DAGs, cloud deployment and broad dashboard redesign remain deferred.

### TASK-198 - Instagram provider transient retry

Status: Done

Phase: Provider depth

Goal: add retry/backoff behavior for transient Instagram HTTP failures.

Acceptance criteria:

- Instagram retries transient HTTP failures such as rate limits and server errors.
- Credential failures still fail fast for unauthorized or forbidden responses.
- Error messages stay sanitized and do not print tokens, raw request URLs, local paths or raw payloads.
- Tests cover retry success, retry exhaustion and fail-fast credential errors.

Evidence:

- `InstagramHttpJsonClient` now retries transient statuses and network-style request errors using configurable attempts and backoff.
- Unauthorized and forbidden responses still fail fast with sanitized messages.
- `.env.example` now exposes local retry tuning placeholders.
- Bootstrap notes mention local Instagram retry tuning without adding real credentials.
- Focused Instagram provider, pipeline and report tests passed.

### TASK-199 - Instagram report operator parity

Status: Done

Phase: Provider depth

Goal: make `instagram-report` closer to the mature YouTube report operator flow.

Acceptance criteria:

- The report command supports at least one missing operator convenience identified in the gap review.
- Existing `instagram-report` behavior remains backward compatible.
- Documentation describes only supported Instagram report options.
- Tests cover the new operator behavior.

Evidence:

- `instagram-report` now supports `--list-artifacts`, `--latest-artifact`, `--count-artifacts` and `--fail-if-missing`.
- List-only modes use sorted processed Instagram artifact paths and relative display paths.
- Existing report generation behavior remains unchanged.
- Bootstrap documents only the supported Instagram report list-only modes.
- Focused `instagram-report` lint and tests passed.

### TASK-200 - Instagram report dry-run planning

Status: Done

Phase: Provider depth

Goal: let operators preview Instagram report paths and selected artifact details without writing files.

Acceptance criteria:

- `instagram-report` supports a dry-run mode.
- Dry-run prints the selected artifact, record count, sorting and planned JSON output path.
- Dry-run does not write report files.
- Existing `instagram-report` behavior remains backward compatible.
- Tests cover dry-run output and no-write behavior.

Evidence:

- `instagram-report` now supports `--dry-run`.
- Dry-run prints selected artifact, records, sorting and planned JSON output path.
- Dry-run returns before writing report files.
- Bootstrap documents the supported dry-run option.
- Focused `instagram-report` lint and tests passed.

### TASK-201 - Package Instagram provider depth batch

Status: Done

Phase: Governance

Goal: commit and open a PR for the Instagram provider depth batch.

Acceptance criteria:

- The batch passes local validation.
- Sensitive-pattern scan is clean for changed files.
- Documentation records the Instagram direction, gap review and operator changes.
- The batch is committed and opened as a PR for GitHub Actions and CodeRabbit.

Evidence:

- Local validation passed with docs verification, Ruff, unit tests and Bandit.
- Sensitive-pattern scan found only existing safe placeholders in `.env.example` and bootstrap docs.
- Documentation records ADR-0003, the Instagram provider gap review and operator changes.
- The branch is prepared for commit and PR review through GitHub Actions and CodeRabbit.

### TASK-202 - PR review for Instagram provider depth batch

Status: Done

Phase: Governance

Goal: review GitHub Actions and CodeRabbit feedback for the Instagram provider depth batch.

Acceptance criteria:

- The PR is open with the Instagram provider depth batch.
- GitHub Actions checks are reviewed.
- CodeRabbit feedback is reviewed according to the documented policy.
- Any blocker is fixed before merge.
- If checks are green and no blocker exists, the PR can be merged.

Evidence:

- PR #49 was opened for the Instagram provider depth batch.
- GitHub Actions `Python quality and security` completed successfully.
- GitHub Actions `Secret scan` completed successfully.
- CodeRabbit status completed successfully.
- PR #49 was squash-merged into `master` with no blocking findings.

### TASK-203 - Instagram provider next slice decision

Status: Pending

Phase: Governance

Goal: choose the next small Instagram provider-depth task after retry and report operator parity.

Acceptance criteria:

- The next Instagram slice is chosen before implementation.
- The decision considers report parity, local runbook clarity and real-run readiness.
- TikTok, PostgreSQL loading, Airflow DAGs and broad dashboard redesign remain explicitly deferred unless selected.
- Public documentation avoids secrets, local paths, raw payloads, ports, IPs and expanded DSNs.

## Deferred Until After v1 Closure

- Broaden run summaries beyond the real YouTube path.
- Add stronger alert delivery beyond the current local fail-on-invalid mode.
- Revisit broader Airflow/observability refinements.
- Expand TikTok only after an official analytics path fits the channel-first dashboard contract.

## Next Candidate Deliveries

- Package the Instagram provider depth batch for review.
- Keep TikTok, cloud deployment and broad operational refinements deferred unless they directly unlock the selected Instagram slice.

## Review Rule

Every implementation PR should pass local validation where practical, GitHub Actions, secret scan and CodeRabbit. Gemini or ChatGPT review packets are used when available.

Small tasks are batched in groups of up to five before commit and PR. Open a PR earlier only when the change is large, risky, security-sensitive, blocks further work, or needs external review before continuing.
