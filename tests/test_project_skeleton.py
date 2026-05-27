from datetime import datetime, timezone
import json
import tempfile
import unittest
from pathlib import Path

from social_analytics_pipeline import __version__
from social_analytics_pipeline.config import PipelineConfig
from social_analytics_pipeline.storage import RawRecord, RawStorage
from social_analytics_pipeline.transform import SocialMetric


class ProjectSkeletonTest(unittest.TestCase):
    def test_package_exposes_version(self) -> None:
        self.assertEqual(__version__, "0.1.0")

    def test_config_builds_data_paths_from_project_root(self) -> None:
        config = PipelineConfig.from_project_root(Path("project"))

        self.assertEqual(config.raw_dir, Path("project/data/raw"))
        self.assertEqual(config.processed_dir, Path("project/data/processed"))

    def test_raw_storage_persists_payload_as_json(self) -> None:
        with tempfile.TemporaryDirectory() as tmpdir:
            storage = RawStorage(Path(tmpdir))
            record = RawRecord(
                provider="mock",
                account_id="account-1",
                collected_at=datetime(2026, 5, 27, 12, 0, tzinfo=timezone.utc),
                payload={"likes": 10},
            )

            path = storage.save(record)

            self.assertTrue(path.exists())
            self.assertEqual(json.loads(path.read_text(encoding="utf-8")), {"likes": 10})

    def test_social_metric_schema_is_constructible(self) -> None:
        metric = SocialMetric(
            provider="mock",
            account_id="account-1",
            content_id="post-1",
            content_type="post",
            collected_at=datetime(2026, 5, 27, tzinfo=timezone.utc),
            published_at=None,
            likes=1,
            comments=2,
            shares=3,
            views=4,
            followers=5,
            raw_path=Path("data/raw/mock/sample.json"),
        )

        self.assertEqual(metric.provider, "mock")
        self.assertEqual(metric.views, 4)


if __name__ == "__main__":
    unittest.main()
