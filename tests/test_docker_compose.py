import unittest
from pathlib import Path


class DockerComposeTest(unittest.TestCase):
    def test_airflow_receives_youtube_runtime_environment_names(self) -> None:
        compose = Path("docker-compose.yml").read_text(encoding="utf-8")

        self.assertIn("AIRFLOW__API_AUTH__JWT_SECRET: ${AIRFLOW_API_AUTH_JWT_SECRET}", compose)
        self.assertIn(
            "AIRFLOW__CORE__EXECUTION_API_SERVER_URL: http://airflow-api-server:8080/execution/",
            compose,
        )

        for variable_name in (
            "YOUTUBE_API_KEY",
            "YOUTUBE_CHANNEL_ID",
            "YOUTUBE_CHANNEL_HANDLE",
            "YOUTUBE_LOCAL_LOAD_TARGET",
            "YOUTUBE_MAX_PAGES",
            "YOUTUBE_SMOKE_LOOKBACK_DAYS",
        ):
            self.assertIn(f"{variable_name}: ${{{variable_name}}}", compose)

    def test_airflow_workers_wait_for_api_server_health(self) -> None:
        compose = Path("docker-compose.yml").read_text(encoding="utf-8")

        for service_name in (
            "airflow-scheduler",
            "airflow-dag-processor",
            "airflow-worker",
            "airflow-triggerer",
        ):
            service_block = compose.split(f"  {service_name}:", 1)[1].split("\n  airflow-", 1)[0]

            self.assertIn("airflow-api-server:", service_block)
            self.assertIn("condition: service_healthy", service_block)

    def test_dashboard_service_uses_configurable_host_port(self) -> None:
        compose = Path("docker-compose.yml").read_text(encoding="utf-8")
        service_block = compose.split("  dashboard:", 1)[1].split("\n  postgres:", 1)[0]

        self.assertIn("container_name: social-analytics-dashboard", service_block)
        self.assertIn('"serve-dashboard", "--host", "0.0.0.0", "--port", "8000"', service_block)
        self.assertIn('"${DASHBOARD_PORT}:8000"', service_block)


if __name__ == "__main__":
    unittest.main()
