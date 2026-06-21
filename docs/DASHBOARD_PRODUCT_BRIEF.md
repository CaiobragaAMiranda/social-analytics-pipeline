# Dashboard Product Brief

## Objective

Provide a single-page, channel-first analytics dashboard for investigating one monitored brand or creator across YouTube, Instagram and TikTok.

The user selects a human channel identity, not a platform. The dashboard then shows the channel name, image, source coverage, content performance and production activity for the selected period.

## Product Rules

- The default analysis period is the most recent six months.
- A future annual view must use the full available year and state its period clearly.
- Production metrics and the production calendar must use every collected content item in the selected period, never only ranked or top-content rows.
- Each production day must expose its total content count through a readable label, tooltip or detail view.
- Platform cards must identify YouTube, Instagram and TikTok as sources within the selected channel.
- Channel names, images, content titles, thumbnails and publication dates are primary display metadata; technical IDs are fallbacks only.
- Numeric metrics may render as `0` when zero is a valid value. Source coverage must still make connected, unavailable and not-monitored sources explicit.

## Current Gaps

- The production calendar currently reflects a limited report subset rather than the full collected production history.
- Daily production counts are encoded visually but are not yet directly inspectable.
- Smoke data proves the channel selector but does not yet represent a complete real channel history.
- Real channel identity and media are available only when the provider report supplies them.
- The selected period needs a clear user-facing label and consistent report contract.

## Evidence For Completion

- A monitored channel can be selected by human name and image.
- The dashboard shows source coverage and consolidated metrics for that channel.
- The six-month production calendar matches every collected item in the report period.
- A user can identify how many productions occurred on a given active day.
- Content investigation uses readable titles, thumbnails, dates and links where available.
- Missing provider or metric data has an explicit state.
