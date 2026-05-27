import unittest
from datetime import UTC, datetime
from pathlib import Path

from social_analytics_pipeline.providers import build_mock_providers
from social_analytics_pipeline.transform import SocialMetric, normalize_payload, normalize_payloads

PROJECT_ROOT = Path(__file__).resolve().parents[1]


class NormalizerTest(unittest.TestCase):
    def setUp(self) -> None:
        self.start_at = datetime(2026, 5, 1, tzinfo=UTC)
        self.end_at = datetime(2026, 5, 27, tzinfo=UTC)
        self.raw_path = Path("data/raw/mock/sample.json")
        self.providers = build_mock_providers(PROJECT_ROOT)

    def test_normalizes_instagram_payload(self) -> None:
        payload = self.providers["instagram"].collect_metrics(
            "ig-account-1", self.start_at, self.end_at
        )[0]

        metric = normalize_payload(payload, self.raw_path)

        self.assertEqual(
            metric,
            SocialMetric(
                provider="instagram",
                account_id="ig-account-1",
                content_id="ig-post-001",
                content_type="post",
                collected_at=self.end_at,
                published_at=datetime(2026, 5, 20, 14, 30, tzinfo=UTC),
                likes=120,
                comments=14,
                shares=None,
                views=2300,
                followers=5400,
                raw_path=self.raw_path,
            ),
        )

    def test_normalizes_youtube_payload(self) -> None:
        payload = self.providers["youtube"].collect_metrics(
            "yt-channel-1", self.start_at, self.end_at
        )[0]

        metric = normalize_payload(payload, self.raw_path)

        self.assertEqual(metric.provider, "youtube")
        self.assertEqual(metric.account_id, "yt-channel-1")
        self.assertEqual(metric.content_id, "yt-video-001")
        self.assertEqual(metric.content_type, "video")
        self.assertEqual(metric.likes, 620)
        self.assertEqual(metric.comments, 48)
        self.assertEqual(metric.shares, None)
        self.assertEqual(metric.views, 8500)
        self.assertEqual(metric.followers, 22000)

    def test_normalizes_tiktok_payload(self) -> None:
        payload = self.providers["tiktok"].collect_metrics(
            "tt-author-1", self.start_at, self.end_at
        )[0]

        metric = normalize_payload(payload, self.raw_path)

        self.assertEqual(metric.provider, "tiktok")
        self.assertEqual(metric.account_id, "tt-author-1")
        self.assertEqual(metric.content_id, "tt-video-001")
        self.assertEqual(metric.likes, 430)
        self.assertEqual(metric.comments, 29)
        self.assertEqual(metric.shares, 18)
        self.assertEqual(metric.views, 12000)
        self.assertEqual(metric.followers, 9100)

    def test_normalizes_multiple_payloads(self) -> None:
        payloads = self.providers["instagram"].collect_metrics(
            "ig-account-1", self.start_at, self.end_at
        )

        metrics = normalize_payloads(payloads, self.raw_path)

        self.assertEqual(len(metrics), 2)
        self.assertEqual([metric.content_id for metric in metrics], ["ig-post-001", "ig-reel-002"])
        self.assertEqual(metrics[1].content_type, "reel")

    def test_rejects_unknown_provider(self) -> None:
        payload = {
            "_collection": {
                "provider": "unknown",
                "account_id": "account-1",
                "start_at": self.start_at.isoformat(),
                "end_at": self.end_at.isoformat(),
            }
        }

        with self.assertRaisesRegex(ValueError, "Unsupported provider"):
            normalize_payload(payload, self.raw_path)

    def test_rejects_missing_collection_metadata(self) -> None:
        with self.assertRaisesRegex(ValueError, "Missing collection metadata"):
            normalize_payload({"id": "orphan"}, self.raw_path)


if __name__ == "__main__":
    unittest.main()
