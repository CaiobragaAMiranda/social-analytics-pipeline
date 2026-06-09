import json
import tempfile
import unittest
from pathlib import Path

from social_analytics_pipeline.cli.youtube_report import (
    build_youtube_report_markdown,
    build_youtube_report_summary,
    find_latest_youtube_processed_artifact,
    load_youtube_report_rows,
    main,
    parse_args,
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
        self.assertEqual(summary.total_likes, 15)
        self.assertEqual(summary.total_comments, 5)
        self.assertEqual(summary.total_shares, 1)
        self.assertEqual(summary.max_followers, 1200)
        self.assertEqual(summary.top_content_id, "video-2")
        self.assertEqual(summary.top_views, 250)
        self.assertEqual(len(summary.top_rows), 2)
        self.assertEqual(summary.top_rows[0]["content_id"], "video-2")

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
            self.assertIn("video-2", markdown)
            self.assertTrue(report_path.exists())
            saved = report_path.read_text(encoding="utf-8")
            self.assertIn("| video-2 | 250 | 5 | 3 | 0 | 1200 |", saved)

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

    def test_parse_args_accepts_artifact_and_output_paths(self) -> None:
        args = parse_args(
            [
                "--artifact",
                "data/processed/youtube/sample.json",
                "--output",
                "data/reports/youtube/sample.md",
            ]
        )

        self.assertEqual(args.artifact, Path("data/processed/youtube/sample.json"))
        self.assertEqual(args.output, Path("data/reports/youtube/sample.md"))

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

            exit_code = main(project_root, artifact_path, output_path)

            self.assertEqual(exit_code, 0)
            self.assertTrue(output_path.exists())

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

            exit_code = main(project_root, artifact_path, output_path)

            self.assertEqual(exit_code, 0)
            self.assertTrue(output_path.exists())


if __name__ == "__main__":
    unittest.main()
