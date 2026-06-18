import argparse
import contextlib
import io
import json
import shutil
import sys
from dataclasses import dataclass, replace
from datetime import UTC, datetime
from pathlib import Path

from social_analytics_pipeline.cli.dashboard import main as build_dashboard
from social_analytics_pipeline.cli.instagram_report import (
    build_instagram_report_summary,
    write_instagram_report_json,
)
from social_analytics_pipeline.cli.youtube_report import (
    build_youtube_report_summary,
    write_youtube_report_json,
)
from social_analytics_pipeline.pipeline import (
    JsonMetricArtifactLoader,
    build_interval_artifact_path,
)
from social_analytics_pipeline.providers import build_mock_providers
from social_analytics_pipeline.transform import normalize_payloads

SMOKE_START_AT = datetime(2026, 5, 1, tzinfo=UTC)
SMOKE_END_AT = datetime(2026, 5, 27, tzinfo=UTC)
SMOKE_WORK_DIR = Path("data/temp/dashboard-smoke")
DEFAULT_SMOKE_DASHBOARD_OUTPUT = Path("data/dashboard/smoke.html")


@dataclass(frozen=True)
class DashboardSmokeSummary:
    youtube_processed_path: Path
    instagram_processed_path: Path
    youtube_report_path: Path
    instagram_report_path: Path
    channels_config_path: Path
    dashboard_path: Path


SMOKE_CHANNELS = (
    {
        "id": "sample-growth-lab",
        "display_name": "Growth Lab",
        "image_url": "https://example.com/channels/growth-lab.jpg",
        "youtube": {
            "account_id": "sample-youtube-growth-lab",
            "channel_name": "Growth Lab",
            "channel_image_url": "https://example.com/channels/growth-lab-youtube.jpg",
            "content_prefix": "Growth Lab",
            "view_multiplier": 1.0,
        },
        "instagram": {
            "account_id": "sample-instagram-growth-lab",
            "channel_name": "Growth Lab",
            "channel_image_url": "https://example.com/channels/growth-lab-instagram.jpg",
            "content_prefix": "Growth Lab",
            "view_multiplier": 1.0,
        },
    },
    {
        "id": "sample-creator-studio",
        "display_name": "Creator Studio",
        "image_url": "https://example.com/channels/creator-studio.jpg",
        "youtube": {
            "account_id": "sample-youtube-creator-studio",
            "channel_name": "Creator Studio",
            "channel_image_url": "https://example.com/channels/creator-studio-youtube.jpg",
            "content_prefix": "Creator Studio",
            "view_multiplier": 0.68,
        },
    },
    {
        "id": "sample-launch-room",
        "display_name": "Launch Room",
        "image_url": "https://example.com/channels/launch-room.jpg",
        "instagram": {
            "account_id": "sample-instagram-launch-room",
            "channel_name": "Launch Room",
            "channel_image_url": "https://example.com/channels/launch-room-instagram.jpg",
            "content_prefix": "Launch Room",
            "view_multiplier": 1.42,
        },
    },
)


def run_dashboard_smoke(
    project_root: Path,
    output_path: Path = DEFAULT_SMOKE_DASHBOARD_OUTPUT,
) -> DashboardSmokeSummary:
    target_output = output_path if output_path.is_absolute() else project_root / output_path
    smoke_root = project_root / SMOKE_WORK_DIR
    if smoke_root.exists():
        shutil.rmtree(smoke_root)
    providers = build_mock_providers(project_root)
    youtube_processed_paths: list[Path] = []
    instagram_processed_paths: list[Path] = []
    youtube_report_paths: list[Path] = []
    instagram_report_paths: list[Path] = []
    for channel in SMOKE_CHANNELS:
        youtube_variant = channel.get("youtube")
        if isinstance(youtube_variant, dict):
            youtube_processed_path = _write_processed_fixture_artifact(
                smoke_root,
                provider_name="youtube",
                account_id=str(youtube_variant["account_id"]),
                output_dir=smoke_root / "data" / "processed" / "youtube",
                fixture_provider=providers["youtube"],
                variant=youtube_variant,
            )
            youtube_processed_paths.append(youtube_processed_path)
            youtube_summary = build_youtube_report_summary(youtube_processed_path)
            youtube_report_paths.append(
                write_youtube_report_json(
                    youtube_summary,
                    smoke_root,
                    smoke_root
                    / "data"
                    / "reports"
                    / "youtube-json"
                    / f"youtube-{channel['id']}.json",
                    generated_at="2026-06-13T12:00:00Z",
                )
            )

        instagram_variant = channel.get("instagram")
        if isinstance(instagram_variant, dict):
            instagram_processed_path = _write_processed_fixture_artifact(
                smoke_root,
                provider_name="instagram",
                account_id=str(instagram_variant["account_id"]),
                output_dir=smoke_root / "data" / "processed" / "instagram",
                fixture_provider=providers["instagram"],
                variant=instagram_variant,
            )
            instagram_processed_paths.append(instagram_processed_path)
            instagram_summary = build_instagram_report_summary(instagram_processed_path)
            instagram_report_paths.append(
                write_instagram_report_json(
                    instagram_summary,
                    smoke_root,
                    smoke_root
                    / "data"
                    / "reports"
                    / "instagram-json"
                    / f"instagram-{channel['id']}.json",
                    generated_at="2026-06-13T12:00:00Z",
                )
            )
    channels_config_path = _write_smoke_channels_config(smoke_root)
    with contextlib.redirect_stdout(io.StringIO()):
        build_dashboard(
            output_path=target_output,
            project_root=smoke_root,
            all_reports=True,
            channels_config_path=channels_config_path,
        )

    return DashboardSmokeSummary(
        youtube_processed_path=youtube_processed_paths[0],
        instagram_processed_path=instagram_processed_paths[0],
        youtube_report_path=youtube_report_paths[0],
        instagram_report_path=instagram_report_paths[0],
        channels_config_path=channels_config_path,
        dashboard_path=target_output,
    )


