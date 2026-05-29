import unittest
from datetime import UTC, datetime
from pathlib import Path
from unittest.mock import patch

from social_analytics_pipeline.load import (
    SOCIAL_METRICS_UPSERT_SQL,
    PostgresMetricLoader,
    metric_to_row,
)
from social_analytics_pipeline.transform import SocialMetric


class PostgresLoaderTest(unittest.TestCase):
    def test_schema_uses_bigint_for_social_counters(self) -> None:
        schema_sql = Path("db/init/001_create_social_metrics.sql").read_text(encoding="utf-8")

        for column in ["likes", "comments", "shares", "views", "followers"]:
            self.assertIn(f"{column} BIGINT", schema_sql)

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

    def test_loader_sanitizes_database_errors(self) -> None:
        import psycopg

        metric = SocialMetric(
            provider="youtube",
            account_id="UCtestchannel",
            content_id="yt-video-001",
            content_type="video",
            collected_at=datetime(2026, 5, 27, tzinfo=UTC),
            published_at=None,
            likes=10,
            comments=2,
            shares=None,
            views=100,
            followers=None,
            raw_path=Path("data/raw/youtube/sample.json"),
        )
        loader = PostgresMetricLoader("postgresql://user:placeholder@localhost:5432/db")

        with (
            patch(
                "psycopg.connect",
                side_effect=psycopg.OperationalError("placeholder localhost"),
            ),
            self.assertRaisesRegex(RuntimeError, "OperationalError") as context,
        ):
            loader.load([metric])

        self.assertNotIn("placeholder", str(context.exception))
        self.assertNotIn("localhost", str(context.exception))


if __name__ == "__main__":
    unittest.main()
