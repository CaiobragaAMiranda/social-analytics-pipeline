from datetime import datetime, timezone
from pathlib import Path
import unittest

from social_analytics_pipeline.providers import FixtureProvider, build_mock_providers


PROJECT_ROOT = Path(__file__).resolve().parents[1]


class MockProvidersTest(unittest.TestCase):
    def test_builds_expected_mock_providers(self) -> None:
        providers = build_mock_providers(PROJECT_ROOT)

        self.assertEqual(set(providers), {"instagram", "youtube", "tiktok"})
        self.assertTrue(all(isinstance(provider, FixtureProvider) for provider in providers.values()))

    def test_each_provider_returns_raw_payloads_with_collection_context(self) -> None:
        providers = build_mock_providers(PROJECT_ROOT)
        start_at = datetime(2026, 5, 1, tzinfo=timezone.utc)
        end_at = datetime(2026, 5, 27, tzinfo=timezone.utc)

        for name, provider in providers.items():
            with self.subTest(provider=name):
                payloads = provider.collect_metrics("account-1", start_at, end_at)

                self.assertGreaterEqual(len(payloads), 1)
                self.assertEqual(payloads[0]["_collection"]["provider"], name)
                self.assertEqual(payloads[0]["_collection"]["account_id"], "account-1")

    def test_fixtures_keep_provider_specific_shapes(self) -> None:
        providers = build_mock_providers(PROJECT_ROOT)
        start_at = datetime(2026, 5, 1, tzinfo=timezone.utc)
        end_at = datetime(2026, 5, 27, tzinfo=timezone.utc)

        instagram = providers["instagram"].collect_metrics("ig-account-1", start_at, end_at)[0]
        youtube = providers["youtube"].collect_metrics("yt-channel-1", start_at, end_at)[0]
        tiktok = providers["tiktok"].collect_metrics("tt-author-1", start_at, end_at)[0]

        self.assertIn("like_count", instagram)
        self.assertIn("statistics", youtube)
        self.assertIn("metrics", tiktok)

    def test_provider_rejects_invalid_date_interval(self) -> None:
        provider = build_mock_providers(PROJECT_ROOT)["instagram"]

        with self.assertRaises(ValueError):
            provider.collect_metrics(
                "account-1",
                datetime(2026, 5, 27, tzinfo=timezone.utc),
                datetime(2026, 5, 1, tzinfo=timezone.utc),
            )


if __name__ == "__main__":
    unittest.main()
