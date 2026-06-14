import unittest
from datetime import UTC, datetime
from pathlib import Path
from typing import Any
from unittest.mock import patch

from social_analytics_pipeline.providers import YouTubeApiConfig, YouTubeDataApiProvider
from social_analytics_pipeline.providers.youtube import HttpJsonClient
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
                        "snippet": {
                            "publishedAt": "2026-05-20T14:30:00Z",
                            "title": f"Video {video_id}",
                            "channelTitle": "Bora Leao",
                            "thumbnails": {
                                "medium": {"url": f"https://example.test/{video_id}.jpg"}
                            },
                        },
                        "statistics": {
                            "likeCount": "10",
                            "commentCount": "2",
                            "viewCount": "100",
                        },
                    }
                    for video_id in ids
                ]
            }

        if url.endswith("/channels"):
            if "id" in params:
                return {
                    "items": [
                        {
                            "id": "UCresolved123",
                            "snippet": {
                                "title": "Bora Leao",
                                "thumbnails": {
                                    "medium": {
                                        "url": "https://example.test/channel.jpg"
                                    }
                                },
                            },
                            "statistics": {"subscriberCount": "1234"},
                        }
                    ]
                }
            return {
                "items": [
                    {
                        "id": "UCresolved123",
                    }
                ]
            }

        raise AssertionError(f"Unexpected URL: {url}")


class FakeHttpErrorResponse:
    status_code = 400

    def raise_for_status(self) -> None:
        try:
            import requests
        except ImportError as exc:  # pragma: no cover
            raise AssertionError("requests is required for this test") from exc

        raise requests.HTTPError("400 Client Error for url with key=secret", response=self)


class FakeRetryableHttpErrorResponse:
    def __init__(self, status_code: int) -> None:
        self.status_code = status_code

    def raise_for_status(self) -> None:
        try:
            import requests
        except ImportError as exc:  # pragma: no cover
            raise AssertionError("requests is required for this test") from exc

        raise requests.HTTPError(
            f"{self.status_code} Client Error for url with key=secret",
            response=self,
        )


class FakeSuccessResponse:
    def __init__(self, payload: dict[str, Any]) -> None:
        self.payload = payload

    def raise_for_status(self) -> None:
        return None

    def json(self) -> dict[str, Any]:
        return self.payload


