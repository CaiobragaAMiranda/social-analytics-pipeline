# Dashboard v1 Acceptance Checklist

This checklist defines the minimum scope needed to close the dashboard v1 cycle.

## Required Checks

- Generate the safe smoke dashboard without real API credentials.
- Serve the smoke dashboard locally using the project command and the URL printed by the command.
- Confirm the selector chooses monitored channels, not individual platforms.
- Confirm the smoke dashboard shows at least three monitored channels.
- Confirm each monitored channel has a human name and a channel image or fallback avatar.
- Confirm YouTube, Instagram and TikTok appear only as source coverage inside the selected channel.
- Confirm the selected channel shows semestral performance, production count, total views and total engagements.
- Confirm production cadence is visible through summary cards and the activity calendar.
- Confirm top content uses titles, thumbnails or fallbacks, platform labels, readable dates and links when available.
- Confirm missing platform sources use compact no-data messaging.
- Confirm supporting diagnostics are collapsed or visually secondary to the main analytics flow.
- Confirm desktop and narrow viewport checks have no console errors or horizontal overflow.
- Confirm the dashboard does not show local paths, raw payloads, token labels, API key labels, raw channel IDs or raw content IDs in the primary flow.

## Out of Scope for v1

- Real TikTok analytics integration.
- Cloud deployment.
- Advanced observability or alerting.
- New Airflow orchestration changes.
- New credential or secret-management features.

## Closure Rule

Dashboard v1 is closed when the required checks pass locally, documentation is updated, the five-task batch is committed, and the PR passes GitHub Actions, secret scan and CodeRabbit review.
