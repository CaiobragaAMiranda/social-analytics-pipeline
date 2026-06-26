import contextlib
import io
import json
import tempfile
import unittest
from pathlib import Path
from unittest import mock

from social_analytics_pipeline.cli.instagram_report import (
    build_instagram_artifact_listing,
    build_instagram_report_json_payload,
    build_instagram_report_summary,
    build_latest_instagram_artifact_listing,
    cli_entrypoint,
    count_instagram_processed_artifacts,
    find_latest_instagram_processed_artifact,
    load_instagram_report_rows,
    main,
    parse_args,
    resolve_instagram_report_json_output_path,
    write_instagram_report_json,
)


class InstagramReportTest(unittest.TestCase):
    def test_build_instagram_report_summary_aggregates_processed_metrics(self) -> None:
        with tempfile.TemporaryDirectory() as tmpdir:
            artifact_path = Path(tmpdir) / "instagram-sample.json"
            artifact_path.write_text(
                json.dumps(
                    [
                        {
                            "content_id": "ig-post-1",
                            "content_type": "post",
                            "published_at": "2026-05-20T14:30:00+00:00",
                            "likes": 10,
                            "comments": 2,
                            "shares": 1,
                            "views": 100,
                            "followers": 1000,
                        },
                        {
                            "content_id": "ig-reel-2",
                            "content_type": "reel",
                            "likes": 5,
                            "comments": 3,
                            "shares": 4,
                            "views": 250,
                            "followers": 1200,
                        },
                    ]
                ),
                encoding="utf-8",
            )

            summary = build_instagram_report_summary(artifact_path)

        self.assertEqual(summary.records, 2)
        self.assertEqual(summary.total_views, 350)
        self.assertEqual(summary.total_likes, 15)
        self.assertEqual(summary.total_comments, 5)
        self.assertEqual(summary.total_shares, 5)
        self.assertEqual(summary.total_engagements, 25)
        self.assertAlmostEqual(summary.engagement_rate, 25 / 350)
        self.assertEqual(summary.max_followers, 1200)
        self.assertEqual(summary.top_content_id, "ig-reel-2")
        self.assertEqual(summary.top_metric_value, 250)

    def test_build_instagram_report_json_payload_matches_dashboard_contract(self) -> None:
        with tempfile.TemporaryDirectory() as tmpdir:
            project_root = Path(tmpdir)
            artifact_path = project_root / "data" / "processed" / "instagram" / "instagram.json"
            artifact_path.parent.mkdir(parents=True)
            artifact_path.write_text(
                json.dumps(
                    [
                        {
                            "content_id": "ig-post-1",
                            "content_type": "post",
                            "title": "Launch post",
                            "thumbnail_url": "https://example.test/post.jpg",
                            "content_url": "https://example.test/post",
                            "channel_name": "Brand Instagram",
                            "channel_image_url": "https://example.test/channel.jpg",
                            "published_at": "2026-05-20T14:30:00+00:00",
                            "likes": 10,
                            "comments": 2,
                            "shares": 1,
                            "views": 100,
                            "followers": 1000,
                        }
                    ]
                ),
                encoding="utf-8",
            )

            summary = build_instagram_report_summary(artifact_path, top_limit=1, sort_by="likes")
            payload = build_instagram_report_json_payload(
                summary,
                project_root,
                generated_at="2026-06-13T12:00:00Z",
            )
            report_path = write_instagram_report_json(
                summary,
                project_root,
                generated_at="2026-06-13T12:00:00Z",
            )
            saved = json.loads(report_path.read_text(encoding="utf-8"))

        self.assertEqual(payload["source"]["provider"], "instagram")
        self.assertEqual(payload["source"]["channel_name"], "Brand Instagram")
        self.assertEqual(payload["records"], 1)
        self.assertEqual(payload["ranking"], {"metric": "likes", "limit": 1})
        self.assertEqual(payload["data_quality"]["status"], "ok")
        self.assertEqual(payload["totals"]["views"], 100)
        self.assertEqual(payload["top_content"]["title"], "Launch post")
        self.assertEqual(payload["top_rows"][0]["thumbnail_url"], "https://example.test/post.jpg")
        self.assertEqual(saved["generated_at"], "2026-06-13T12:00:00Z")
        self.assertEqual(saved["source"], payload["source"])

    def test_instagram_report_json_keeps_all_production_dates_beyond_top_limit(
        self,
    ) -> None:
        with tempfile.TemporaryDirectory() as tmpdir:
            project_root = Path(tmpdir)
            artifact_path = project_root / "data" / "processed" / "instagram" / "instagram.json"
            artifact_path.parent.mkdir(parents=True)
            artifact_path.write_text(
                json.dumps(
                    [
                        {
                            "content_id": "ig-post-1",
                            "views": 100,
                            "published_at": "2026-01-01T10:00:00+00:00",
                        },
                        {
                            "content_id": "ig-post-2",
                            "views": 900,
                            "published_at": "2026-02-01T10:00:00+00:00",
                        },
                        {
                            "content_id": "ig-post-3",
                            "views": 50,
                            "published_at": "2026-03-01T10:00:00+00:00",
                        },
                    ]
                ),
                encoding="utf-8",
            )

            summary = build_instagram_report_summary(
                artifact_path,
                top_limit=1,
                sort_by="views",
            )
            payload = build_instagram_report_json_payload(summary, project_root)

        self.assertEqual(len(payload["top_rows"]), 1)
        self.assertEqual(
            payload["production_dates"],
            [
                "2026-01-01T10:00:00+00:00",
                "2026-02-01T10:00:00+00:00",
                "2026-03-01T10:00:00+00:00",
            ],
        )
        self.assertEqual(
            payload["production"],
            {
                "period": "latest_6_months",
                "date_source": "all_processed_rows",
                "dates_count": 3,
            },
        )

    def test_empty_artifact_writes_empty_quality_payload(self) -> None:
        with tempfile.TemporaryDirectory() as tmpdir:
            project_root = Path(tmpdir)
            artifact_path = project_root / "data" / "processed" / "instagram" / "empty.json"
            artifact_path.parent.mkdir(parents=True)
            artifact_path.write_text("[]", encoding="utf-8")

            summary = build_instagram_report_summary(artifact_path)
            payload = build_instagram_report_json_payload(summary, project_root)

        self.assertEqual(payload["records"], 0)
        self.assertEqual(payload["data_quality"]["status"], "empty")
        self.assertEqual(payload["top_content"]["content_id"], None)
        self.assertEqual(payload["top_rows"], [])

    def test_main_writes_latest_instagram_report(self) -> None:
        with tempfile.TemporaryDirectory() as tmpdir:
            project_root = Path(tmpdir)
            artifact_dir = project_root / "data" / "processed" / "instagram"
            artifact_dir.mkdir(parents=True)
            artifact_path = artifact_dir / "instagram-20260501T000000-20260527T000000.json"
            artifact_path.write_text(
                json.dumps([{"content_id": "ig-post-1", "views": 100}]),
                encoding="utf-8",
            )

            exit_code = main(project_root=project_root, quiet=True)
            report_path = (
                project_root
                / "data"
                / "reports"
                / "instagram-json"
                / "instagram-20260501T000000-20260527T000000.json"
            )
            report_exists = report_path.exists()

        self.assertEqual(exit_code, 0)
        self.assertTrue(report_exists)

    def test_main_can_fail_when_selected_artifact_is_empty(self) -> None:
        with tempfile.TemporaryDirectory() as tmpdir:
            project_root = Path(tmpdir)
            artifact_path = project_root / "instagram-empty.json"
            artifact_path.write_text("[]", encoding="utf-8")
            stdout = io.StringIO()

            with contextlib.redirect_stdout(stdout):
                exit_code = main(
                    project_root=project_root,
                    artifact_path=artifact_path,
                    fail_if_empty=True,
                )

        self.assertEqual(exit_code, 1)
        self.assertIn("0 records", stdout.getvalue())

    def test_find_latest_instagram_processed_artifact_fails_when_missing(self) -> None:
        with tempfile.TemporaryDirectory() as tmpdir, self.assertRaisesRegex(
            RuntimeError,
            "No processed Instagram",
        ):
            find_latest_instagram_processed_artifact(Path(tmpdir))

    def test_build_instagram_artifact_listing_uses_sorted_relative_paths(self) -> None:
        with tempfile.TemporaryDirectory() as tmpdir:
            project_root = Path(tmpdir)
            artifact_dir = project_root / "data" / "processed" / "instagram"
            artifact_dir.mkdir(parents=True)
            older = artifact_dir / "instagram-20260501T000000-20260502T000000.json"
            newer = artifact_dir / "instagram-20260502T000000-20260503T000000.json"
            newer.write_text("[]", encoding="utf-8")
            older.write_text("[]", encoding="utf-8")

            listing = build_instagram_artifact_listing(project_root)
            latest = build_latest_instagram_artifact_listing(project_root)
            count = count_instagram_processed_artifacts(project_root)

        self.assertEqual(
            listing,
            [
                "data/processed/instagram/instagram-20260501T000000-20260502T000000.json",
                "data/processed/instagram/instagram-20260502T000000-20260503T000000.json",
            ],
        )
        self.assertEqual(
            latest,
            "data/processed/instagram/instagram-20260502T000000-20260503T000000.json",
        )
        self.assertEqual(count, 2)

    def test_main_list_artifacts_prints_processed_instagram_artifacts(self) -> None:
        with tempfile.TemporaryDirectory() as tmpdir:
            project_root = Path(tmpdir)
            artifact_dir = project_root / "data" / "processed" / "instagram"
            artifact_dir.mkdir(parents=True)
            artifact_path = artifact_dir / "instagram-20260501T000000-20260502T000000.json"
            artifact_path.write_text("[]", encoding="utf-8")
            stdout = io.StringIO()

            with contextlib.redirect_stdout(stdout):
                exit_code = main(project_root=project_root, list_artifacts=True)

        self.assertEqual(exit_code, 0)
        self.assertIn(
            "data/processed/instagram/instagram-20260501T000000-20260502T000000.json",
            stdout.getvalue(),
        )

    def test_main_count_artifacts_can_fail_when_missing(self) -> None:
        with tempfile.TemporaryDirectory() as tmpdir:
            stdout = io.StringIO()

            with contextlib.redirect_stdout(stdout):
                exit_code = main(
                    project_root=Path(tmpdir),
                    count_artifacts=True,
                    fail_if_missing=True,
                )

        self.assertEqual(exit_code, 1)
        self.assertEqual(stdout.getvalue().strip(), "0")

    def test_main_latest_artifact_prints_latest_processed_instagram_artifact(self) -> None:
        with tempfile.TemporaryDirectory() as tmpdir:
            project_root = Path(tmpdir)
            artifact_dir = project_root / "data" / "processed" / "instagram"
            artifact_dir.mkdir(parents=True)
            older = artifact_dir / "instagram-20260501T000000-20260502T000000.json"
            newer = artifact_dir / "instagram-20260502T000000-20260503T000000.json"
            older.write_text("[]", encoding="utf-8")
            newer.write_text("[]", encoding="utf-8")
            stdout = io.StringIO()

            with contextlib.redirect_stdout(stdout):
                exit_code = main(project_root=project_root, latest_artifact=True)

        self.assertEqual(exit_code, 0)
        self.assertEqual(
            stdout.getvalue().strip(),
            "data/processed/instagram/instagram-20260502T000000-20260503T000000.json",
        )

    def test_main_dry_run_prints_plan_without_writing_report(self) -> None:
        with tempfile.TemporaryDirectory() as tmpdir:
            project_root = Path(tmpdir)
            artifact_dir = project_root / "data" / "processed" / "instagram"
            artifact_dir.mkdir(parents=True)
            artifact_path = artifact_dir / "instagram-20260501T000000-20260502T000000.json"
            artifact_path.write_text(
                json.dumps([{"content_id": "ig-post-1", "views": 100}]),
                encoding="utf-8",
            )
            report_path = (
                project_root
                / "data"
                / "reports"
                / "instagram-json"
                / "instagram-20260501T000000-20260502T000000.json"
            )
            stdout = io.StringIO()

            with contextlib.redirect_stdout(stdout):
                exit_code = main(project_root=project_root, dry_run=True)

            report_exists = report_path.exists()

        self.assertEqual(exit_code, 0)
        self.assertFalse(report_exists)
        self.assertIn("Instagram report dry run", stdout.getvalue())
        self.assertIn(
            "artifact_path=data/processed/instagram/"
            "instagram-20260501T000000-20260502T000000.json",
            stdout.getvalue(),
        )
        self.assertIn("records=1", stdout.getvalue())
        self.assertIn("sort_by=views", stdout.getvalue())
        self.assertIn(
            "json_output_path=data/reports/instagram-json/"
            "instagram-20260501T000000-20260502T000000.json",
            stdout.getvalue(),
        )

    def test_main_writes_report_to_json_output_dir(self) -> None:
        with tempfile.TemporaryDirectory() as tmpdir:
            project_root = Path(tmpdir)
            artifact_dir = project_root / "data" / "processed" / "instagram"
            artifact_dir.mkdir(parents=True)
            artifact_path = artifact_dir / "instagram-20260501T000000-20260502T000000.json"
            artifact_path.write_text(
                json.dumps([{"content_id": "ig-post-1", "views": 100}]),
                encoding="utf-8",
            )
            output_dir = project_root / "custom-json"

            exit_code = main(
                project_root=project_root,
                json_output_dir=output_dir,
                quiet=True,
            )
            report_path = output_dir / "instagram-20260501T000000-20260502T000000.json"
            report_exists = report_path.exists()

        self.assertEqual(exit_code, 0)
        self.assertTrue(report_exists)

    def test_main_rejects_conflicting_json_output_options(self) -> None:
        with tempfile.TemporaryDirectory() as tmpdir:
            project_root = Path(tmpdir)
            artifact_path = project_root / "instagram.json"
            artifact_path.write_text("[]", encoding="utf-8")

            with self.assertRaisesRegex(RuntimeError, "json-output"):
                main(
                    project_root=project_root,
                    artifact_path=artifact_path,
                    json_output_path=project_root / "report.json",
                    json_output_dir=project_root / "reports",
                )

    def test_dry_run_uses_json_output_dir_path(self) -> None:
        with tempfile.TemporaryDirectory() as tmpdir:
            project_root = Path(tmpdir)
            artifact_path = project_root / "instagram-20260501T000000-20260502T000000.json"
            artifact_path.write_text(
                json.dumps([{"content_id": "ig-post-1", "views": 100}]),
                encoding="utf-8",
            )
            stdout = io.StringIO()

            with contextlib.redirect_stdout(stdout):
                exit_code = main(
                    project_root=project_root,
                    artifact_path=artifact_path,
                    json_output_dir=project_root / "custom-json",
                    dry_run=True,
                )

        self.assertEqual(exit_code, 0)
        self.assertIn(
            "json_output_path=custom-json/instagram-20260501T000000-20260502T000000.json",
            stdout.getvalue(),
        )

    def test_resolve_instagram_report_json_output_path_rejects_conflict(self) -> None:
        with self.assertRaisesRegex(RuntimeError, "json-output"):
            resolve_instagram_report_json_output_path(
                Path("project"),
                Path("instagram.json"),
                Path("report.json"),
                Path("reports"),
            )

    def test_parse_args_accepts_list_only_modes(self) -> None:
        list_args = parse_args(["--list-artifacts", "--fail-if-missing"])
        latest_args = parse_args(["--latest-artifact"])
        count_args = parse_args(["--count-artifacts"])
        dry_run_args = parse_args(["--dry-run"])
        output_dir_args = parse_args(["--json-output-dir", "reports"])

        self.assertTrue(list_args.list_artifacts)
        self.assertTrue(list_args.fail_if_missing)
        self.assertTrue(latest_args.latest_artifact)
        self.assertTrue(count_args.count_artifacts)
        self.assertTrue(dry_run_args.dry_run)
        self.assertEqual(output_dir_args.json_output_dir, Path("reports"))

    def test_parse_args_rejects_multiple_list_only_modes(self) -> None:
        with self.assertRaises(SystemExit):
            parse_args(["--list-artifacts", "--latest-artifact"])

    def test_load_instagram_report_rows_rejects_non_list_payload(self) -> None:
        with tempfile.TemporaryDirectory() as tmpdir:
            artifact_path = Path(tmpdir) / "invalid.json"
            artifact_path.write_text("{}", encoding="utf-8")

            with self.assertRaisesRegex(RuntimeError, "JSON list"):
                load_instagram_report_rows(artifact_path)

    def test_cli_entrypoint_uses_parser_and_main(self) -> None:
        with tempfile.TemporaryDirectory() as tmpdir:
            artifact_path = Path(tmpdir) / "instagram-sample.json"
            artifact_path.write_text(
                json.dumps([{"content_id": "ig-post-1", "views": 100}]),
                encoding="utf-8",
            )
            stdout = io.StringIO()

            with (
                mock.patch(
                    "sys.argv",
                    [
                        "instagram-report",
                        "--artifact",
                        str(artifact_path),
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
