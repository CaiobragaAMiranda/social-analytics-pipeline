import unittest
from datetime import UTC, datetime
from pathlib import Path

from social_analytics_pipeline.transform import (
    MetricValidationError,
    SocialMetric,
    validate_metric,
)


class MetricValidationTest(unittest.TestCase):
    def test_accepts_valid_metric(self) -> None:
        metric = self._metric()

        self.assertEqual(validate_metric(metric), metric)

    def test_rejects_negative_counts(self) -> None:
        metric = self._metric(likes=-1)

        with self.assertRaisesRegex(MetricValidationError, "likes"):
            validate_metric(metric)

    def test_rejects_published_at_after_collected_at(self) -> None:
        metric = self._metric(
            published_at=datetime(2026, 5, 28, tzinfo=UTC),
            collected_at=datetime(2026, 5, 27, tzinfo=UTC),
        )

        with self.assertRaisesRegex(MetricValidationError, "published_at"):
            validate_metric(metric)

    def test_rejects_empty_required_text_fields(self) -> None:
        metric = self._metric(content_id=" ")

        with self.assertRaisesRegex(MetricValidationError, "content_id"):
            validate_metric(metric)

    def _metric(self, **overrides: object) -> SocialMetric:
        values = {
            "provider": "youtube",
            "account_id": "yt-channel-1",
            "content_id": "yt-video-001",
            "content_type": "video",
            "collected_at": datetime(2026, 5, 27, tzinfo=UTC),
            "published_at": datetime(2026, 5, 20, tzinfo=UTC),
            "likes": 10,
            "comments": 2,
            "shares": None,
            "views": 100,
            "followers": 500,
            "raw_path": Path("data/raw/youtube/sample.json"),
        }
        values.update(overrides)
        return SocialMetric(**values)


if __name__ == "__main__":
    unittest.main()
