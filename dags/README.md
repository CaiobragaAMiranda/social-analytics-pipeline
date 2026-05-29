# Airflow DAGs

This directory is mounted into the local Airflow containers at `/opt/airflow/dags`.

Current DAGs:

- `social_analytics_smoke`: validates that the local Airflow environment can parse and run a minimal DAG.
- `social_analytics_mock_pipeline`: runs mock providers through raw storage, normalization and configurable JSON/PostgreSQL loading every 15 days, with catchup enabled for historical intervals.
