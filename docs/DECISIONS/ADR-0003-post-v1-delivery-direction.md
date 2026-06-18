# ADR-0003 - Post-v1 Delivery Direction

## Status

Accepted

## Context

The dashboard v1 cycle is closed. The project now has a channel-first dashboard contract, safe smoke data, readable channel/content labels, responsive browser QA and an explicit review policy.

The next slice should add product value without expanding operational complexity too early.

## Options Considered

1. Provider expansion.
   - Strength: moves the project closer to real multi-source analytics.
   - Tradeoff: requires official API access and careful local credential handling.
   - Best fit: Instagram depth, because the project already selected Instagram as the second real provider and has local report compatibility.

2. Dashboard product polish.
   - Strength: improves analysis clarity for existing reports.
   - Tradeoff: less valuable if the dashboard still depends mostly on YouTube plus safe fixtures.
   - Best fit: defer until another real provider path is stronger.

3. Operational quality.
   - Strength: improves reliability, observability and automation confidence.
   - Tradeoff: can slow product learning if added before the data sources prove useful.
   - Best fit: defer unless it directly supports the next provider slice.

## Decision

The next delivery direction is Instagram provider depth.

The slice should improve the real Instagram path and its dashboard/report compatibility without adding TikTok, cloud deployment or broader orchestration changes.

## Included

- Review the current Instagram provider, report and dashboard compatibility.
- Identify the smallest remaining gaps for a useful local Instagram real-provider flow.
- Keep official Meta API boundaries and authorized professional accounts only.
- Keep local credentials out of committed files and public documentation.
- Preserve the channel-first dashboard contract.

## Deferred

- Real TikTok analytics integration.
- Cloud deployment.
- Advanced observability and alerting.
- Large-scale async fetching.
- Dashboard redesign beyond changes required to consume the provider slice.

## Consequences

The next task should start with an Instagram provider gap review before implementation. This avoids adding code before the remaining provider, report and dashboard requirements are clear.
