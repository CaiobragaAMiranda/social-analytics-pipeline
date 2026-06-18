import json
import unittest
from contextlib import redirect_stdout
from datetime import UTC, datetime
from io import StringIO
from pathlib import Path
from tempfile import TemporaryDirectory
from typing import Any

from social_analytics_pipeline.cli.instagram_local_pipeline import (
    InstagramLocalPipelineSummary,
    build_instagram_local_loader,
    enforce_instagram_loaded_records,
    main,
    parse_args,
    resolve_instagram_interval,
    run_instagram_local_pipeline,
)
from social_analytics_pipeline.pipeline import JsonMetricArtifactLoader, LocalPipelineResult
from social_analytics_pipeline.providers import InstagramApiConfig, InstagramGraphApiProvider


class FakeInstagramHttpJsonClient:
    def get_json(self, url: str, params: dict[str, str | int]) -> dict[str, Any]:
        if url.endswith("/ig-account-1"):
            return {
                "id": "ig-account-1",
                "username": "example_account",
                "followers_count": 1200,
                "profile_picture_url": "https://example.test/profile.jpg",
            }
        if url.endswith("/ig-account-1/media"):
            return {
                "data": [
                    {
                        "id": "ig-media-1",
                        "media_type": "IMAGE",
                        "timestamp": "2026-05-20T14:30:00Z",
                        "caption": "Launch post",
                        "permalink": "https://example.test/post",
                        "media_url": "https://example.test/post.jpg",
                        "like_count": 12,
                        "comments_count": 3,
                        "impressions": 100,
                    }
                ]
            }
        raise AssertionError(f"Unexpected URL: {url}")


