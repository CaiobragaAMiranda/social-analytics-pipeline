import tempfile
import unittest
from pathlib import Path

from social_analytics_pipeline.cli.channel_catalog import (
    add_channel,
    list_channels,
    remove_channel,
    rename_channel,
    set_platform_enabled,
)


class ChannelCatalogCliTest(unittest.TestCase):
    def test_catalog_operations_manage_one_local_channel(self) -> None:
        with tempfile.TemporaryDirectory() as tmpdir:
            catalog_path = Path(tmpdir) / "channels.local.json"
            add_channel(catalog_path, "brand", "Brand Channel")
            rename_channel(catalog_path, "brand", "Brand Studio")
            set_platform_enabled(catalog_path, "brand", "youtube", True)
            set_platform_enabled(catalog_path, "brand", "youtube", False)
            channels = list_channels(catalog_path)
            remove_channel(catalog_path, "brand")

        self.assertEqual(channels[0].display_name, "Brand Studio")
        self.assertFalse(channels[0].platforms[0].enabled)


if __name__ == "__main__":
    unittest.main()
