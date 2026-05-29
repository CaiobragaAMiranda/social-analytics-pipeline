import os
from collections.abc import Mapping
from datetime import datetime
from pathlib import Path

from social_analytics_pipeline.load import PostgresMetricLoader
from social_analytics_pipeline.orchestration.airflow_settings import MOCK_PIPELINE_LOAD
from social_analytics_pipeline.pipeline import (
    JsonMetricArtifactLoader,
    MetricLoader,
    build_interval_artifact_path,
)


def build_airflow_metric_loader(
    provider_name: str,
    start_at: datetime,
    end_at: datetime,
    project_root: Path,
    env: Mapping[str, str] | None = None,
) -> MetricLoader:
    runtime_env = env or os.environ
    target = runtime_env.get(
        "SOCIAL_ANALYTICS_AIRFLOW_LOAD_TARGET",
        MOCK_PIPELINE_LOAD.target,
    ).lower()

    if target == "postgres":
        dsn = runtime_env.get(MOCK_PIPELINE_LOAD.postgres_dsn_env_var)
        if not dsn:
            raise RuntimeError(
                f"{MOCK_PIPELINE_LOAD.postgres_dsn_env_var} is required when "
                "SOCIAL_ANALYTICS_AIRFLOW_LOAD_TARGET=postgres."
            )
        return PostgresMetricLoader(dsn)

    if target != "json":
        raise RuntimeError(
            "SOCIAL_ANALYTICS_AIRFLOW_LOAD_TARGET must be either 'json' or 'postgres'."
        )

    output_path = build_interval_artifact_path(
        project_root / "data" / "processed" / "airflow",
        provider_name,
        start_at,
        end_at,
    )
    return JsonMetricArtifactLoader(output_path)
