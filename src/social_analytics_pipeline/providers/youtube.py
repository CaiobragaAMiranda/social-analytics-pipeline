import os
import time
from collections.abc import Mapping
from dataclasses import dataclass
from datetime import UTC, datetime
from typing import Any

from social_analytics_pipeline.providers.base import SocialProvider

YOUTUBE_API_BASE_URL = "https://www.googleapis.com/youtube/v3"
RETRYABLE_STATUS_CODES = {429, 500, 502, 503, 504}
DEFAULT_HTTP_MAX_ATTEMPTS = 3
DEFAULT_HTTP_BACKOFF_SECONDS = 1.0


class HttpJsonClient:
    def __init__(
        self,
        max_attempts: int = DEFAULT_HTTP_MAX_ATTEMPTS,
        backoff_seconds: float = DEFAULT_HTTP_BACKOFF_SECONDS,
        sleeper: Any | None = None,
    ) -> None:
        self.max_attempts = max_attempts
        self.backoff_seconds = backoff_seconds
        self.sleeper = sleeper or time.sleep

    def get_json(self, url: str, params: Mapping[str, str | int]) -> dict[str, Any]:
        try:
            import requests
        except ImportError as exc:
            raise RuntimeError("Install requests to use YouTubeDataApiProvider.") from exc

        for attempt in range(1, self.max_attempts + 1):
            try:
                response = requests.get(
                    url,
                    params=params,
                    headers={"Accept": "application/json"},
                    timeout=30,
                )
                response.raise_for_status()
                return response.json()
            except requests.RequestException as exc:
                if not self._should_retry(exc, requests) or attempt == self.max_attempts:
                    raise RuntimeError(self._build_error_message(exc, attempt)) from None

                self.sleeper(self.backoff_seconds * attempt)

        raise RuntimeError("YouTube API request failed before a response was returned.")

    def _should_retry(self, exc: Exception, requests_module: Any) -> bool:
        if isinstance(exc, requests_module.Timeout | requests_module.ConnectionError):
            return True

        status_code = getattr(getattr(exc, "response", None), "status_code", None)
        return status_code in RETRYABLE_STATUS_CODES

    def _build_error_message(self, exc: Exception, attempt: int) -> str:
        status_code = getattr(getattr(exc, "response", None), "status_code", None)
        if status_code == 401:
            return (
                "YouTube API request failed with status 401. "
                "Check local API credentials before retrying."
            )
        if status_code == 403:
            return (
                "YouTube API request failed with status 403. "
                "Check local API credentials, API access, or quota before retrying."
            )
        if status_code:
            if status_code in RETRYABLE_STATUS_CODES and attempt > 1:
                return (
                    f"YouTube API request failed with status {status_code} "
                    f"after {attempt} attempts."
                )
            return f"YouTube API request failed with status {status_code}."

        if attempt > 1:
            return f"YouTube API request failed after {attempt} attempts due to a network error."
        return "YouTube API request failed before a response was returned."


@dataclass(frozen=True)
class YouTubeApiConfig:
    api_key: str
    base_url: str = YOUTUBE_API_BASE_URL
    max_results: int = 50
    max_pages: int = 1
    http_max_attempts: int = DEFAULT_HTTP_MAX_ATTEMPTS
    http_backoff_seconds: float = DEFAULT_HTTP_BACKOFF_SECONDS

    @classmethod
    def from_env(cls, env: Mapping[str, str] | None = None) -> "YouTubeApiConfig":
        runtime_env = env or os.environ
        api_key = runtime_env.get("YOUTUBE_API_KEY", "")
        if not api_key:
            raise RuntimeError("YOUTUBE_API_KEY is required to use YouTubeDataApiProvider.")

        max_pages = _parse_positive_int(runtime_env, "YOUTUBE_MAX_PAGES", default=1)
        if max_pages < 1:
            raise RuntimeError("YOUTUBE_MAX_PAGES must be greater than or equal to 1.")

        http_max_attempts = _parse_positive_int(
            runtime_env,
            "YOUTUBE_HTTP_MAX_ATTEMPTS",
            default=DEFAULT_HTTP_MAX_ATTEMPTS,
        )
        if http_max_attempts < 1:
            raise RuntimeError("YOUTUBE_HTTP_MAX_ATTEMPTS must be greater than or equal to 1.")

        http_backoff_seconds = _parse_positive_float(
            runtime_env,
            "YOUTUBE_HTTP_BACKOFF_SECONDS",
            default=DEFAULT_HTTP_BACKOFF_SECONDS,
        )
        if http_backoff_seconds < 0:
            raise RuntimeError("YOUTUBE_HTTP_BACKOFF_SECONDS must be greater than or equal to 0.")

        return cls(
            api_key=api_key,
            max_pages=max_pages,
            http_max_attempts=http_max_attempts,
            http_backoff_seconds=http_backoff_seconds,
        )


class YouTubeDataApiProvider(SocialProvider):
    name = "youtube"

    def __init__(
        self,
        config: YouTubeApiConfig,
        http_client: HttpJsonClient | None = None,
    ) -> None:
        self.config = config
        self.http_client = http_client or HttpJsonClient(
            max_attempts=config.http_max_attempts,
            backoff_seconds=config.http_backoff_seconds,
        )

    def resolve_channel_id(self, handle: str) -> str:
        response = self.http_client.get_json(
            f"{self.config.base_url}/channels",
            {
                "part": "id",
                "forHandle": _normalize_handle(handle),
                "key": self.config.api_key,
            },
        )
        items = response.get("items", [])
        if not items:
            raise RuntimeError("YOUTUBE_CHANNEL_HANDLE did not resolve to a public channel.")

        channel_id = str(items[0].get("id", ""))
        if not channel_id.startswith("UC"):
            raise RuntimeError("Resolved YouTube channel id did not match the expected format.")

        return channel_id

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


def _normalize_handle(value: str) -> str:
    handle = value.strip()
    if "/@" in handle:
        handle = handle.rsplit("/@", 1)[1]
    if handle.startswith("@"):
        handle = handle[1:]
    return handle


def _rfc3339_utc(value: datetime) -> str:
    return value.astimezone(UTC).isoformat().replace("+00:00", "Z")


def _parse_positive_int(runtime_env: Mapping[str, str], key: str, default: int) -> int:
    raw_value = runtime_env.get(key, str(default))
    try:
        return int(raw_value)
    except ValueError as exc:
        raise RuntimeError(f"{key} must be an integer.") from exc


def _parse_positive_float(runtime_env: Mapping[str, str], key: str, default: float) -> float:
    raw_value = runtime_env.get(key, str(default))
    try:
        return float(raw_value)
    except ValueError as exc:
        raise RuntimeError(f"{key} must be a number.") from exc
