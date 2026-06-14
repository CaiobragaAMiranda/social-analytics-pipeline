from dataclasses import dataclass
from datetime import datetime
from pathlib import Path


@dataclass(frozen=True)
class SocialMetric:
    provider: str
    account_id: str
    content_id: str
    content_type: str
    collected_at: datetime
    published_at: datetime | None
    likes: int | None
    comments: int | None
    shares: int | None
    views: int | None
    followers: int | None
    raw_path: Path
    title: str | None = None
    thumbnail_url: str | None = None
    content_url: str | None = None
    channel_name: str | None = None
    channel_image_url: str | None = None
