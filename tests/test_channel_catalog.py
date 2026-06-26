import tempfile
import unittest
from pathlib import Path

from social_analytics_pipeline.cli.channel_catalog import (
    add_channel,
    collection_plan,
    list_channels,
    load_collection_status,
    main,
    record_collection_status,
    remove_channel,
    rename_channel,
    set_channel_image,
    set_channel_schedule,
    set_platform_enabled,
    set_platform_reference,
)


class ChannelCatalogCliTest(unittest.TestCase):
    def test_catalog_operations_manage_one_local_channel(self) -> None:
        with tempfile.TemporaryDirectory() as tmpdir:
            catalog_path = Path(tmpdir) / "channels.local.json"
            add_channel(catalog_path, "brand", "Brand Channel")
            rename_channel(catalog_path, "brand", "Brand Studio")
            set_platform_enabled(catalog_path, "brand", "youtube", True)
            set_platform_enabled(catalog_path, "brand", "youtube", False)
            set_platform_reference(catalog_path, "brand", "youtube", "@brand")
            channels = list_channels(catalog_path)
            remove_channel(catalog_path, "brand")

        self.assertEqual(channels[0].display_name, "Brand Studio")
        self.assertFalse(channels[0].platforms[0].enabled)
        self.assertEqual(channels[0].platforms[0].handle, "@brand")

    def test_set_channel_schedule_persists_daily_or_weekly_collection_intent(self) -> None:
        with tempfile.TemporaryDirectory() as tmpdir:
            catalog_path = Path(tmpdir) / "channels.local.json"
            add_channel(catalog_path, "brand", "Brand")
            set_channel_schedule(catalog_path, "brand", "weekly")
            channels = list_channels(catalog_path)

        self.assertEqual(channels[0].schedule, "weekly")

    def test_set_channel_image_persists_public_channel_image_url(self) -> None:
        with tempfile.TemporaryDirectory() as tmpdir:
            catalog_path = Path(tmpdir) / "channels.local.json"
            add_channel(catalog_path, "brand", "Brand")
            set_channel_image(catalog_path, "brand", "https://images.example/brand.png")
            channels = list_channels(catalog_path)

        self.assertEqual(channels[0].image_url, "https://images.example/brand.png")

    def test_cli_updates_channel_image_reference_and_schedule(self) -> None:
        with tempfile.TemporaryDirectory() as tmpdir:
            catalog_path = Path(tmpdir) / "channels.local.json"
            main(["--catalog", str(catalog_path), "--add", "brand", "--name", "Brand"])
            main(
                [
                    "--catalog",
                    str(catalog_path),
                    "--set-image",
                    "brand",
                    "--image-url",
                    "https://images.example/brand.png",
                ]
            )
            main(
                [
                    "--catalog",
                    str(catalog_path),
                    "--reference",
                    "brand",
                    "youtube",
                    "--handle",
                    "@brand",
                ]
            )
            main(["--catalog", str(catalog_path), "--schedule", "brand", "weekly"])
            channels = list_channels(catalog_path)

        self.assertEqual(channels[0].image_url, "https://images.example/brand.png")
        self.assertEqual(channels[0].platforms[0].handle, "@brand")
        self.assertEqual(channels[0].schedule, "weekly")

    def test_collection_plan_marks_only_enabled_referenced_sources_ready(self) -> None:
        with tempfile.TemporaryDirectory() as tmpdir:
            catalog_path = Path(tmpdir) / "channels.local.json"
            add_channel(catalog_path, "brand", "Brand")
            set_platform_reference(catalog_path, "brand", "youtube", "@brand")
            set_platform_enabled(catalog_path, "brand", "youtube", True)
            set_platform_enabled(catalog_path, "brand", "instagram", True)
            plan = collection_plan(catalog_path, "brand")

        self.assertEqual(plan[0]["status"], "ready")
        self.assertTrue(plan[0]["selected"])
        self.assertEqual(plan[1]["status"], "pending")
        self.assertFalse(plan[1]["selected"])

    def test_set_platform_reference_trims_user_input(self) -> None:
        with tempfile.TemporaryDirectory() as tmpdir:
            catalog_path = Path(tmpdir) / "channels.local.json"
            add_channel(catalog_path, "brand", "Brand")

            channel = set_platform_reference(
                catalog_path,
                "brand",
                "youtube",
                "  https://www.youtube.com/@brand  ",
            )

        self.assertEqual(channel.platforms[0].handle, "https://www.youtube.com/@brand")

    def test_record_collection_status_persists_safe_source_outcomes(self) -> None:
        with tempfile.TemporaryDirectory() as tmpdir:
            status_path = Path(tmpdir) / "collection_status.local.json"
            record_collection_status(
                status_path,
                "brand",
                [
                    {"provider": "youtube", "selected": True},
                    {"provider": "instagram", "selected": False},
                ],
            )
            status = load_collection_status(status_path)

        sources = status["channels"]["brand"]["sources"]
        self.assertEqual(sources["youtube"]["status"], "planned")
        self.assertEqual(sources["instagram"]["status"], "pending")
        self.assertIn("last_attempt", sources["youtube"])
        self.assertEqual(sources["youtube"]["last_success"], "")


if __name__ == "__main__":
    unittest.main()