def main(
    project_root: Path | None = None,
    output_path: Path = DEFAULT_SMOKE_DASHBOARD_OUTPUT,
    quiet: bool = False,
) -> int:
    root = project_root or Path.cwd()
    summary = run_dashboard_smoke(root, output_path)
    if not quiet:
        print("Dashboard smoke summary")
        print(f"youtube_processed_path={_display_path(summary.youtube_processed_path, root)}")
        print(f"instagram_processed_path={_display_path(summary.instagram_processed_path, root)}")
        print(f"youtube_report_path={_display_path(summary.youtube_report_path, root)}")
        print(f"instagram_report_path={_display_path(summary.instagram_report_path, root)}")
        print(f"channels_config_path={_display_path(summary.channels_config_path, root)}")
        print(f"dashboard_path={_display_path(summary.dashboard_path, root)}")
    return 0


def parse_args(argv: list[str] | None = None) -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Generate a safe sample multi-provider dashboard smoke artifact."
    )
    parser.add_argument(
        "--project-root",
        type=Path,
        default=Path.cwd(),
        help="Project root containing data/fixtures. Defaults to the current directory.",
    )
    parser.add_argument(
        "--output",
        type=Path,
        default=DEFAULT_SMOKE_DASHBOARD_OUTPUT,
        help=f"Dashboard output path. Defaults to {DEFAULT_SMOKE_DASHBOARD_OUTPUT}.",
    )
    parser.add_argument("--quiet", action="store_true", help="Suppress summary output.")
    return parser.parse_args(argv)


def cli_entrypoint() -> int:
    try:
        args = parse_args()
        return main(
            project_root=args.project_root,
            output_path=args.output,
            quiet=args.quiet,
        )
    except RuntimeError as exc:
        print(f"Error: {exc}", file=sys.stderr)
        return 1


def _write_processed_fixture_artifact(
    project_root: Path,
    provider_name: str,
    account_id: str,
    output_dir: Path,
    fixture_provider: object,
    variant: dict[str, object] | None = None,
) -> Path:
    output_path = build_interval_artifact_path(
        output_dir,
        f"{provider_name}-{account_id}",
        SMOKE_START_AT,
        SMOKE_END_AT,
    )
    payloads = fixture_provider.collect_metrics(account_id, SMOKE_START_AT, SMOKE_END_AT)
    metrics = normalize_payloads(payloads, Path(f"data/fixtures/{provider_name}_metrics.json"))
    if variant:
        metrics = [_smoke_metric_variant(metric, variant) for metric in metrics]
    JsonMetricArtifactLoader(output_path).load(metrics)
    return output_path


def _write_smoke_channels_config(smoke_root: Path) -> Path:
    config_path = smoke_root / "config" / "channels.local.json"
    config_path.parent.mkdir(parents=True, exist_ok=True)
    payload = {"channels": [_smoke_channel_config(channel) for channel in SMOKE_CHANNELS]}
    config_path.write_text(json.dumps(payload, indent=2), encoding="utf-8")
    return config_path


def _smoke_metric_variant(metric: object, variant: dict[str, object]) -> object:
    values = metric.__dict__.copy()
    values["account_id"] = str(variant["account_id"])
    values["channel_name"] = str(variant["channel_name"])
    values["channel_image_url"] = str(variant["channel_image_url"])
    prefix = str(variant["content_prefix"])
    values["content_id"] = f"{values['account_id']}-{values['content_id']}"
    if values.get("title"):
        values["title"] = f"{prefix}: {values['title']}"
    multiplier = float(variant.get("view_multiplier", 1.0))
    for field in ("views", "likes", "comments", "shares", "followers"):
        value = values.get(field)
        values[field] = round(value * multiplier) if value is not None else None
    return replace(metric, **values)


def _smoke_channel_config(channel: dict[str, object]) -> dict[str, object]:
    platforms: dict[str, dict[str, str]] = {
        "tiktok": {"handle": f"@{channel['id']}-tiktok"}
    }
    youtube = channel.get("youtube")
    if isinstance(youtube, dict):
        platforms["youtube"] = {
            "account_id": str(youtube["account_id"]),
            "handle": str(youtube["channel_name"]),
        }
    instagram = channel.get("instagram")
    if isinstance(instagram, dict):
        platforms["instagram"] = {
            "account_id": str(instagram["account_id"]),
            "handle": str(instagram["channel_name"]),
        }
    return {
        "id": str(channel["id"]),
        "display_name": str(channel["display_name"]),
        "image_url": str(channel["image_url"]),
        "platforms": platforms,
    }


def _display_path(path: Path, project_root: Path) -> str:
    try:
        return path.relative_to(project_root).as_posix()
    except ValueError:
        return path.as_posix()


if __name__ == "__main__":
    raise SystemExit(cli_entrypoint())
