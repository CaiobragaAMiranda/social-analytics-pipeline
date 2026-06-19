import contextlib
import io
import tempfile
import unittest
from pathlib import Path
from unittest import mock

from social_analytics_pipeline.cli.serve_dashboard import (
    cli_entrypoint,
    dashboard_url,
    main,
    parse_args,
)


class ServeDashboardTest(unittest.TestCase):
    def test_dashboard_url_uses_project_relative_output_path(self) -> None:
        project_root = Path("project")
        dashboard_path = project_root / "data" / "dashboard" / "smoke.html"

        url = dashboard_url(project_root, dashboard_path, "127.0.0.1", 8000)

        self.assertEqual(url, "http://127.0.0.1:8000/data/dashboard/smoke.html")

    def test_dashboard_url_displays_localhost_when_binding_all_interfaces(self) -> None:
        project_root = Path("project")
        dashboard_path = project_root / "data" / "dashboard" / "smoke.html"

        url = dashboard_url(project_root, dashboard_path, "0.0.0.0", 8000)

        self.assertEqual(url, "http://localhost:8000/data/dashboard/smoke.html")

    def test_parse_args_accepts_host_port_output_and_no_smoke(self) -> None:
        args = parse_args(
            [
                "--project-root",
                "project",
                "--output",
                "data/dashboard/custom.html",
                "--host",
                "127.0.0.1",
                "--port",
                "9000",
                "--no-smoke",
            ]
        )

        self.assertEqual(args.project_root, Path("project"))
        self.assertEqual(args.output, Path("data/dashboard/custom.html"))
        self.assertEqual(args.host, "127.0.0.1")
        self.assertEqual(args.port, 9000)
        self.assertTrue(args.no_smoke)

    def test_main_can_generate_smoke_and_skip_blocking_server(self) -> None:
        with tempfile.TemporaryDirectory() as tmpdir:
            project_root = Path(tmpdir)
            dashboard_path = project_root / "data" / "dashboard" / "smoke.html"
            summary = mock.Mock(dashboard_path=dashboard_path)
            stdout = io.StringIO()

            with (
                mock.patch(
                    "social_analytics_pipeline.cli.serve_dashboard.run_dashboard_smoke",
                    return_value=summary,
                ) as run_smoke,
                contextlib.redirect_stdout(stdout),
            ):
                exit_code = main(project_root=project_root, start_server=False)

        self.assertEqual(exit_code, 0)
        run_smoke.assert_called_once_with(project_root, Path("data/dashboard/smoke.html"))
        self.assertIn(
            "dashboard_url=http://127.0.0.1:8000/data/dashboard/smoke.html",
            stdout.getvalue(),
        )

    def test_main_reports_bind_failure_with_host_and_port(self) -> None:
        with tempfile.TemporaryDirectory() as tmpdir:
            project_root = Path(tmpdir)
            stdout = io.StringIO()
            stderr = io.StringIO()

            with (
                mock.patch(
                    "social_analytics_pipeline.cli.serve_dashboard.serve_directory",
                    side_effect=OSError("address already in use"),
                ),
                contextlib.redirect_stdout(stdout),
                contextlib.redirect_stderr(stderr),
            ):
                exit_code = main(
                    project_root=project_root,
                    output_path=Path("data/dashboard/existing.html"),
                    host="127.0.0.1",
                    port=9000,
                    generate_smoke=False,
                )

        self.assertEqual(exit_code, 1)
        self.assertIn("could not bind dashboard server at 127.0.0.1:9000", stderr.getvalue())

    def test_cli_entrypoint_uses_parser_and_main(self) -> None:
        with tempfile.TemporaryDirectory() as tmpdir:
            project_root = Path(tmpdir)
            with (
                mock.patch(
                    "sys.argv",
                    [
                        "serve-dashboard",
                        "--project-root",
                        str(project_root),
                        "--output",
                        "data/dashboard/existing.html",
                        "--host",
                        "127.0.0.1",
                        "--port",
                        "9000",
                        "--no-smoke",
                    ],
                ),
                mock.patch("social_analytics_pipeline.cli.serve_dashboard.main") as run_main,
            ):
                run_main.return_value = 0
                exit_code = cli_entrypoint()

        self.assertEqual(exit_code, 0)
        run_main.assert_called_once_with(
            project_root=project_root,
            output_path=Path("data/dashboard/existing.html"),
            host="127.0.0.1",
            port=9000,
            generate_smoke=False,
        )


if __name__ == "__main__":
    unittest.main()
