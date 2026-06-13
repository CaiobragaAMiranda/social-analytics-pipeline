import json
import tempfile
import unittest
from pathlib import Path

from social_analytics_pipeline.cli.dashboard import (
    build_dashboard_html,
    build_multi_report_dashboard_payload,
    find_latest_report_json,
    find_report_json_files,
    load_report_payload,
    main,
    parse_args,
    write_dashboard_html,
)


class DashboardTest(unittest.TestCase):
    def test_build_dashboard_html_renders_summary_cards_and_top_rows(self) -> None:
        payload = {
            "generated_at": "2026-06-12T12:00:00Z",
            "source": {
                "provider": "youtube",
                "artifact": "data/processed/youtube/sample.json",
            },
            "report_schema_version": 1,
            "records": 1,
            "totals": {
                "views": 100,
                "engagements": 13,
                "engagement_rate_percent": 13.0,
                "average_views_per_record": 100.0,
                "average_engagements_per_record": 13.0,
                "average_likes_per_record": 10.0,
                "average_comments_per_record": 2.0,
                "average_shares_per_record": 1.0,
            },
            "ranking": {"metric": "views", "limit": 5},
            "engagement_breakdown": {
                "likes_percent": 76.92,
                "comments_percent": 15.38,
                "shares_percent": 7.69,
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
        self.assertIn("Channel Analytics", html)
        self.assertIn('class="channel-select"', html)
        self.assertIn("Semiannual Performance", html)
        self.assertIn("Productions", html)
        self.assertIn("channel-fallback", html)
        self.assertIn("2026-06-12 12:00 UTC", html)
        self.assertIn("Semiannual Performance", html)
        self.assertIn("13.00%", html)
        self.assertIn("Engagement Breakdown", html)
        self.assertIn("76.92%", html)
        self.assertIn("15.38%", html)
        self.assertIn("7.69%", html)
        self.assertIn("Per-Record Averages", html)
        self.assertIn("100.00", html)
        self.assertIn("10.00", html)
        self.assertIn("Report Metadata", html)
        self.assertIn("Schema version", html)
        self.assertIn("Ranking metric", html)
        self.assertIn("views", html)
        self.assertIn("Source artifact", html)
        self.assertIn("data/processed/youtube/sample.json", html)
        self.assertIn("Data Quality", html)
        self.assertIn("video-1", html)

    def test_build_dashboard_html_escapes_text_values(self) -> None:
        html = build_dashboard_html(
            {
                "source": {"provider": "<script>"},
                "generated_at": "<date>",
                "artifact": "<artifact>",
                "ranking": {"metric": "<metric>"},
                "top_content": {"content_id": "<bad>"},
                "top_rows": [{"content_id": "<row>"}],
            }
        )

        self.assertIn("&lt;script&gt;", html)
        self.assertIn("&lt;date&gt;", html)
        self.assertIn("&lt;artifact&gt;", html)
        self.assertIn("&lt;metric&gt;", html)
        self.assertIn("&lt;bad&gt;", html)
        self.assertIn("&lt;row&gt;", html)
        self.assertIn("\\u003cscript\\u003e", html)
        self.assertNotIn("><script>", html)

    def test_build_dashboard_html_renders_unknown_report_metadata(self) -> None:
        html = build_dashboard_html({"source": {"provider": "youtube"}})

        self.assertIn("Report Metadata", html)
        self.assertIn("unknown", html)
        self.assertIn("Engagement Breakdown", html)
        self.assertIn("0.00%", html)
        self.assertIn("Per-Record Averages", html)
        self.assertIn("0.00", html)

    def test_build_dashboard_html_uses_top_level_artifact_fallback(self) -> None:
        html = build_dashboard_html(
            {
                "artifact": "data/processed/youtube/fallback.json",
                "source": {"provider": "youtube"},
            }
        )

        self.assertIn("Source artifact", html)
        self.assertIn("data/processed/youtube/fallback.json", html)

    def test_build_dashboard_html_renders_multiple_channel_options(self) -> None:
        html = build_dashboard_html(
            {
                "channels": [
                    {
                        "source": {"provider": "youtube", "channel_name": "Channel A"},
                        "records": 2,
                        "totals": {"views": 100},
                    },
                    {
                        "source": {"provider": "youtube", "channel_name": "Channel B"},
                        "records": 3,
                        "totals": {"views": 200},
                    },
                ]
            }
        )

        self.assertIn('<option value="0">Channel A</option>', html)
        self.assertIn('<option value="1">Channel B</option>', html)
        self.assertIn('"name": "Channel B"', html)
        self.assertIn('"views": "200"', html)

    def test_build_dashboard_html_supports_cross_platform_channel_contract(self) -> None:
        html = build_dashboard_html(
            {
                "channels": [
                    {
                        "source": {
                            "provider": "multi-platform",
                            "channel_name": "Brand Channel",
                        },
                        "records": 8,
                        "platforms": [
                            {
                                "provider": "youtube",
                                "records": 3,
                                "totals": {
                                    "views": 100,
                                    "engagements": 10,
                                    "engagement_rate_percent": 10.0,
                                },
                            },
                            {
                                "provider": "tiktok",
                                "records": 4,
                                "totals": {
                                    "views": 250,
                                    "engagements": 50,
                                    "engagement_rate_percent": 20.0,
                                },
                            },
                            {
                                "provider": "instagram",
                                "records": 1,
                                "totals": {
                                    "views": 150,
                                    "engagements": 15,
                                    "engagement_rate_percent": 10.0,
                                },
                            },
                        ],
                    }
                ]
            }
        )

        self.assertIn('<option value="0">Brand Channel</option>', html)
        self.assertIn('"platforms": [', html)
        self.assertIn('"provider": "youtube"', html)
        self.assertIn('"provider": "tiktok"', html)
        self.assertIn('"provider": "instagram"', html)
        self.assertIn('"views": "500"', html)
        self.assertIn('"engagements": "75"', html)
        self.assertIn('"engagement_rate": "15.00%"', html)
        self.assertIn("Platform Sources", html)
        self.assertIn('<strong>youtube</strong>', html)
        self.assertIn('<strong>tiktok</strong>', html)
        self.assertIn('<strong>instagram</strong>', html)

    def test_build_dashboard_html_marks_missing_platform_sources_unavailable(self) -> None:
        html = build_dashboard_html(
            {
                "channels": [
                    {
                        "source": {"provider": "multi-platform", "channel_name": "Partial"},
                        "platforms": [
                            {
                                "provider": "youtube",
                                "records": 1,
                                "totals": {"views": 100, "engagements": 10},
                            }
                        ],
                    }
                ]
            }
        )

        self.assertIn("Platform Sources", html)
        self.assertIn('<strong>youtube</strong>', html)
        self.assertIn('<strong>tiktok</strong>', html)
        self.assertIn('<strong>instagram</strong>', html)
        self.assertIn("unavailable", html)

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

    def test_build_dashboard_html_renders_empty_top_content_state(self) -> None:
        html = build_dashboard_html(
            {
                "source": {"provider": "youtube"},
                "top_content": {"content_id": "<none>"},
                "top_rows": [],
            }
        )

        self.assertIn("No top content available", html)
        self.assertIn("No top content rows available for this report.", html)
        self.assertIn('class="empty-row"', html)
        self.assertNotIn("<td>&lt;none&gt;</td><td>0</td><td>0</td>", html)

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

    def test_main_writes_dashboard_from_multiple_report_json_files(self) -> None:
        with tempfile.TemporaryDirectory() as tmpdir:
            root = Path(tmpdir)
            youtube_path = root / "youtube.json"
            tiktok_path = root / "tiktok.json"
            output_path = root / "index.html"
            youtube_path.write_text(
                json.dumps(
                    {
                        "generated_at": "2026-06-12T12:00:00Z",
                        "source": {
                            "provider": "youtube",
                            "channel_name": "Brand Channel",
                        },
                        "records": 2,
                        "totals": {"views": 100, "engagements": 10},
                    }
                ),
                encoding="utf-8",
            )
            tiktok_path.write_text(
                json.dumps(
                    {
                        "generated_at": "2026-06-13T12:00:00Z",
                        "source": {
                            "provider": "tiktok",
                            "channel_name": "Brand Channel",
                        },
                        "records": 3,
                        "totals": {"views": 200, "engagements": 30},
                    }
                ),
                encoding="utf-8",
            )

            exit_code = main([youtube_path, tiktok_path], output_path)

            html = output_path.read_text(encoding="utf-8")
            self.assertEqual(exit_code, 0)
            self.assertIn('<option value="0">Brand Channel</option>', html)
            self.assertIn('"provider": "youtube"', html)
            self.assertIn('"provider": "tiktok"', html)
            self.assertIn('"views": "300"', html)
            self.assertIn('"engagements": "40"', html)

    def test_build_multi_report_dashboard_payload_groups_by_channel_identity(self) -> None:
        payload = build_multi_report_dashboard_payload(
            [
                {
                    "source": {"provider": "youtube", "channel_handle": "@brand"},
                    "records": 1,
                    "totals": {"views": 100},
                },
                {
                    "source": {"provider": "instagram", "channel_handle": "@brand"},
                    "records": 2,
                    "totals": {"views": 150},
                },
                {
                    "source": {"provider": "youtube", "channel_handle": "@other"},
                    "records": 3,
                    "totals": {"views": 250},
                },
            ]
        )

        self.assertEqual(len(payload["channels"]), 2)
        self.assertEqual(payload["channels"][0]["records"], 3)
        self.assertEqual(len(payload["channels"][0]["platforms"]), 2)
        self.assertEqual(payload["channels"][1]["records"], 3)

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

    def test_find_report_json_files_uses_sorted_reports(self) -> None:
        with tempfile.TemporaryDirectory() as tmpdir:
            project_root = Path(tmpdir)
            report_dir = project_root / "data" / "reports" / "youtube-json"
            report_dir.mkdir(parents=True)
            first = report_dir / "youtube-20260501.json"
            second = report_dir / "youtube-20260502.json"
            second.write_text("{}", encoding="utf-8")
            first.write_text("{}", encoding="utf-8")

            self.assertEqual(find_report_json_files(project_root), [first, second])

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

    def test_main_all_reports_discovers_report_json_files(self) -> None:
        with tempfile.TemporaryDirectory() as tmpdir:
            project_root = Path(tmpdir)
            report_dir = project_root / "data" / "reports" / "youtube-json"
            report_dir.mkdir(parents=True)
            youtube_path = report_dir / "youtube-20260501.json"
            tiktok_path = report_dir / "tiktok-20260501.json"
            output_path = project_root / "dashboard.html"
            youtube_path.write_text(
                json.dumps(
                    {
                        "source": {
                            "provider": "youtube",
                            "channel_name": "Brand Channel",
                        },
                        "records": 1,
                    }
                ),
                encoding="utf-8",
            )
            tiktok_path.write_text(
                json.dumps(
                    {
                        "source": {
                            "provider": "tiktok",
                            "channel_name": "Brand Channel",
                        },
                        "records": 1,
                    }
                ),
                encoding="utf-8",
            )

            exit_code = main(
                output_path=output_path,
                project_root=project_root,
                all_reports=True,
            )

            html = output_path.read_text(encoding="utf-8")
            self.assertEqual(exit_code, 0)
            self.assertIn('"provider": "youtube"', html)
            self.assertIn('"provider": "tiktok"', html)

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

        self.assertEqual(args.report_json, [Path("report.json")])
        self.assertEqual(args.output, Path("dashboard.html"))
        self.assertEqual(args.project_root, Path("workspace"))
        self.assertFalse(args.all_reports)

    def test_parse_args_accepts_multiple_report_json_files(self) -> None:
        args = parse_args(
            [
                "--report-json",
                "youtube.json",
                "--report-json",
                "tiktok.json",
            ]
        )

        self.assertEqual(args.report_json, [Path("youtube.json"), Path("tiktok.json")])

    def test_parse_args_accepts_all_reports(self) -> None:
        args = parse_args(["--all-reports"])

        self.assertTrue(args.all_reports)
        self.assertIsNone(args.report_json)

    def test_parse_args_allows_default_report_json(self) -> None:
        args = parse_args([])

        self.assertIsNone(args.report_json)
        self.assertFalse(args.all_reports)


if __name__ == "__main__":
    unittest.main()
