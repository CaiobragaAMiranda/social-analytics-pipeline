# Work Plan

## Goal

Build a local-first social analytics pipeline that can collect public social data, preserve raw payloads, normalize metrics into one schema, load them locally and orchestrate scheduled runs.

## Principles

- The repository is the source of truth.
- Every task must have a clear acceptance target.
- Public documentation must not contain secrets, local paths, real payloads or expanded connection strings.
- Real API calls are manual or locally configured; automated tests use mocks/fakes.
- Keep documentation compact enough to be useful.

## Phases

| Phase | Focus | Status |
| --- | --- | --- |
| Phase 0 - Governance | Docs, task tracking, review contracts and safety rules. | Mostly done |
| Phase 1 - MVP Core | Providers, raw storage, normalization and local PostgreSQL loading. | YouTube path done |
| Phase 2 - Orchestration and History | Airflow, scheduled DAGs and catchup. | In progress |
| Phase 3 - Resilience | Retries, rate limits, alerts and DLQ. | Pending |
| Phase 4 - Quality and Scale | Data validation, metrics, profiling and scaling choices. | Pending |

## Near-Term Direction

1. Validate the real YouTube DAG inside local Airflow.
2. Add resilience around API failures and expired configuration.
3. Add data validation before load.
4. Decide whether to expand to another provider or harden YouTube first.

## Out of Scope for Now

- Cloud deployment.
- Full analytics dashboard.
- Paid API integrations before the local MVP is stable.
- Large-scale async fetching before real volume requires it.
