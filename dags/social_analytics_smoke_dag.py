from datetime import datetime

from airflow.sdk import dag, task


@dag(
    dag_id="social_analytics_smoke",
    description="Smoke DAG for validating the local Airflow environment.",
    schedule=None,
    start_date=datetime(2026, 1, 1),
    catchup=False,
    tags=["social-analytics", "smoke"],
)
def social_analytics_smoke() -> None:
    @task
    def healthcheck() -> str:
        return "social-analytics-airflow-ok"

    healthcheck()


social_analytics_smoke()
