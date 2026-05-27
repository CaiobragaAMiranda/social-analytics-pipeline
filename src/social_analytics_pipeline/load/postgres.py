from collections.abc import Iterable
from typing import Any

from social_analytics_pipeline.transform import SocialMetric

SOCIAL_METRICS_UPSERT_SQL = """
INSERT INTO social_metrics (
    provider,
    account_id,
    content_id,
    content_type,
    collected_at,
    published_at,
    likes,
    comments,
    shares,
    views,
    followers,
    raw_path
) VALUES (
    %(provider)s,
    %(account_id)s,
    %(content_id)s,
    %(content_type)s,
    %(collected_at)s,
    %(published_at)s,
    %(likes)s,
    %(comments)s,
    %(shares)s,
    %(views)s,
    %(followers)s,
    %(raw_path)s
)
ON CONFLICT (provider, account_id, content_id, collected_at)
DO UPDATE SET
    content_type = EXCLUDED.content_type,
    published_at = EXCLUDED.published_at,
    likes = EXCLUDED.likes,
    comments = EXCLUDED.comments,
    shares = EXCLUDED.shares,
    views = EXCLUDED.views,
    followers = EXCLUDED.followers,
    raw_path = EXCLUDED.raw_path,
    updated_at = NOW();
"""


def metric_to_row(metric: SocialMetric) -> dict[str, Any]:
    return {
        "provider": metric.provider,
        "account_id": metric.account_id,
        "content_id": metric.content_id,
        "content_type": metric.content_type,
        "collected_at": metric.collected_at,
        "published_at": metric.published_at,
        "likes": metric.likes,
        "comments": metric.comments,
        "shares": metric.shares,
        "views": metric.views,
        "followers": metric.followers,
        "raw_path": metric.raw_path.as_posix(),
    }


class PostgresMetricLoader:
    """Load normalized metrics into PostgreSQL using an idempotent upsert."""

    def __init__(self, dsn: str) -> None:
        self.dsn = dsn

    def load(self, metrics: Iterable[SocialMetric]) -> int:
        rows = [metric_to_row(metric) for metric in metrics]
        if not rows:
            return 0

        try:
            import psycopg
        except ImportError as exc:
            raise RuntimeError("Install psycopg to load metrics into PostgreSQL.") from exc

        with psycopg.connect(self.dsn) as connection:
            with connection.cursor() as cursor:
                cursor.executemany(SOCIAL_METRICS_UPSERT_SQL, rows)
            connection.commit()

        return len(rows)
