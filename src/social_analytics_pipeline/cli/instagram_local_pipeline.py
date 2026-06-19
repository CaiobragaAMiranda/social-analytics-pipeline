import argparse
import json
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
    start_at_override: str | None = None,
    end_at_override: str | None = None,
    lookback_days_override: int | None = None,
) -> tuple[datetime, datetime]:
    if start_at_override or end_at_override:
        if not start_at_override or not end_at_override:
            raise RuntimeError("--start-at and --end-at must be set together.")
        start_at = _parse_configured_datetime(start_at_override, "--start-at")
        end_at = _parse_configured_datetime(end_at_override, "--end-at")
        if start_at > end_at:
            raise RuntimeError("--start-at must be before or equal to --end-at.")
        return start_at, end_at

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

    lookback_days = lookback_days_override
    if lookback_days is None:
        lookback_days = _parse_positive_int(
            runtime_env,
            "INSTAGRAM_SMOKE_LOOKBACK_DAYS",
            DEFAULT_INSTAGRAM_LOOKBACK_DAYS,
        )
    if lookback_days < 1:
        raise RuntimeError("Instagram lookback days must be greater than or equal to 1.")

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


def main(
    env: Mapping[str, str] | None = None,
    project_root: Path | None = None,
    argv: list[str] | None = None,
) -> int:
    root = project_root or Path.cwd()
    args = parse_args(argv or [])
    if args.list_run_summaries:
        return print_instagram_run_summary_paths(root, fail_if_missing=args.fail_if_missing)
    if args.count_run_summaries:
        return print_instagram_run_summary_count(root, fail_if_missing=args.fail_if_missing)
    if args.latest_run_summary:
        return print_latest_instagram_run_summary_path(root, fail_if_missing=args.fail_if_missing)
    if args.validate_run_summaries:
        return validate_instagram_run_summaries(root, fail_if_missing=args.fail_if_missing)
    if args.validate_latest_run_summary:
        return validate_latest_instagram_run_summary(root, fail_if_missing=args.fail_if_missing)
    if args.validate_run_summary:
        return validate_selected_instagram_run_summary(root, args.validate_run_summary)
    if args.show_run_summary:
        return print_selected_instagram_run_summary(root, args.show_run_summary)
    if args.show_latest_run_summary:
        return print_latest_instagram_run_summary(root, fail_if_missing=args.fail_if_missing)

    runtime_env = build_runtime_env(env, root / ".env")
    start_at, end_at = resolve_instagram_interval(
        runtime_env,
        start_at_override=args.start_at,
        end_at_override=args.end_at,
        lookback_days_override=args.lookback_days,
    )
    if args.dry_run:
        return print_instagram_local_pipeline_dry_run(
            runtime_env=runtime_env,
            start_at=start_at,
            end_at=end_at,
            project_root=root,
        )

    required_settings = require_instagram_settings(
        runtime_env,
        ("INSTAGRAM_ACCESS_TOKEN", "INSTAGRAM_USER_ID"),
        root / ".env",
    )
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
    enforce_instagram_loaded_records(summary, fail_if_empty=args.fail_if_empty)

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


def find_instagram_run_summary_artifacts(project_root: Path) -> list[Path]:
    return sorted((project_root / "data" / "runs" / "instagram").glob("instagram-run-*.json"))


def find_latest_instagram_run_summary_artifact(project_root: Path) -> Path | None:
    artifacts = find_instagram_run_summary_artifacts(project_root)
    if not artifacts:
        return None
    return artifacts[-1]


def print_latest_instagram_run_summary_path(
    project_root: Path,
    fail_if_missing: bool = False,
) -> int:
    artifact_path = find_latest_instagram_run_summary_artifact(project_root)
    if not artifact_path:
        print("No Instagram run summaries found.")
        if fail_if_missing:
            raise RuntimeError("No Instagram run summaries found.")
        return 0

    print(artifact_path.relative_to(project_root).as_posix())
    return 0


