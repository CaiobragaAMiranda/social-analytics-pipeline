import json
import tempfile
import unittest
from datetime import UTC, datetime
from pathlib import Path

from social_analytics_pipeline.pipeline import (
    JsonMetricArtifactLoader,
    build_interval_artifact_path,
    metric_to_artifact_row,
)
from social_analytics_pipeline.transform import SocialMetric


class ArtifactLoaderTest(unittest.TestCase):
    def test_metric_to_artifact_row_serializes_datetime_and_path(self) -> None:
        metric = self._metric()

        row = metric_to_artifact_row(metric)

        self.assertEqual(row["collected_at"], "2026-05-28T00:00:00+00:00")
        self.assertEqual(row["published_at"], None)
        self.assertEqual(row["raw_path"], "data/raw/mock/sample.json")
        self.assertEqual(row["title"], "Post title")
        self.assertEqual(row["thumbnail_url"], "https://example.test/post.jpg")
        self.assertEqual(row["content_url"], "https://example.test/post")
        self.assertEqual(row["channel_name"], "Brand Channel")
        self.assertEqual(row["channel_image_url"], "https://example.test/channel.jpg")

    def test_json_metric_artifact_loader_writes_metrics(self) -> None:
        with tempfile.TemporaryDirectory() as tmpdir:
            output_path = Path(tmpdir) / "processed" / "metrics.json"
            loader = JsonMetricArtifactLoader(output_path)

            loaded = loader.load([self._metric()])

            self.assertEqual(loaded, 1)
            self.assertTrue(output_path.exists())
            rows = json.loads(output_path.read_text(encoding="utf-8"))
            self.assertEqual(rows[0]["provider"], "mock")

    def test_json_metric_artifact_loader_writes_empty_list(self) -> None:
        with tempfile.TemporaryDirectory() as tmpdir:
            output_path = Path(tmpdir) / "processed" / "metrics.json"
            loader = JsonMetricArtifactLoader(output_path)

            loaded = loader.load([])

            self.assertEqual(loaded, 0)
            self.assertEqual(json.loads(output_path.read_text(encoding="utf-8")), [])

    def test_build_interval_artifact_path_uses_provider_and_interval(self) -> None:
        path = build_interval_artifact_path(
            Path("data/processed/airflow"),
            "youtube",
            datetime(2026, 1, 1, tzinfo=UTC),
            datetime(2026, 1, 16, tzinfo=UTC),
        )

        self.assertEqual(
            path.as_posix(),
            "data/processed/airflow/youtube-20260101T000000-20260116T000000.json",
        )

    def _metric(self) -> SocialMetric:
        return SocialMetric(
            provider="mock",
            account_id="account-1",
            content_id="post-1",
            content_type="post",
            collected_at=datetime(2026, 5, 28, tzinfo=UTC),
            published_at=None,
            likes=1,
            comments=2,
            shares=3,
            views=4,
            followers=5,
            raw_path=Path("data/raw/mock/sample.json"),
            title="Post title",
            thumbnail_url="https://example.test/post.jpg",
            content_url="https://example.test/post",
            channel_name="Brand Channel",
            channel_image_url="https://example.test/channel.jpg",
        )


if __name__ == "__main__":
    unittest.main()
