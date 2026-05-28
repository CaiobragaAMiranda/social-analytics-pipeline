import sys
from datetime import UTC, datetime
from pathlib import Path

from airflow.sdk import dag, get_current_context, task

AIRFLOW_PROJECT_ROOT = Path("/opt/airflow/project")
AIRFLOW_SRC = AIRFLOW_PROJECT_ROOT / "src"

if str(AIRFLOW_SRC) not in sys.path:
    sys.path.insert(0, str(AIRFLOW_SRC))


@dag(
    dag_id="social_analytics_mock_pipeline",
    description="Run the local mock social analytics pipeline inside Airflow.",
    schedule=None,
    start_date=datetime(2026, 1, 1),
    catchup=False,
    tags=["social-analytics", "mock", "pipeline"],
)
def social_analytics_mock_pipeline() -> None:
    @task
    def run_mock_pipeline() -> list[dict[str, int | str]]:
        from social_analytics_pipeline.pipeline import (
            JsonMetricArtifactLoader,
            run_provider_pipeline,
        )
        from social_analytics_pipeline.providers import build_mock_providers
        from social_analytics_pipeline.storage import RawStorage

        context = get_current_context()
        start_at = context.get("data_interval_start") or datetime.now(UTC)
        end_at = context.get("data_interval_end") or datetime.now(UTC)

        project_root = AIRFLOW_PROJECT_ROOT
        providers = build_mock_providers(project_root)
        results: list[dict[str, int | str]] = []

        for provider_name, provider in providers.items():
            output_path = (
                project_root
                / "data"
                / "processed"
                / "airflow"
                / f"{provider_name}-{end_at.strftime('%Y%m%dT%H%M%S')}.json"
            )
            result = run_provider_pipeline(
                provider=provider,
                account_id=f"{provider_name}-mock-account",
                start_at=start_at,
                end_at=end_at,
                raw_storage=RawStorage(project_root / "data" / "raw"),
                loader=JsonMetricArtifactLoader(output_path),
            )
            results.append(
                {
                    "provider": result.provider,
                    "raw_records": result.raw_records,
                    "loaded_records": result.loaded_records,
                }
            )

        return results

    run_mock_pipeline()


social_analytics_mock_pipeline()