def print_instagram_run_summary_paths(
    project_root: Path,
    fail_if_missing: bool = False,
) -> int:
    artifact_paths = find_instagram_run_summary_artifacts(project_root)
    if not artifact_paths:
        print("No Instagram run summaries found.")
        if fail_if_missing:
            raise RuntimeError("No Instagram run summaries found.")
        return 0

    for artifact_path in artifact_paths:
        print(artifact_path.relative_to(project_root).as_posix())
    return 0


def print_instagram_run_summary_count(
    project_root: Path,
    fail_if_missing: bool = False,
) -> int:
    artifact_count = len(find_instagram_run_summary_artifacts(project_root))
    print(artifact_count)
    if fail_if_missing and artifact_count == 0:
        raise RuntimeError("No Instagram run summaries found.")
    return 0


def print_latest_instagram_run_summary(
    project_root: Path,
    fail_if_missing: bool = False,
) -> int:
    artifact_path = find_latest_instagram_run_summary_artifact(project_root)
    if not artifact_path:
        print("No Instagram run summaries found.")
        if fail_if_missing:
            raise RuntimeError("No Instagram run summaries found.")
        return 0

    return print_instagram_run_summary(
        project_root,
        artifact_path,
        heading="Latest Instagram run summary",
    )


def print_selected_instagram_run_summary(project_root: Path, run_summary_path: str) -> int:
    artifact_path = resolve_instagram_run_summary_path(project_root, run_summary_path)
    return print_instagram_run_summary(project_root, artifact_path, heading="Instagram run summary")


def validate_latest_instagram_run_summary(
    project_root: Path,
    fail_if_missing: bool = False,
) -> int:
    artifact_path = find_latest_instagram_run_summary_artifact(project_root)
    if not artifact_path:
        print("No Instagram run summaries found.")
        if fail_if_missing:
            raise RuntimeError("No Instagram run summaries found.")
        return 0
    return validate_instagram_run_summary(
        project_root,
        artifact_path,
        heading="Latest Instagram run summary validation",
    )


def validate_instagram_run_summaries(
    project_root: Path,
    fail_if_missing: bool = False,
) -> int:
    artifact_paths = find_instagram_run_summary_artifacts(project_root)
    if not artifact_paths:
        print("No Instagram run summaries found.")
        if fail_if_missing:
            raise RuntimeError("No Instagram run summaries found.")
        return 0

    root = project_root.resolve()
    for artifact_path in artifact_paths:
        try:
            payload = load_instagram_run_summary_payload(artifact_path)
            validate_instagram_run_summary_payload(payload)
        except RuntimeError as exc:
            relative_path = artifact_path.resolve().relative_to(root).as_posix()
            raise RuntimeError(f"Invalid Instagram run summary {relative_path}: {exc}") from exc

    print("Instagram run summaries validation")
    print(f"valid_summaries={len(artifact_paths)}")
    return 0


def validate_selected_instagram_run_summary(project_root: Path, run_summary_path: str) -> int:
    artifact_path = resolve_instagram_run_summary_path(project_root, run_summary_path)
    return validate_instagram_run_summary(
        project_root,
        artifact_path,
        heading="Instagram run summary validation",
    )


def validate_instagram_run_summary(
    project_root: Path,
    artifact_path: Path,
    heading: str,
) -> int:
    payload = load_instagram_run_summary_payload(artifact_path)
    validate_instagram_run_summary_payload(payload)
    counts = payload["counts"]
    print(heading)
    print(f"run_summary_path={artifact_path.relative_to(project_root.resolve()).as_posix()}")
    print("status=valid")
    print(f"provider={payload['provider']}")
    print(f"run_status={payload['status']}")
    print(f"raw_records={counts['raw_records']}")
    print(f"valid_records={counts['valid_records']}")
    print(f"invalid_records={counts['invalid_records']}")
    print(f"loaded_records={counts['loaded_records']}")
    return 0


