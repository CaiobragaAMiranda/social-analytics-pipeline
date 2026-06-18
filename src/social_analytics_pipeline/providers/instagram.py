import os
import time
from collections.abc import Mapping
from dataclasses import dataclass
from datetime import datetime
from typing import Any

from social_analytics_pipeline.providers.base import SocialProvider

INSTAGRAM_GRAPH_API_BASE_URL = "https://graph.facebook.com"
RETRYABLE_STATUS_CODES = {429, 500, 502, 503, 504}
DEFAULT_HTTP_MAX_ATTEMPTS = 3
DEFAULT_HTTP_BACKOFF_SECONDS = 1.0
DEFAULT_INSTAGRAM_MEDIA_FIELDS = (
    "id,media_type,timestamp,like_count,comments_count,caption,permalink,"
    "media_url,thumbnail_url,plays,impressions,shares"
)


class InstagramHttpJsonClient:
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
            raise RuntimeError("Install requests to use InstagramGraphApiProvider.") from exc

        for attempt in range(1, self.max_attempts + 1):
            try:
                response = requests.get(
                    url,
                    params=params,
                    headers={"Accept": "application/json"},
                    timeout=30,
                )
                response.raise_for_status()
                payload = response.json()
            except requests.RequestException as exc:
                if not self._should_retry(exc, requests) or attempt == self.max_attempts:
                    raise RuntimeError(self._build_error_message(exc, attempt)) from None

                self.sleeper(self.backoff_seconds * attempt)
                continue

            if not isinstance(payload, dict):
                raise RuntimeError("Instagram API response must contain an object.")
            return payload

        raise RuntimeError("Instagram API request failed before a response was returned.")

    def _should_retry(self, exc: Exception, requests_module: Any) -> bool:
        if isinstance(exc, requests_module.Timeout | requests_module.ConnectionError):
            return True

        status_code = getattr(getattr(exc, "response", None), "status_code", None)
        return status_code in RETRYABLE_STATUS_CODES

    def _build_error_message(self, exc: Exception, attempt: int) -> str:
        status_code = getattr(getattr(exc, "response", None), "status_code", None)
        if status_code in {401, 403}:
            return (
                f"Instagram API request failed with status {status_code}. "
                "Check local credentials and account permissions before retrying."
            )
        if status_code:
            if status_code in RETRYABLE_STATUS_CODES and attempt > 1:
                return (
                    f"Instagram API request failed with status {status_code} "
                    f"after {attempt} attempts."
                )
            return f"Instagram API request failed with status {status_code}."

        if attempt > 1:
            return f"Instagram API request failed after {attempt} attempts due to a network error."
        return "Instagram API request failed before a response was returned."


@dataclass(frozen=True)
class InstagramApiConfig:
    access_token: str
    account_id: str
    base_url: str = INSTAGRAM_GRAPH_API_BASE_URL
    max_pages: int = 1
    media_fields: str = DEFAULT_INSTAGRAM_MEDIA_FIELDS
    http_max_attempts: int = DEFAULT_HTTP_MAX_ATTEMPTS
    http_backoff_seconds: float = DEFAULT_HTTP_BACKOFF_SECONDS

    @classmethod
    def from_env(cls, env: Mapping[str, str] | None = None) -> "InstagramApiConfig":
        runtime_env = env or os.environ
        access_token = runtime_env.get("INSTAGRAM_ACCESS_TOKEN", "")
        account_id = runtime_env.get("INSTAGRAM_USER_ID", "")
        if not access_token:
            raise RuntimeError(
                "INSTAGRAM_ACCESS_TOKEN is required to use InstagramGraphApiProvider."
            )
        if not account_id:
            raise RuntimeError("INSTAGRAM_USER_ID is required to use InstagramGraphApiProvider.")

        max_pages = _parse_positive_int(runtime_env, "INSTAGRAM_MAX_PAGES", default=1)
        if max_pages < 1:
            raise RuntimeError("INSTAGRAM_MAX_PAGES must be greater than or equal to 1.")

        http_max_attempts = _parse_positive_int(
            runtime_env,
            "INSTAGRAM_HTTP_MAX_ATTEMPTS",
            default=DEFAULT_HTTP_MAX_ATTEMPTS,
        )
        if http_max_attempts < 1:
            raise RuntimeError("INSTAGRAM_HTTP_MAX_ATTEMPTS must be greater than or equal to 1.")

        http_backoff_seconds = _parse_positive_float(
            runtime_env,
            "INSTAGRAM_HTTP_BACKOFF_SECONDS",
            default=DEFAULT_HTTP_BACKOFF_SECONDS,
        )
        if http_backoff_seconds < 0:
            raise RuntimeError(
                "INSTAGRAM_HTTP_BACKOFF_SECONDS must be greater than or equal to 0."
            )

        return cls(
            access_token=access_token,
            account_id=account_id,
            base_url=runtime_env.get("INSTAGRAM_GRAPH_API_BASE_URL", INSTAGRAM_GRAPH_API_BASE_URL),
            max_pages=max_pages,
            http_max_attempts=http_max_attempts,
            http_backoff_seconds=http_backoff_seconds,
        )


