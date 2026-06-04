import unittest
from datetime import UTC, datetime, timedelta

from social_analytics_pipeline.orchestration import (
    MOCK_PIPELINE_DAG,
    MOCK_PIPELINE_LOAD,
    YOUTUBE_PIPELINE_DAG,
)


class AirflowSettingsTest(unittest.TestCase):
    def test_mock_pipeline_dag_is_scheduled_for_biweekly_catchup(self) -> None:
        self.assertEqual(MOCK_PIPELINE_DAG.dag_id, "social_analytics_mock_pipeline")
        self.assertEqual(MOCK_PIPELINE_DAG.schedule, timedelta(days=15))
        self.assertEqual(MOCK_PIPELINE_DAG.start_date, datetime(2026, 1, 1, tzinfo=UTC))
        self.assertTrue(MOCK_PIPELINE_DAG.catchup)
        self.assertIn("catchup", MOCK_PIPELINE_DAG.tags)

    def test_mock_pipeline_load_defaults_to_json_and_env_dsn(self) -> None:
        self.assertEqual(MOCK_PIPELINE_LOAD.target, "json")
        self.assertFalse(MOCK_PIPELINE_LOAD.uses_postgres)
        self.assertEqual(MOCK_PIPELINE_LOAD.postgres_dsn_env_var, "SOCIAL_ANALYTICS_POSTGRES_DSN")

    def test_youtube_pipeline_dag_is_scheduled_without_automatic_catchup(self) -> None:
        self.assertEqual(YOUTUBE_PIPELINE_DAG.dag_id, "social_analytics_youtube_pipeline")
        self.assertEqual(YOUTUBE_PIPELINE_DAG.schedule, timedelta(days=15))
        self.assertEqual(YOUTUBE_PIPELINE_DAG.start_date, datetime(2026, 1, 1, tzinfo=UTC))
        self.assertFalse(YOUTUBE_PIPELINE_DAG.catchup)
        self.assertIn("youtube", YOUTUBE_PIPELINE_DAG.tags)
        self.assertNotIn("catchup", YOUTUBE_PIPELINE_DAG.tags)


if __name__ == "__main__":
    unittest.main()
