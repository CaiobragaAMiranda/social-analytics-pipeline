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


@dataclass(frozen=True)
class AirflowLoadSettings:
    target: str
    postgres_dsn_env_var: str

    @property
    def uses_postgres(self) -> bool:
        return self.target == "postgres"


MOCK_PIPELINE_DAG = AirflowDagSettings(
    dag_id="social_analytics_mock_pipeline",
    description="Run the local mock social analytics pipeline inside Airflow.",
    schedule=timedelta(days=15),
    start_date=datetime(2026, 1, 1, tzinfo=UTC),
    catchup=True,
    tags=("social-analytics", "mock", "pipeline", "catchup"),
)

YOUTUBE_PIPELINE_DAG = AirflowDagSettings(
    dag_id="social_analytics_youtube_pipeline",
    description="Run the real YouTube social analytics pipeline inside Airflow.",
    schedule=timedelta(days=15),
    start_date=datetime(2026, 1, 1, tzinfo=UTC),
    catchup=True,
    tags=("social-analytics", "youtube", "pipeline", "catchup"),
)

MOCK_PIPELINE_LOAD = AirflowLoadSettings(
    target="json",
    postgres_dsn_env_var="SOCIAL_ANALYTICS_POSTGRES_DSN",
)
