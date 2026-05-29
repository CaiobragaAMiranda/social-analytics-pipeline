import unittest
from datetime import UTC, datetime
from pathlib import Path
from typing import Any

from social_analytics_pipeline.providers import YouTubeApiConfig, YouTubeDataApiProvider
from social_analytics_pipeline.transform import normalize_payload


class FakeHttpJsonClient:
    def __init__(self) -> None:
        self.calls: list[tuple[str, dict[str, str | int]]] = []

    def get_json(self, url: str, params: dict[str, str | int]) -> dict[str, Any]:
        self.calls.append((url, params))
        if url.endswith("/search"):
            page_token = params.get("pageToken")
            if page_token == "page-2":
                return {
                    "items": [{"id": {"videoId": "yt-video-002"}}],
                }
            return {
                "nextPageToken": "page-2",
                "items": [{"id": {"videoId": "yt-video-001"}}],
            }

        if url.endswith("/videos"):
            ids = str(params["id"]).split(",")
            return {
                "items": [
                    {
                        "id": video_id,
                        "snippet": {"publishedAt": "2026-05-20T14:30:00Z"},
                        "statistics": {
                            "likeCount": "10",
                            "commentCount": "2",
                            "viewCount": "100",
                        },
                    }
                    for video_id in ids
                ]
            }

        raise AssertionError(f"Unexpected URL: {url}")


class YouTubeProviderTest(unittest.TestCase):
    def test_config_from_env_requires_api_key(self) -> None:
        with self.assertRaisesRegex(RuntimeError, "YOUTUBE_API_KEY"):
            YouTubeApiConfig.from_env({})

    def test_collect_metrics_uses_search_pagination_and_video_statistics(self) -> None:
        http_client = FakeHttpJsonClient()
        provider = YouTubeDataApiProvider(
            YouTubeApiConfig(api_key="test-api-key", max_pages=2),
            http_client=http_client,
        )

        payloads = provider.collect_metrics(
            account_id="yt-channel-1",
            start_at=datetime(2026, 5, 1, tzinfo=UTC),
            end_at=datetime(2026, 5, 27, tzinfo=UTC),
        )

        self.assertEqual([payload["id"] for payload in payloads], ["yt-video-001", "yt-video-002"])
        self.assertEqual(payloads[0]["_collection"]["provider"], "youtube")
        self.assertEqual(payloads[0]["_collection"]["account_id"], "yt-channel-1")
        self.assertEqual(len(http_client.calls), 3)
        self.assertEqual(http_client.calls[0][1]["publishedAfter"], "2026-05-01T00:00:00Z")
        self.assertEqual(http_client.calls[0][1]["publishedBefore"], "2026-05-27T00:00:00Z")
        self.assertEqual(http_client.calls[1][1]["pageToken"], "page-2")
        self.assertEqual(http_client.calls[2][1]["part"], "snippet,statistics")

    def test_real_youtube_payload_normalizes_without_fixture_video_id_field(self) -> None:
        http_client = FakeHttpJsonClient()
        provider = YouTubeDataApiProvider(
            YouTubeApiConfig(api_key="test-api-key", max_pages=1),
            http_client=http_client,
        )

        payload = provider.collect_metrics(
            account_id="yt-channel-1",
            start_at=datetime(2026, 5, 1, tzinfo=UTC),
            end_at=datetime(2026, 5, 27, tzinfo=UTC),
        )[0]
        metric = normalize_payload(payload, raw_path=Path("data/raw/youtube/sample.json"))

        self.assertEqual(metric.content_id, "yt-video-001")
        self.assertEqual(metric.likes, 10)
        self.assertEqual(metric.comments, 2)
        self.assertEqual(metric.views, 100)
        self.assertIsNone(metric.followers)


if __name__ == "__main__":
    unittest.main()
