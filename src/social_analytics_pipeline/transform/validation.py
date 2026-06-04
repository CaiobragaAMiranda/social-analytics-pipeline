from social_analytics_pipeline.transform.schema import SocialMetric


class MetricValidationError(ValueError):
    pass


def validate_metric(metric: SocialMetric) -> SocialMetric:
    _require_text(metric.provider, "provider", metric)
    _require_text(metric.account_id, "account_id", metric)
    _require_text(metric.content_id, "content_id", metric)
    _require_text(metric.content_type, "content_type", metric)

    for field_name in ("likes", "comments", "shares", "views", "followers"):
        _require_non_negative(getattr(metric, field_name), field_name, metric)

    if metric.published_at and metric.published_at > metric.collected_at:
        raise MetricValidationError(
            _error_message(
                metric,
                "published_at",
                "must be before or equal to collected_at",
            )
        )

    return metric


def validate_metrics(metrics: list[SocialMetric]) -> list[SocialMetric]:
    return [validate_metric(metric) for metric in metrics]


def _require_text(value: str, field_name: str, metric: SocialMetric) -> None:
    if value.strip():
        return

    raise MetricValidationError(_error_message(metric, field_name, "must not be empty"))


def _require_non_negative(value: int | None, field_name: str, metric: SocialMetric) -> None:
    if value is None or value >= 0:
        return

    raise MetricValidationError(
        _error_message(metric, field_name, "must be greater than or equal to 0")
    )


def _error_message(metric: SocialMetric, field_name: str, reason: str) -> str:
    return (
        f"Metric validation failed for field '{field_name}': {reason}. "
        f"provider={metric.provider or '<empty>'} "
        f"content_id={metric.content_id or '<empty>'} "
        f"raw_path={metric.raw_path.as_posix()}"
    )
