import argparse
import datetime as dt
import json
from pathlib import Path
from typing import Any

from social_analytics_pipeline.config import (
    ChannelIdentityConfig,
    ChannelPlatformIdentity,
    add_channel_identity,
    load_channel_identity_config,
    remove_channel_identity,
    update_channel_identity,
    write_channel_identity_config,
)

DEFAULT_CATALOG_PATH = Path("config/channels.local.json")


def list_channels(catalog_path: Path) -> tuple[ChannelIdentityConfig, ...]:
    return load_channel_identity_config(catalog_path) if catalog_path.exists() else ()


def add_channel(catalog_path: Path, channel_id: str, display_name: str) -> ChannelIdentityConfig:
    channel = ChannelIdentityConfig(channel_id, display_name, "", ())
    write_channel_identity_config(
        catalog_path, add_channel_identity(list_channels(catalog_path), channel)
    )
    return channel


def rename_channel(catalog_path: Path, channel_id: str, display_name: str) -> ChannelIdentityConfig:
    channel = _channel_by_id(list_channels(catalog_path), channel_id)
    updated = ChannelIdentityConfig(
        channel.channel_id,
        display_name,
        channel.image_url,
        channel.platforms,
        channel.schedule,
    )
    write_channel_identity_config(
        catalog_path, update_channel_identity(list_channels(catalog_path), updated)
    )
    return updated


def set_channel_image(
    catalog_path: Path,
    channel_id: str,
    image_url: str,
) -> ChannelIdentityConfig:
    channel = _channel_by_id(list_channels(catalog_path), channel_id)
    updated = ChannelIdentityConfig(
        channel.channel_id,
        channel.display_name,
        image_url,
        channel.platforms,
        channel.schedule,
    )
    write_channel_identity_config(
        catalog_path, update_channel_identity(list_channels(catalog_path), updated)
    )
    return updated


def remove_channel(catalog_path: Path, channel_id: str) -> None:
    write_channel_identity_config(
        catalog_path, remove_channel_identity(list_channels(catalog_path), channel_id)
    )


def set_platform_enabled(
    catalog_path: Path,
    channel_id: str,
    provider: str,
    enabled: bool,
) -> ChannelIdentityConfig:
    channel = _channel_by_id(list_channels(catalog_path), channel_id)
    platforms = tuple(
        ChannelPlatformIdentity(
            item.provider, item.channel_id, item.handle, item.account_id, enabled
        )
        if item.provider == provider
        else item
        for item in channel.platforms
    )
    if not any(item.provider == provider for item in platforms):
        platforms += (ChannelPlatformIdentity(provider, enabled=enabled),)
    updated = ChannelIdentityConfig(
        channel.channel_id,
        channel.display_name,
        channel.image_url,
        platforms,
        channel.schedule,
    )
    write_channel_identity_config(
        catalog_path, update_channel_identity(list_channels(catalog_path), updated)
    )
    return updated


def set_platform_reference(
    catalog_path: Path,
    channel_id: str,
    provider: str,
    handle: str,
) -> ChannelIdentityConfig:
    channel = _channel_by_id(list_channels(catalog_path), channel_id)
    normalized_handle = handle.strip()
    platforms = tuple(
        ChannelPlatformIdentity(
            item.provider, item.channel_id, normalized_handle, item.account_id, item.enabled
        )
        if item.provider == provider
        else item
        for item in channel.platforms
    )
    if not any(item.provider == provider for item in platforms):
        platforms += (
            ChannelPlatformIdentity(provider, handle=normalized_handle, enabled=False),
        )
    updated = ChannelIdentityConfig(
        channel.channel_id,
        channel.display_name,
        channel.image_url,
        platforms,
        channel.schedule,
    )
    write_channel_identity_config(
        catalog_path, update_channel_identity(list_channels(catalog_path), updated)
    )
    return updated


def set_channel_schedule(
    catalog_path: Path,
    channel_id: str,
    schedule: str,
) -> ChannelIdentityConfig:
    channel = _channel_by_id(list_channels(catalog_path), channel_id)
    updated = ChannelIdentityConfig(
        channel.channel_id,
        channel.display_name,
        channel.image_url,
        channel.platforms,
        schedule,
    )
    write_channel_identity_config(
        catalog_path, update_channel_identity(list_channels(catalog_path), updated)
    )
    return updated


def collection_plan(catalog_path: Path, channel_id: str) -> tuple[dict[str, Any], ...]:
    channel = _channel_by_id(list_channels(catalog_path), channel_id)
    return tuple(
        {
            "provider": platform.provider,
            "status": "ready" if platform.enabled and platform.handle else "pending",
            "reference": platform.handle,
            "selected": bool(platform.enabled and platform.handle),
        }
        for platform in channel.platforms
    )


def load_collection_status(status_path: Path) -> dict[str, Any]:
    if not status_path.exists():
        return {"channels": {}}
    payload = json.loads(status_path.read_text(encoding="utf-8"))
    if not isinstance(payload, dict):
        raise RuntimeError("Collection status must contain an object.")
    channels = payload.setdefault("channels", {})
    if not isinstance(channels, dict):
        raise RuntimeError("Collection status 'channels' must contain an object.")
    return payload


