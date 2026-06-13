# Work Plan

## Goal

Build a local-first social analytics pipeline that can collect public social data, preserve raw payloads, normalize metrics into one schema, load them locally and orchestrate scheduled runs.

## Principles

- The repository is the source of truth.
- Every task must have a clear acceptance target.
- Public documentation must not contain secrets, local paths, real payloads or expanded connection strings.
- Real API calls are manual or locally configured; automated tests use mocks/fakes.
- Keep documentation compact enough to be useful.
- Prefer closing a working delivery slice before adding more engineering sophistication.

## Phases

| Phase | Focus | Status |
| --- | --- | --- |
| Phase 0 - Governance | Docs, task tracking, review contracts and safety rules. | Mostly done |
| Phase 1 - MVP Core | Providers, raw storage, normalization and local PostgreSQL loading. | YouTube v1 closed |
| Phase 2 - Orchestration and History | Airflow, scheduled DAGs and catchup. | Usable for YouTube |
| Phase 3 - Resilience | Retries, rate limits, alerts and DLQ. | Baseline done for YouTube |
| Phase 4 - Quality and Scale | Data validation, metrics, profiling and scaling choices. | Deferred until after v1 closure |
| Phase 5 - Consumption Layer | Build a channel-first dashboard from generated report artifacts. | Current |
| Phase 6 - Second Real Provider | Add one more real provider after the channel contract is useful. | Next |

## Near-Term Direction

1. Treat the current YouTube v1 slice as closed in repository context.
2. Build a local channel-first dashboard from existing report JSON files.
3. Make the user-facing selector choose monitored channels/accounts, not platforms.
4. Treat YouTube, TikTok and Instagram as platform sources inside the selected channel.
5. Add a second real provider only after the channel dashboard data contract is clear.
6. Prefer static/local artifacts before adding a web server or cloud deployment.

## Next Delivery Sequence

1. Channel contract: define one monitored channel with consolidated totals and platform sources.
2. Dashboard breakdown: show selected-channel totals plus per-platform YouTube, TikTok and Instagram cards.
3. Multi-report aggregation: group multiple report JSON files into channel options.
4. Channel identity config: map platform handles/IDs to one monitored channel identity.
5. Second provider decision: prefer an official API only after the channel contract can absorb it.

## Out of Scope for Now

- Cloud deployment.
- Full analytics dashboard beyond the channel-first MVP.
- Paid API integrations before the local MVP is stable.
- Non-official scraping or bypassing platform access rules.
- Large-scale async fetching before real volume requires it.
- Additional engineering polish that does not change the current YouTube delivery outcome.
