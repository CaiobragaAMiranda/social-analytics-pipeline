import argparse
from pathlib import Path

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
        channel.channel_id, display_name, channel.image_url, channel.platforms
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
        channel.channel_id, channel.display_name, channel.image_url, platforms
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
    platforms = tuple(
        ChannelPlatformIdentity(
            item.provider, item.channel_id, handle, item.account_id, item.enabled
        )
        if item.provider == provider
        else item
        for item in channel.platforms
    )
    if not any(item.provider == provider for item in platforms):
        platforms += (ChannelPlatformIdentity(provider, handle=handle, enabled=False),)
    updated = ChannelIdentityConfig(
        channel.channel_id, channel.display_name, channel.image_url, platforms
    )
    write_channel_identity_config(
        catalog_path, update_channel_identity(list_channels(catalog_path), updated)
    )
    return updated


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
    actions.add_argument("--enable", nargs=2, metavar=("ID", "PROVIDER"))
    actions.add_argument("--disable", nargs=2, metavar=("ID", "PROVIDER"))
    parser.add_argument("--name")
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


if __name__ == "__main__":
    raise SystemExit(main())