class YouTubeProviderTest(unittest.TestCase):
    def test_config_from_env_requires_api_key(self) -> None:
        with self.assertRaisesRegex(RuntimeError, "YOUTUBE_API_KEY"):
            YouTubeApiConfig.from_env({})

    def test_config_from_env_reads_max_pages(self) -> None:
        config = YouTubeApiConfig.from_env(
            {
                "YOUTUBE_API_KEY": "test-api-key",
                "YOUTUBE_MAX_PAGES": "3",
                "YOUTUBE_HTTP_MAX_ATTEMPTS": "4",
                "YOUTUBE_HTTP_BACKOFF_SECONDS": "2.5",
            }
        )

        self.assertEqual(config.max_pages, 3)
        self.assertEqual(config.http_max_attempts, 4)
        self.assertEqual(config.http_backoff_seconds, 2.5)

    def test_config_from_env_rejects_invalid_max_pages(self) -> None:
        with self.assertRaisesRegex(RuntimeError, "YOUTUBE_MAX_PAGES"):
            YouTubeApiConfig.from_env(
                {
                    "YOUTUBE_API_KEY": "test-api-key",
                    "YOUTUBE_MAX_PAGES": "0",
                }
            )

    def test_config_from_env_rejects_invalid_retry_values(self) -> None:
        with self.assertRaisesRegex(RuntimeError, "YOUTUBE_HTTP_MAX_ATTEMPTS"):
            YouTubeApiConfig.from_env(
                {
                    "YOUTUBE_API_KEY": "test-api-key",
                    "YOUTUBE_HTTP_MAX_ATTEMPTS": "abc",
                }
            )

        with self.assertRaisesRegex(RuntimeError, "YOUTUBE_HTTP_BACKOFF_SECONDS"):
            YouTubeApiConfig.from_env(
                {
                    "YOUTUBE_API_KEY": "test-api-key",
                    "YOUTUBE_HTTP_BACKOFF_SECONDS": "abc",
                }
            )

    def test_http_json_client_sanitizes_http_errors(self) -> None:
        with (
            patch("requests.get", return_value=FakeHttpErrorResponse()),
            self.assertRaisesRegex(RuntimeError, "status 400") as context,
        ):
            HttpJsonClient().get_json(
                "https://www.googleapis.com/youtube/v3/search",
                {"key": "secret", "channelId": "bad-channel"},
            )

        self.assertNotIn("secret", str(context.exception))
        self.assertNotIn("googleapis", str(context.exception))

    def test_http_json_client_retries_retryable_status_codes(self) -> None:
        responses = [
            FakeRetryableHttpErrorResponse(429),
            FakeSuccessResponse({"items": []}),
        ]
        sleep_calls: list[float] = []
        client = HttpJsonClient(
            max_attempts=3,
            backoff_seconds=0.5,
            sleeper=sleep_calls.append,
        )

        with patch("requests.get", side_effect=responses):
            payload = client.get_json(
                "https://www.googleapis.com/youtube/v3/search",
                {"key": "secret", "channelId": "retry-channel"},
            )

        self.assertEqual(payload, {"items": []})
        self.assertEqual(sleep_calls, [0.5])

    def test_http_json_client_stops_on_credential_errors(self) -> None:
        client = HttpJsonClient(
            max_attempts=3,
            backoff_seconds=0.5,
            sleeper=lambda _seconds: None,
        )

        with (
            patch("requests.get", return_value=FakeRetryableHttpErrorResponse(403)),
            self.assertRaisesRegex(RuntimeError, "status 403") as context,
        ):
            client.get_json(
                "https://www.googleapis.com/youtube/v3/search",
                {"key": "secret", "channelId": "credential-channel"},
            )

        self.assertIn("quota", str(context.exception))
        self.assertNotIn("secret", str(context.exception))

    def test_http_json_client_reports_retry_exhaustion_without_leaking_secret(self) -> None:
        client = HttpJsonClient(
            max_attempts=3,
            backoff_seconds=0.5,
            sleeper=lambda _seconds: None,
        )

        with (
            patch("requests.get", return_value=FakeRetryableHttpErrorResponse(503)),
            self.assertRaisesRegex(RuntimeError, "after 3 attempts") as context,
        ):
            client.get_json(
                "https://www.googleapis.com/youtube/v3/search",
                {"key": "secret", "channelId": "unstable-channel"},
            )

        self.assertNotIn("secret", str(context.exception))

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
        self.assertEqual(payloads[0]["channel"]["title"], "Bora Leao")
        self.assertEqual(len(http_client.calls), 4)
        self.assertEqual(http_client.calls[0][1]["publishedAfter"], "2026-05-01T00:00:00Z")
        self.assertEqual(http_client.calls[0][1]["publishedBefore"], "2026-05-27T00:00:00Z")
        self.assertEqual(http_client.calls[1][1]["pageToken"], "page-2")
        self.assertEqual(http_client.calls[2][1]["part"], "snippet,statistics")
        self.assertEqual(http_client.calls[3][1]["part"], "snippet,statistics")

    def test_resolve_channel_id_uses_handle_without_at_sign(self) -> None:
        http_client = FakeHttpJsonClient()
        provider = YouTubeDataApiProvider(
            YouTubeApiConfig(api_key="test-api-key"),
            http_client=http_client,
        )

        channel_id = provider.resolve_channel_id("https://www.youtube.com/@public-handle")

        self.assertEqual(channel_id, "UCresolved123")
        self.assertEqual(http_client.calls[0][1]["part"], "id")
        self.assertEqual(http_client.calls[0][1]["forHandle"], "public-handle")

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
        self.assertEqual(metric.followers, 1234)
        self.assertEqual(metric.title, "Video yt-video-001")
        self.assertEqual(metric.thumbnail_url, "https://example.test/yt-video-001.jpg")
        self.assertEqual(metric.content_url, "https://www.youtube.com/watch?v=yt-video-001")
        self.assertEqual(metric.channel_name, "Bora Leao")
        self.assertEqual(metric.channel_image_url, "https://example.test/channel.jpg")


if __name__ == "__main__":
    unittest.main()