class InstagramGraphApiProvider(SocialProvider):
    name = "instagram"

    def __init__(
        self,
        config: InstagramApiConfig,
        http_client: InstagramHttpJsonClient | None = None,
    ) -> None:
        self.config = config
        self.http_client = http_client or InstagramHttpJsonClient(
            max_attempts=config.http_max_attempts,
            backoff_seconds=config.http_backoff_seconds,
        )

    def collect_metrics(
        self,
        account_id: str,
        start_at: datetime,
        end_at: datetime,
    ) -> list[dict[str, Any]]:
        if start_at > end_at:
            raise ValueError("start_at must be before or equal to end_at")

        target_account_id = account_id or self.config.account_id
        account = self._collect_account(target_account_id)
        media_payloads = self._collect_media(target_account_id)
        return [
            self._with_collection_context(media, account, target_account_id, start_at, end_at)
            for media in media_payloads
            if _is_in_interval(media, start_at, end_at)
        ]

    def _collect_account(self, account_id: str) -> dict[str, Any]:
        return self.http_client.get_json(
            f"{self.config.base_url}/{account_id}",
            {
                "fields": "id,username,followers_count,profile_picture_url",
                "access_token": self.config.access_token,
            },
        )

    def _collect_media(self, account_id: str) -> list[dict[str, Any]]:
        media: list[dict[str, Any]] = []
        next_url: str | None = f"{self.config.base_url}/{account_id}/media"
        params: dict[str, str | int] = {
            "fields": self.config.media_fields,
            "access_token": self.config.access_token,
        }

        for _ in range(self.config.max_pages):
            if next_url is None:
                break
            response = self.http_client.get_json(next_url, params)
            items = response.get("data", [])
            if isinstance(items, list):
                media.extend(item for item in items if isinstance(item, dict))
            paging = response.get("paging", {})
            next_url = paging.get("next") if isinstance(paging, dict) else None
            params = {}

        return media

    def _with_collection_context(
        self,
        payload: dict[str, Any],
        account: dict[str, Any],
        account_id: str,
        start_at: datetime,
        end_at: datetime,
    ) -> dict[str, Any]:
        enriched = dict(payload)
        enriched["account"] = account
        enriched["_collection"] = {
            "provider": self.name,
            "account_id": account_id,
            "start_at": start_at.isoformat(),
            "end_at": end_at.isoformat(),
        }
        return enriched


def _is_in_interval(payload: dict[str, Any], start_at: datetime, end_at: datetime) -> bool:
    timestamp = payload.get("timestamp")
    if not timestamp:
        return True
    published_at = datetime.fromisoformat(str(timestamp).replace("Z", "+00:00"))
    return start_at <= published_at <= end_at


def _parse_positive_int(
    env: Mapping[str, str],
    key: str,
    default: int,
) -> int:
    raw_value = env.get(key)
    if raw_value is None:
        return default
    try:
        return int(raw_value)
    except ValueError as exc:
        raise RuntimeError(f"{key} must be an integer.") from exc


def _parse_positive_float(
    env: Mapping[str, str],
    key: str,
    default: float,
) -> float:
    raw_value = env.get(key)
    if raw_value is None:
        return default
    try:
        return float(raw_value)
    except ValueError as exc:
        raise RuntimeError(f"{key} must be a number.") from exc
