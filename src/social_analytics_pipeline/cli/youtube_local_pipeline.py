import sys
from collections.abc import Mapping
from dataclasses import dataclass
from datetime import UTC, datetime, timedelta
from pathlib import Path

from social_analytics_pipeline.cli.youtube_smoke import (
    build_runtime_env,
    require_smoke_settings,
    resolve_smoke_channel_id,
)
from social_analytics_pipeline.pipeline import (
    JsonMetricArtifactLoader,
    LocalPipelineResult,
    build_interval_artifact_path,
    run_provider_pipeline,
)
from social_analytics_pipeline.providers import YouTubeApiConfig, YouTubeDataApiProvider
from social_analytics_pipeline.storage import RawStorage


@dataclass(frozen=True)
class YouTubeLocalPipelineSummary:
    result: LocalPipelineResult
    processed_path: Path
    raw_root: Path


def run_youtube_local_pipeline(
    provider: YouTubeDataApiProvider,
    channel_id: str,
    start_at: datetime,
    end_at: datetime,
    project_root: Path,
) -> YouTubeLocalPipelineSummary:
    processed_path = build_interval_artifact_path(
        project_root / "data" / "processed" / "youtube",
        provider.name,
        start_at,
        end_at,
    )
    raw_root = project_root / "data" / "raw"

    result = run_provider_pipeline(
        provider=provider,
        account_id=channel_id,
        start_at=start_at,
        end_at=end_at,
        raw_storage=RawStorage(raw_root),
        loader=JsonMetricArtifactLoader(processed_path),
    )

    return YouTubeLocalPipelineSummary(
        result=result,
        processed_path=processed_path,
        raw_root=raw_root,
    )


def main(env: Mapping[str, str] | None = None, project_root: Path | None = None) -> int:
    root = project_root or Path.cwd()
    runtime_env = build_runtime_env(env, root / ".env")
    required_settings = require_smoke_settings(
        runtime_env,
        ("YOUTUBE_API_KEY",),
        root / ".env",
    )

    lookback_days = int(runtime_env.get("YOUTUBE_SMOKE_LOOKBACK_DAYS", "30"))
    if lookback_days < 1:
        raise RuntimeError("YOUTUBE_SMOKE_LOOKBACK_DAYS must be greater than or equal to 1.")

    end_at = datetime.now(UTC)
    start_at = end_at - timedelta(days=lookback_days)
    provider = YouTubeDataApiProvider(YouTubeApiConfig.from_env(runtime_env))
    channel_id = resolve_smoke_channel_id(
        {**runtime_env, **required_settings},
        provider,
        root / ".env",
    )
    summary = run_youtube_local_pipeline(provider, channel_id, start_at, end_at, root)

    print("YouTube local pipeline summary")
    print(f"provider={summary.result.provider}")
    print("channel_id=<configured>")
    print(f"raw_records={summary.result.raw_records}")
    print(f"loaded_records={summary.result.loaded_records}")
    print(f"processed_path={summary.processed_path.relative_to(root).as_posix()}")
    print(f"raw_root={summary.raw_root.relative_to(root).as_posix()}")
    return 0


if __name__ == "__main__":
    try:
        raise SystemExit(main())
    except RuntimeError as exc:
        print(f"Error: {exc}", file=sys.stderr)
        raise SystemExit(1) from None
