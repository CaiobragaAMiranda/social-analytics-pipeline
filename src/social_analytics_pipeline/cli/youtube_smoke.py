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


class YouTubeChannelResolver(Protocol):
    def resolve_channel_id(self, handle: str) -> str:
        """Resolve a public YouTube handle to a channel id."""


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
    current_env = dict(os.environ if env is None else env)
    file_env = load_env_file(env_path or Path(".env"))
    return {**file_env, **current_env}


def require_smoke_setting(
    runtime_env: Mapping[str, str],
    key: str,
    env_path: Path | None = None,
) -> str:
    value = runtime_env.get(key, "")
    if value:
        return value

    if not (env_path or Path(".env")).exists():
        raise RuntimeError(
            f"{key} is required. Create a local .env from .env.example and fill YouTube settings."
        )

    raise RuntimeError(f"{key} is required in environment or local .env.")


def require_smoke_settings(
    runtime_env: Mapping[str, str],
    keys: tuple[str, ...],
    env_path: Path | None = None,
) -> dict[str, str]:
    missing = [key for key in keys if not runtime_env.get(key, "")]
    if not missing:
        return {key: runtime_env[key] for key in keys}

    missing_text = ", ".join(missing)
    if not (env_path or Path(".env")).exists():
        raise RuntimeError(
            f"{missing_text} required. Create a local .env from .env.example "
            "and fill YouTube settings."
        )

    raise RuntimeError(f"{missing_text} required in environment or local .env.")


def require_youtube_channel_id(channel_id: str) -> str:
    if not channel_id.startswith("UC"):
        raise RuntimeError(
            "YOUTUBE_CHANNEL_ID must be a public YouTube channel ID that starts with UC, "
            "not a channel name or handle."
        )
    return channel_id


def resolve_smoke_channel_id(
    runtime_env: Mapping[str, str],
    resolver: YouTubeChannelResolver,
    env_path: Path | None = None,
) -> str:
    channel_id = runtime_env.get("YOUTUBE_CHANNEL_ID", "")
    if channel_id:
        return require_youtube_channel_id(channel_id)

    handle = runtime_env.get("YOUTUBE_CHANNEL_HANDLE", "")
    if handle:
        return resolver.resolve_channel_id(handle)

    if not (env_path or Path(".env")).exists():
        raise RuntimeError(
            "YOUTUBE_CHANNEL_ID or YOUTUBE_CHANNEL_HANDLE required. Create a local .env "
            "from .env.example and fill YouTube settings."
        )

    raise RuntimeError("YOUTUBE_CHANNEL_ID or YOUTUBE_CHANNEL_HANDLE required in local .env.")


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


def main(env: Mapping[str, str] | None = None, env_path: Path | None = None) -> int:
    runtime_env = build_runtime_env(env, env_path)
    required_settings = require_smoke_settings(
        runtime_env,
        ("YOUTUBE_API_KEY",),
        env_path,
    )

    lookback_days = int(runtime_env.get("YOUTUBE_SMOKE_LOOKBACK_DAYS", "30"))
    if lookback_days < 1:
        raise RuntimeError("YOUTUBE_SMOKE_LOOKBACK_DAYS must be greater than or equal to 1.")

    end_at = datetime.now(UTC)
    start_at = end_at - timedelta(days=lookback_days)
    provider = YouTubeDataApiProvider(YouTubeApiConfig.from_env(runtime_env))
    channel_id = resolve_smoke_channel_id({**runtime_env, **required_settings}, provider, env_path)
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
