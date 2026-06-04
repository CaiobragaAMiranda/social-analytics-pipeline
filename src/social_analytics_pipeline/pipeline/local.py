from dataclasses import dataclass
from datetime import datetime
from typing import Protocol

from social_analytics_pipeline.providers import SocialProvider
from social_analytics_pipeline.storage import (
    DeadLetterRecord,
    DeadLetterStorage,
    RawRecord,
    RawStorage,
)
from social_analytics_pipeline.transform import (
    MetricValidationError,
    SocialMetric,
    normalize_payload,
    validate_metric,
)


class MetricLoader(Protocol):
    def load(self, metrics: list[SocialMetric]) -> int:
        """Load normalized metrics and return the number of loaded records."""


@dataclass(frozen=True)
class LocalPipelineResult:
    provider: str
    raw_records: int
    metrics: list[SocialMetric]
    invalid_records: int
    loaded_records: int

    @property
    def valid_records(self) -> int:
        return len(self.metrics)


def run_provider_pipeline(
    provider: SocialProvider,
    account_id: str,
    start_at: datetime,
    end_at: datetime,
    raw_storage: RawStorage,
    loader: MetricLoader,
    dead_letter_storage: DeadLetterStorage | None = None,
) -> LocalPipelineResult:
    payloads = provider.collect_metrics(account_id, start_at, end_at)
    metrics: list[SocialMetric] = []
    invalid_records = 0
    dlq_storage = dead_letter_storage or DeadLetterStorage(raw_storage.root_dir.parent / "dlq")

    for payload in payloads:
        raw_path = raw_storage.save(
            RawRecord(
                provider=provider.name,
                account_id=account_id,
                collected_at=end_at,
                payload=payload,
            )
        )
        try:
            metric = normalize_payload(payload, raw_path)
            metrics.append(validate_metric(metric))
        except (MetricValidationError, ValueError) as exc:
            invalid_records += 1
            dlq_storage.save(
                DeadLetterRecord(
                    provider=provider.name,
                    account_id=account_id,
                    collected_at=end_at,
                    raw_path=raw_path,
                    reason=str(exc),
                )
            )

    loaded_records = loader.load(metrics)

    return LocalPipelineResult(
        provider=provider.name,
        raw_records=len(payloads),
        metrics=metrics,
        invalid_records=invalid_records,
        loaded_records=loaded_records,
    )
