import json
from datetime import datetime
from pathlib import Path
from typing import Any

from social_analytics_pipeline.transform import SocialMetric


def metric_to_artifact_row(metric: SocialMetric) -> dict[str, Any]:
    return {
        "provider": metric.provider,
        "account_id": metric.account_id,
        "content_id": metric.content_id,
        "content_type": metric.content_type,
        "collected_at": _serialize_datetime(metric.collected_at),
        "published_at": _serialize_datetime(metric.published_at),
        "likes": metric.likes,
        "comments": metric.comments,
        "shares": metric.shares,
        "views": metric.views,
        "followers": metric.followers,
        "raw_path": metric.raw_path.as_posix(),
    }


class JsonMetricArtifactLoader:
    """Load normalized metrics into a local JSON artifact for Airflow smoke runs."""

    def __init__(self, output_path: Path) -> None:
        self.output_path = output_path

    def load(self, metrics: list[SocialMetric]) -> int:
        self.output_path.parent.mkdir(parents=True, exist_ok=True)
        rows = [metric_to_artifact_row(metric) for metric in metrics]
        self.output_path.write_text(
            json.dumps(rows, ensure_ascii=False, indent=2),
            encoding="utf-8",
        )
        return len(rows)


def _serialize_datetime(value: datetime | None) -> str | None:
    if value is None:
        return None
    return value.isoformat()
