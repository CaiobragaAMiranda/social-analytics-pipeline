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

Status: Pending

Phase: Consumption layer

Goal: map platform-specific accounts to a single monitored channel identity.

Acceptance criteria:

- Local configuration can map one channel to YouTube, TikTok and Instagram handles/IDs.
- Configuration examples use placeholders only.
- The dashboard/report layer can use the configured display name and image URL.
- Missing platform handles are allowed.
- Tests cover complete and partial channel mappings.

### TASK-103 - Second real provider decision

Status: Pending

Phase: Second real provider

Goal: choose the next real provider only after the channel contract can absorb it.

Acceptance criteria:

- The decision compares TikTok and Instagram official API availability.
- The selected provider has local credential requirements documented with placeholders only.
- The implementation plan avoids scraping and non-official access.
- The provider must produce metrics compatible with the channel dashboard contract.

## Deferred Until After v1 Closure

- Broaden run summaries beyond the real YouTube path.
- Add stronger alert delivery beyond the current local fail-on-invalid mode.
- Revisit broader Airflow/observability refinements.
- Expand to TikTok or Instagram real APIs only after the channel-first dashboard contract is useful.

## Next Candidate Deliveries

- Define and implement the channel-first multi-platform dashboard contract.
- Group multiple reports into monitored channels before provider expansion.
- Add a second real provider path only if official local access is practical and compatible with the channel contract.
- Keep extra architecture refinement deferred unless it directly unlocks the next delivery.

## Review Rule

Every implementation PR should pass local validation where practical, GitHub Actions, secret scan and CodeRabbit. Gemini or ChatGPT review packets are used when available.
