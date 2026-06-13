# ADR-0002 - Second Real Provider

Status: Accepted

Date: 2026-06-13

## Context

The YouTube v1 slice is closed and the dashboard now supports monitored channels with platform source breakdowns. The next provider must use official access only, avoid scraping and produce metrics compatible with the shared channel dashboard contract.

The candidate providers are TikTok and Instagram.

## Decision

Select Instagram as the next real provider, limited to authorized Instagram professional accounts.

TikTok remains deferred until the project needs a research-focused integration or TikTok provides a better official analytics path for the monitored-channel use case.

## Comparison

| Provider | Fit | Notes |
| --- | --- | --- |
| Instagram | Better next fit | Official Meta APIs support professional account and media insights for authorized accounts. This maps naturally to channel/account analytics, totals, engagement and content-level metrics. |
| TikTok | Defer | Official TikTok APIs are useful, but the relevant public-data path is research-oriented and constrained. The Research API requires `research.data.basic`, supports query windows, and its video query endpoint is limited to a maximum 30-day date span per request. |

## Credential Requirements

Use placeholders only in public documentation:

- `INSTAGRAM_ACCESS_TOKEN`
- `INSTAGRAM_USER_ID`
- `INSTAGRAM_ACCOUNT_HANDLE`

Any real access token, account ID, app secret or account handle must stay in local `.env` or `config/channels.local.json`, both uncommitted.

## Implementation Direction

The first Instagram slice should be intentionally small:

1. Add an Instagram provider interface backed by official API calls only.
2. Require explicit local credentials and fail closed when they are missing.
3. Normalize returned media/account metrics into the existing `SocialMetric` schema.
4. Preserve raw payloads locally without committing generated artifacts.
5. Produce report JSON compatible with the channel-first dashboard.

## Consequences

Benefits:

- The next provider aligns with the existing dashboard contract.
- The implementation can reuse the YouTube local provider shape, storage, validation and report flow.
- The project avoids scraping and avoids building around restricted research APIs too early.

Costs:

- Instagram access depends on authorized professional accounts, not arbitrary public profiles.
- The project cannot promise public analytics for every Instagram channel without the required Meta permissions.
- TikTok remains unavailable as a real provider until a better official path is selected.

## Sources Checked

- TikTok Research API Query Videos: https://developers.tiktok.com/doc/research-api-specs-query-videos/
- TikTok Content Posting API Get Started: https://developers.tiktok.com/doc/content-posting-api-get-started/
- Meta Instagram Platform documentation: https://developers.facebook.com/docs/instagram-platform/
