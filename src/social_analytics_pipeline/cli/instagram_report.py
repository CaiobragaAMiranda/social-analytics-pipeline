import argparse
import json
import sys
from dataclasses import dataclass
from datetime import UTC, datetime
from pathlib import Path
from typing import Any

DEFAULT_TOP_LIMIT = 5
DEFAULT_SORT_BY = "views"
DEFAULT_JSON_INDENT = 2
INSTAGRAM_REPORT_SCHEMA_VERSION = 1
SORTABLE_METRICS = ("views", "likes", "comments", "shares")


@dataclass(frozen=True)
class InstagramReportSummary:
    artifact_path: Path
    records: int
    sort_by: str
    top_limit: int
    total_views: int
    average_views_per_record: float
    total_likes: int
    average_likes_per_record: float
    total_comments: int
    average_comments_per_record: float
    total_shares: int
    average_shares_per_record: float
    total_engagements: int
    average_engagements_per_record: float
    engagement_rate: float
    max_followers: int
    has_followers: bool
    top_content_id: str | None
    top_views: int
    top_metric_value: int
    top_rows: list[dict[str, Any]]


def list_instagram_processed_artifacts(project_root: Path) -> list[Path]:
    artifact_dir = project_root / "data" / "processed" / "instagram"
    return sorted(artifact_dir.glob("instagram-*.json"))


def build_instagram_artifact_listing(project_root: Path) -> list[str]:
    return [
        _display_path(path, project_root)
        for path in list_instagram_processed_artifacts(project_root)
    ]


def build_latest_instagram_artifact_listing(project_root: Path) -> str:
    return _display_path(find_latest_instagram_processed_artifact(project_root), project_root)


def count_instagram_processed_artifacts(project_root: Path) -> int:
    return len(list_instagram_processed_artifacts(project_root))


def find_latest_instagram_processed_artifact(project_root: Path) -> Path:
    artifacts = list_instagram_processed_artifacts(project_root)
    if not artifacts:
        raise RuntimeError(
            "No processed Instagram artifacts found. Run the local Instagram pipeline first."
        )
    return artifacts[-1]


def load_instagram_report_rows(artifact_path: Path) -> list[dict[str, Any]]:
    rows = json.loads(artifact_path.read_text(encoding="utf-8"))
    if not isinstance(rows, list):
        raise RuntimeError("Processed Instagram artifact must contain a JSON list.")
    return rows


def build_instagram_report_summary(
    artifact_path: Path,
    top_limit: int = DEFAULT_TOP_LIMIT,
    sort_by: str = DEFAULT_SORT_BY,
) -> InstagramReportSummary:
    if top_limit < 1:
        raise RuntimeError("top_limit must be greater than or equal to 1.")
    if sort_by not in SORTABLE_METRICS:
        allowed = ", ".join(SORTABLE_METRICS)
        raise RuntimeError(f"sort_by must be one of: {allowed}.")

    rows = load_instagram_report_rows(artifact_path)
    top_rows = sorted(rows, key=lambda row: _metric_value(row, sort_by), reverse=True)[
        :top_limit
    ]
    top_row = top_rows[0] if top_rows else None
    total_likes = sum(_metric_value(row, "likes") for row in rows)
    total_comments = sum(_metric_value(row, "comments") for row in rows)
    total_shares = sum(_metric_value(row, "shares") for row in rows)
    total_views = sum(_metric_value(row, "views") for row in rows)
    total_engagements = total_likes + total_comments + total_shares

    return InstagramReportSummary(
        artifact_path=artifact_path,
        records=len(rows),
        sort_by=sort_by,
        top_limit=top_limit,
        total_views=total_views,
        average_views_per_record=_rate(total_views, len(rows)),
        total_likes=total_likes,
        average_likes_per_record=_rate(total_likes, len(rows)),
        total_comments=total_comments,
        average_comments_per_record=_rate(total_comments, len(rows)),
        total_shares=total_shares,
        average_shares_per_record=_rate(total_shares, len(rows)),
        total_engagements=total_engagements,
        average_engagements_per_record=_rate(total_engagements, len(rows)),
        engagement_rate=_rate(total_engagements, total_views),
        max_followers=max((_metric_value(row, "followers") for row in rows), default=0),
        has_followers=any(row.get("followers") is not None for row in rows),
        top_content_id=top_row.get("content_id") if top_row else None,
        top_views=_metric_value(top_row, "views") if top_row else 0,
        top_metric_value=_metric_value(top_row, sort_by) if top_row else 0,
        top_rows=top_rows,
    )


def build_instagram_report_json_output_path(project_root: Path, artifact_path: Path) -> Path:
    return project_root / "data" / "reports" / "instagram-json" / f"{artifact_path.stem}.json"


