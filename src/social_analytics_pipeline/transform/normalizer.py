from collections.abc import Callable
from datetime import datetime
from pathlib import Path
from typing import Any

from social_analytics_pipeline.transform.schema import SocialMetric

Normalizer = Callable[[dict[str, Any], Path], SocialMetric]


def normalize_payload(payload: dict[str, Any], raw_path: Path) -> SocialMetric:
    provider = _collection_value(payload, "provider")
    normalizers: dict[str, Normalizer] = {
        "instagram": _normalize_instagram,
        "youtube": _normalize_youtube,
        "tiktok": _normalize_tiktok,
    }

    try:
        normalizer = normalizers[provider]
    except KeyError as exc:
        raise ValueError(f"Unsupported provider: {provider}") from exc

    return normalizer(payload, raw_path)


def normalize_payloads(payloads: list[dict[str, Any]], raw_path: Path) -> list[SocialMetric]:
    return [normalize_payload(payload, raw_path) for payload in payloads]


def _normalize_instagram(payload: dict[str, Any], raw_path: Path) -> SocialMetric:
    content_type = _instagram_content_type(str(payload["media_type"]))
    account = payload.get("account", {})

    return SocialMetric(
        provider="instagram",
        account_id=_collection_value(payload, "account_id"),
        content_id=str(payload["id"]),
        content_type=content_type,
        collected_at=_parse_datetime(_collection_value(payload, "end_at")),
        published_at=_parse_datetime(payload["timestamp"]),
        likes=_to_int(payload.get("like_count")),
        comments=_to_int(payload.get("comments_count")),
        shares=_to_int(payload.get("shares")),
        views=_to_int(payload.get("plays", payload.get("impressions"))),
        followers=_to_int(account.get("followers_count")),
        raw_path=raw_path,
        title=_optional_text(payload.get("caption")),
        thumbnail_url=_optional_text(payload.get("thumbnail_url") or payload.get("media_url")),
        content_url=_optional_text(payload.get("permalink")),
        channel_name=_optional_text(account.get("username")),
        channel_image_url=_optional_text(account.get("profile_picture_url")),
    )


def _normalize_youtube(payload: dict[str, Any], raw_path: Path) -> SocialMetric:
    statistics = payload.get("statistics", {})
    channel = payload.get("channel", {})
    snippet = payload.get("snippet", {})

    return SocialMetric(
        provider="youtube",
        account_id=_collection_value(payload, "account_id"),
        content_id=_youtube_content_id(payload),
        content_type="video",
        collected_at=_parse_datetime(_collection_value(payload, "end_at")),
        published_at=_parse_datetime(snippet["publishedAt"]),
        likes=_to_int(statistics.get("likeCount")),
        comments=_to_int(statistics.get("commentCount")),
        shares=None,
        views=_to_int(statistics.get("viewCount")),
        followers=_to_int(channel.get("subscriberCount")),
        raw_path=raw_path,
        title=_optional_text(snippet.get("title")),
        thumbnail_url=_youtube_thumbnail_url(snippet),
        content_url=f"https://www.youtube.com/watch?v={_youtube_content_id(payload)}",
        channel_name=_optional_text(snippet.get("channelTitle") or channel.get("title")),
        channel_image_url=_youtube_thumbnail_url(channel),
    )


def _normalize_tiktok(payload: dict[str, Any], raw_path: Path) -> SocialMetric:
    metrics = payload.get("metrics", {})
    author = payload.get("author", {})

    return SocialMetric(
        provider="tiktok",
        account_id=_collection_value(payload, "account_id"),
        content_id=str(payload["item_id"]),
        content_type="video",
        collected_at=_parse_datetime(_collection_value(payload, "end_at")),
        published_at=_parse_datetime(payload["create_time"]),
        likes=_to_int(metrics.get("digg_count")),
        comments=_to_int(metrics.get("comment_count")),
        shares=_to_int(metrics.get("share_count")),
        views=_to_int(metrics.get("play_count")),
        followers=_to_int(author.get("follower_count")),
        raw_path=raw_path,
    )


def _collection_value(payload: dict[str, Any], key: str) -> str:
    collection = payload.get("_collection")
    if not isinstance(collection, dict) or key not in collection:
        raise ValueError(f"Missing collection metadata: {key}")
    return str(collection[key])


def _parse_datetime(value: str) -> datetime:
    return datetime.fromisoformat(value.replace("Z", "+00:00"))


def _to_int(value: Any) -> int | None:
    if value is None:
        return None
    return int(value)


def _youtube_content_id(payload: dict[str, Any]) -> str:
    if "videoId" in payload:
        return str(payload["videoId"])
    return str(payload["id"])


def _youtube_thumbnail_url(payload: dict[str, Any]) -> str | None:
    thumbnails = payload.get("thumbnails")
    if not isinstance(thumbnails, dict):
        return None
    for key in ("high", "medium", "default"):
        item = thumbnails.get(key)
        if isinstance(item, dict) and item.get("url"):
            return str(item["url"])
    return None


def _optional_text(value: object) -> str | None:
    return str(value) if value not in (None, "") else None


def _instagram_content_type(media_type: str) -> str:
    mapping = {
        "IMAGE": "post",
        "CAROUSEL_ALBUM": "post",
        "VIDEO": "video",
        "REELS": "reel",
    }
    return mapping.get(media_type, media_type.lower())
