import unittest
from datetime import UTC, datetime
from pathlib import Path
from tempfile import TemporaryDirectory
from typing import Any

from social_analytics_pipeline.cli.youtube_smoke import (
    build_runtime_env,
    build_youtube_smoke_summary,
    load_env_file,
    main,
    require_smoke_setting,
    require_smoke_settings,
    require_youtube_channel_id,
    resolve_backfill_interval,
    resolve_smoke_channel_id,
)


class FakeYouTubeCollector:
    def collect_metrics(
        self,
        account_id: str,
        start_at: datetime,
        end_at: datetime,
    ) -> list[dict[str, Any]]:
        return [
            {
                "id": "yt-video-001",
                "snippet": {"publishedAt": "2026-05-20T14:30:00Z"},
                "statistics": {"likeCount": "10", "commentCount": "2", "viewCount": "100"},
                "_collection": {
                    "provider": "youtube",
                    "account_id": account_id,
                    "start_at": start_at.isoformat(),
                    "end_at": end_at.isoformat(),
                },
            }
        ]


class FakeYouTubeResolver:
    def __init__(self) -> None:
        self.handles: list[str] = []

    def resolve_channel_id(self, handle: str) -> str:
        self.handles.append(handle)
        return "UCresolved123"


class YouTubeSmokeTest(unittest.TestCase):
    def test_build_youtube_smoke_summary_counts_raw_and_normalized_records(self) -> None:
        start_at = datetime(2026, 5, 1, tzinfo=UTC)
        end_at = datetime(2026, 5, 27, tzinfo=UTC)

        summary = build_youtube_smoke_summary(
            FakeYouTubeCollector(),
            "yt-channel-1",
            start_at,
            end_at,
        )

        self.assertEqual(summary.provider, "youtube")
        self.assertEqual(summary.channel_id, "yt-channel-1")
        self.assertEqual(summary.raw_records, 1)
        self.assertEqual(summary.normalized_records, 1)

    def test_main_reports_missing_api_key_before_network(self) -> None:
        with TemporaryDirectory() as tmpdir:
            missing_env_path = Path(tmpdir) / ".env"

            with self.assertRaisesRegex(RuntimeError, "YOUTUBE_API_KEY"):
                main({}, missing_env_path)

    def test_require_smoke_setting_explains_missing_env_file(self) -> None:
        with TemporaryDirectory() as tmpdir:
            missing_env_path = Path(tmpdir) / ".env"

            with self.assertRaisesRegex(RuntimeError, "Create a local .env"):
                require_smoke_setting({}, "YOUTUBE_CHANNEL_ID", missing_env_path)

    def test_require_smoke_setting_explains_empty_existing_env_file(self) -> None:
        with TemporaryDirectory() as tmpdir:
            env_path = Path(tmpdir) / ".env"
            env_path.write_text("", encoding="utf-8")

            with self.assertRaisesRegex(RuntimeError, "environment or local .env"):
                require_smoke_setting({}, "YOUTUBE_CHANNEL_ID", env_path)

    def test_require_smoke_setting_returns_configured_value(self) -> None:
        value = require_smoke_setting({"YOUTUBE_CHANNEL_ID": "yt-channel-1"}, "YOUTUBE_CHANNEL_ID")

        self.assertEqual(value, "yt-channel-1")

    def test_require_smoke_settings_reports_missing_env_file(self) -> None:
        with TemporaryDirectory() as tmpdir:
            missing_env_path = Path(tmpdir) / ".env"

            with self.assertRaisesRegex(RuntimeError, "YOUTUBE_CHANNEL_ID, YOUTUBE_API_KEY"):
                require_smoke_settings(
                    {},
                    ("YOUTUBE_CHANNEL_ID", "YOUTUBE_API_KEY"),
                    missing_env_path,
                )

    def test_require_smoke_settings_reports_all_empty_existing_env_values(self) -> None:
        with TemporaryDirectory() as tmpdir:
            env_path = Path(tmpdir) / ".env"
            env_path.write_text("", encoding="utf-8")

            with self.assertRaisesRegex(RuntimeError, "YOUTUBE_CHANNEL_ID, YOUTUBE_API_KEY"):
                require_smoke_settings(
                    {},
                    ("YOUTUBE_CHANNEL_ID", "YOUTUBE_API_KEY"),
                    env_path,
                )

    def test_require_smoke_settings_returns_configured_values(self) -> None:
        values = require_smoke_settings(
            {
                "YOUTUBE_CHANNEL_ID": "yt-channel-1",
                "YOUTUBE_API_KEY": "test-api-key",
            },
            ("YOUTUBE_CHANNEL_ID", "YOUTUBE_API_KEY"),
        )

        self.assertEqual(values["YOUTUBE_CHANNEL_ID"], "yt-channel-1")
        self.assertEqual(values["YOUTUBE_API_KEY"], "test-api-key")

    def test_require_youtube_channel_id_rejects_names_and_handles(self) -> None:
        with self.assertRaisesRegex(RuntimeError, "starts with UC"):
            require_youtube_channel_id("Channel Name")

    def test_require_youtube_channel_id_accepts_public_channel_id(self) -> None:
        self.assertEqual(require_youtube_channel_id("UCabc123"), "UCabc123")

    def test_resolve_smoke_channel_id_prefers_channel_id(self) -> None:
        resolver = FakeYouTubeResolver()

        channel_id = resolve_smoke_channel_id(
            {
                "YOUTUBE_CHANNEL_ID": "UCabc123",
                "YOUTUBE_CHANNEL_HANDLE": "@public-handle",
            },
            resolver,
        )

        self.assertEqual(channel_id, "UCabc123")
        self.assertEqual(resolver.handles, [])

    def test_resolve_smoke_channel_id_uses_handle_when_channel_id_missing(self) -> None:
        resolver = FakeYouTubeResolver()

        channel_id = resolve_smoke_channel_id(
            {"YOUTUBE_CHANNEL_HANDLE": "@public-handle"},
            resolver,
        )

        self.assertEqual(channel_id, "UCresolved123")
        self.assertEqual(resolver.handles, ["@public-handle"])

    def test_resolve_smoke_channel_id_requires_id_or_handle(self) -> None:
        with TemporaryDirectory() as tmpdir:
            env_path = Path(tmpdir) / ".env"
            env_path.write_text("", encoding="utf-8")

            expected_error = "YOUTUBE_CHANNEL_ID or YOUTUBE_CHANNEL_HANDLE"
            with self.assertRaisesRegex(RuntimeError, expected_error):
                resolve_smoke_channel_id({}, FakeYouTubeResolver(), env_path)

    def test_resolve_backfill_interval_returns_none_when_unset(self) -> None:
        self.assertIsNone(resolve_backfill_interval({}))

    def test_resolve_backfill_interval_reads_explicit_utc_range(self) -> None:
        interval = resolve_backfill_interval(
            {
                "YOUTUBE_BACKFILL_START_AT": "2026-05-01T00:00:00Z",
                "YOUTUBE_BACKFILL_END_AT": "2026-05-15T00:00:00Z",
            }
        )

        assert interval is not None
        start_at, end_at = interval
        self.assertEqual(start_at, datetime(2026, 5, 1, tzinfo=UTC))
        self.assertEqual(end_at, datetime(2026, 5, 15, tzinfo=UTC))

    def test_resolve_backfill_interval_requires_both_values(self) -> None:
        with self.assertRaisesRegex(RuntimeError, "must be set together"):
            resolve_backfill_interval({"YOUTUBE_BACKFILL_START_AT": "2026-05-01T00:00:00Z"})

    def test_resolve_backfill_interval_rejects_missing_timezone(self) -> None:
        with self.assertRaisesRegex(RuntimeError, "timezone"):
            resolve_backfill_interval(
                {
                    "YOUTUBE_BACKFILL_START_AT": "2026-05-01T00:00:00",
                    "YOUTUBE_BACKFILL_END_AT": "2026-05-15T00:00:00Z",
                }
            )

    def test_resolve_backfill_interval_rejects_reversed_range(self) -> None:
        with self.assertRaisesRegex(RuntimeError, "before or equal"):
            resolve_backfill_interval(
                {
                    "YOUTUBE_BACKFILL_START_AT": "2026-05-16T00:00:00Z",
                    "YOUTUBE_BACKFILL_END_AT": "2026-05-15T00:00:00Z",
                }
            )

    def test_load_env_file_reads_simple_values_without_logging_secrets(self) -> None:
        with TemporaryDirectory() as tmpdir:
            env_path = Path(tmpdir) / ".env"
            env_path.write_text(
                "\n".join(
                    [
                        "# local only",
                        "YOUTUBE_API_KEY='test-api-key'",
                        'YOUTUBE_CHANNEL_ID="yt-channel-1"',
                        "YOUTUBE_MAX_PAGES=2",
                        "",
                    ]
                ),
                encoding="utf-8",
            )

            values = load_env_file(env_path)

        self.assertEqual(values["YOUTUBE_API_KEY"], "test-api-key")
        self.assertEqual(values["YOUTUBE_CHANNEL_ID"], "yt-channel-1")
        self.assertEqual(values["YOUTUBE_MAX_PAGES"], "2")

    def test_build_runtime_env_prefers_explicit_environment_over_env_file(self) -> None:
        with TemporaryDirectory() as tmpdir:
            env_path = Path(tmpdir) / ".env"
            env_path.write_text("YOUTUBE_MAX_PAGES=1", encoding="utf-8")

            values = build_runtime_env({"YOUTUBE_MAX_PAGES": "3"}, env_path)

        self.assertEqual(values["YOUTUBE_MAX_PAGES"], "3")


if __name__ == "__main__":
    unittest.main()