def record_collection_status(
    status_path: Path,
    channel_id: str,
    sources: tuple[dict[str, Any], ...] | list[dict[str, Any]],
    attempted_at: dt.datetime | None = None,
) -> dict[str, Any]:
    timestamp = _status_timestamp(attempted_at)
    payload = load_collection_status(status_path)
    channels = payload.setdefault("channels", {})
    channel_status = channels.setdefault(channel_id, {"sources": {}})
    source_statuses = channel_status.setdefault("sources", {})
    for source in sources:
        provider = str(source.get("provider", ""))
        if not provider:
            continue
        selected = bool(source.get("selected"))
        existing = source_statuses.get(provider, {})
        status = str(source.get("collection_status", "planned" if selected else "pending"))
        outcome = str(
            source.get(
                "outcome",
                (
                    "Ready for provider collection"
                    if selected
                    else "Missing enabled public source reference"
                ),
            )
        )
        source_statuses[provider] = {
            "last_attempt": timestamp,
            "last_success": timestamp if status == "ok" else str(existing.get("last_success", "")),
            "status": status,
            "outcome": outcome,
        }
        if "loaded_records" in source:
            source_statuses[provider]["loaded_records"] = int(source.get("loaded_records", 0))
    status_path.parent.mkdir(parents=True, exist_ok=True)
    status_path.write_text(json.dumps(payload, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    return payload


def _status_timestamp(value: dt.datetime | None) -> str:
    timestamp = value or dt.datetime.now(dt.UTC)
    if timestamp.tzinfo is None:
        timestamp = timestamp.replace(tzinfo=dt.UTC)
    return timestamp.astimezone(dt.UTC).replace(microsecond=0).isoformat().replace("+00:00", "Z")


def _channel_by_id(
    channels: tuple[ChannelIdentityConfig, ...], channel_id: str
) -> ChannelIdentityConfig:
    for channel in channels:
        if channel.channel_id == channel_id:
            return channel
    raise RuntimeError(f"Channel identity '{channel_id}' does not exist.")


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description="Manage the local monitored channel catalog.")
    parser.add_argument("--catalog", type=Path, default=DEFAULT_CATALOG_PATH)
    actions = parser.add_mutually_exclusive_group(required=True)
    actions.add_argument("--list", action="store_true")
    actions.add_argument("--add", metavar="ID")
    actions.add_argument("--rename", metavar="ID")
    actions.add_argument("--remove", metavar="ID")
    actions.add_argument("--set-image", metavar="ID")
    actions.add_argument("--reference", nargs=2, metavar=("ID", "PROVIDER"))
    actions.add_argument("--schedule", nargs=2, metavar=("ID", "SCHEDULE"))
    actions.add_argument("--enable", nargs=2, metavar=("ID", "PROVIDER"))
    actions.add_argument("--disable", nargs=2, metavar=("ID", "PROVIDER"))
    parser.add_argument("--name")
    parser.add_argument("--image-url")
    parser.add_argument("--handle")
    args = parser.parse_args(argv)
    if args.list:
        for channel in list_channels(args.catalog):
            print(f"channel={channel.channel_id} name={channel.display_name}")
    elif args.add:
        print(f"added={add_channel(args.catalog, args.add, _required_name(args)).channel_id}")
    elif args.rename:
        print(
            f"renamed={rename_channel(args.catalog, args.rename, _required_name(args)).channel_id}"
        )
    elif args.remove:
        remove_channel(args.catalog, args.remove)
        print(f"removed={args.remove}")
    elif args.set_image:
        channel = set_channel_image(args.catalog, args.set_image, _required_image_url(args))
        print(f"image_updated={channel.channel_id}")
    elif args.reference:
        channel_id, provider = args.reference
        set_platform_reference(args.catalog, channel_id, provider, _required_handle(args))
        print(f"reference_updated={provider} channel={channel_id}")
    elif args.schedule:
        channel_id, schedule = args.schedule
        set_channel_schedule(args.catalog, channel_id, schedule)
        print(f"schedule={schedule or 'off'} channel={channel_id}")
    else:
        channel_id, provider = args.enable or args.disable
        enabled = args.enable is not None
        set_platform_enabled(args.catalog, channel_id, provider, enabled)
        print(f"platform={provider} enabled={str(enabled).lower()} channel={channel_id}")
    return 0


def _required_name(args: argparse.Namespace) -> str:
    if not args.name:
        raise RuntimeError("--name is required for this action.")
    return args.name


def _required_image_url(args: argparse.Namespace) -> str:
    if args.image_url is None:
        raise RuntimeError("--image-url is required for this action.")
    return args.image_url


def _required_handle(args: argparse.Namespace) -> str:
    if args.handle is None:
        raise RuntimeError("--handle is required for this action.")
    return args.handle


if __name__ == "__main__":
    raise SystemExit(main())
