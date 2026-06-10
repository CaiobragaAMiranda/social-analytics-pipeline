import json
from collections.abc import Mapping
from datetime import datetime
from pathlib import Path
from typing import Any

from social_analytics_pipeline.transform import SocialMetric


def build_interval_artifact_path(
    base_dir: Path,
    provider_name: str,
    start_at: datetime,
    end_at: datetime,
) -> Path:
    start_slug = _datetime_slug(start_at)
    end_slug = _datetime_slug(end_at)
    return base_dir / f"{provider_name}-{start_slug}-{end_slug}.json"


def build_run_summary_artifact_path(
    base_dir: Path,
    provider_name: str,
    start_at: datetime,
    end_at: datetime,
) -> Path:
    start_slug = _datetime_slug(start_at)
    end_slug = _datetime_slug(end_at)
    return base_dir / f"{provider_name}-run-{start_slug}-{end_slug}.json"


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


def write_json_artifact(output_path: Path, payload: Mapping[str, Any]) -> Path:
    output_path.parent.mkdir(parents=True, exist_ok=True)
    output_path.write_text(
        json.dumps(dict(payload), ensure_ascii=False, indent=2),
        encoding="utf-8",
    )
    return output_path


def _serialize_datetime(value: datetime | None) -> str | None:
    if value is None:
        return None
    return value.isoformat()


def _datetime_slug(value: datetime) -> str:
    return value.strftime("%Y%m%dT%H%M%S")