class InstagramLocalPipelineTest(unittest.TestCase):
    def test_runs_instagram_provider_into_raw_and_processed_artifacts(self) -> None:
        provider = InstagramGraphApiProvider(
            InstagramApiConfig(
                access_token="test-token",
                account_id="ig-account-1",
            ),
            http_client=FakeInstagramHttpJsonClient(),
        )

        with TemporaryDirectory() as tmpdir:
            project_root = Path(tmpdir)
            summary = run_instagram_local_pipeline(
                provider=provider,
                account_id="ig-account-1",
                start_at=datetime(2026, 5, 1, tzinfo=UTC),
                end_at=datetime(2026, 5, 27, tzinfo=UTC),
                project_root=project_root,
            )

            raw_files = sorted((project_root / "data" / "raw").glob("instagram/**/*.json"))
            processed_rows = json.loads(summary.processed_path.read_text(encoding="utf-8"))
            run_summary = json.loads(summary.run_summary_path.read_text(encoding="utf-8"))

        self.assertEqual(summary.result.provider, "instagram")
        self.assertEqual(summary.result.raw_records, 1)
        self.assertEqual(summary.result.valid_records, 1)
        self.assertEqual(summary.result.loaded_records, 1)
        self.assertEqual(len(raw_files), 1)
        self.assertEqual(processed_rows[0]["provider"], "instagram")
        self.assertEqual(processed_rows[0]["content_id"], "ig-media-1")
        self.assertEqual(processed_rows[0]["title"], "Launch post")
        self.assertEqual(processed_rows[0]["thumbnail_url"], "https://example.test/post.jpg")
        self.assertEqual(processed_rows[0]["content_url"], "https://example.test/post")
        self.assertEqual(processed_rows[0]["channel_name"], "example_account")
        self.assertEqual(
            processed_rows[0]["channel_image_url"],
            "https://example.test/profile.jpg",
        )
        self.assertEqual(run_summary["provider"], "instagram")
        self.assertEqual(run_summary["status"], "ok")
        self.assertEqual(run_summary["counts"]["valid_records"], 1)
        self.assertEqual(
            run_summary["artifacts"]["processed_path"],
            summary.processed_path.relative_to(project_root).as_posix(),
        )

    def test_build_instagram_local_loader_defaults_to_json_artifact(self) -> None:
        loader, processed_path = build_instagram_local_loader(
            runtime_env={},
            provider_name="instagram",
            start_at=datetime(2026, 5, 1, tzinfo=UTC),
            end_at=datetime(2026, 5, 27, tzinfo=UTC),
            project_root=Path("project"),
        )

        self.assertIsInstance(loader, JsonMetricArtifactLoader)
        self.assertEqual(
            processed_path.as_posix(),
            "project/data/processed/instagram/instagram-20260501T000000-20260527T000000.json",
        )

    def test_build_instagram_local_loader_rejects_unknown_target(self) -> None:
        with self.assertRaisesRegex(RuntimeError, "INSTAGRAM_LOCAL_LOAD_TARGET"):
            build_instagram_local_loader(
                runtime_env={"INSTAGRAM_LOCAL_LOAD_TARGET": "postgres"},
                provider_name="instagram",
                start_at=datetime(2026, 5, 1, tzinfo=UTC),
                end_at=datetime(2026, 5, 27, tzinfo=UTC),
                project_root=Path("project"),
            )

    def test_resolve_instagram_interval_accepts_explicit_backfill(self) -> None:
        start_at, end_at = resolve_instagram_interval(
            {
                "INSTAGRAM_BACKFILL_START_AT": "2026-05-01T00:00:00Z",
                "INSTAGRAM_BACKFILL_END_AT": "2026-05-27T00:00:00Z",
            }
        )

        self.assertEqual(start_at, datetime(2026, 5, 1, tzinfo=UTC))
        self.assertEqual(end_at, datetime(2026, 5, 27, tzinfo=UTC))

    def test_resolve_instagram_interval_uses_lookback_days(self) -> None:
        start_at, end_at = resolve_instagram_interval(
            {"INSTAGRAM_SMOKE_LOOKBACK_DAYS": "7"},
            now=datetime(2026, 5, 27, tzinfo=UTC),
        )

        self.assertEqual(start_at, datetime(2026, 5, 20, tzinfo=UTC))
        self.assertEqual(end_at, datetime(2026, 5, 27, tzinfo=UTC))

    def test_resolve_instagram_interval_prefers_cli_interval_over_environment(
        self,
    ) -> None:
        start_at, end_at = resolve_instagram_interval(
            {
                "INSTAGRAM_BACKFILL_START_AT": "2026-04-01T00:00:00Z",
                "INSTAGRAM_BACKFILL_END_AT": "2026-04-30T00:00:00Z",
            },
            start_at_override="2026-05-01T00:00:00Z",
            end_at_override="2026-05-27T00:00:00Z",
        )

        self.assertEqual(start_at, datetime(2026, 5, 1, tzinfo=UTC))
        self.assertEqual(end_at, datetime(2026, 5, 27, tzinfo=UTC))

    def test_resolve_instagram_interval_rejects_partial_cli_interval(self) -> None:
        with self.assertRaisesRegex(RuntimeError, "--start-at and --end-at"):
            resolve_instagram_interval(
                {},
                start_at_override="2026-05-01T00:00:00Z",
            )

    def test_resolve_instagram_interval_accepts_cli_lookback_override(self) -> None:
        start_at, end_at = resolve_instagram_interval(
            {"INSTAGRAM_SMOKE_LOOKBACK_DAYS": "30"},
            now=datetime(2026, 5, 27, tzinfo=UTC),
            lookback_days_override=3,
        )

        self.assertEqual(start_at, datetime(2026, 5, 24, tzinfo=UTC))
        self.assertEqual(end_at, datetime(2026, 5, 27, tzinfo=UTC))

    def test_main_fails_closed_when_credentials_are_missing(self) -> None:
        with TemporaryDirectory() as tmpdir, self.assertRaisesRegex(
            RuntimeError,
            "INSTAGRAM_ACCESS_TOKEN, INSTAGRAM_USER_ID",
        ):
            main(env={}, project_root=Path(tmpdir))

    def test_main_dry_run_does_not_require_credentials_or_write_artifacts(self) -> None:
        with TemporaryDirectory() as tmpdir:
            project_root = Path(tmpdir)
            stdout = StringIO()

            with redirect_stdout(stdout):
                exit_code = main(
                    env={
                        "INSTAGRAM_BACKFILL_START_AT": "2026-05-01T00:00:00Z",
                        "INSTAGRAM_BACKFILL_END_AT": "2026-05-27T00:00:00Z",
                    },
                    project_root=project_root,
                    argv=["--dry-run"],
                )

            output = stdout.getvalue()

        self.assertEqual(exit_code, 0)
        self.assertIn("Instagram local pipeline dry run", output)
        self.assertIn("provider=instagram", output)
        self.assertIn("credentials_configured=no", output)
        self.assertIn("interval_start_at=2026-05-01T00:00:00+00:00", output)
        self.assertIn(
            "planned_processed_path=data/processed/instagram/"
            "instagram-20260501T000000-20260527T000000.json",
            output,
        )
        self.assertFalse((project_root / "data").exists())

    def test_main_dry_run_accepts_cli_interval(self) -> None:
        with TemporaryDirectory() as tmpdir:
            stdout = StringIO()

            with redirect_stdout(stdout):
                exit_code = main(
                    env={
                        "INSTAGRAM_BACKFILL_START_AT": "2026-04-01T00:00:00Z",
                        "INSTAGRAM_BACKFILL_END_AT": "2026-04-30T00:00:00Z",
                    },
                    project_root=Path(tmpdir),
                    argv=[
                        "--dry-run",
                        "--start-at",
                        "2026-05-01T00:00:00Z",
                        "--end-at",
                        "2026-05-27T00:00:00Z",
                    ],
                )

            output = stdout.getvalue()

        self.assertEqual(exit_code, 0)
        self.assertIn("interval_start_at=2026-05-01T00:00:00+00:00", output)
        self.assertIn("interval_end_at=2026-05-27T00:00:00+00:00", output)

    def test_parse_args_accepts_operator_options(self) -> None:
        args = parse_args(
            [
                "--dry-run",
                "--start-at",
                "2026-05-01T00:00:00Z",
                "--end-at",
                "2026-05-27T00:00:00Z",
                "--lookback-days",
                "7",
                "--fail-if-empty",
            ]
        )

        self.assertTrue(args.dry_run)
        self.assertEqual(args.start_at, "2026-05-01T00:00:00Z")
        self.assertEqual(args.end_at, "2026-05-27T00:00:00Z")
        self.assertEqual(args.lookback_days, 7)
        self.assertTrue(args.fail_if_empty)

    def test_main_dry_run_ignores_fail_if_empty_without_credentials(self) -> None:
        with TemporaryDirectory() as tmpdir:
            stdout = StringIO()

            with redirect_stdout(stdout):
                exit_code = main(
                    env={},
                    project_root=Path(tmpdir),
                    argv=["--dry-run", "--lookback-days", "1", "--fail-if-empty"],
                )

            output = stdout.getvalue()

        self.assertEqual(exit_code, 0)
        self.assertIn("Instagram local pipeline dry run", output)
        self.assertIn("credentials_configured=no", output)

    def test_enforce_instagram_loaded_records_rejects_empty_run_when_enabled(self) -> None:
        summary = InstagramLocalPipelineSummary(
            result=LocalPipelineResult(
                provider="instagram",
                raw_records=0,
                metrics=[],
                invalid_records=0,
                loaded_records=0,
            ),
            processed_path=Path("data/processed/instagram/empty.json"),
            raw_root=Path("data/raw"),
            run_summary_path=Path("data/runs/instagram/empty.json"),
        )

        with self.assertRaisesRegex(RuntimeError, "loaded 0 records"):
            enforce_instagram_loaded_records(summary, fail_if_empty=True)

    def test_enforce_instagram_loaded_records_keeps_default_empty_run_allowed(self) -> None:
        summary = InstagramLocalPipelineSummary(
            result=LocalPipelineResult(
                provider="instagram",
                raw_records=0,
                metrics=[],
                invalid_records=0,
                loaded_records=0,
            ),
            processed_path=Path("data/processed/instagram/empty.json"),
            raw_root=Path("data/raw"),
            run_summary_path=Path("data/runs/instagram/empty.json"),
        )

        enforce_instagram_loaded_records(summary, fail_if_empty=False)


if __name__ == "__main__":
    unittest.main()
