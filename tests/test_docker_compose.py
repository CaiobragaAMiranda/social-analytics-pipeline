import unittest
from pathlib import Path


class DockerComposeTest(unittest.TestCase):
    def test_airflow_receives_youtube_runtime_environment_names(self) -> None:
        compose = Path("docker-compose.yml").read_text(encoding="utf-8")

        self.assertIn("AIRFLOW__API_AUTH__JWT_SECRET: ${AIRFLOW_API_AUTH_JWT_SECRET}", compose)

        for variable_name in (
            "YOUTUBE_API_KEY",
            "YOUTUBE_CHANNEL_ID",
            "YOUTUBE_CHANNEL_HANDLE",
            "YOUTUBE_LOCAL_LOAD_TARGET",
            "YOUTUBE_MAX_PAGES",
            "YOUTUBE_SMOKE_LOOKBACK_DAYS",
        ):
            self.assertIn(f"{variable_name}: ${{{variable_name}}}", compose)


if __name__ == "__main__":
    unittest.main()
