import json
from datetime import datetime
from pathlib import Path
from typing import Any

from social_analytics_pipeline.providers.base import SocialProvider


class FixtureProvider(SocialProvider):
    """Provider that returns deterministic raw payloads from a fixture file."""

    def __init__(self, name: str, fixture_path: Path) -> None:
        self.name = name
        self.fixture_path = fixture_path

    def collect_metrics(
        self,
        account_id: str,
        start_at: datetime,
        end_at: datetime,
    ) -> list[dict[str, Any]]:
        if start_at > end_at:
            raise ValueError("start_at must be before or equal to end_at")

        payloads = json.loads(self.fixture_path.read_text(encoding="utf-8"))
        return [
            self._with_collection_context(payload, account_id, start_at, end_at)
            for payload in payloads
        ]

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


def default_fixture_dir(project_root: Path) -> Path:
    return project_root / "data" / "fixtures"


def build_mock_providers(project_root: Path) -> dict[str, FixtureProvider]:
    fixture_dir = default_fixture_dir(project_root)
    return {
        "instagram": FixtureProvider("instagram", fixture_dir / "instagram_metrics.json"),
        "youtube": FixtureProvider("youtube", fixture_dir / "youtube_metrics.json"),
        "tiktok": FixtureProvider("tiktok", fixture_dir / "tiktok_metrics.json"),
    }
