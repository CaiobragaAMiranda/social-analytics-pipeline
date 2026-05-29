import os
import sys
from collections.abc import Mapping
from dataclasses import dataclass
from datetime import UTC, datetime, timedelta
from pathlib import Path
from typing import Protocol

from social_analytics_pipeline.providers import YouTubeApiConfig, YouTubeDataApiProvider
from social_analytics_pipeline.transform import normalize_payload


class YouTubeCollector(Protocol):
    def collect_metrics(
        self,
        account_id: str,
        start_at: datetime,
        end_at: datetime,
    ) -> list[dict]:
        """Collect raw YouTube payloads for a channel and interval."""


@dataclass(frozen=True)
class YouTubeSmokeSummary:
    provider: str
    channel_id: str
    start_at: datetime
    end_at: datetime
    raw_records: int
    normalized_records: int


def load_env_file(path: Path) -> dict[str, str]:
    if not path.exists():
        return {}

    values: dict[str, str] = {}
    for line in path.read_text(encoding="utf-8").splitlines():
        stripped = line.strip()
        if not stripped or stripped.startswith("#") or "=" not in stripped:
            continue

        key, value = stripped.split("=", 1)
        key = key.strip()
        if key:
            values[key] = _strip_env_value(value.strip())

    return values


def build_runtime_env(
    env: Mapping[str, str] | None = None,
    env_path: Path | None = None,
) -> dict[str, str]:
    current_env = dict(env or os.environ)
    file_env = load_env_file(env_path or Path(".env"))
    return {**file_env, **current_env}


def build_youtube_smoke_summary(
    provider: YouTubeCollector,
    channel_id: str,
    start_at: datetime,
    end_at: datetime,
) -> YouTubeSmokeSummary:
    payloads = provider.collect_metrics(channel_id, start_at, end_at)
    metrics = [
        normalize_payload(payload, raw_path=Path(f"youtube-smoke/{index}.json"))
        for index, payload in enumerate(payloads, start=1)
    ]
    return YouTubeSmokeSummary(
        provider="youtube",
        channel_id=channel_id,
        start_at=start_at,
        end_at=end_at,
        raw_records=len(payloads),
        normalized_records=len(metrics),
    )


def main(env: Mapping[str, str] | None = None) -> int:
    runtime_env = build_runtime_env(env)
    channel_id = runtime_env.get("YOUTUBE_CHANNEL_ID", "")
    if not channel_id:
        raise RuntimeError("YOUTUBE_CHANNEL_ID is required for the YouTube smoke command.")

    lookback_days = int(runtime_env.get("YOUTUBE_SMOKE_LOOKBACK_DAYS", "30"))
    if lookback_days < 1:
        raise RuntimeError("YOUTUBE_SMOKE_LOOKBACK_DAYS must be greater than or equal to 1.")

    end_at = datetime.now(UTC)
    start_at = end_at - timedelta(days=lookback_days)
    provider = YouTubeDataApiProvider(YouTubeApiConfig.from_env(runtime_env))
    summary = build_youtube_smoke_summary(provider, channel_id, start_at, end_at)

    print("YouTube smoke summary")
    print(f"provider={summary.provider}")
    print("channel_id=<configured>")
    print(f"start_at={summary.start_at.isoformat()}")
    print(f"end_at={summary.end_at.isoformat()}")
    print(f"raw_records={summary.raw_records}")
    print(f"normalized_records={summary.normalized_records}")
    return 0


def _strip_env_value(value: str) -> str:
    if len(value) >= 2 and value[0] == value[-1] and value[0] in {'"', "'"}:
        return value[1:-1]
    return value


if __name__ == "__main__":
    try:
        raise SystemExit(main())
    except RuntimeError as exc:
        print(f"Error: {exc}", file=sys.stderr)
        raise SystemExit(1) from None
