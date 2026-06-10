import json
import unittest
from datetime import UTC, datetime
from pathlib import Path
from tempfile import TemporaryDirectory
from typing import Any

from social_analytics_pipeline.cli.youtube_local_pipeline import (
    build_youtube_local_loader,
    enforce_invalid_record_policy,
    run_youtube_local_pipeline,
)
from social_analytics_pipeline.load import PostgresMetricLoader
from social_analytics_pipeline.pipeline import JsonMetricArtifactLoader
from social_analytics_pipeline.providers import YouTubeApiConfig, YouTubeDataApiProvider


class FakeHttpJsonClient:
    def get_json(self, url: str, params: dict[str, str | int]) -> dict[str, Any]:
        if url.endswith("/search"):
            return {
                "items": [{"id": {"videoId": "yt-video-001"}}],
            }

        if url.endswith("/videos"):
            return {
                "items": [
                    {
                        "id": "yt-video-001",
                        "snippet": {"publishedAt": "2026-05-20T14:30:00Z"},
                        "statistics": {
                            "likeCount": "10",
                            "commentCount": "2",
                            "viewCount": "100",
                        },
                    }
                ]
            }

        raise AssertionError(f"Unexpected URL: {url}")


class FakeInvalidHttpJsonClient:
    def get_json(self, url: str, params: dict[str, str | int]) -> dict[str, Any]:
        if url.endswith("/search"):
            return {
                "items": [{"id": {"videoId": "yt-video-001"}}],
            }

        if url.endswith("/videos"):
            return {
                "items": [
                    {
                        "id": "yt-video-001",
                        "snippet": {"publishedAt": "2026-05-20T14:30:00Z"},
                        "statistics": {
                            "likeCount": "-10",
                            "commentCount": "2",
                            "viewCount": "100",
                        },
                    }
                ]
            }

        raise AssertionError(f"Unexpected URL: {url}")


