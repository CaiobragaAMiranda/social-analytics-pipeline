import json
import unittest
from datetime import UTC, datetime
from pathlib import Path
from tempfile import TemporaryDirectory
from typing import Any

from social_analytics_pipeline.cli.youtube_local_pipeline import (
    build_youtube_local_loader,
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

        self.assertEqual(summary.result.provider, "youtube")
        self.assertEqual(summary.result.raw_records, 1)
        self.assertEqual(summary.result.loaded_records, 1)
        self.assertEqual(len(raw_files), 1)
        self.assertEqual(len(processed_rows), 1)
        self.assertEqual(processed_rows[0]["provider"], "youtube")
        self.assertEqual(processed_rows[0]["content_id"], "yt-video-001")

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