def resolve_instagram_report_json_output_path(
    project_root: Path,
    artifact_path: Path,
    output_path: Path | None,
    output_dir: Path | None,
) -> Path:
    if output_path and output_dir:
        raise RuntimeError("--json-output and --json-output-dir cannot be used together.")
    if output_path:
        return output_path
    if output_dir:
        return output_dir / f"{artifact_path.stem}.json"
    return build_instagram_report_json_output_path(project_root, artifact_path)


def build_instagram_report_json_payload(
    summary: InstagramReportSummary,
    project_root: Path,
    generated_at: str | None = None,
) -> dict[str, Any]:
    artifact = _display_path(summary.artifact_path, project_root)
    all_rows = load_instagram_report_rows(summary.artifact_path)
    top_row = summary.top_rows[0] if summary.top_rows else None
    return {
        "report_schema_version": INSTAGRAM_REPORT_SCHEMA_VERSION,
        "generated_at": generated_at or _utc_now_iso(),
        "artifact": artifact,
        "source": {
            "provider": "instagram",
            "artifact": artifact,
            "channel_name": _channel_name(top_row),
            "channel_image_url": _channel_image_url(top_row),
        },
        "records": summary.records,
        "sort_by": summary.sort_by,
        "ranking": {
            "metric": summary.sort_by,
            "limit": summary.top_limit,
        },
        "data_quality": {
            "has_engagements": summary.total_engagements > 0,
            "has_followers": summary.has_followers,
            "has_records": summary.records > 0,
            "has_top_content": summary.top_content_id is not None,
            "is_partial": False,
            "status": _data_quality_status(summary),
            "top_rows_count": len(summary.top_rows),
        },
        "totals": {
            "views": summary.total_views,
            "average_views_per_record": summary.average_views_per_record,
            "likes": summary.total_likes,
            "average_likes_per_record": summary.average_likes_per_record,
            "comments": summary.total_comments,
            "average_comments_per_record": summary.average_comments_per_record,
            "shares": summary.total_shares,
            "average_shares_per_record": summary.average_shares_per_record,
            "engagements": summary.total_engagements,
            "average_engagements_per_record": summary.average_engagements_per_record,
            "engagement_rate": summary.engagement_rate,
            "engagement_rate_percent": _percent(summary.engagement_rate),
            "max_followers": summary.max_followers,
        },
        "engagement_breakdown": {
            "likes_percent": _percent(_rate(summary.total_likes, summary.total_engagements)),
            "comments_percent": _percent(
                _rate(summary.total_comments, summary.total_engagements)
            ),
            "shares_percent": _percent(_rate(summary.total_shares, summary.total_engagements)),
        },
        "top_content": {
            "content_id": summary.top_content_id,
            "title": _content_title(top_row) if top_row else None,
            "thumbnail_url": _content_thumbnail_url(top_row) if top_row else None,
            "content_url": _content_url(top_row) if top_row else None,
            "content_type": _content_type(top_row) if top_row else None,
            "published_at": top_row.get("published_at") if top_row else None,
            "views": summary.top_views,
            "metric": summary.sort_by,
            "metric_value": summary.top_metric_value,
        },
        "production_dates": _production_dates(summary.top_rows, all_rows),
        "top_rows": [_report_row(row) for row in summary.top_rows],
    }


def build_instagram_report_json_text(
    summary: InstagramReportSummary,
    project_root: Path,
    indent: int = DEFAULT_JSON_INDENT,
    generated_at: str | None = None,
) -> str:
    json_indent = None if indent == 0 else indent
    return (
        json.dumps(
            build_instagram_report_json_payload(summary, project_root, generated_at),
            indent=json_indent,
            sort_keys=True,
        )
        + "\n"
    )


def write_instagram_report_json(
    summary: InstagramReportSummary,
    project_root: Path,
    output_path: Path | None = None,
    indent: int = DEFAULT_JSON_INDENT,
    generated_at: str | None = None,
) -> Path:
    target = output_path or build_instagram_report_json_output_path(
        project_root,
        summary.artifact_path,
    )
    target.parent.mkdir(parents=True, exist_ok=True)
    target.write_text(
        build_instagram_report_json_text(summary, project_root, indent, generated_at),
        encoding="utf-8",
    )
    return target


