import argparse
import contextlib
import io
import json
import sys
from dataclasses import dataclass
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


def run_dashboard_smoke(
    project_root: Path,
    output_path: Path = DEFAULT_SMOKE_DASHBOARD_OUTPUT,
) -> DashboardSmokeSummary:
    target_output = output_path if output_path.is_absolute() else project_root / output_path
    smoke_root = project_root / SMOKE_WORK_DIR
    providers = build_mock_providers(project_root)
    youtube_processed_path = _write_processed_fixture_artifact(
        smoke_root,
        provider_name="youtube",
        account_id="sample-youtube-channel",
        output_dir=smoke_root / "data" / "processed" / "youtube",
        fixture_provider=providers["youtube"],
    )
    instagram_processed_path = _write_processed_fixture_artifact(
        smoke_root,
        provider_name="instagram",
        account_id="sample-instagram-account",
        output_dir=smoke_root / "data" / "processed" / "instagram",
        fixture_provider=providers["instagram"],
    )

    youtube_summary = build_youtube_report_summary(youtube_processed_path)
    youtube_report_path = write_youtube_report_json(
        youtube_summary,
        smoke_root,
        smoke_root / "data" / "reports" / "youtube-json" / "youtube-smoke.json",
        generated_at="2026-06-13T12:00:00Z",
    )
    instagram_summary = build_instagram_report_summary(instagram_processed_path)
    instagram_report_path = write_instagram_report_json(
        instagram_summary,
        smoke_root,
        smoke_root / "data" / "reports" / "instagram-json" / "instagram-smoke.json",
        generated_at="2026-06-13T12:00:00Z",
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
        youtube_processed_path=youtube_processed_path,
        instagram_processed_path=instagram_processed_path,
        youtube_report_path=youtube_report_path,
        instagram_report_path=instagram_report_path,
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
) -> Path:
    output_path = build_interval_artifact_path(
        output_dir,
        f"{provider_name}-smoke",
        SMOKE_START_AT,
        SMOKE_END_AT,
    )
    payloads = fixture_provider.collect_metrics(account_id, SMOKE_START_AT, SMOKE_END_AT)
    metrics = normalize_payloads(payloads, Path(f"data/fixtures/{provider_name}_metrics.json"))
    JsonMetricArtifactLoader(output_path).load(metrics)
    return output_path


def _write_smoke_channels_config(smoke_root: Path) -> Path:
    config_path = smoke_root / "config" / "channels.local.json"
    config_path.parent.mkdir(parents=True, exist_ok=True)
    payload = {
        "channels": [
            {
                "id": "sample-monitored-channel",
                "display_name": "Sample Monitored Channel",
                "image_url": "https://example.com/sample-channel.jpg",
                "platforms": {
                    "youtube": {
                        "channel_id": "yt-channel-1",
                        "handle": "Mock YouTube Channel",
                    },
                    "instagram": {
                        "account_id": "ig-account-1",
                        "handle": "example_instagram",
                    },
                },
            }
        ]
    }
    config_path.write_text(json.dumps(payload, indent=2), encoding="utf-8")
    return config_path


def _display_path(path: Path, project_root: Path) -> str:
    try:
        return path.relative_to(project_root).as_posix()
    except ValueError:
        return path.as_posix()


if __name__ == "__main__":
    raise SystemExit(cli_entrypoint())
