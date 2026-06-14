import unittest
from datetime import UTC, datetime
from pathlib import Path
from typing import Any
from unittest.mock import patch

from social_analytics_pipeline.providers import InstagramApiConfig, InstagramGraphApiProvider
from social_analytics_pipeline.providers.instagram import InstagramHttpJsonClient
from social_analytics_pipeline.transform import normalize_payload


class FakeInstagramHttpJsonClient:
    def __init__(self) -> None:
        self.calls: list[tuple[str, dict[str, str | int]]] = []

    def get_json(self, url: str, params: dict[str, str | int]) -> dict[str, Any]:
        self.calls.append((url, params))
        if url.endswith("/ig-account-1"):
            return {
                "id": "ig-account-1",
                "username": "example_account",
                "followers_count": 1200,
            }
        if url.endswith("/ig-account-1/media"):
            return {
                "paging": {"next": "https://graph.facebook.com/next-page"},
                "data": [
                    {
                        "id": "ig-media-1",
                        "media_type": "IMAGE",
                        "timestamp": "2026-05-20T14:30:00Z",
                        "like_count": 12,
                        "comments_count": 3,
                        "impressions": 100,
                    }
                ],
            }
        if url.endswith("/next-page"):
            return {
                "data": [
                    {
                        "id": "ig-media-2",
                        "media_type": "REELS",
                        "timestamp": "2026-05-21T14:30:00Z",
                        "like_count": 20,
                        "comments_count": 5,
                        "plays": 250,
                        "shares": 4,
                    },
                    {
                        "id": "old-media",
                        "media_type": "IMAGE",
                        "timestamp": "2026-04-01T14:30:00Z",
                    },
                ]
            }
        raise AssertionError(f"Unexpected URL: {url}")


class FakeInstagramHttpErrorResponse:
    status_code = 403

    def raise_for_status(self) -> None:
        try:
            import requests
        except ImportError as exc:  # pragma: no cover
            raise AssertionError("requests is required for this test") from exc

        raise requests.HTTPError("403 Client Error with access_token=secret", response=self)


class InstagramProviderTest(unittest.TestCase):
    def test_config_from_env_requires_access_token(self) -> None:
        with self.assertRaisesRegex(RuntimeError, "INSTAGRAM_ACCESS_TOKEN"):
            InstagramApiConfig.from_env({"INSTAGRAM_USER_ID": "ig-account-1"})

    def test_config_from_env_requires_user_id(self) -> None:
        with self.assertRaisesRegex(RuntimeError, "INSTAGRAM_USER_ID"):
            InstagramApiConfig.from_env({"INSTAGRAM_ACCESS_TOKEN": "test-token"})

    def test_config_from_env_reads_max_pages(self) -> None:
        config = InstagramApiConfig.from_env(
            {
                "INSTAGRAM_ACCESS_TOKEN": "test-token",
                "INSTAGRAM_USER_ID": "ig-account-1",
                "INSTAGRAM_MAX_PAGES": "2",
            }
        )

        self.assertEqual(config.max_pages, 2)
        self.assertEqual(config.account_id, "ig-account-1")

    def test_config_from_env_rejects_invalid_max_pages(self) -> None:
        with self.assertRaisesRegex(RuntimeError, "INSTAGRAM_MAX_PAGES"):
            InstagramApiConfig.from_env(
                {
                    "INSTAGRAM_ACCESS_TOKEN": "test-token",
                    "INSTAGRAM_USER_ID": "ig-account-1",
                    "INSTAGRAM_MAX_PAGES": "0",
                }
            )

    def test_http_json_client_sanitizes_http_errors(self) -> None:
        with (
            patch("requests.get", return_value=FakeInstagramHttpErrorResponse()),
            self.assertRaisesRegex(RuntimeError, "status 403") as context,
        ):
            InstagramHttpJsonClient().get_json(
                "https://graph.facebook.com/ig-account-1/media",
                {"access_token": "secret"},
            )

        self.assertNotIn("secret", str(context.exception))
        self.assertNotIn("graph.facebook", str(context.exception))

    def test_collect_metrics_uses_account_media_and_pagination(self) -> None:
        http_client = FakeInstagramHttpJsonClient()
        provider = InstagramGraphApiProvider(
            InstagramApiConfig(
                access_token="test-token",
                account_id="ig-account-1",
                max_pages=2,
            ),
            http_client=http_client,
        )

        payloads = provider.collect_metrics(
            account_id="ig-account-1",
            start_at=datetime(2026, 5, 1, tzinfo=UTC),
            end_at=datetime(2026, 5, 31, tzinfo=UTC),
        )

        self.assertEqual([payload["id"] for payload in payloads], ["ig-media-1", "ig-media-2"])
        self.assertEqual(payloads[0]["_collection"]["provider"], "instagram")
        self.assertEqual(payloads[0]["account"]["followers_count"], 1200)
        self.assertEqual(len(http_client.calls), 3)
        self.assertEqual(http_client.calls[1][1]["access_token"], "test-token")
        self.assertEqual(http_client.calls[2][1], {})

    def test_collect_metrics_normalizes_to_social_metric_schema(self) -> None:
        provider = InstagramGraphApiProvider(
            InstagramApiConfig(
                access_token="test-token",
                account_id="ig-account-1",
                max_pages=1,
            ),
            http_client=FakeInstagramHttpJsonClient(),
        )

        payload = provider.collect_metrics(
            account_id="",
            start_at=datetime(2026, 5, 1, tzinfo=UTC),
            end_at=datetime(2026, 5, 31, tzinfo=UTC),
        )[0]
        metric = normalize_payload(payload, Path("data/raw/instagram/sample.json"))

        self.assertEqual(metric.provider, "instagram")
        self.assertEqual(metric.account_id, "ig-account-1")
        self.assertEqual(metric.content_id, "ig-media-1")
        self.assertEqual(metric.content_type, "post")
        self.assertEqual(metric.views, 100)
        self.assertEqual(metric.followers, 1200)


if __name__ == "__main__":
    unittest.main()
