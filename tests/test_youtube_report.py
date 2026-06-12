import contextlib
import io
import json
import sys
import tempfile
import unittest
from pathlib import Path
from unittest import mock

from social_analytics_pipeline.cli.youtube_report import (
    build_latest_youtube_artifact_listing,
    build_youtube_artifact_listing,
    build_youtube_report_json_output_path_in_dir,
    build_youtube_report_json_payload,
    build_youtube_report_json_text,
    build_youtube_report_markdown,
    build_youtube_report_output_path_in_dir,
    build_youtube_report_summary,
    build_youtube_report_summary_with_limit,
    build_youtube_report_summary_with_options,
    cli_entrypoint,
    count_youtube_processed_artifacts,
    find_latest_youtube_processed_artifact,
    load_youtube_report_rows,
    main,
    parse_args,
    write_youtube_report_json,
    write_youtube_report_markdown,
)


class YouTubeReportTest(unittest.TestCase):
    def test_find_latest_youtube_processed_artifact_uses_last_sorted_file(self) -> None:
        with tempfile.TemporaryDirectory() as tmpdir:
            artifact_dir = Path(tmpdir) / "data" / "processed" / "youtube"
            artifact_dir.mkdir(parents=True, exist_ok=True)
            first = artifact_dir / "youtube-20260501T000000-20260515T000000.json"
            second = artifact_dir / "youtube-20260516T000000-20260531T000000.json"
            first.write_text("[]", encoding="utf-8")
            second.write_text("[]", encoding="utf-8")

            latest = find_latest_youtube_processed_artifact(Path(tmpdir))

        self.assertEqual(latest.name, second.name)

    def test_build_youtube_artifact_listing_returns_relative_sorted_paths(self) -> None:
        with tempfile.TemporaryDirectory() as tmpdir:
            project_root = Path(tmpdir)
            artifact_dir = project_root / "data" / "processed" / "youtube"
            artifact_dir.mkdir(parents=True, exist_ok=True)
            first = artifact_dir / "youtube-20260501T000000-20260515T000000.json"
            second = artifact_dir / "youtube-20260516T000000-20260531T000000.json"
            second.write_text("[]", encoding="utf-8")
            first.write_text("[]", encoding="utf-8")

            artifacts = build_youtube_artifact_listing(project_root)

        self.assertEqual(
            artifacts,
            [
                "data/processed/youtube/youtube-20260501T000000-20260515T000000.json",
                "data/processed/youtube/youtube-20260516T000000-20260531T000000.json",
            ],
        )

    def test_build_latest_youtube_artifact_listing_returns_latest_relative_path(self) -> None:
        with tempfile.TemporaryDirectory() as tmpdir:
            project_root = Path(tmpdir)
            artifact_dir = project_root / "data" / "processed" / "youtube"
            artifact_dir.mkdir(parents=True, exist_ok=True)
            first = artifact_dir / "youtube-20260501T000000-20260515T000000.json"
            second = artifact_dir / "youtube-20260516T000000-20260531T000000.json"
            first.write_text("[]", encoding="utf-8")
            second.write_text("[]", encoding="utf-8")

            artifact = build_latest_youtube_artifact_listing(project_root)

        self.assertEqual(
            artifact,
            "data/processed/youtube/youtube-20260516T000000-20260531T000000.json",
        )

    def test_count_youtube_processed_artifacts_returns_artifact_count(self) -> None:
        with tempfile.TemporaryDirectory() as tmpdir:
            project_root = Path(tmpdir)
            artifact_dir = project_root / "data" / "processed" / "youtube"
            artifact_dir.mkdir(parents=True, exist_ok=True)
            (artifact_dir / "youtube-1.json").write_text("[]", encoding="utf-8")
            (artifact_dir / "youtube-2.json").write_text("[]", encoding="utf-8")

            count = count_youtube_processed_artifacts(project_root)

        self.assertEqual(count, 2)

    def test_build_youtube_report_summary_aggregates_processed_metrics(self) -> None:
        with tempfile.TemporaryDirectory() as tmpdir:
            artifact_path = Path(tmpdir) / "youtube-20260516T000000-20260531T000000.json"
            artifact_path.write_text(
                json.dumps(
                    [
                        {
                            "content_id": "video-1",
                            "likes": 10,
                            "comments": 2,
                            "shares": 1,
                            "views": 100,
                            "followers": 1000,
                        },
                        {
                            "content_id": "video-2",
                            "likes": 5,
                            "comments": 3,
                            "shares": 0,
                            "views": 250,
                            "followers": 1200,
                        },
                    ]
                ),
                encoding="utf-8",
            )

            summary = build_youtube_report_summary(artifact_path)

        self.assertEqual(summary.records, 2)
        self.assertEqual(summary.total_views, 350)
        self.assertEqual(summary.average_views_per_record, 175.0)
        self.assertEqual(summary.total_likes, 15)
        self.assertEqual(summary.average_likes_per_record, 7.5)
        self.assertEqual(summary.total_comments, 5)
        self.assertEqual(summary.average_comments_per_record, 2.5)
        self.assertEqual(summary.total_shares, 1)
        self.assertEqual(summary.average_shares_per_record, 0.5)
        self.assertEqual(summary.total_engagements, 21)
        self.assertEqual(summary.average_engagements_per_record, 10.5)
        self.assertAlmostEqual(summary.engagement_rate, 0.06)
        self.assertEqual(summary.max_followers, 1200)
        self.assertEqual(summary.top_content_id, "video-2")
        self.assertEqual(summary.top_views, 250)
        self.assertEqual(summary.top_metric_value, 250)
        self.assertEqual(summary.sort_by, "views")
        self.assertEqual(summary.top_limit, 5)
        self.assertEqual(len(summary.top_rows), 2)
        self.assertEqual(summary.top_rows[0]["content_id"], "video-2")

    def test_build_youtube_report_summary_with_limit_controls_top_rows(self) -> None:
        with tempfile.TemporaryDirectory() as tmpdir:
            artifact_path = Path(tmpdir) / "youtube-20260516T000000-20260531T000000.json"
            artifact_path.write_text(
                json.dumps(
                    [
                        {"content_id": "video-1", "views": 100},
                        {"content_id": "video-2", "views": 250},
                        {"content_id": "video-3", "views": 50},
                    ]
                ),
                encoding="utf-8",
            )

            summary = build_youtube_report_summary_with_limit(artifact_path, 1)

        self.assertEqual(len(summary.top_rows), 1)
        self.assertEqual(summary.top_limit, 1)
        self.assertEqual(summary.top_rows[0]["content_id"], "video-2")

    def test_build_youtube_report_summary_with_limit_rejects_invalid_limit(self) -> None:
        with tempfile.TemporaryDirectory() as tmpdir:
            artifact_path = Path(tmpdir) / "youtube-empty.json"
            artifact_path.write_text("[]", encoding="utf-8")

            with self.assertRaisesRegex(RuntimeError, "top_limit"):
                build_youtube_report_summary_with_limit(artifact_path, 0)

    def test_build_youtube_report_summary_with_options_sorts_by_selected_metric(self) -> None:
        with tempfile.TemporaryDirectory() as tmpdir:
            artifact_path = Path(tmpdir) / "youtube-20260516T000000-20260531T000000.json"
            artifact_path.write_text(
                json.dumps(
                    [
                        {"content_id": "video-views", "views": 300, "likes": 1},
                        {"content_id": "video-likes", "views": 10, "likes": 50},
                    ]
                ),
                encoding="utf-8",
            )

            summary = build_youtube_report_summary_with_options(artifact_path, 2, "likes")

        self.assertEqual(summary.sort_by, "likes")
        self.assertEqual(summary.top_rows[0]["content_id"], "video-likes")
        self.assertEqual(summary.top_metric_value, 50)

    def test_build_youtube_report_summary_uses_zero_rate_when_views_are_zero(self) -> None:
        with tempfile.TemporaryDirectory() as tmpdir:
            artifact_path = Path(tmpdir) / "youtube-zero-views.json"
            artifact_path.write_text(
                json.dumps([{"content_id": "video-1", "views": 0, "likes": 10}]),
                encoding="utf-8",
            )

            summary = build_youtube_report_summary(artifact_path)

        self.assertEqual(summary.total_engagements, 10)
        self.assertEqual(summary.engagement_rate, 0.0)

    def test_build_youtube_report_summary_uses_zero_average_when_artifact_is_empty(self) -> None:
        with tempfile.TemporaryDirectory() as tmpdir:
            artifact_path = Path(tmpdir) / "youtube-empty.json"
            artifact_path.write_text("[]", encoding="utf-8")

            summary = build_youtube_report_summary(artifact_path)

        self.assertEqual(summary.records, 0)
        self.assertEqual(summary.average_views_per_record, 0.0)
        self.assertEqual(summary.average_likes_per_record, 0.0)
        self.assertEqual(summary.average_comments_per_record, 0.0)
        self.assertEqual(summary.average_shares_per_record, 0.0)
        self.assertEqual(summary.average_engagements_per_record, 0.0)

    def test_build_youtube_report_summary_with_options_rejects_unknown_metric(self) -> None:
        with tempfile.TemporaryDirectory() as tmpdir:
            artifact_path = Path(tmpdir) / "youtube-empty.json"
            artifact_path.write_text("[]", encoding="utf-8")

            with self.assertRaisesRegex(RuntimeError, "sort_by"):
                build_youtube_report_summary_with_options(artifact_path, 1, "followers")

    def test_load_youtube_report_rows_rejects_non_list_payload(self) -> None:
        with tempfile.TemporaryDirectory() as tmpdir:
            artifact_path = Path(tmpdir) / "youtube-invalid.json"
            artifact_path.write_text('{"content_id":"video-1"}', encoding="utf-8")

            with self.assertRaisesRegex(RuntimeError, "JSON list"):
                load_youtube_report_rows(artifact_path)

    def test_write_youtube_report_markdown_persists_ranked_summary(self) -> None:
        with tempfile.TemporaryDirectory() as tmpdir:
            project_root = Path(tmpdir)
            artifact_dir = project_root / "data" / "processed" / "youtube"
            artifact_dir.mkdir(parents=True, exist_ok=True)
            artifact_path = artifact_dir / "youtube-20260516T000000-20260531T000000.json"
            artifact_path.write_text(
                json.dumps(
                    [
                        {
                            "content_id": "video-1",
                            "likes": 10,
                            "comments": 2,
                            "shares": 1,
                            "views": 100,
                            "followers": 1000,
                        },
                        {
                            "content_id": "video-2",
                            "likes": 5,
                            "comments": 3,
                            "shares": 0,
                            "views": 250,
                            "followers": 1200,
                        },
                    ]
                ),
                encoding="utf-8",
            )

            summary = build_youtube_report_summary(artifact_path)
            markdown = build_youtube_report_markdown(summary, project_root)
            report_path = write_youtube_report_markdown(summary, project_root)

            self.assertIn("# YouTube Report", markdown)
            self.assertIn("- Ranking metric: `views`", markdown)
            self.assertIn("- Average views per record: `175.00`", markdown)
            self.assertIn("- Average likes per record: `7.50`", markdown)
            self.assertIn("- Average comments per record: `2.50`", markdown)
            self.assertIn("- Average shares per record: `0.50`", markdown)
            self.assertIn("- Total engagements: `21`", markdown)
            self.assertIn("- Average engagements per record: `10.50`", markdown)
            self.assertIn("- Engagement rate: `6.00%`", markdown)
            self.assertIn("## Top Content by Views", markdown)
            self.assertIn("video-2", markdown)
            self.assertTrue(report_path.exists())
            saved = report_path.read_text(encoding="utf-8")
            self.assertIn("| video-2 | 250 | 5 | 3 | 0 | 1200 |", saved)

    def test_build_youtube_report_markdown_uses_selected_ranking_metric(self) -> None:
        with tempfile.TemporaryDirectory() as tmpdir:
            project_root = Path(tmpdir)
            artifact_path = project_root / "data" / "processed" / "youtube" / "youtube-sample.json"
            artifact_path.parent.mkdir(parents=True, exist_ok=True)
            artifact_path.write_text(
                json.dumps(
                    [
                        {"content_id": "video-views", "views": 300, "likes": 1},
                        {"content_id": "video-likes", "views": 10, "likes": 50},
                    ]
                ),
                encoding="utf-8",
            )

            summary = build_youtube_report_summary_with_options(artifact_path, 2, "likes")
            markdown = build_youtube_report_markdown(summary, project_root)

        self.assertIn("- Ranking metric: `likes`", markdown)
        self.assertIn("- Top likes: `50`", markdown)
        self.assertIn("## Top Content by Likes", markdown)
        self.assertLess(markdown.index("video-likes"), markdown.index("video-views"))

    def test_write_youtube_report_json_persists_compact_summary(self) -> None:
        with tempfile.TemporaryDirectory() as tmpdir:
            project_root = Path(tmpdir)
            artifact_path = project_root / "data" / "processed" / "youtube" / "youtube-sample.json"
            artifact_path.parent.mkdir(parents=True, exist_ok=True)
            artifact_path.write_text(
                json.dumps(
                    [
                        {
                            "content_id": "video-1",
                            "likes": 10,
                            "comments": 2,
                            "shares": 1,
                            "views": 100,
                            "followers": 1000,
                            "ignored_extra_field": "not exported",
                        }
                    ]
                ),
                encoding="utf-8",
            )
            output_path = project_root / "data" / "reports" / "youtube" / "summary.json"

            summary = build_youtube_report_summary_with_options(artifact_path, 1, "likes")
            payload = build_youtube_report_json_payload(
                summary,
                project_root,
                generated_at="2026-06-11T12:00:00Z",
            )
            report_path = write_youtube_report_json(
                summary,
                project_root,
                output_path,
                generated_at="2026-06-11T12:00:00Z",
            )
            saved = json.loads(report_path.read_text(encoding="utf-8"))

        self.assertEqual(payload["report_schema_version"], 1)
        self.assertEqual(payload["generated_at"], "2026-06-11T12:00:00Z")
        self.assertEqual(payload["source"]["provider"], "youtube")
        self.assertEqual(
            payload["source"]["artifact"],
            "data/processed/youtube/youtube-sample.json",
        )
        self.assertEqual(payload["ranking"], {"metric": "likes", "limit": 1})
        self.assertEqual(
            payload["data_quality"],
            {
                "has_engagements": True,
                "has_records": True,
                "has_top_content": True,
                "is_partial": False,
                "status": "ok",
                "top_rows_count": 1,
            },
        )
        self.assertEqual(saved["generated_at"], "2026-06-11T12:00:00Z")
        self.assertEqual(saved["source"], payload["source"])
        self.assertEqual(saved["ranking"], payload["ranking"])
        self.assertEqual(saved["data_quality"], payload["data_quality"])
        self.assertEqual(payload["sort_by"], "likes")
        self.assertEqual(saved["totals"]["views"], 100)
        self.assertEqual(saved["totals"]["average_views_per_record"], 100.0)
        self.assertEqual(saved["totals"]["average_likes_per_record"], 10.0)
        self.assertEqual(saved["totals"]["average_comments_per_record"], 2.0)
        self.assertEqual(saved["totals"]["average_shares_per_record"], 1.0)
        self.assertEqual(saved["totals"]["engagements"], 13)
        self.assertEqual(saved["totals"]["average_engagements_per_record"], 13.0)
        self.assertAlmostEqual(saved["totals"]["engagement_rate"], 0.13)
        self.assertAlmostEqual(saved["totals"]["engagement_rate_percent"], 13.0)
        self.assertAlmostEqual(saved["engagement_breakdown"]["likes_percent"], 76.923076923)
        self.assertAlmostEqual(saved["engagement_breakdown"]["comments_percent"], 15.384615384)
        self.assertAlmostEqual(saved["engagement_breakdown"]["shares_percent"], 7.692307692)
        self.assertEqual(saved["top_content"]["metric"], "likes")
        self.assertEqual(saved["top_content"]["metric_value"], 10)
        self.assertEqual(saved["top_rows"][0]["content_id"], "video-1")
        self.assertNotIn("ignored_extra_field", saved["top_rows"][0])

    def test_build_youtube_report_json_payload_uses_zero_breakdown_without_engagements(
        self,
    ) -> None:
        with tempfile.TemporaryDirectory() as tmpdir:
            project_root = Path(tmpdir)
            artifact_path = project_root / "data" / "processed" / "youtube" / "youtube-empty.json"
            artifact_path.parent.mkdir(parents=True, exist_ok=True)
            artifact_path.write_text(
                json.dumps([{"content_id": "video-1", "views": 100}]),
                encoding="utf-8",
            )

            summary = build_youtube_report_summary(artifact_path)
            payload = build_youtube_report_json_payload(summary, project_root)

        self.assertEqual(payload["totals"]["engagements"], 0)
        self.assertEqual(
            payload["data_quality"],
            {
                "has_engagements": False,
                "has_records": True,
                "has_top_content": True,
                "is_partial": False,
                "status": "ok",
                "top_rows_count": 1,
            },
        )
        self.assertEqual(payload["engagement_breakdown"]["likes_percent"], 0.0)
        self.assertEqual(payload["engagement_breakdown"]["comments_percent"], 0.0)
        self.assertEqual(payload["engagement_breakdown"]["shares_percent"], 0.0)

    def test_build_youtube_report_json_payload_marks_empty_data_quality(self) -> None:
        with tempfile.TemporaryDirectory() as tmpdir:
            project_root = Path(tmpdir)
            artifact_path = project_root / "data" / "processed" / "youtube" / "youtube-empty.json"
            artifact_path.parent.mkdir(parents=True, exist_ok=True)
            artifact_path.write_text("[]", encoding="utf-8")

            summary = build_youtube_report_summary(artifact_path)
            payload = build_youtube_report_json_payload(summary, project_root)

        self.assertEqual(payload["records"], 0)
        self.assertEqual(
            payload["data_quality"],
            {
                "has_engagements": False,
                "has_records": False,
                "has_top_content": False,
                "is_partial": False,
                "status": "empty",
                "top_rows_count": 0,
            },
        )

    def test_write_youtube_report_json_allows_compact_output(self) -> None:
        with tempfile.TemporaryDirectory() as tmpdir:
            project_root = Path(tmpdir)
            artifact_path = project_root / "data" / "processed" / "youtube" / "youtube-sample.json"
            artifact_path.parent.mkdir(parents=True, exist_ok=True)
            artifact_path.write_text(
                json.dumps([{"content_id": "video-1", "views": 100}]),
                encoding="utf-8",
            )
            output_path = project_root / "data" / "reports" / "youtube" / "summary.json"

            summary = build_youtube_report_summary(artifact_path)
            write_youtube_report_json(summary, project_root, output_path, indent=0)
            saved = output_path.read_text(encoding="utf-8")

        self.assertNotIn("\n  ", saved)
        self.assertTrue(saved.endswith("\n"))

    def test_build_youtube_report_json_text_allows_compact_output(self) -> None:
        with tempfile.TemporaryDirectory() as tmpdir:
            project_root = Path(tmpdir)
            artifact_path = project_root / "data" / "processed" / "youtube" / "youtube-sample.json"
            artifact_path.parent.mkdir(parents=True, exist_ok=True)
            artifact_path.write_text(
                json.dumps([{"content_id": "video-1", "views": 100}]),
                encoding="utf-8",
            )

            summary = build_youtube_report_summary(artifact_path)
            text = build_youtube_report_json_text(
                summary,
                project_root,
                indent=0,
                generated_at="2026-06-11T12:00:00Z",
            )

        self.assertNotIn("\n  ", text)
        self.assertEqual(json.loads(text)["records"], 1)
        self.assertEqual(json.loads(text)["generated_at"], "2026-06-11T12:00:00Z")

    def test_write_youtube_report_markdown_allows_custom_output_path(self) -> None:
        with tempfile.TemporaryDirectory() as tmpdir:
            project_root = Path(tmpdir)
            artifact_path = project_root / "data" / "processed" / "youtube" / "youtube-sample.json"
            artifact_path.parent.mkdir(parents=True, exist_ok=True)
            artifact_path.write_text("[]", encoding="utf-8")
            output_path = project_root / "custom" / "youtube-report.md"

            summary = build_youtube_report_summary(artifact_path)
            report_path = write_youtube_report_markdown(summary, project_root, output_path)

            self.assertEqual(report_path, output_path)
            self.assertTrue(output_path.exists())

    def test_build_youtube_report_output_path_in_dir_uses_artifact_stem(self) -> None:
        output_path = build_youtube_report_output_path_in_dir(
            Path("custom/reports"),
            Path("data/processed/youtube/youtube-sample.json"),
        )

        self.assertEqual(output_path, Path("custom/reports/youtube-sample.md"))

    def test_build_youtube_report_json_output_path_in_dir_uses_artifact_stem(self) -> None:
        output_path = build_youtube_report_json_output_path_in_dir(
            Path("custom/reports"),
            Path("data/processed/youtube/youtube-sample.json"),
        )

        self.assertEqual(output_path, Path("custom/reports/youtube-sample.json"))

    def test_parse_args_accepts_artifact_and_output_paths(self) -> None:
        args = parse_args(
            [
                "--artifact",
                "data/processed/youtube/sample.json",
                "--output-dir",
                "data/reports/youtube",
                "--json-output-dir",
                "data/reports/youtube-json",
                "--json-indent",
                "0",
                "--no-markdown",
                "--quiet",
                "--print-json",
                "--dry-run",
                "--list-artifacts",
                "--fail-if-missing",
                "--fail-if-empty",
                "--min-records",
                "2",
                "--top",
                "3",
                "--sort-by",
                "likes",
            ]
        )

        self.assertEqual(args.artifact, Path("data/processed/youtube/sample.json"))
        self.assertIsNone(args.output)
        self.assertEqual(args.output_dir, Path("data/reports/youtube"))
        self.assertIsNone(args.json_output)
        self.assertEqual(args.json_output_dir, Path("data/reports/youtube-json"))
        self.assertEqual(args.json_indent, 0)
        self.assertTrue(args.no_markdown)
        self.assertTrue(args.quiet)
        self.assertTrue(args.print_json)
        self.assertTrue(args.dry_run)
        self.assertTrue(args.list_artifacts)
        self.assertFalse(args.latest_artifact)
        self.assertTrue(args.fail_if_missing)
        self.assertTrue(args.fail_if_empty)
        self.assertEqual(args.min_records, 2)
        self.assertEqual(args.top, 3)
        self.assertEqual(args.sort_by, "likes")

    def test_parse_args_accepts_latest_artifact_mode(self) -> None:
        args = parse_args(["--latest-artifact"])

        self.assertFalse(args.list_artifacts)
        self.assertTrue(args.latest_artifact)
        self.assertFalse(args.count_artifacts)

    def test_parse_args_accepts_count_artifacts_mode(self) -> None:
        args = parse_args(["--count-artifacts", "--fail-if-missing"])

        self.assertFalse(args.list_artifacts)
        self.assertFalse(args.latest_artifact)
        self.assertTrue(args.count_artifacts)
        self.assertTrue(args.fail_if_missing)

    def test_parse_args_rejects_multiple_list_only_modes(self) -> None:
        with self.assertRaises(SystemExit):
            parse_args(["--list-artifacts", "--latest-artifact"])

        with self.assertRaises(SystemExit):
            parse_args(["--latest-artifact", "--count-artifacts"])

    def test_parse_args_rejects_invalid_top_limit(self) -> None:
        with self.assertRaises(SystemExit):
            parse_args(["--top", "0"])

    def test_parse_args_rejects_invalid_json_indent(self) -> None:
        with self.assertRaises(SystemExit):
            parse_args(["--json-indent", "-1"])

    def test_parse_args_rejects_invalid_min_records(self) -> None:
        with self.assertRaises(SystemExit):
            parse_args(["--min-records", "-1"])

    def test_parse_args_rejects_no_markdown_without_json_destination(self) -> None:
        with self.assertRaises(SystemExit):
            parse_args(["--no-markdown"])

    def test_parse_args_allows_no_markdown_with_print_json(self) -> None:
        args = parse_args(["--no-markdown", "--print-json"])

        self.assertTrue(args.no_markdown)
        self.assertTrue(args.print_json)

    def test_parse_args_rejects_output_and_output_dir_together(self) -> None:
        with self.assertRaises(SystemExit):
            parse_args(["--output", "report.md", "--output-dir", "reports"])

    def test_parse_args_rejects_json_output_and_json_output_dir_together(self) -> None:
        with self.assertRaises(SystemExit):
            parse_args(
                [
                    "--json-output",
                    "report.json",
                    "--json-output-dir",
                    "reports",
                ]
            )

    def test_main_uses_explicit_artifact_and_output_paths(self) -> None:
        with tempfile.TemporaryDirectory() as tmpdir:
            project_root = Path(tmpdir)
            artifact_path = project_root / "data" / "processed" / "youtube" / "youtube-sample.json"
            artifact_path.parent.mkdir(parents=True, exist_ok=True)
            artifact_path.write_text(
                json.dumps(
                    [
                        {
                            "content_id": "video-1",
                            "likes": 1,
                            "comments": 2,
                            "shares": 3,
                            "views": 4,
                            "followers": 5,
                        }
                    ]
                ),
                encoding="utf-8",
            )
            output_path = project_root / "custom" / "report.md"
            json_output_path = project_root / "custom" / "report.json"

            exit_code = main(
                project_root,
                artifact_path,
                output_path,
                json_output_path,
                top_limit=1,
                sort_by="likes",
            )

            self.assertEqual(exit_code, 0)
            self.assertTrue(output_path.exists())
            self.assertTrue(json_output_path.exists())

    def test_main_uses_output_dir_with_artifact_file_name(self) -> None:
        with tempfile.TemporaryDirectory() as tmpdir:
            project_root = Path(tmpdir)
            artifact_path = project_root / "data" / "processed" / "youtube" / "youtube-sample.json"
            artifact_path.parent.mkdir(parents=True, exist_ok=True)
            artifact_path.write_text("[]", encoding="utf-8")
            output_dir = project_root / "custom-reports"

            exit_code = main(
                project_root,
                artifact_path=artifact_path,
                output_dir=output_dir,
                quiet=True,
            )

            output_path = output_dir / "youtube-sample.md"
            self.assertEqual(exit_code, 0)
            self.assertTrue(output_path.exists())

    def test_main_uses_json_output_dir_with_artifact_file_name(self) -> None:
        with tempfile.TemporaryDirectory() as tmpdir:
            project_root = Path(tmpdir)
            artifact_path = project_root / "data" / "processed" / "youtube" / "youtube-sample.json"
            artifact_path.parent.mkdir(parents=True, exist_ok=True)
            artifact_path.write_text("[]", encoding="utf-8")
            json_output_dir = project_root / "custom-json-reports"

            exit_code = main(
                project_root,
                artifact_path=artifact_path,
                json_output_dir=json_output_dir,
                json_indent=0,
                quiet=True,
            )

            output_path = json_output_dir / "youtube-sample.json"
            self.assertEqual(exit_code, 0)
            self.assertTrue(output_path.exists())
            self.assertNotIn("\n  ", output_path.read_text(encoding="utf-8"))

    def test_main_rejects_json_output_and_json_output_dir_together(self) -> None:
        with tempfile.TemporaryDirectory() as tmpdir:
            project_root = Path(tmpdir)
            artifact_path = project_root / "data" / "processed" / "youtube" / "youtube-sample.json"
            artifact_path.parent.mkdir(parents=True, exist_ok=True)
            artifact_path.write_text("[]", encoding="utf-8")

            with self.assertRaisesRegex(RuntimeError, "--json-output"):
                main(
                    project_root,
                    artifact_path=artifact_path,
                    json_output_path=project_root / "report.json",
                    json_output_dir=project_root / "reports",
                )

    def test_main_rejects_output_and_output_dir_together(self) -> None:
        with tempfile.TemporaryDirectory() as tmpdir:
            project_root = Path(tmpdir)
            artifact_path = project_root / "data" / "processed" / "youtube" / "youtube-sample.json"
            artifact_path.parent.mkdir(parents=True, exist_ok=True)
            artifact_path.write_text("[]", encoding="utf-8")

            with self.assertRaisesRegex(RuntimeError, "--output"):
                main(
                    project_root,
                    artifact_path=artifact_path,
                    output_path=project_root / "report.md",
                    output_dir=project_root / "reports",
                )

    def test_main_can_write_json_without_markdown(self) -> None:
        with tempfile.TemporaryDirectory() as tmpdir:
            project_root = Path(tmpdir)
            artifact_path = project_root / "data" / "processed" / "youtube" / "youtube-sample.json"
            artifact_path.parent.mkdir(parents=True, exist_ok=True)
            artifact_path.write_text(
                json.dumps(
                    [
                        {
                            "content_id": "video-1",
                            "likes": 1,
                            "comments": 2,
                            "shares": 3,
                            "views": 4,
                            "followers": 5,
                        }
                    ]
                ),
                encoding="utf-8",
            )
            json_output_path = project_root / "custom" / "report.json"

            exit_code = main(
                project_root,
                artifact_path=artifact_path,
                json_output_path=json_output_path,
                no_markdown=True,
            )

            markdown_path = project_root / "data" / "reports" / "youtube" / "youtube-sample.md"
            self.assertEqual(exit_code, 0)
            self.assertTrue(json_output_path.exists())
            self.assertFalse(markdown_path.exists())

    def test_main_can_print_json_without_writing_report_files(self) -> None:
        with tempfile.TemporaryDirectory() as tmpdir:
            project_root = Path(tmpdir)
            artifact_path = project_root / "data" / "processed" / "youtube" / "youtube-sample.json"
            artifact_path.parent.mkdir(parents=True, exist_ok=True)
            artifact_path.write_text(
                json.dumps([{"content_id": "video-1", "views": 100}]),
                encoding="utf-8",
            )
            stdout = io.StringIO()

            with contextlib.redirect_stdout(stdout):
                exit_code = main(
                    project_root,
                    artifact_path=artifact_path,
                    no_markdown=True,
                    print_json=True,
                    quiet=True,
                )

            report_dir = project_root / "data" / "reports"

        self.assertEqual(exit_code, 0)
        self.assertEqual(json.loads(stdout.getvalue())["records"], 1)
        self.assertFalse(report_dir.exists())

    def test_main_rejects_no_markdown_without_json_destination(self) -> None:
        with tempfile.TemporaryDirectory() as tmpdir:
            project_root = Path(tmpdir)
            artifact_path = project_root / "data" / "processed" / "youtube" / "youtube-sample.json"
            artifact_path.parent.mkdir(parents=True, exist_ok=True)
            artifact_path.write_text("[]", encoding="utf-8")

            with self.assertRaisesRegex(RuntimeError, "--json-output"):
                main(
                    project_root,
                    artifact_path=artifact_path,
                    no_markdown=True,
                )

    def test_main_quiet_writes_report_without_summary_output(self) -> None:
        with tempfile.TemporaryDirectory() as tmpdir:
            project_root = Path(tmpdir)
            artifact_path = project_root / "data" / "processed" / "youtube" / "youtube-sample.json"
            artifact_path.parent.mkdir(parents=True, exist_ok=True)
            artifact_path.write_text(
                json.dumps(
                    [
                        {
                            "content_id": "video-1",
                            "likes": 1,
                            "comments": 2,
                            "shares": 3,
                            "views": 4,
                            "followers": 5,
                        }
                    ]
                ),
                encoding="utf-8",
            )
            stdout = io.StringIO()

            with contextlib.redirect_stdout(stdout):
                exit_code = main(project_root, artifact_path=artifact_path, quiet=True)

            markdown_path = project_root / "data" / "reports" / "youtube" / "youtube-sample.md"
            self.assertEqual(exit_code, 0)
            self.assertEqual(stdout.getvalue(), "")
            self.assertTrue(markdown_path.exists())

    def test_main_can_print_json_without_summary_output(self) -> None:
        with tempfile.TemporaryDirectory() as tmpdir:
            project_root = Path(tmpdir)
            artifact_path = project_root / "data" / "processed" / "youtube" / "youtube-sample.json"
            artifact_path.parent.mkdir(parents=True, exist_ok=True)
            artifact_path.write_text(
                json.dumps(
                    [
                        {
                            "content_id": "video-1",
                            "likes": 1,
                            "comments": 2,
                            "shares": 3,
                            "views": 4,
                            "followers": 5,
                        }
                    ]
                ),
                encoding="utf-8",
            )
            stdout = io.StringIO()

            with contextlib.redirect_stdout(stdout):
                exit_code = main(
                    project_root,
                    artifact_path=artifact_path,
                    quiet=True,
                    print_json=True,
                    json_indent=0,
                )

        self.assertEqual(exit_code, 0)
        self.assertEqual(json.loads(stdout.getvalue())["records"], 1)
        self.assertNotIn("YouTube report summary", stdout.getvalue())

    def test_main_can_fail_when_selected_artifact_is_empty(self) -> None:
        with tempfile.TemporaryDirectory() as tmpdir:
            project_root = Path(tmpdir)
            artifact_path = project_root / "data" / "processed" / "youtube" / "youtube-empty.json"
            artifact_path.parent.mkdir(parents=True, exist_ok=True)
            artifact_path.write_text("[]", encoding="utf-8")
            stdout = io.StringIO()

            with contextlib.redirect_stdout(stdout):
                exit_code = main(
                    project_root,
                    artifact_path=artifact_path,
                    fail_if_empty=True,
                )

            report_dir = project_root / "data" / "reports"

        self.assertEqual(exit_code, 1)
        self.assertIn("required at least 1", stdout.getvalue())
        self.assertFalse(report_dir.exists())

    def test_main_quiet_empty_failure_does_not_print_summary(self) -> None:
        with tempfile.TemporaryDirectory() as tmpdir:
            project_root = Path(tmpdir)
            artifact_path = project_root / "data" / "processed" / "youtube" / "youtube-empty.json"
            artifact_path.parent.mkdir(parents=True, exist_ok=True)
            artifact_path.write_text("[]", encoding="utf-8")
            stdout = io.StringIO()

            with contextlib.redirect_stdout(stdout):
                exit_code = main(
                    project_root,
                    artifact_path=artifact_path,
                    fail_if_empty=True,
                    quiet=True,
                )

        self.assertEqual(exit_code, 1)
        self.assertEqual(stdout.getvalue(), "")

    def test_main_can_fail_when_selected_artifact_is_below_min_records(self) -> None:
        with tempfile.TemporaryDirectory() as tmpdir:
            project_root = Path(tmpdir)
            artifact_path = project_root / "data" / "processed" / "youtube" / "youtube-sample.json"
            artifact_path.parent.mkdir(parents=True, exist_ok=True)
            artifact_path.write_text(
                json.dumps([{"content_id": "video-1", "views": 100}]),
                encoding="utf-8",
            )
            stdout = io.StringIO()

            with contextlib.redirect_stdout(stdout):
                exit_code = main(
                    project_root,
                    artifact_path=artifact_path,
                    min_records=2,
                )

            report_dir = project_root / "data" / "reports"

        self.assertEqual(exit_code, 1)
        self.assertIn("required at least 2", stdout.getvalue())
        self.assertFalse(report_dir.exists())

    def test_main_allows_selected_artifact_that_meets_min_records(self) -> None:
        with tempfile.TemporaryDirectory() as tmpdir:
            project_root = Path(tmpdir)
            artifact_path = project_root / "data" / "processed" / "youtube" / "youtube-sample.json"
            artifact_path.parent.mkdir(parents=True, exist_ok=True)
            artifact_path.write_text(
                json.dumps([{"content_id": "video-1", "views": 100}]),
                encoding="utf-8",
            )

            exit_code = main(
                project_root,
                artifact_path=artifact_path,
                min_records=1,
                quiet=True,
            )

            report_path = project_root / "data" / "reports" / "youtube" / "youtube-sample.md"
            self.assertEqual(exit_code, 0)
            self.assertTrue(report_path.exists())

    def test_main_dry_run_reports_planned_outputs_without_writing_files(self) -> None:
        with tempfile.TemporaryDirectory() as tmpdir:
            project_root = Path(tmpdir)
            artifact_path = project_root / "data" / "processed" / "youtube" / "youtube-sample.json"
            artifact_path.parent.mkdir(parents=True, exist_ok=True)
            artifact_path.write_text(
                json.dumps([{"content_id": "video-1", "views": 100}]),
                encoding="utf-8",
            )
            output_dir = project_root / "custom-reports"
            json_output_dir = project_root / "custom-json"
            stdout = io.StringIO()

            with contextlib.redirect_stdout(stdout):
                exit_code = main(
                    project_root,
                    artifact_path=artifact_path,
                    output_dir=output_dir,
                    json_output_dir=json_output_dir,
                    dry_run=True,
                )

            markdown_path = output_dir / "youtube-sample.md"
            json_path = json_output_dir / "youtube-sample.json"

        self.assertEqual(exit_code, 0)
        self.assertIn("YouTube report dry run", stdout.getvalue())
        self.assertIn("markdown_output_path=custom-reports/youtube-sample.md", stdout.getvalue())
        self.assertIn("json_output_path=custom-json/youtube-sample.json", stdout.getvalue())
        self.assertFalse(markdown_path.exists())
        self.assertFalse(json_path.exists())

    def test_main_dry_run_respects_min_records_before_planned_outputs(self) -> None:
        with tempfile.TemporaryDirectory() as tmpdir:
            project_root = Path(tmpdir)
            artifact_path = project_root / "data" / "processed" / "youtube" / "youtube-sample.json"
            artifact_path.parent.mkdir(parents=True, exist_ok=True)
            artifact_path.write_text(
                json.dumps([{"content_id": "video-1", "views": 100}]),
                encoding="utf-8",
            )
            stdout = io.StringIO()

            with contextlib.redirect_stdout(stdout):
                exit_code = main(
                    project_root,
                    artifact_path=artifact_path,
                    dry_run=True,
                    min_records=2,
                )

            report_dir = project_root / "data" / "reports"

        self.assertEqual(exit_code, 1)
        self.assertIn("required at least 2", stdout.getvalue())
        self.assertNotIn("YouTube report dry run", stdout.getvalue())
        self.assertFalse(report_dir.exists())

    def test_main_lists_artifacts_without_writing_reports(self) -> None:
        with tempfile.TemporaryDirectory() as tmpdir:
            project_root = Path(tmpdir)
            artifact_dir = project_root / "data" / "processed" / "youtube"
            artifact_dir.mkdir(parents=True, exist_ok=True)
            artifact_path = artifact_dir / "youtube-sample.json"
            artifact_path.write_text("[]", encoding="utf-8")
            stdout = io.StringIO()

            with contextlib.redirect_stdout(stdout):
                exit_code = main(project_root, list_artifacts=True)

            report_dir = project_root / "data" / "reports"

        self.assertEqual(exit_code, 0)
        self.assertIn("data/processed/youtube/youtube-sample.json", stdout.getvalue())
        self.assertFalse(report_dir.exists())

    def test_main_list_artifacts_can_fail_when_artifacts_are_missing(self) -> None:
        with tempfile.TemporaryDirectory() as tmpdir:
            project_root = Path(tmpdir)
            stdout = io.StringIO()

            with contextlib.redirect_stdout(stdout):
                exit_code = main(
                    project_root,
                    list_artifacts=True,
                    fail_if_missing=True,
                )

        self.assertEqual(exit_code, 1)
        self.assertIn("No processed YouTube artifacts found.", stdout.getvalue())

    def test_main_prints_latest_artifact_without_writing_reports(self) -> None:
        with tempfile.TemporaryDirectory() as tmpdir:
            project_root = Path(tmpdir)
            artifact_dir = project_root / "data" / "processed" / "youtube"
            artifact_dir.mkdir(parents=True, exist_ok=True)
            first = artifact_dir / "youtube-20260501T000000-20260515T000000.json"
            second = artifact_dir / "youtube-20260516T000000-20260531T000000.json"
            first.write_text("[]", encoding="utf-8")
            second.write_text("[]", encoding="utf-8")
            stdout = io.StringIO()

            with contextlib.redirect_stdout(stdout):
                exit_code = main(project_root, latest_artifact=True)

            report_dir = project_root / "data" / "reports"

        self.assertEqual(exit_code, 0)
        self.assertEqual(
            stdout.getvalue().strip(),
            "data/processed/youtube/youtube-20260516T000000-20260531T000000.json",
        )
        self.assertFalse(report_dir.exists())

    def test_main_counts_artifacts_without_writing_reports(self) -> None:
        with tempfile.TemporaryDirectory() as tmpdir:
            project_root = Path(tmpdir)
            artifact_dir = project_root / "data" / "processed" / "youtube"
            artifact_dir.mkdir(parents=True, exist_ok=True)
            (artifact_dir / "youtube-1.json").write_text("[]", encoding="utf-8")
            (artifact_dir / "youtube-2.json").write_text("[]", encoding="utf-8")
            stdout = io.StringIO()

            with contextlib.redirect_stdout(stdout):
                exit_code = main(project_root, count_artifacts=True)

            report_dir = project_root / "data" / "reports"

        self.assertEqual(exit_code, 0)
        self.assertEqual(stdout.getvalue().strip(), "2")
        self.assertFalse(report_dir.exists())

    def test_main_count_artifacts_can_fail_when_artifacts_are_missing(self) -> None:
        with tempfile.TemporaryDirectory() as tmpdir:
            project_root = Path(tmpdir)
            stdout = io.StringIO()

            with contextlib.redirect_stdout(stdout):
                exit_code = main(
                    project_root,
                    count_artifacts=True,
                    fail_if_missing=True,
                )

        self.assertEqual(exit_code, 1)
        self.assertEqual(stdout.getvalue().strip(), "0")

    def test_main_allows_explicit_output_path_outside_project_root(self) -> None:
        with tempfile.TemporaryDirectory() as tmpdir:
            workspace = Path(tmpdir)
            project_root = workspace / "project"
            artifact_path = project_root / "data" / "processed" / "youtube" / "youtube-sample.json"
            artifact_path.parent.mkdir(parents=True, exist_ok=True)
            artifact_path.write_text(
                json.dumps(
                    [
                        {
                            "content_id": "video-1",
                            "likes": 1,
                            "comments": 2,
                            "shares": 3,
                            "views": 4,
                            "followers": 5,
                        }
                    ]
                ),
                encoding="utf-8",
            )
            output_path = workspace / "external" / "report.md"

            exit_code = main(project_root, artifact_path, output_path, top_limit=1)

            self.assertEqual(exit_code, 0)
            self.assertTrue(output_path.exists())

    def test_cli_entrypoint_uses_parser_and_main(self) -> None:
        with tempfile.TemporaryDirectory() as tmpdir:
            artifact_path = Path(tmpdir) / "youtube-sample.json"
            artifact_path.write_text(
                json.dumps([{"content_id": "video-1", "views": 100}]),
                encoding="utf-8",
            )
            stdout = io.StringIO()

            with (
                mock.patch.object(
                    sys,
                    "argv",
                    [
                        "youtube-report",
                        "--artifact",
                        str(artifact_path),
                        "--no-markdown",
                        "--print-json",
                        "--quiet",
                    ],
                ),
                contextlib.redirect_stdout(stdout),
            ):
                exit_code = cli_entrypoint()

        self.assertEqual(exit_code, 0)
        self.assertEqual(json.loads(stdout.getvalue())["records"], 1)


if __name__ == "__main__":
    unittest.main()
