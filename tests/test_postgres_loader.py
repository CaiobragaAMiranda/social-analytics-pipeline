import unittest
from datetime import UTC, datetime
from pathlib import Path

from social_analytics_pipeline.load import (
    SOCIAL_METRICS_UPSERT_SQL,
    PostgresMetricLoader,
    metric_to_row,
)
from social_analytics_pipeline.transform import SocialMetric


class PostgresLoaderTest(unittest.TestCase):
    def test_metric_to_row_converts_raw_path_to_string(self) -> None:
        metric = SocialMetric(
            provider="instagram",
            account_id="ig-account-1",
            content_id="ig-post-001",
            content_type="post",
            collected_at=datetime(2026, 5, 27, tzinfo=UTC),
            published_at=None,
            likes=10,
            comments=2,
            shares=None,
            views=100,
            followers=1000,
            raw_path=Path("data/raw/instagram/sample.json"),
        )

        row = metric_to_row(metric)

        self.assertEqual(row["provider"], "instagram")
        self.assertEqual(row["raw_path"], "data/raw/instagram/sample.json")
        self.assertEqual(set(row), {
            "provider",
            "account_id",
            "content_id",
            "content_type",
            "collected_at",
            "published_at",
            "likes",
            "comments",
            "shares",
            "views",
            "followers",
            "raw_path",
        })

    def test_upsert_sql_uses_expected_natural_key(self) -> None:
        self.assertIn(
            "ON CONFLICT (provider, account_id, content_id, collected_at)",
            SOCIAL_METRICS_UPSERT_SQL,
        )
        self.assertIn("DO UPDATE SET", SOCIAL_METRICS_UPSERT_SQL)
        self.assertIn("updated_at = NOW()", SOCIAL_METRICS_UPSERT_SQL)

    def test_loader_returns_zero_for_empty_batch_without_database_dependency(self) -> None:
        loader = PostgresMetricLoader("postgresql://unused")

        self.assertEqual(loader.load([]), 0)


if __name__ == "__main__":
    unittest.main()
