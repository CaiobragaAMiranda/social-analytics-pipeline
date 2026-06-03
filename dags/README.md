# Airflow DAGs

This directory is mounted into the local Airflow containers at `/opt/airflow/dags`.

Current DAGs:

- `social_analytics_smoke`: validates that the local Airflow environment can parse and run a minimal DAG.
- `social_analytics_mock_pipeline`: runs mock providers through raw storage, normalization and configurable JSON/PostgreSQL loading every 15 days, with catchup enabled for historical intervals.
- `social_analytics_youtube_pipeline`: runs the real YouTube provider through raw storage, normalization and configurable JSON/PostgreSQL loading every 15 days, using only environment variables for API key, channel and load target. Automatic catchup is disabled to avoid unexpected YouTube API quota usage; historical runs should be triggered deliberately.