class YouTubeLocalPipelineTest(unittest.TestCase):
    def test_runs_youtube_provider_into_raw_and_processed_artifacts(self) -> None:
        provider = YouTubeDataApiProvider(
            YouTubeApiConfig(api_key="test-api-key"),
            http_client=FakeHttpJsonClient(),
        )

        with TemporaryDirectory() as tmpdir:
            project_root = Path(tmpdir)
            summary = run_youtube_local_pipeline(
                provider=provider,
                channel_id="UCtestchannel",
                start_at=datetime(2026, 5, 1, tzinfo=UTC),
                end_at=datetime(2026, 5, 27, tzinfo=UTC),
                project_root=project_root,
            )

            raw_files = sorted((project_root / "data" / "raw").glob("youtube/**/*.json"))
            processed_rows = json.loads(summary.processed_path.read_text(encoding="utf-8"))
            run_summary = json.loads(summary.run_summary_path.read_text(encoding="utf-8"))
            run_summary_exists = summary.run_summary_path.exists()

        self.assertEqual(summary.result.provider, "youtube")
        self.assertEqual(summary.result.raw_records, 1)
        self.assertEqual(summary.result.valid_records, 1)
        self.assertEqual(summary.result.loaded_records, 1)
        self.assertEqual(len(raw_files), 1)
        self.assertEqual(len(processed_rows), 1)
        self.assertTrue(run_summary_exists)
        self.assertEqual(processed_rows[0]["provider"], "youtube")
        self.assertEqual(processed_rows[0]["content_id"], "yt-video-001")
        self.assertEqual(run_summary["provider"], "youtube")
        self.assertEqual(run_summary["status"], "ok")
        self.assertEqual(run_summary["counts"]["valid_records"], 1)
        self.assertEqual(
            run_summary["artifacts"]["processed_path"],
            summary.processed_path.relative_to(project_root).as_posix(),
        )

    def test_enforce_invalid_record_policy_raises_when_enabled(self) -> None:
        provider = YouTubeDataApiProvider(
            YouTubeApiConfig(api_key="test-api-key"),
            http_client=FakeInvalidHttpJsonClient(),
        )

        with TemporaryDirectory() as tmpdir:
            project_root = Path(tmpdir)
            summary = run_youtube_local_pipeline(
                provider=provider,
                channel_id="UCtestchannel",
                start_at=datetime(2026, 5, 1, tzinfo=UTC),
                end_at=datetime(2026, 5, 27, tzinfo=UTC),
                project_root=project_root,
            )

            with self.assertRaisesRegex(RuntimeError, "invalid records"):
                enforce_invalid_record_policy(
                    {"YOUTUBE_FAIL_ON_INVALID_RECORDS": "true"},
                    summary,
                )

    def test_enforce_invalid_record_policy_allows_warning_mode(self) -> None:
        provider = YouTubeDataApiProvider(
            YouTubeApiConfig(api_key="test-api-key"),
            http_client=FakeInvalidHttpJsonClient(),
        )

        with TemporaryDirectory() as tmpdir:
            project_root = Path(tmpdir)
            summary = run_youtube_local_pipeline(
                provider=provider,
                channel_id="UCtestchannel",
                start_at=datetime(2026, 5, 1, tzinfo=UTC),
                end_at=datetime(2026, 5, 27, tzinfo=UTC),
                project_root=project_root,
            )
            run_summary = json.loads(summary.run_summary_path.read_text(encoding="utf-8"))

        self.assertEqual(summary.result.valid_records, 0)
        self.assertEqual(summary.result.invalid_records, 1)
        enforce_invalid_record_policy({}, summary)
        self.assertEqual(run_summary["status"], "warning")
        self.assertEqual(run_summary["counts"]["invalid_records"], 1)

    def test_build_youtube_local_loader_defaults_to_json_artifact(self) -> None:
        loader, processed_path = build_youtube_local_loader(
            runtime_env={},
            provider_name="youtube",
            start_at=datetime(2026, 5, 1, tzinfo=UTC),
            end_at=datetime(2026, 5, 27, tzinfo=UTC),
            project_root=Path("project"),
        )

        self.assertIsInstance(loader, JsonMetricArtifactLoader)
        self.assertEqual(
            processed_path.as_posix(),
            "project/data/processed/youtube/youtube-20260501T000000-20260527T000000.json",
        )

    def test_build_youtube_local_loader_uses_postgres_when_enabled(self) -> None:
        loader, processed_path = build_youtube_local_loader(
            runtime_env={
                "YOUTUBE_LOCAL_LOAD_TARGET": "postgres",
                "SOCIAL_ANALYTICS_POSTGRES_DSN": "postgresql://example",
            },
            provider_name="youtube",
            start_at=datetime(2026, 5, 1, tzinfo=UTC),
            end_at=datetime(2026, 5, 27, tzinfo=UTC),
            project_root=Path("project"),
        )

        self.assertIsInstance(loader, PostgresMetricLoader)
        self.assertEqual(loader.dsn, "postgresql://example")
        self.assertEqual(
            processed_path.as_posix(),
            "project/data/processed/youtube/youtube-20260501T000000-20260527T000000.json",
        )

    def test_build_youtube_local_loader_requires_postgres_dsn(self) -> None:
        with self.assertRaisesRegex(RuntimeError, "SOCIAL_ANALYTICS_POSTGRES_DSN"):
            build_youtube_local_loader(
                runtime_env={"YOUTUBE_LOCAL_LOAD_TARGET": "postgres"},
                provider_name="youtube",
                start_at=datetime(2026, 5, 1, tzinfo=UTC),
                end_at=datetime(2026, 5, 27, tzinfo=UTC),
                project_root=Path("project"),
            )

    def test_build_youtube_local_loader_rejects_unknown_target(self) -> None:
        with self.assertRaisesRegex(RuntimeError, "json' or 'postgres"):
            build_youtube_local_loader(
                runtime_env={"YOUTUBE_LOCAL_LOAD_TARGET": "warehouse"},
                provider_name="youtube",
                start_at=datetime(2026, 5, 1, tzinfo=UTC),
                end_at=datetime(2026, 5, 27, tzinfo=UTC),
                project_root=Path("project"),
            )


if __name__ == "__main__":
    unittest.main()