def resolve_instagram_run_summary_path(project_root: Path, run_summary_path: str) -> Path:
    root = project_root.resolve()
    candidate = Path(run_summary_path)
    if not candidate.is_absolute():
        candidate = root / candidate
    artifact_path = candidate.resolve()

    try:
        artifact_path.relative_to(root)
    except ValueError as exc:
        raise RuntimeError("Instagram run summary path must stay inside the project root.") from exc

    if not artifact_path.exists():
        raise RuntimeError("Instagram run summary not found.")
    if not artifact_path.is_file():
        raise RuntimeError("Instagram run summary path must point to a file.")
    return artifact_path


def load_instagram_run_summary_payload(artifact_path: Path) -> dict[str, object]:
    try:
        payload = json.loads(artifact_path.read_text(encoding="utf-8"))
    except json.JSONDecodeError as exc:
        raise RuntimeError("Invalid Instagram run summary JSON.") from exc
    if not isinstance(payload, dict):
        raise RuntimeError("Instagram run summary JSON must be an object.")
    return payload


def validate_instagram_run_summary_payload(payload: Mapping[str, object]) -> None:
    missing_fields = [
        field
        for field in ("provider", "status", "interval", "counts")
        if field not in payload
    ]
    interval = payload.get("interval")
    if not isinstance(interval, Mapping):
        missing_fields.append("interval.start_at")
        missing_fields.append("interval.end_at")
    else:
        missing_fields.extend(
            field
            for field in ("start_at", "end_at")
            if field not in interval
        )

    counts = payload.get("counts")
    if not isinstance(counts, Mapping):
        missing_fields.append("counts.raw_records")
        missing_fields.append("counts.valid_records")
        missing_fields.append("counts.invalid_records")
        missing_fields.append("counts.loaded_records")
    else:
        missing_fields.extend(
            f"counts.{field}"
            for field in ("raw_records", "valid_records", "invalid_records", "loaded_records")
            if field not in counts
        )

    if missing_fields:
        missing = ", ".join(dict.fromkeys(missing_fields))
        raise RuntimeError(f"Instagram run summary is missing required fields: {missing}.")


def print_instagram_run_summary(
    project_root: Path,
    artifact_path: Path,
    heading: str,
) -> int:
    root = project_root.resolve()
    payload = load_instagram_run_summary_payload(artifact_path)
    counts = payload.get("counts", {})
    interval = payload.get("interval", {})
    print(heading)
    print(f"run_summary_path={artifact_path.resolve().relative_to(root).as_posix()}")
    print(f"provider={payload.get('provider', 'instagram')}")
    print(f"status={payload.get('status', 'unknown')}")
    print(f"interval_start_at={interval.get('start_at', '')}")
    print(f"interval_end_at={interval.get('end_at', '')}")
    print(f"raw_records={counts.get('raw_records', 0)}")
    print(f"valid_records={counts.get('valid_records', 0)}")
    print(f"invalid_records={counts.get('invalid_records', 0)}")
    print(f"loaded_records={counts.get('loaded_records', 0)}")
    return 0


def enforce_instagram_loaded_records(
    summary: InstagramLocalPipelineSummary,
    fail_if_empty: bool,
) -> None:
    if fail_if_empty and summary.result.loaded_records == 0:
        raise RuntimeError(
            "Instagram local pipeline loaded 0 records. Review account access, "
            "the selected interval or media availability."
        )