def main(
    project_root: Path | None = None,
    artifact_path: Path | None = None,
    json_output_path: Path | None = None,
    json_output_dir: Path | None = None,
    json_indent: int = DEFAULT_JSON_INDENT,
    quiet: bool = False,
    print_json: bool = False,
    top_limit: int = DEFAULT_TOP_LIMIT,
    sort_by: str = DEFAULT_SORT_BY,
    fail_if_empty: bool = False,
    dry_run: bool = False,
    list_artifacts: bool = False,
    latest_artifact: bool = False,
    count_artifacts: bool = False,
    fail_if_missing: bool = False,
) -> int:
    root = project_root or Path.cwd()

    if count_artifacts:
        artifact_count = count_instagram_processed_artifacts(root)
        print(artifact_count)
        return 1 if fail_if_missing and artifact_count == 0 else 0

    if latest_artifact:
        print(build_latest_instagram_artifact_listing(root))
        return 0

    if list_artifacts:
        artifacts = build_instagram_artifact_listing(root)
        if not artifacts:
            print("No processed Instagram artifacts found.")
            return 1 if fail_if_missing else 0

        for artifact in artifacts:
            print(artifact)
        return 0

    target = artifact_path or find_latest_instagram_processed_artifact(root)
    summary = build_instagram_report_summary(target, top_limit, sort_by)
    if fail_if_empty and summary.records < 1:
        if not quiet:
            print("Selected Instagram artifact has 0 records; required at least 1.")
        return 1

    planned_report_path = resolve_instagram_report_json_output_path(
        root,
        target,
        json_output_path,
        json_output_dir,
    )
    if dry_run:
        if not quiet:
            print("Instagram report dry run")
            print(f"artifact_path={_display_path(summary.artifact_path, root)}")
            print(f"records={summary.records}")
            print(f"sort_by={summary.sort_by}")
            print(f"json_output_path={_display_path(planned_report_path, root)}")
        return 0

    report_path = write_instagram_report_json(
        summary,
        root,
        planned_report_path,
        indent=json_indent,
    )
    if not quiet:
        print("Instagram report summary")
        print(f"artifact_path={_display_path(summary.artifact_path, root)}")
        print(f"records={summary.records}")
        print(f"total_views={summary.total_views}")
        print(f"total_engagements={summary.total_engagements}")
        print(f"engagement_rate={summary.engagement_rate}")
        print(f"top_content_id={summary.top_content_id or '<none>'}")
        print(f"sort_by={summary.sort_by}")
        print(f"json_report_path={_display_path(report_path, root)}")
    if print_json:
        print(build_instagram_report_json_text(summary, root, json_indent), end="")
    return 0


def parse_args(argv: list[str] | None = None) -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Build a local Instagram report JSON from processed metrics artifacts."
    )
    parser.add_argument(
        "--artifact",
        type=Path,
        help="Processed Instagram JSON artifact to report. Defaults to the latest artifact.",
    )
    parser.add_argument(
        "--json-output",
        type=Path,
        help="JSON summary output path. Defaults to data/reports/instagram-json/<artifact>.json.",
    )
    parser.add_argument(
        "--json-output-dir",
        type=Path,
        help="JSON summary output directory while preserving the selected artifact file name.",
    )
    parser.add_argument(
        "--json-indent",
        type=_non_negative_int("--json-indent"),
        default=DEFAULT_JSON_INDENT,
        help=(
            "JSON summary indentation. Use 0 for compact output. "
            f"Defaults to {DEFAULT_JSON_INDENT}."
        ),
    )
    parser.add_argument("--quiet", action="store_true", help="Suppress summary output.")
    parser.add_argument("--print-json", action="store_true", help="Print JSON to stdout.")
    parser.add_argument(
        "--dry-run",
        action="store_true",
        help="Validate selected inputs and show planned report output without writing files.",
    )
    parser.add_argument(
        "--fail-if-empty",
        action="store_true",
        help="Exit with failure when the selected artifact has no records.",
    )
    list_group = parser.add_mutually_exclusive_group()
    list_group.add_argument(
        "--list-artifacts",
        action="store_true",
        help="List processed Instagram artifacts without writing a report.",
    )
    list_group.add_argument(
        "--latest-artifact",
        action="store_true",
        help="Print the latest processed Instagram artifact path without writing a report.",
    )
    list_group.add_argument(
        "--count-artifacts",
        action="store_true",
        help="Print the processed Instagram artifact count without writing a report.",
    )
    parser.add_argument(
        "--fail-if-missing",
        action="store_true",
        help="Exit with failure in list-only modes when no processed artifacts exist.",
    )
    parser.add_argument(
        "--top",
        type=_positive_int,
        default=DEFAULT_TOP_LIMIT,
        help=f"Number of top content rows to include. Defaults to {DEFAULT_TOP_LIMIT}.",
    )
    parser.add_argument(
        "--sort-by",
        choices=SORTABLE_METRICS,
        default=DEFAULT_SORT_BY,
        help=f"Metric used for top-content ranking. Defaults to {DEFAULT_SORT_BY}.",
    )
    return parser.parse_args(argv)


