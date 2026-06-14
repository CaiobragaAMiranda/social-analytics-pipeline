import json
from dataclasses import dataclass
from pathlib import Path
from typing import Any


@dataclass(frozen=True)
class PipelineConfig:
    """Runtime paths used by the local MVP pipeline."""

    project_root: Path
    raw_dir: Path
    processed_dir: Path

    @classmethod
    def from_project_root(cls, project_root: Path) -> "PipelineConfig":
        data_dir = project_root / "data"
        return cls(
            project_root=project_root,
            raw_dir=data_dir / "raw",
            processed_dir=data_dir / "processed",
        )


@dataclass(frozen=True)
class ChannelPlatformIdentity:
    provider: str
    channel_id: str = ""
    handle: str = ""
    account_id: str = ""


@dataclass(frozen=True)
class ChannelIdentityConfig:
    channel_id: str
    display_name: str
    image_url: str
    platforms: tuple[ChannelPlatformIdentity, ...]


def load_channel_identity_config(config_path: Path) -> tuple[ChannelIdentityConfig, ...]:
    payload = json.loads(config_path.read_text(encoding="utf-8"))
    if not isinstance(payload, dict):
        raise RuntimeError("Channel identity config must contain an object.")
    channels = payload.get("channels", [])
    if not isinstance(channels, list):
        raise RuntimeError("Channel identity config 'channels' must be a list.")
    return tuple(_channel_identity_config(channel) for channel in channels)


def match_channel_identity(
    report_payload: dict[str, Any],
    channels: tuple[ChannelIdentityConfig, ...],
) -> ChannelIdentityConfig | None:
    source = report_payload.get("source", {})
    if not isinstance(source, dict):
        source = {}
    provider = str(source.get("provider", report_payload.get("provider", ""))).lower()
    candidates = {
        str(value).strip().lower()
        for value in (
            source.get("channel_id"),
            source.get("channel_handle"),
            source.get("handle"),
            source.get("account_id"),
            source.get("name"),
            source.get("channel_name"),
            report_payload.get("channel_id"),
            report_payload.get("channel_handle"),
            report_payload.get("account_id"),
            report_payload.get("channel_name"),
        )
        if value
    }

    for channel in channels:
        for platform in channel.platforms:
            if platform.provider.lower() != provider:
                continue
            platform_candidates = {
                value.strip().lower()
                for value in (platform.channel_id, platform.handle, platform.account_id)
                if value
            }
            if candidates & platform_candidates:
                return channel
    provider_matches = [
        channel
        for channel in channels
        for platform in channel.platforms
        if platform.provider.lower() == provider
    ]
    if not candidates and len(provider_matches) == 1:
        return provider_matches[0]
    return None


def _channel_identity_config(payload: object) -> ChannelIdentityConfig:
    if not isinstance(payload, dict):
        raise RuntimeError("Each channel identity entry must contain an object.")
    channel_id = _required_text(payload, "id")
    display_name = _required_text(payload, "display_name")
    image_url = str(payload.get("image_url", ""))
    platforms = payload.get("platforms", {})
    if not isinstance(platforms, dict):
        raise RuntimeError("Channel identity config 'platforms' must be an object.")
    return ChannelIdentityConfig(
        channel_id=channel_id,
        display_name=display_name,
        image_url=image_url,
        platforms=tuple(
            _platform_identity(provider, platform_payload)
            for provider, platform_payload in platforms.items()
        ),
    )


def _platform_identity(provider: object, payload: object) -> ChannelPlatformIdentity:
    if not isinstance(payload, dict):
        raise RuntimeError("Each platform identity entry must contain an object.")
    return ChannelPlatformIdentity(
        provider=str(provider),
        channel_id=str(payload.get("channel_id", "")),
        handle=str(payload.get("handle", "")),
        account_id=str(payload.get("account_id", "")),
    )


def _required_text(payload: dict[str, Any], key: str) -> str:
    value = payload.get(key)
    if not value:
        raise RuntimeError(f"Channel identity config requires '{key}'.")
    return str(value)
