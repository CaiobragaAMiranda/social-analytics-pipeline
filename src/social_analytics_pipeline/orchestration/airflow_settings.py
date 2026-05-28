from dataclasses import dataclass
from datetime import UTC, datetime, timedelta


@dataclass(frozen=True)
class AirflowDagSettings:
    dag_id: str
    description: str
    schedule: timedelta
    start_date: datetime
    catchup: bool
    tags: tuple[str, ...]


MOCK_PIPELINE_DAG = AirflowDagSettings(
    dag_id="social_analytics_mock_pipeline",
    description="Run the local mock social analytics pipeline inside Airflow.",
    schedule=timedelta(days=15),
    start_date=datetime(2026, 1, 1, tzinfo=UTC),
    catchup=True,
    tags=("social-analytics", "mock", "pipeline", "catchup"),
)
