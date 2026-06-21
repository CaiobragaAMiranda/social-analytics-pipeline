import json
import tempfile
import unittest
from pathlib import Path

from social_analytics_pipeline.config import (
    add_channel_identity,
    load_channel_identity_config,
    match_channel_identity,
    remove_channel_identity,
    update_channel_identity,
    write_channel_identity_config,
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
            self.assertTrue(channels[0].platforms[0].enabled)

    def test_load_channel_identity_config_preserves_platform_enabled_state(self) -> None:
        with tempfile.TemporaryDirectory() as tmpdir:
            config_path = Path(tmpdir) / "channels.json"
            config_path.write_text(
                json.dumps(
                    {
                        "channels": [
                            {
                                "id": "brand",
                                "display_name": "Brand Channel",
                                "platforms": {
                                    "youtube": {"handle": "@brand", "enabled": False}
                                },
                            }
                        ]
                    }
                ),
                encoding="utf-8",
            )

            channels = load_channel_identity_config(config_path)

        self.assertFalse(channels[0].platforms[0].enabled)

    def test_write_channel_identity_config_round_trips_catalog(self) -> None:
        with tempfile.TemporaryDirectory() as tmpdir:
            source_path = Path(tmpdir) / "source.json"
            target_path = Path(tmpdir) / "catalog" / "channels.json"
            source_path.write_text(
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

            write_channel_identity_config(
                target_path,
                load_channel_identity_config(source_path),
            )
            saved = load_channel_identity_config(target_path)

        self.assertEqual(saved[0].channel_id, "brand")
        self.assertTrue(saved[0].platforms[0].enabled)

    def test_load_channel_identity_config_rejects_duplicate_ids(self) -> None:
        with tempfile.TemporaryDirectory() as tmpdir:
            config_path = Path(tmpdir) / "channels.json"
            config_path.write_text(
                json.dumps(
                    {
                        "channels": [
                            {"id": "brand", "display_name": "One", "platforms": {}},
                            {"id": "BRAND", "display_name": "Two", "platforms": {}},
                        ]
                    }
                ),
                encoding="utf-8",
            )

            with self.assertRaisesRegex(RuntimeError, "duplicate IDs"):
                load_channel_identity_config(config_path)

    def test_catalog_operations_add_update_and_remove_channel(self) -> None:
        with tempfile.TemporaryDirectory() as tmpdir:
            config_path = Path(tmpdir) / "channels.json"
            config_path.write_text(
                json.dumps(
                    {
                        "channels": [
                            {"id": "brand", "display_name": "Brand", "platforms": {}}
                        ]
                    }
                ),
                encoding="utf-8",
            )
            original = load_channel_identity_config(config_path)
            channel_type = original[0].__class__
            added = add_channel_identity(
                original,
                channel_type("studio", "Studio", "", ()),
            )
            updated = update_channel_identity(
                added,
                added[1].__class__("studio", "Studio Updated", "", ()),
            )
            remaining = remove_channel_identity(updated, "brand")

        self.assertEqual(remaining[0].display_name, "Studio Updated")

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
