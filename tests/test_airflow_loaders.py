import unittest
from datetime import UTC, datetime
from pathlib import Path

from social_analytics_pipeline.load import PostgresMetricLoader
from social_analytics_pipeline.orchestration.loaders import build_airflow_metric_loader
from social_analytics_pipeline.pipeline import JsonMetricArtifactLoader


class AirflowLoadersTest(unittest.TestCase):
    def test_build_airflow_metric_loader_uses_json_by_default(self) -> None:
        loader = build_airflow_metric_loader(
            provider_name="youtube",
            start_at=datetime(2026, 1, 1, tzinfo=UTC),
            end_at=datetime(2026, 1, 16, tzinfo=UTC),
            project_root=Path("project"),
            env={},
        )

        self.assertIsInstance(loader, JsonMetricArtifactLoader)
        self.assertEqual(
            loader.output_path.as_posix(),
            "project/data/processed/airflow/youtube-20260101T000000-20260116T000000.json",
        )

    def test_build_airflow_metric_loader_uses_postgres_when_enabled(self) -> None:
        loader = build_airflow_metric_loader(
            provider_name="youtube",
            start_at=datetime(2026, 1, 1, tzinfo=UTC),
            end_at=datetime(2026, 1, 16, tzinfo=UTC),
            project_root=Path("project"),
            env={
                "SOCIAL_ANALYTICS_AIRFLOW_LOAD_TARGET": "postgres",
                "SOCIAL_ANALYTICS_POSTGRES_DSN": "postgresql://example",
            },
        )

        self.assertIsInstance(loader, PostgresMetricLoader)
        self.assertEqual(loader.dsn, "postgresql://example")

    def test_build_airflow_metric_loader_requires_postgres_dsn(self) -> None:
        with self.assertRaisesRegex(RuntimeError, "SOCIAL_ANALYTICS_POSTGRES_DSN"):
            build_airflow_metric_loader(
                provider_name="youtube",
                start_at=datetime(2026, 1, 1, tzinfo=UTC),
                end_at=datetime(2026, 1, 16, tzinfo=UTC),
                project_root=Path("project"),
                env={"SOCIAL_ANALYTICS_AIRFLOW_LOAD_TARGET": "postgres"},
            )

    def test_build_airflow_metric_loader_rejects_unknown_target(self) -> None:
        with self.assertRaisesRegex(RuntimeError, "json' or 'postgres"):
            build_airflow_metric_loader(
                provider_name="youtube",
                start_at=datetime(2026, 1, 1, tzinfo=UTC),
                end_at=datetime(2026, 1, 16, tzinfo=UTC),
                project_root=Path("project"),
                env={"SOCIAL_ANALYTICS_AIRFLOW_LOAD_TARGET": "warehouse"},
            )


if __name__ == "__main__":
    unittest.main()
