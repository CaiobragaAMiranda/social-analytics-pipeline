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
| Phase 1 - MVP Core | Providers, raw storage, normalization and local PostgreSQL loading. | Closing current YouTube v1 |
| Phase 2 - Orchestration and History | Airflow, scheduled DAGs and catchup. | Usable for YouTube |
| Phase 3 - Resilience | Retries, rate limits, alerts and DLQ. | Baseline done for YouTube |
| Phase 4 - Quality and Scale | Data validation, metrics, profiling and scaling choices. | Deferred until after v1 closure |

## Near-Term Direction

1. Close the current YouTube v1 cycle with a concise operator runbook and closure checkpoint.
2. Publish the already completed YouTube hardening work in a clean review cycle.
3. Only then decide between another real provider or the next layer of engineering refinement.

## Out of Scope for Now

- Cloud deployment.
- Full analytics dashboard.
- Paid API integrations before the local MVP is stable.
- Large-scale async fetching before real volume requires it.
- Additional engineering polish that does not change the current YouTube delivery outcome.