def print_instagram_local_pipeline_dry_run(
    runtime_env: Mapping[str, str],
    start_at: datetime,
    end_at: datetime,
    project_root: Path,
) -> int:
    _, processed_path = build_instagram_local_loader(
        runtime_env=runtime_env,
        provider_name="instagram",
        start_at=start_at,
        end_at=end_at,
        project_root=project_root,
    )
    raw_root = project_root / "data" / "raw"
    run_summary_path = build_run_summary_artifact_path(
        project_root / "data" / "runs" / "instagram",
        "instagram",
        start_at,
        end_at,
    )
    credentials_configured = (
        bool(runtime_env.get("INSTAGRAM_ACCESS_TOKEN"))
        and bool(runtime_env.get("INSTAGRAM_USER_ID"))
    )

    print("Instagram local pipeline dry run")
    print("provider=instagram")
    print(f"credentials_configured={'yes' if credentials_configured else 'no'}")
    print(f"interval_start_at={start_at.isoformat()}")
    print(f"interval_end_at={end_at.isoformat()}")
    print(f"load_target={runtime_env.get('INSTAGRAM_LOCAL_LOAD_TARGET', 'json').lower()}")
    print(f"planned_processed_path={processed_path.relative_to(project_root).as_posix()}")
    print(f"planned_raw_root={raw_root.relative_to(project_root).as_posix()}")
    print(f"planned_run_summary_path={run_summary_path.relative_to(project_root).as_posix()}")
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


def parse_args(argv: list[str] | None = None) -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Run the local Instagram provider pipeline into ignored JSON artifacts."
    )
    summary_modes = parser.add_mutually_exclusive_group()
    summary_modes.add_argument(
        "--list-run-summaries",
        action="store_true",
        help="List local Instagram run-summary artifact paths without API calls.",
    )
    summary_modes.add_argument(
        "--count-run-summaries",
        action="store_true",
        help="Print the number of local Instagram run-summary artifacts without API calls.",
    )
    summary_modes.add_argument(
        "--latest-run-summary",
        action="store_true",
        help="Print the latest local Instagram run-summary artifact path without API calls.",
    )
    summary_modes.add_argument(
        "--show-latest-run-summary",
        action="store_true",
        help="Print compact status and counts from the latest local Instagram run summary.",
    )
    summary_modes.add_argument(
        "--validate-latest-run-summary",
        action="store_true",
        help="Validate the latest local Instagram run summary without API calls.",
    )
    summary_modes.add_argument(
        "--validate-run-summaries",
        action="store_true",
        help="Validate all local Instagram run summaries without API calls.",
    )
    summary_modes.add_argument(
        "--validate-run-summary",
        help="Validate a selected local Instagram run-summary path without API calls.",
    )
    summary_modes.add_argument(
        "--show-run-summary",
        help="Print compact status and counts from a selected local Instagram run-summary path.",
    )
    parser.add_argument(
        "--dry-run",
        action="store_true",
        help=(
            "Print the planned local Instagram pipeline inputs and artifact paths "
            "without API calls."
        ),
    )
    parser.add_argument(
        "--start-at",
        help="ISO-8601 interval start. Must be used with --end-at.",
    )
    parser.add_argument(
        "--end-at",
        help="ISO-8601 interval end. Must be used with --start-at.",
    )
    parser.add_argument(
        "--lookback-days",
        type=_parse_arg_positive_int,
        help="Lookback window for default interval planning.",
    )
    parser.add_argument(
        "--fail-if-empty",
        action="store_true",
        help="Fail after a real local run when no records are loaded.",
    )
    parser.add_argument(
        "--fail-if-missing",
        action="store_true",
        help="Fail list-style local inspection modes when no matching artifact exists.",
    )
    return parser.parse_args(argv)


def _parse_arg_positive_int(value: str) -> int:
    try:
        parsed = int(value)
    except ValueError as exc:
        raise argparse.ArgumentTypeError("must be an integer") from exc
    if parsed < 1:
        raise argparse.ArgumentTypeError("must be greater than or equal to 1")
    return parsed


def cli_entrypoint() -> int:
    return main(argv=sys.argv[1:])


if __name__ == "__main__":
    try:
        raise SystemExit(cli_entrypoint())
    except RuntimeError as exc:
        print(f"Error: {exc}", file=sys.stderr)
        raise SystemExit(1) from None
