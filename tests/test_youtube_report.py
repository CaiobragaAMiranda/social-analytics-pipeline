import json
import tempfile
import unittest
from pathlib import Path

from social_analytics_pipeline.cli.youtube_report import (
    build_youtube_report_summary,
    find_latest_youtube_processed_artifact,
    load_youtube_report_rows,
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

    def test_load_youtube_report_rows_rejects_non_list_payload(self) -> None:
        with tempfile.TemporaryDirectory() as tmpdir:
            artifact_path = Path(tmpdir) / "youtube-invalid.json"
            artifact_path.write_text('{"content_id":"video-1"}', encoding="utf-8")

            with self.assertRaisesRegex(RuntimeError, "JSON list"):
                load_youtube_report_rows(artifact_path)


if __name__ == "__main__":
    unittest.main()
