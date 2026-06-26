import contextlib
import io
import tempfile
import unittest
from pathlib import Path
from unittest import mock

from social_analytics_pipeline.cli.serve_dashboard import (
    _apply_catalog_action,
    cli_entrypoint,
    dashboard_url,
    main,
    parse_args,
)


class ServeDashboardTest(unittest.TestCase):
    def test_catalog_api_actions_persist_safe_channel_payload(self) -> None:
        with tempfile.TemporaryDirectory() as tmpdir:
            catalog_path = Path(tmpdir) / "channels.local.json"
            added = _apply_catalog_action(
                catalog_path,
                {"action": "add", "id": "brand", "name": "Brand Channel"},
            )
            enabled = _apply_catalog_action(
                catalog_path,
                {"action": "enable", "id": "brand", "provider": "youtube"},
            )
            scheduled = _apply_catalog_action(
                catalog_path,
                {"action": "schedule", "id": "brand", "schedule": "daily"},
            )
            referenced = _apply_catalog_action(
                catalog_path,
                {
                    "action": "reference",
                    "id": "brand",
                    "provider": "youtube",
                    "reference": "@brand",
                },
            )
            with mock.patch(
                "social_analytics_pipeline.cli.serve_dashboard._run_youtube_catalog_collection",
                return_value=mock.Mock(result=mock.Mock(loaded_records=7)),
            ):
                plan = _apply_catalog_action(
                    catalog_path,
                    {"action": "collect", "id": "brand"},
                    project_root=Path(tmpdir),
                )

        self.assertEqual(added["channels"][0]["name"], "Brand Channel")
        self.assertNotIn("handle", added["channels"][0])
        self.assertTrue(enabled["channels"][0]["platforms"]["youtube"]["enabled"])
        self.assertEqual(scheduled["channels"][0]["schedule"], "daily")
        self.assertEqual(
            referenced["channels"][0]["platforms"]["youtube"]["reference"], "@brand"
        )
        self.assertTrue(referenced["channels"][0]["platforms"]["youtube"]["ready"])
        self.assertEqual(plan["channel_id"], "brand")
        self.assertEqual(
            plan["sources"],
            [
                {
                    "provider": "youtube",
                    "status": "ready",
                    "reference": "@brand",
                    "selected": True,
                    "collection_status": "ok",
                    "outcome": "YouTube collection completed",
                    "loaded_records": 7,
                }
            ],
        )
        self.assertEqual(plan["status"]["sources"]["youtube"]["status"], "ok")
        self.assertEqual(plan["status"]["sources"]["youtube"]["loaded_records"], 7)

    def test_catalog_collect_records_safe_failure_when_youtube_is_not_configured(self) -> None:
        with tempfile.TemporaryDirectory() as tmpdir:
            catalog_path = Path(tmpdir) / "channels.local.json"
            _apply_catalog_action(
                catalog_path,
                {"action": "add", "id": "brand", "name": "Brand Channel"},
            )
            _apply_catalog_action(
                catalog_path,
                {"action": "enable", "id": "brand", "provider": "youtube"},
            )
            _apply_catalog_action(
                catalog_path,
                {
                    "action": "reference",
                    "id": "brand",
                    "provider": "youtube",
                    "reference": "@brand",
                },
            )

            plan = _apply_catalog_action(
                catalog_path,
                {"action": "collect", "id": "brand"},
                project_root=Path(tmpdir),
            )

        self.assertEqual(plan["sources"][0]["collection_status"], "failed")
        self.assertEqual(
            plan["status"]["sources"]["youtube"]["outcome"],
            "YouTube credentials are missing or invalid",
        )

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

    def test_dashboard_url_wraps_ipv6_host_in_brackets(self) -> None:
        project_root = Path("project")
        dashboard_path = project_root / "data" / "dashboard" / "smoke.html"

        url = dashboard_url(project_root, dashboard_path, "::1", 8000)

        self.assertEqual(url, "http://[::1]:8000/data/dashboard/smoke.html")

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
            dashboard_path = project_root / "data" / "dashboard" / "existing.html"
            dashboard_path.parent.mkdir(parents=True)
            dashboard_path.write_text("<html></html>", encoding="utf-8")
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

    def test_main_rejects_missing_dashboard_in_no_smoke_mode(self) -> None:
        with tempfile.TemporaryDirectory() as tmpdir:
            project_root = Path(tmpdir)
            stderr = io.StringIO()

            with (
                mock.patch(
                    "social_analytics_pipeline.cli.serve_dashboard.serve_directory"
                ) as serve_directory,
                contextlib.redirect_stderr(stderr),
            ):
                exit_code = main(
                    project_root=project_root,
                    output_path=Path("data/dashboard/missing.html"),
                    generate_smoke=False,
                )

        self.assertEqual(exit_code, 1)
        serve_directory.assert_not_called()
        self.assertIn(
            "dashboard output not found: data/dashboard/missing.html",
            stderr.getvalue(),
        )

    def test_main_rejects_dashboard_output_outside_project_root(self) -> None:
        with tempfile.TemporaryDirectory() as tmpdir:
            project_root = Path(tmpdir)
            stderr = io.StringIO()

            with (
                mock.patch(
                    "social_analytics_pipeline.cli.serve_dashboard.run_dashboard_smoke"
                ) as run_smoke,
                contextlib.redirect_stderr(stderr),
            ):
                exit_code = main(
                    project_root=project_root,
                    output_path=Path("../outside.html"),
                    start_server=False,
                )

        self.assertEqual(exit_code, 1)
        run_smoke.assert_not_called()
        self.assertEqual(
            stderr.getvalue(),
            "Error: dashboard output must be inside the project root.\n",
        )

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