def cli_entrypoint() -> int:
    try:
        args = parse_args()
        return main(
            artifact_path=args.artifact,
            json_output_path=args.json_output,
            json_output_dir=args.json_output_dir,
            json_indent=args.json_indent,
            quiet=args.quiet,
            print_json=args.print_json,
            top_limit=args.top,
            sort_by=args.sort_by,
            fail_if_empty=args.fail_if_empty,
            dry_run=args.dry_run,
            list_artifacts=args.list_artifacts,
            latest_artifact=args.latest_artifact,
            count_artifacts=args.count_artifacts,
            fail_if_missing=args.fail_if_missing,
        )
    except RuntimeError as exc:
        print(f"Error: {exc}", file=sys.stderr)
        return 1


def _metric_value(row: dict[str, Any] | None, field: str) -> int:
    if not row:
        return 0
    value = row.get(field, 0)
    if isinstance(value, int):
        return value
    return 0


def _report_row(row: dict[str, Any]) -> dict[str, Any]:
    return {
        "content_id": row.get("content_id", "<none>"),
        "title": _content_title(row),
        "thumbnail_url": _content_thumbnail_url(row),
        "content_url": _content_url(row),
        "content_type": _content_type(row),
        "channel_name": _channel_name(row),
        "channel_image_url": _channel_image_url(row),
        "published_at": row.get("published_at"),
        "views": _metric_value(row, "views"),
        "likes": _metric_value(row, "likes"),
        "comments": _metric_value(row, "comments"),
        "shares": _metric_value(row, "shares"),
        "followers": _metric_value(row, "followers"),
    }


def _production_dates(
    top_rows: list[dict[str, Any]],
    all_rows: list[dict[str, Any]],
) -> list[str]:
    rows = all_rows or top_rows
    return [
        str(row["published_at"])
        for row in rows
        if isinstance(row, dict) and row.get("published_at")
    ]


def _content_title(row: dict[str, Any] | None) -> str | None:
    if not row:
        return None
    for key in ("title", "content_title", "name", "caption"):
        value = row.get(key)
        if value not in (None, ""):
            return str(value)
    content_id = row.get("content_id")
    return str(content_id) if content_id not in (None, "", "<none>") else None


def _content_thumbnail_url(row: dict[str, Any] | None) -> str | None:
    if not row:
        return None
    for key in ("thumbnail_url", "image_url", "media_url", "picture_url"):
        value = row.get(key)
        if value not in (None, ""):
            return str(value)
    return None


def _content_url(row: dict[str, Any] | None) -> str | None:
    if not row:
        return None
    for key in ("content_url", "url", "permalink"):
        value = row.get(key)
        if value not in (None, ""):
            return str(value)
    return None


def _content_type(row: dict[str, Any] | None) -> str:
    if not row:
        return "post"
    value = row.get("content_type") or row.get("type")
    return str(value) if value not in (None, "") else "post"


def _channel_name(row: dict[str, Any] | None) -> str | None:
    if not row:
        return None
    value = row.get("channel_name")
    return str(value) if value not in (None, "") else None


def _channel_image_url(row: dict[str, Any] | None) -> str | None:
    if not row:
        return None
    value = row.get("channel_image_url")
    return str(value) if value not in (None, "") else None


def _rate(numerator: int, denominator: int) -> float:
    if denominator == 0:
        return 0.0
    return numerator / denominator


def _percent(value: float) -> float:
    return value * 100


def _data_quality_status(summary: InstagramReportSummary) -> str:
    return "ok" if summary.records > 0 else "empty"


def _display_path(path: Path, project_root: Path) -> str:
    try:
        return path.relative_to(project_root).as_posix()
    except ValueError:
        return path.as_posix()


def _utc_now_iso() -> str:
    return datetime.now(UTC).isoformat().replace("+00:00", "Z")


def _positive_int(value: str) -> int:
    try:
        parsed = int(value)
    except ValueError as exc:
        raise argparse.ArgumentTypeError("--top must be greater than or equal to 1.") from exc
    if parsed < 1:
        raise argparse.ArgumentTypeError("--top must be greater than or equal to 1.")
    return parsed


def _non_negative_int(option_name: str) -> Any:
    def parse(value: str) -> int:
        try:
            parsed = int(value)
        except ValueError as exc:
            raise argparse.ArgumentTypeError(
                f"{option_name} must be greater than or equal to 0."
            ) from exc
        if parsed < 0:
            raise argparse.ArgumentTypeError(
                f"{option_name} must be greater than or equal to 0."
            )
        return parsed

    return parse


if __name__ == "__main__":
    raise SystemExit(cli_entrypoint())
