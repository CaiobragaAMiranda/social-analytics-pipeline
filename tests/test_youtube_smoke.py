import unittest
from datetime import UTC, datetime
from typing import Any

from social_analytics_pipeline.cli.youtube_smoke import build_youtube_smoke_summary, main


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

    def test_main_requires_channel_id_before_network_or_api_key(self) -> None:
        with self.assertRaisesRegex(RuntimeError, "YOUTUBE_CHANNEL_ID"):
            main({})


if __name__ == "__main__":
    unittest.main()
