import sys
from collections.abc import Mapping
from dataclasses import dataclass
from datetime import UTC, datetime, timedelta
from pathlib import Path
from typing import Any

from social_analytics_pipeline.cli.youtube_smoke import build_runtime_env
from social_analytics_pipeline.pipeline import (
    JsonMetricArtifactLoader,
    LocalPipelineResult,
    MetricLoader,
    build_interval_artifact_path,
    build_run_summary_artifact_path,
    run_provider_pipeline,
    write_json_artifact,
)
from social_analytics_pipeline.providers import InstagramApiConfig, InstagramGraphApiProvider
from social_analytics_pipeline.storage import RawStorage

DEFAULT_INSTAGRAM_LOOKBACK_DAYS = 30


@dataclass(frozen=True)
class InstagramLocalPipelineSummary:
    result: LocalPipelineResult
    processed_path: Path
    raw_root: Path
    run_summary_path: Path


def run_instagram_local_pipeline(
    provider: InstagramGraphApiProvider,
    account_id: str,
    start_at: datetime,
    end_at: datetime,
    project_root: Path,
    loader: MetricLoader | None = None,
) -> InstagramLocalPipelineSummary:
    processed_path = build_interval_artifact_path(
        project_root / "data" / "processed" / "instagram",
        provider.name,
        start_at,
        end_at,
    )
    raw_root = project_root / "data" / "raw"

    result = run_provider_pipeline(
        provider=provider,
        account_id=account_id,
        start_at=start_at,
        end_at=end_at,
        raw_storage=RawStorage(raw_root),
        loader=loader or JsonMetricArtifactLoader(processed_path),
    )
    run_summary_path = build_run_summary_artifact_path(
        project_root / "data" / "runs" / "instagram",
        provider.name,
        start_at,
        end_at,
    )
    write_json_artifact(
        run_summary_path,
        build_instagram_run_summary_payload(
            summary_result=result,
            processed_path=processed_path,
            raw_root=raw_root,
            run_summary_path=run_summary_path,
            start_at=start_at,
            end_at=end_at,
            project_root=project_root,
        ),
    )

    return InstagramLocalPipelineSummary(
        result=result,
        processed_path=processed_path,
        raw_root=raw_root,
        run_summary_path=run_summary_path,
    )


def build_instagram_local_loader(
    runtime_env: Mapping[str, str],
    provider_name: str,
    start_at: datetime,
    end_at: datetime,
    project_root: Path,
) -> tuple[MetricLoader, Path]:
    processed_path = build_interval_artifact_path(
        project_root / "data" / "processed" / "instagram",
        provider_name,
        start_at,
        end_at,
    )
    target = runtime_env.get("INSTAGRAM_LOCAL_LOAD_TARGET", "json").lower()
    if target == "json":
        return JsonMetricArtifactLoader(processed_path), processed_path
    raise RuntimeError("INSTAGRAM_LOCAL_LOAD_TARGET must be 'json'.")


def resolve_instagram_interval(
    runtime_env: Mapping[str, str],
    now: datetime | None = None,
) -> tuple[datetime, datetime]:
    start_value = runtime_env.get("INSTAGRAM_BACKFILL_START_AT", "").strip()
    end_value = runtime_env.get("INSTAGRAM_BACKFILL_END_AT", "").strip()
    if start_value or end_value:
        if not start_value or not end_value:
            raise RuntimeError(
                "INSTAGRAM_BACKFILL_START_AT and INSTAGRAM_BACKFILL_END_AT must be set together."
            )
        start_at = _parse_configured_datetime(start_value, "INSTAGRAM_BACKFILL_START_AT")
        end_at = _parse_configured_datetime(end_value, "INSTAGRAM_BACKFILL_END_AT")
        if start_at > end_at:
            raise RuntimeError(
                "INSTAGRAM_BACKFILL_START_AT must be before or equal to "
                "INSTAGRAM_BACKFILL_END_AT."
            )
        return start_at, end_at

    lookback_days = _parse_positive_int(
        runtime_env,
        "INSTAGRAM_SMOKE_LOOKBACK_DAYS",
        DEFAULT_INSTAGRAM_LOOKBACK_DAYS,
    )
    if lookback_days < 1:
        raise RuntimeError("INSTAGRAM_SMOKE_LOOKBACK_DAYS must be greater than or equal to 1.")

    end_at = now or datetime.now(UTC)
    return end_at - timedelta(days=lookback_days), end_at


