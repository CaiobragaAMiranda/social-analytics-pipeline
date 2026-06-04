import tempfile
import unittest
from datetime import UTC, datetime
from pathlib import Path

from social_analytics_pipeline.pipeline import run_provider_pipeline
from social_analytics_pipeline.providers import FixtureProvider, build_mock_providers
from social_analytics_pipeline.storage import DeadLetterStorage, RawStorage
from social_analytics_pipeline.transform import SocialMetric

PROJECT_ROOT = Path(__file__).resolve().parents[1]


class FakeMetricLoader:
    def __init__(self) -> None:
        self.loaded_batches: list[list[SocialMetric]] = []

    def load(self, metrics: list[SocialMetric]) -> int:
        self.loaded_batches.append(metrics)
        return len(metrics)


class LocalPipelineTest(unittest.TestCase):
    def test_runs_mock_provider_through_raw_normalize_and_load(self) -> None:
        providers = build_mock_providers(PROJECT_ROOT)
        provider = providers["instagram"]
        loader = FakeMetricLoader()

        with tempfile.TemporaryDirectory() as tmpdir:
            result = run_provider_pipeline(
                provider=provider,
                account_id="ig-account-1",
                start_at=datetime(2026, 5, 1, tzinfo=UTC),
                end_at=datetime(2026, 5, 27, tzinfo=UTC),
                raw_storage=RawStorage(Path(tmpdir)),
                loader=loader,
            )

            raw_files = sorted(Path(tmpdir).glob("instagram/2026-05-27/*.json"))

        self.assertEqual(result.provider, "instagram")
        self.assertEqual(result.raw_records, 2)
        self.assertEqual(result.invalid_records, 0)
        self.assertEqual(result.loaded_records, 2)
        self.assertEqual(len(result.metrics), 2)
        self.assertEqual(len(raw_files), 2)
        self.assertEqual(len(loader.loaded_batches), 1)
        self.assertEqual(loader.loaded_batches[0], result.metrics)
        self.assertEqual(
            [metric.content_id for metric in result.metrics],
            ["ig-post-001", "ig-reel-002"],
        )

    def test_loads_empty_provider_result_without_raw_files(self) -> None:
        loader = FakeMetricLoader()

        with tempfile.TemporaryDirectory() as tmpdir:
            temp_root = Path(tmpdir)
            empty_fixture = temp_root / "empty_metrics.json"
            empty_fixture.write_text("[]", encoding="utf-8")
            provider = FixtureProvider(name="instagram", fixture_path=empty_fixture)

            result = run_provider_pipeline(
                provider=provider,
                account_id="ig-account-1",
                start_at=datetime(2026, 5, 1, tzinfo=UTC),
                end_at=datetime(2026, 5, 27, tzinfo=UTC),
                raw_storage=RawStorage(temp_root / "raw"),
                loader=loader,
            )

            raw_files = list((temp_root / "raw").glob("**/*.json"))

        self.assertEqual(result.raw_records, 0)
        self.assertEqual(result.invalid_records, 0)
        self.assertEqual(result.loaded_records, 0)
        self.assertEqual(result.metrics, [])
        self.assertEqual(raw_files, [])
        self.assertEqual(loader.loaded_batches, [[]])

    def test_routes_invalid_normalized_metric_to_dlq_and_continues(self) -> None:
        loader = FakeMetricLoader()

        with tempfile.TemporaryDirectory() as tmpdir:
            temp_root = Path(tmpdir)
            invalid_fixture = temp_root / "invalid_metrics.json"
            invalid_fixture.write_text(
                """
                [
                  {
                    "id": "ig-post-001",
                    "media_type": "IMAGE",
                    "timestamp": "2026-05-28T14:30:00Z",
                    "like_count": -1,
                    "comments_count": 14,
                    "impressions": 2300,
                    "account": {"followers_count": 5400},
                    "_collection": {
                      "provider": "instagram",
                      "account_id": "ig-account-1",
                      "start_at": "2026-05-01T00:00:00+00:00",
                      "end_at": "2026-05-27T00:00:00+00:00"
                    }
                  }
                ]
                """.strip(),
                encoding="utf-8",
            )
            provider = FixtureProvider(name="instagram", fixture_path=invalid_fixture)
            dlq_storage = DeadLetterStorage(temp_root / "dlq")

            result = run_provider_pipeline(
                provider=provider,
                account_id="ig-account-1",
                start_at=datetime(2026, 5, 1, tzinfo=UTC),
                end_at=datetime(2026, 5, 27, tzinfo=UTC),
                raw_storage=RawStorage(temp_root / "raw"),
                loader=loader,
                dead_letter_storage=dlq_storage,
            )

            dlq_files = list((temp_root / "dlq").glob("**/*.json"))
            dlq_text = dlq_files[0].read_text(encoding="utf-8")

        self.assertEqual(result.raw_records, 1)
        self.assertEqual(result.invalid_records, 1)
        self.assertEqual(result.loaded_records, 0)
        self.assertEqual(result.metrics, [])
        self.assertEqual(len(loader.loaded_batches), 1)
        self.assertEqual(loader.loaded_batches[0], [])
        self.assertEqual(len(dlq_files), 1)
        self.assertIn("likes", dlq_text)


if __name__ == "__main__":
    unittest.main()
