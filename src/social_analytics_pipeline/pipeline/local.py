from dataclasses import dataclass
from datetime import datetime
from typing import Protocol

from social_analytics_pipeline.providers import SocialProvider
from social_analytics_pipeline.storage import RawRecord, RawStorage
from social_analytics_pipeline.transform import SocialMetric, normalize_payload


class MetricLoader(Protocol):
    def load(self, metrics: list[SocialMetric]) -> int:
        """Load normalized metrics and return the number of loaded records."""


@dataclass(frozen=True)
class LocalPipelineResult:
    provider: str
    raw_records: int
    metrics: list[SocialMetric]
    loaded_records: int


def run_provider_pipeline(
    provider: SocialProvider,
    account_id: str,
    start_at: datetime,
    end_at: datetime,
    raw_storage: RawStorage,
    loader: MetricLoader,
) -> LocalPipelineResult:
    payloads = provider.collect_metrics(account_id, start_at, end_at)
    metrics: list[SocialMetric] = []

    for payload in payloads:
        raw_path = raw_storage.save(
            RawRecord(
                provider=provider.name,
                account_id=account_id,
                collected_at=end_at,
                payload=payload,
            )
        )
        metrics.append(normalize_payload(payload, raw_path))

    loaded_records = loader.load(metrics)

    return LocalPipelineResult(
        provider=provider.name,
        raw_records=len(payloads),
        metrics=metrics,
        loaded_records=loaded_records,
    )
