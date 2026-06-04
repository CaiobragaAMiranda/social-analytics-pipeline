import sys
from datetime import UTC, datetime, timedelta
from pathlib import Path

from airflow.sdk import dag, get_current_context, task

AIRFLOW_PROJECT_ROOT = Path("/opt/airflow/project")
AIRFLOW_SRC = AIRFLOW_PROJECT_ROOT / "src"
DEFAULT_LOOKBACK_DAYS = 30
MAX_LOOKBACK_DAYS = 365

if str(AIRFLOW_SRC) not in sys.path:
    sys.path.insert(0, str(AIRFLOW_SRC))

from social_analytics_pipeline.orchestration import YOUTUBE_PIPELINE_DAG  # noqa: E402


@dag(
    dag_id=YOUTUBE_PIPELINE_DAG.dag_id,
    description=YOUTUBE_PIPELINE_DAG.description,
    schedule=YOUTUBE_PIPELINE_DAG.schedule,
    start_date=YOUTUBE_PIPELINE_DAG.start_date,
    catchup=YOUTUBE_PIPELINE_DAG.catchup,
    tags=list(YOUTUBE_PIPELINE_DAG.tags),
)
def social_analytics_youtube_pipeline() -> None:
    def _resolve_lookback_days(value: str | None) -> int:
        try:
            lookback_days = int(value or DEFAULT_LOOKBACK_DAYS)
        except ValueError:
            return DEFAULT_LOOKBACK_DAYS

        return min(max(lookback_days, 1), MAX_LOOKBACK_DAYS)

    @task
    def run_youtube_pipeline() -> dict[str, int | str]:
        import os

        from social_analytics_pipeline.cli.youtube_local_pipeline import (
            build_runtime_env,
            build_youtube_local_loader,
            require_smoke_settings,
            resolve_backfill_interval,
            resolve_smoke_channel_id,
            run_youtube_local_pipeline,
        )
        from social_analytics_pipeline.providers import (
            YouTubeApiConfig,
            YouTubeDataApiProvider,
        )

        context = get_current_context()
        project_root = AIRFLOW_PROJECT_ROOT
        runtime_env = build_runtime_env(os.environ, project_root / ".env")
        fallback_end_at = datetime.now(UTC)
        lookback_days = _resolve_lookback_days(runtime_env.get("YOUTUBE_SMOKE_LOOKBACK_DAYS"))
        fallback_start_at = fallback_end_at - timedelta(days=lookback_days)
        backfill_interval = resolve_backfill_interval(runtime_env)
        start_at = context.get("data_interval_start")
        end_at = context.get("data_interval_end")
        if start_at is None or end_at is None:
            if backfill_interval:
                start_at, end_at = backfill_interval
            else:
                start_at = fallback_start_at
                end_at = fallback_end_at
        required_settings = require_smoke_settings(
            runtime_env,
            ("YOUTUBE_API_KEY",),
            project_root / ".env",
        )
        provider = YouTubeDataApiProvider(YouTubeApiConfig.from_env(runtime_env))
        channel_id = resolve_smoke_channel_id(
            {**runtime_env, **required_settings},
            provider,
            project_root / ".env",
        )
        loader, _processed_path = build_youtube_local_loader(
            runtime_env,
            provider.name,
            start_at,
            end_at,
            project_root,
        )
        summary = run_youtube_local_pipeline(
            provider,
            channel_id,
            start_at,
            end_at,
            project_root,
            loader,
        )

        return {
            "provider": summary.result.provider,
            "channel_id": "<configured>",
            "raw_records": summary.result.raw_records,
            "loaded_records": summary.result.loaded_records,
        }

    run_youtube_pipeline()


social_analytics_youtube_pipeline()
