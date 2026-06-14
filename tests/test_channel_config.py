import json
import tempfile
import unittest
from pathlib import Path

from social_analytics_pipeline.config import (
    load_channel_identity_config,
    match_channel_identity,
)


class ChannelConfigTest(unittest.TestCase):
    def test_load_channel_identity_config_accepts_complete_mapping(self) -> None:
        with tempfile.TemporaryDirectory() as tmpdir:
            config_path = Path(tmpdir) / "channels.json"
            config_path.write_text(
                json.dumps(
                    {
                        "channels": [
                            {
                                "id": "brand",
                                "display_name": "Brand Channel",
                                "image_url": "https://example.com/brand.png",
                                "platforms": {
                                    "youtube": {
                                        "channel_id": "UC_EXAMPLE",
                                        "handle": "@brand-youtube",
                                    },
                                    "tiktok": {"handle": "@brand-tiktok"},
                                    "instagram": {"handle": "@brand-instagram"},
                                },
                            }
                        ]
                    }
                ),
                encoding="utf-8",
            )

            channels = load_channel_identity_config(config_path)

            self.assertEqual(len(channels), 1)
            self.assertEqual(channels[0].channel_id, "brand")
            self.assertEqual(channels[0].display_name, "Brand Channel")
            self.assertEqual(len(channels[0].platforms), 3)

    def test_load_channel_identity_config_allows_missing_platforms(self) -> None:
        with tempfile.TemporaryDirectory() as tmpdir:
            config_path = Path(tmpdir) / "channels.json"
            config_path.write_text(
                json.dumps(
                    {
                        "channels": [
                            {
                                "id": "brand",
                                "display_name": "Brand Channel",
                                "platforms": {"youtube": {"handle": "@brand"}},
                            }
                        ]
                    }
                ),
                encoding="utf-8",
            )

            channels = load_channel_identity_config(config_path)

            self.assertEqual(len(channels[0].platforms), 1)

    def test_match_channel_identity_uses_provider_and_handle(self) -> None:
        with tempfile.TemporaryDirectory() as tmpdir:
            config_path = Path(tmpdir) / "channels.json"
            config_path.write_text(
                json.dumps(
                    {
                        "channels": [
                            {
                                "id": "brand",
                                "display_name": "Brand Channel",
                                "platforms": {"youtube": {"handle": "@brand"}},
                            }
                        ]
                    }
                ),
                encoding="utf-8",
            )
            channels = load_channel_identity_config(config_path)

            match = match_channel_identity(
                {"source": {"provider": "youtube", "channel_handle": "@brand"}},
                channels,
            )

            self.assertIsNotNone(match)
            self.assertEqual(match.display_name if match else "", "Brand Channel")

    def test_match_channel_identity_does_not_cross_match_provider(self) -> None:
        with tempfile.TemporaryDirectory() as tmpdir:
            config_path = Path(tmpdir) / "channels.json"
            config_path.write_text(
                json.dumps(
                    {
                        "channels": [
                            {
                                "id": "brand",
                                "display_name": "Brand Channel",
                                "platforms": {"instagram": {"handle": "@brand"}},
                            }
                        ]
                    }
                ),
                encoding="utf-8",
            )
            channels = load_channel_identity_config(config_path)

            match = match_channel_identity(
                {"source": {"provider": "youtube", "channel_handle": "@brand"}},
                channels,
            )

            self.assertIsNone(match)

    def test_match_channel_identity_uses_single_provider_fallback(self) -> None:
        with tempfile.TemporaryDirectory() as tmpdir:
            config_path = Path(tmpdir) / "channels.json"
            config_path.write_text(
                json.dumps(
                    {
                        "channels": [
                            {
                                "id": "brand",
                                "display_name": "Brand Channel",
                                "platforms": {"youtube": {"handle": "@brand"}},
                            }
                        ]
                    }
                ),
                encoding="utf-8",
            )
            channels = load_channel_identity_config(config_path)

            match = match_channel_identity({"source": {"provider": "youtube"}}, channels)

            self.assertIsNotNone(match)
            self.assertEqual(match.display_name if match else "", "Brand Channel")


if __name__ == "__main__":
    unittest.main()
