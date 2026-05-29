import os
from collections.abc import Mapping
from dataclasses import dataclass
from datetime import UTC, datetime
from typing import Any

from social_analytics_pipeline.providers.base import SocialProvider

YOUTUBE_API_BASE_URL = "https://www.googleapis.com/youtube/v3"


class HttpJsonClient:
    def get_json(self, url: str, params: Mapping[str, str | int]) -> dict[str, Any]:
        try:
            import requests
        except ImportError as exc:
            raise RuntimeError("Install requests to use YouTubeDataApiProvider.") from exc

        response = requests.get(
            url,
            params=params,
            headers={"Accept": "application/json"},
            timeout=30,
        )
        response.raise_for_status()
        return response.json()


@dataclass(frozen=True)
class YouTubeApiConfig:
    api_key: str
    base_url: str = YOUTUBE_API_BASE_URL
    max_results: int = 50
    max_pages: int = 1

    @classmethod
    def from_env(cls, env: Mapping[str, str] | None = None) -> "YouTubeApiConfig":
        runtime_env = env or os.environ
        api_key = runtime_env.get("YOUTUBE_API_KEY", "")
        if not api_key:
            raise RuntimeError("YOUTUBE_API_KEY is required to use YouTubeDataApiProvider.")
        return cls(api_key=api_key)


class YouTubeDataApiProvider(SocialProvider):
    name = "youtube"

    def __init__(
        self,
        config: YouTubeApiConfig,
        http_client: HttpJsonClient | None = None,
    ) -> None:
        self.config = config
        self.http_client = http_client or HttpJsonClient()

    def collect_metrics(
        self,
        account_id: str,
        start_at: datetime,
        end_at: datetime,
    ) -> list[dict[str, Any]]:
        if start_at > end_at:
            raise ValueError("start_at must be before or equal to end_at")

        video_ids = self._collect_video_ids(account_id, start_at, end_at)
        if not video_ids:
            return []

        videos: list[dict[str, Any]] = []
        for batch in _chunks(video_ids, 50):
            response = self.http_client.get_json(
                f"{self.config.base_url}/videos",
                {
                    "part": "snippet,statistics",
                    "id": ",".join(batch),
                    "key": self.config.api_key,
                },
            )
            videos.extend(
                self._with_collection_context(item, account_id, start_at, end_at)
                for item in response.get("items", [])
            )

        return videos

    def _collect_video_ids(
        self,
        channel_id: str,
        start_at: datetime,
        end_at: datetime,
    ) -> list[str]:
        video_ids: list[str] = []
        page_token: str | None = None

        for _ in range(self.config.max_pages):
            params: dict[str, str | int] = {
                "part": "id",
                "channelId": channel_id,
                "type": "video",
                "order": "date",
                "maxResults": self.config.max_results,
                "publishedAfter": _rfc3339_utc(start_at),
                "publishedBefore": _rfc3339_utc(end_at),
                "key": self.config.api_key,
            }
            if page_token:
                params["pageToken"] = page_token

            response = self.http_client.get_json(f"{self.config.base_url}/search", params)
            for item in response.get("items", []):
                video_id = item.get("id", {}).get("videoId")
                if video_id:
                    video_ids.append(str(video_id))

            page_token = response.get("nextPageToken")
            if not page_token:
                break

        return video_ids

    def _with_collection_context(
        self,
        payload: dict[str, Any],
        account_id: str,
        start_at: datetime,
        end_at: datetime,
    ) -> dict[str, Any]:
        enriched = dict(payload)
        enriched["_collection"] = {
            "provider": self.name,
            "account_id": account_id,
            "start_at": start_at.isoformat(),
            "end_at": end_at.isoformat(),
        }
        return enriched


def _chunks(values: list[str], size: int) -> list[list[str]]:
    return [values[index : index + size] for index in range(0, len(values), size)]


def _rfc3339_utc(value: datetime) -> str:
    return value.astimezone(UTC).isoformat().replace("+00:00", "Z")
