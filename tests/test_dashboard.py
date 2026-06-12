import json
import tempfile
import unittest
from pathlib import Path

from social_analytics_pipeline.cli.dashboard import (
    build_dashboard_html,
    find_latest_report_json,
    load_report_payload,
    main,
    parse_args,
    write_dashboard_html,
)


class DashboardTest(unittest.TestCase):
    def test_build_dashboard_html_renders_summary_cards_and_top_rows(self) -> None:
        payload = {
            "generated_at": "2026-06-12T12:00:00Z",
            "source": {"provider": "youtube"},
            "records": 1,
            "totals": {
                "views": 100,
                "engagements": 13,
                "engagement_rate_percent": 13.0,
            },
            "data_quality": {"status": "ok", "has_engagements": True},
            "top_content": {"content_id": "video-1"},
            "top_rows": [
                {
                    "content_id": "video-1",
                    "views": 100,
                    "likes": 10,
                    "comments": 2,
                    "shares": 1,
                }
            ],
        }

        html = build_dashboard_html(payload)

        self.assertIn("Social Analytics Dashboard", html)
        self.assertIn('class="dashboard-shell"', html)
        self.assertIn('class="provider-pill">youtube', html)
        self.assertIn("channel-fallback", html)
        self.assertIn("2026-06-12T12:00:00Z", html)
        self.assertIn("Engagement Rate", html)
        self.assertIn("13.00%", html)
        self.assertIn("Data Quality", html)
        self.assertIn("video-1", html)

    def test_build_dashboard_html_escapes_text_values(self) -> None:
        html = build_dashboard_html(
            {
                "source": {"provider": "<script>"},
                "top_content": {"content_id": "<bad>"},
                "top_rows": [{"content_id": "<row>"}],
            }
        )

        self.assertIn("&lt;script&gt;", html)
        self.assertIn("&lt;bad&gt;", html)
        self.assertIn("&lt;row&gt;", html)
        self.assertNotIn("<script>", html)

    def test_build_dashboard_html_renders_source_image_url(self) -> None:
        html = build_dashboard_html(
            {
                "source": {
                    "provider": "youtube",
                    "image_url": "https://example.test/channel.png",
                }
            }
        )

        self.assertIn('class="channel-image"', html)
        self.assertIn('src="https://example.test/channel.png"', html)
        self.assertIn('alt="youtube channel image"', html)

    def test_build_dashboard_html_renders_channel_image_url_alias(self) -> None:
        html = build_dashboard_html(
            {
                "source": {
                    "provider": "youtube",
                    "channel_image_url": "https://example.test/channel-alias.png",
                }
            }
        )

        self.assertIn('src="https://example.test/channel-alias.png"', html)

    def test_load_report_payload_rejects_non_object_json(self) -> None:
        with tempfile.TemporaryDirectory() as tmpdir:
            report_path = Path(tmpdir) / "report.json"
            report_path.write_text("[]", encoding="utf-8")

            with self.assertRaisesRegex(RuntimeError, "object"):
                load_report_payload(report_path)

    def test_write_dashboard_html_persists_file(self) -> None:
        with tempfile.TemporaryDirectory() as tmpdir:
            output_path = Path(tmpdir) / "dashboard" / "index.html"

            path = write_dashboard_html({"records": 0}, output_path)

            self.assertEqual(path, output_path)
            self.assertTrue(path.exists())
            self.assertIn("Social Analytics Dashboard", path.read_text(encoding="utf-8"))

    def test_main_writes_dashboard_from_report_json(self) -> None:
        with tempfile.TemporaryDirectory() as tmpdir:
            report_path = Path(tmpdir) / "report.json"
            output_path = Path(tmpdir) / "index.html"
            report_path.write_text(json.dumps({"records": 1}), encoding="utf-8")

            exit_code = main(report_path, output_path)

            self.assertEqual(exit_code, 0)
            self.assertTrue(output_path.exists())

    def test_find_latest_report_json_uses_sorted_latest_report(self) -> None:
        with tempfile.TemporaryDirectory() as tmpdir:
            project_root = Path(tmpdir)
            report_dir = project_root / "data" / "reports" / "youtube-json"
            report_dir.mkdir(parents=True)
            older = report_dir / "youtube-20260501.json"
            newer = report_dir / "youtube-20260502.json"
            older.write_text("{}", encoding="utf-8")
            newer.write_text("{}", encoding="utf-8")

            self.assertEqual(find_latest_report_json(project_root), newer)

    def test_find_latest_report_json_fails_when_missing(self) -> None:
        with (
            tempfile.TemporaryDirectory() as tmpdir,
            self.assertRaisesRegex(RuntimeError, "No report JSON"),
        ):
            find_latest_report_json(Path(tmpdir))

    def test_main_defaults_to_latest_report_json(self) -> None:
        with tempfile.TemporaryDirectory() as tmpdir:
            project_root = Path(tmpdir)
            report_dir = project_root / "data" / "reports" / "youtube-json"
            report_dir.mkdir(parents=True)
            report_path = report_dir / "youtube-20260502.json"
            output_path = project_root / "dashboard.html"
            report_path.write_text(json.dumps({"records": 1}), encoding="utf-8")

            exit_code = main(output_path=output_path, project_root=project_root)

            self.assertEqual(exit_code, 0)
            self.assertTrue(output_path.exists())

    def test_parse_args_accepts_optional_report_json_and_output(self) -> None:
        args = parse_args(
            [
                "--report-json",
                "report.json",
                "--output",
                "dashboard.html",
                "--project-root",
                "workspace",
            ]
        )

        self.assertEqual(args.report_json, Path("report.json"))
        self.assertEqual(args.output, Path("dashboard.html"))
        self.assertEqual(args.project_root, Path("workspace"))

    def test_parse_args_allows_default_report_json(self) -> None:
        args = parse_args([])

        self.assertIsNone(args.report_json)


if __name__ == "__main__":
    unittest.main()