def build_instagram_run_summary_payload(
    summary_result: LocalPipelineResult,
    processed_path: Path,
    raw_root: Path,
    run_summary_path: Path,
    start_at: datetime,
    end_at: datetime,
    project_root: Path,
) -> dict[str, Any]:
    return {
        "provider": summary_result.provider,
        "status": "warning" if summary_result.invalid_records else "ok",
        "interval": {
            "start_at": start_at.isoformat(),
            "end_at": end_at.isoformat(),
        },
        "counts": {
            "raw_records": summary_result.raw_records,
            "valid_records": summary_result.valid_records,
            "invalid_records": summary_result.invalid_records,
            "loaded_records": summary_result.loaded_records,
        },
        "artifacts": {
            "processed_path": processed_path.relative_to(project_root).as_posix(),
            "raw_root": raw_root.relative_to(project_root).as_posix(),
            "run_summary_path": run_summary_path.relative_to(project_root).as_posix(),
        },
    }


def main(env: Mapping[str, str] | None = None, project_root: Path | None = None) -> int:
    root = project_root or Path.cwd()
    runtime_env = build_runtime_env(env, root / ".env")
    required_settings = require_instagram_settings(
        runtime_env,
        ("INSTAGRAM_ACCESS_TOKEN", "INSTAGRAM_USER_ID"),
        root / ".env",
    )
    start_at, end_at = resolve_instagram_interval(runtime_env)
    provider = InstagramGraphApiProvider(InstagramApiConfig.from_env(runtime_env))
    account_id = required_settings["INSTAGRAM_USER_ID"]
    loader, processed_path = build_instagram_local_loader(
        runtime_env,
        provider.name,
        start_at,
        end_at,
        root,
    )
    summary = run_instagram_local_pipeline(
        provider=provider,
        account_id=account_id,
        start_at=start_at,
        end_at=end_at,
        project_root=root,
        loader=loader,
    )

    print("Instagram local pipeline summary")
    print(f"provider={summary.result.provider}")
    print("account_id=<configured>")
    print(f"raw_records={summary.result.raw_records}")
    print(f"valid_records={summary.result.valid_records}")
    print(f"invalid_records={summary.result.invalid_records}")
    print(f"loaded_records={summary.result.loaded_records}")
    print(f"load_target={runtime_env.get('INSTAGRAM_LOCAL_LOAD_TARGET', 'json').lower()}")
    print(f"processed_path={processed_path.relative_to(root).as_posix()}")
    print(f"raw_root={summary.raw_root.relative_to(root).as_posix()}")
    print(f"run_summary_path={summary.run_summary_path.relative_to(root).as_posix()}")
    return 0


def require_instagram_settings(
    runtime_env: Mapping[str, str],
    keys: tuple[str, ...],
    env_path: Path | None = None,
) -> dict[str, str]:
    missing = [key for key in keys if not runtime_env.get(key, "")]
    if not missing:
        return {key: runtime_env[key] for key in keys}

    missing_text = ", ".join(missing)
    if not (env_path or Path(".env")).exists():
        raise RuntimeError(
            f"{missing_text} required. Create a local .env from .env.example "
            "and fill Instagram settings."
        )

    raise RuntimeError(f"{missing_text} required in environment or local .env.")


def _parse_configured_datetime(value: str, key: str) -> datetime:
    try:
        return datetime.fromisoformat(value.replace("Z", "+00:00"))
    except ValueError as exc:
        raise RuntimeError(f"{key} must be an ISO-8601 datetime.") from exc


def _parse_positive_int(env: Mapping[str, str], key: str, default: int) -> int:
    raw_value = env.get(key)
    if raw_value is None:
        return default
    try:
        return int(raw_value)
    except ValueError as exc:
        raise RuntimeError(f"{key} must be an integer.") from exc


if __name__ == "__main__":
    try:
        raise SystemExit(main())
    except RuntimeError as exc:
        print(f"Error: {exc}", file=sys.stderr)
        raise SystemExit(1) from None
