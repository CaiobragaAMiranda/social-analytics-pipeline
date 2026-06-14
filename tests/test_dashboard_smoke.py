import contextlib
import io
import json
import shutil
import tempfile
import unittest
from pathlib import Path
from unittest import mock

from social_analytics_pipeline.cli.dashboard_smoke import (
    cli_entrypoint,
    main,
    run_dashboard_smoke,
)


class DashboardSmokeTest(unittest.TestCase):
    def test_run_dashboard_smoke_generates_safe_multi_provider_artifacts(self) -> None:
        with self._sample_project_root() as tmpdir:
            project_root = Path(tmpdir)
            summary = run_dashboard_smoke(project_root)
            dashboard_html = summary.dashboard_path.read_text(encoding="utf-8")
            youtube_report = json.loads(summary.youtube_report_path.read_text(encoding="utf-8"))
            instagram_report = json.loads(
                summary.instagram_report_path.read_text(encoding="utf-8")
            )
            channels_config = json.loads(
                summary.channels_config_path.read_text(encoding="utf-8")
            )
            youtube_processed_exists = summary.youtube_processed_path.exists()
            instagram_processed_exists = summary.instagram_processed_path.exists()

        self.assertTrue(youtube_processed_exists)
        self.assertTrue(instagram_processed_exists)
        self.assertEqual(
            channels_config["channels"][0]["display_name"],
            "Sample Monitored Channel",
        )
        self.assertEqual(youtube_report["source"]["provider"], "youtube")
        self.assertEqual(instagram_report["source"]["provider"], "instagram")
        self.assertIn("Sample Monitored Channel", dashboard_html)
        self.assertIn('<option value="0">Sample Monitored Channel</option>', dashboard_html)
        self.assertNotIn('<option value="1">', dashboard_html)
        self.assertIn('"provider": "youtube"', dashboard_html)
        self.assertIn('"provider": "instagram"', dashboard_html)

    def test_main_writes_relative_output_under_project_root(self) -> None:
        with self._sample_project_root() as tmpdir:
            project_root = Path(tmpdir)
            stdout = io.StringIO()

            with contextlib.redirect_stdout(stdout):
                exit_code = main(
                    project_root=project_root,
                    output_path=Path("data/dashboard/custom-smoke.html"),
                )
            output_path = project_root / "data" / "dashboard" / "custom-smoke.html"
            output_exists = output_path.exists()

        self.assertEqual(exit_code, 0)
        self.assertTrue(output_exists)
        self.assertIn("dashboard_path=data/dashboard/custom-smoke.html", stdout.getvalue())
        self.assertIn(
            "channels_config_path=data/temp/dashboard-smoke/config/channels.local.json",
            stdout.getvalue(),
        )
        self.assertNotIn(str(project_root), stdout.getvalue())

    def test_cli_entrypoint_uses_parser_and_main(self) -> None:
        with self._sample_project_root() as tmpdir:
            project_root = Path(tmpdir)
            output_path = project_root / "data" / "dashboard" / "cli-smoke.html"
            stdout = io.StringIO()

            with (
                mock.patch(
                    "sys.argv",
                    [
                        "dashboard-smoke",
                        "--project-root",
                        str(project_root),
                        "--output",
                        str(output_path),
                        "--quiet",
                    ],
                ),
                contextlib.redirect_stdout(stdout),
            ):
                exit_code = cli_entrypoint()
            output_exists = output_path.exists()

        self.assertEqual(exit_code, 0)
        self.assertTrue(output_exists)
        self.assertEqual("", stdout.getvalue())
        self.assertNotIn("Dashboard smoke summary", stdout.getvalue())

    def _sample_project_root(self) -> tempfile.TemporaryDirectory[str]:
        temp_dir = tempfile.TemporaryDirectory()
        project_root = Path(temp_dir.name)
        fixture_dir = project_root / "data" / "fixtures"
        fixture_dir.mkdir(parents=True)
        source_fixture_dir = Path(__file__).resolve().parents[1] / "data" / "fixtures"
        shutil.copy(source_fixture_dir / "youtube_metrics.json", fixture_dir)
        shutil.copy(source_fixture_dir / "instagram_metrics.json", fixture_dir)
        return temp_dir


if __name__ == "__main__":
    unittest.main()
