import argparse
import json
import os
import sys
from dataclasses import dataclass
from pathlib import Path
from typing import Any

DEFAULT_TOP_LIMIT = 5
DEFAULT_SORT_BY = "views"
SORTABLE_METRICS = ("views", "likes", "comments", "shares")


@dataclass(frozen=True)
class YouTubeReportSummary:
    artifact_path: Path
    records: int
    sort_by: str
    total_views: int
    total_likes: int
    total_comments: int
    total_shares: int
    max_followers: int
    top_content_id: str | None
    top_views: int
    top_rows: list[dict[str, Any]]


def list_youtube_processed_artifacts(project_root: Path) -> list[Path]:
    artifact_dir = project_root / "data" / "processed" / "youtube"
    return sorted(artifact_dir.glob("youtube-*.json"))


def build_youtube_artifact_listing(project_root: Path) -> list[str]:
    return [
        _display_path(path, project_root)
        for path in list_youtube_processed_artifacts(project_root)
    ]


def find_latest_youtube_processed_artifact(project_root: Path) -> Path:
    artifacts = list_youtube_processed_artifacts(project_root)
    if not artifacts:
        raise RuntimeError(
            "No processed YouTube artifacts found. Run the local YouTube pipeline first."
        )
    return artifacts[-1]


def load_youtube_report_rows(artifact_path: Path) -> list[dict[str, Any]]:
    rows = json.loads(artifact_path.read_text(encoding="utf-8"))
    if not isinstance(rows, list):
        raise RuntimeError("Processed YouTube artifact must contain a JSON list.")
    return rows


def build_youtube_report_summary(artifact_path: Path) -> YouTubeReportSummary:
    return build_youtube_report_summary_with_options(
        artifact_path,
        DEFAULT_TOP_LIMIT,
        DEFAULT_SORT_BY,
    )


def build_youtube_report_summary_with_limit(
    artifact_path: Path,
    top_limit: int,
) -> YouTubeReportSummary:
    return build_youtube_report_summary_with_options(artifact_path, top_limit, DEFAULT_SORT_BY)


def build_youtube_report_summary_with_options(
    artifact_path: Path,
    top_limit: int,
    sort_by: str,
) -> YouTubeReportSummary:
    if top_limit < 1:
        raise RuntimeError("top_limit must be greater than or equal to 1.")

    if sort_by not in SORTABLE_METRICS:
        allowed = ", ".join(SORTABLE_METRICS)
        raise RuntimeError(f"sort_by must be one of: {allowed}.")

    rows = load_youtube_report_rows(artifact_path)
    top_rows = sorted(rows, key=lambda row: _metric_value(row, sort_by), reverse=True)[
        :top_limit
    ]
    top_row = top_rows[0] if top_rows else None

    return YouTubeReportSummary(
        artifact_path=artifact_path,
        records=len(rows),
        sort_by=sort_by,
        total_views=sum(_metric_value(row, "views") for row in rows),
        total_likes=sum(_metric_value(row, "likes") for row in rows),
        total_comments=sum(_metric_value(row, "comments") for row in rows),
        total_shares=sum(_metric_value(row, "shares") for row in rows),
        max_followers=max((_metric_value(row, "followers") for row in rows), default=0),
        top_content_id=top_row.get("content_id") if top_row else None,
        top_views=_metric_value(top_row, "views") if top_row else 0,
        top_rows=top_rows,
    )


def build_youtube_report_markdown(summary: YouTubeReportSummary, project_root: Path) -> str:
    artifact_path = _display_path(summary.artifact_path, project_root)
    lines = [
        "# YouTube Report",
        "",
        f"- Artifact: `{artifact_path}`",
        f"- Records: `{summary.records}`",
        f"- Total views: `{summary.total_views}`",
        f"- Total likes: `{summary.total_likes}`",
        f"- Total comments: `{summary.total_comments}`",
        f"- Total shares: `{summary.total_shares}`",
        f"- Max followers: `{summary.max_followers}`",
        f"- Top content: `{summary.top_content_id or '<none>'}`",
        f"- Top views: `{summary.top_views}`",
        f"- Ranking metric: `{summary.sort_by}`",
        "",
        f"## Top Content by {_metric_label(summary.sort_by)}",
        "",
        "| Content ID | Views | Likes | Comments | Shares | Followers |",
        "| --- | ---: | ---: | ---: | ---: | ---: |",
    ]

    for row in summary.top_rows:
        lines.append(
            "| "
            f"{row.get('content_id', '<none>')} | "
            f"{_metric_value(row, 'views')} | "
            f"{_metric_value(row, 'likes')} | "
            f"{_metric_value(row, 'comments')} | "
            f"{_metric_value(row, 'shares')} | "
            f"{_metric_value(row, 'followers')} |"
        )

    if not summary.top_rows:
        lines.append("| <none> | 0 | 0 | 0 | 0 | 0 |")

    return "\n".join(lines) + "\n"


def build_youtube_report_output_path(project_root: Path, artifact_path: Path) -> Path:
    stem = artifact_path.stem
    return project_root / "data" / "reports" / "youtube" / f"{stem}.md"


def write_youtube_report_markdown(
    summary: YouTubeReportSummary,
    project_root: Path,
    output_path: Path | None = None,
) -> Path:
    target = output_path or build_youtube_report_output_path(project_root, summary.artifact_path)
    target.parent.mkdir(parents=True, exist_ok=True)
    target.write_text(
        build_youtube_report_markdown(summary, project_root),
        encoding="utf-8",
    )
    return target


def build_youtube_report_json_payload(
    summary: YouTubeReportSummary,
    project_root: Path,
) -> dict[str, Any]:
    return {
        "artifact": _display_path(summary.artifact_path, project_root),
        "records": summary.records,
        "sort_by": summary.sort_by,
        "totals": {
            "views": summary.total_views,
            "likes": summary.total_likes,
            "comments": summary.total_comments,
            "shares": summary.total_shares,
            "max_followers": summary.max_followers,
        },
        "top_content": {
            "content_id": summary.top_content_id,
            "views": summary.top_views,
        },
        "top_rows": [_report_row(row) for row in summary.top_rows],
    }


def write_youtube_report_json(
    summary: YouTubeReportSummary,
    project_root: Path,
    output_path: Path,
) -> Path:
    output_path.parent.mkdir(parents=True, exist_ok=True)
    output_path.write_text(
        json.dumps(
            build_youtube_report_json_payload(summary, project_root),
            indent=2,
            sort_keys=True,
        )
        + "\n",
        encoding="utf-8",
    )
    return output_path


def main(
    project_root: Path | None = None,
    artifact_path: Path | None = None,
    output_path: Path | None = None,
    json_output_path: Path | None = None,
    top_limit: int = DEFAULT_TOP_LIMIT,
    sort_by: str = DEFAULT_SORT_BY,
    list_artifacts: bool = False,
) -> int:
    root = project_root or Path.cwd()

    if list_artifacts:
        artifacts = build_youtube_artifact_listing(root)
        if not artifacts:
            print("No processed YouTube artifacts found.")
            return 0

        for artifact in artifacts:
            print(artifact)
        return 0

    target = artifact_path or find_latest_youtube_processed_artifact(root)
    summary = build_youtube_report_summary_with_options(target, top_limit, sort_by)
    report_path = write_youtube_report_markdown(summary, root, output_path)
    json_report_path = (
        write_youtube_report_json(summary, root, json_output_path)
        if json_output_path
        else None
    )

    print("YouTube report summary")
    print(f"artifact_path={_display_path(summary.artifact_path, root)}")
    print(f"records={summary.records}")
    print(f"total_views={summary.total_views}")
    print(f"total_likes={summary.total_likes}")
    print(f"total_comments={summary.total_comments}")
    print(f"total_shares={summary.total_shares}")
    print(f"max_followers={summary.max_followers}")
    print(f"top_content_id={summary.top_content_id or '<none>'}")
    print(f"top_views={summary.top_views}")
    print(f"sort_by={summary.sort_by}")
    print(f"report_path={_display_path(report_path, root)}")
    if json_report_path:
        print(f"json_report_path={_display_path(json_report_path, root)}")
    return 0


def parse_args(argv: list[str] | None = None) -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Build a local YouTube report from processed metrics artifacts."
    )
    parser.add_argument(
        "--artifact",
        type=Path,
        help="Processed YouTube JSON artifact to report. Defaults to the latest artifact.",
    )
    parser.add_argument(
        "--output",
        type=Path,
        help="Markdown output path. Defaults to data/reports/youtube/<artifact>.md.",
    )
    parser.add_argument(
        "--json-output",
        type=Path,
        help="Optional JSON summary output path.",
    )
    parser.add_argument(
        "--list-artifacts",
        action="store_true",
        help="List processed YouTube artifacts and exit without writing reports.",
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
        "views": _metric_value(row, "views"),
        "likes": _metric_value(row, "likes"),
        "comments": _metric_value(row, "comments"),
        "shares": _metric_value(row, "shares"),
        "followers": _metric_value(row, "followers"),
    }


def _metric_label(metric: str) -> str:
    return metric.replace("_", " ").title()


def _display_path(path: Path, project_root: Path) -> str:
    try:
        return path.relative_to(project_root).as_posix()
    except ValueError:
        try:
            return Path(os.path.relpath(path, project_root)).as_posix()
        except ValueError:
            return path.as_posix()


def _positive_int(value: str) -> int:
    try:
        parsed = int(value)
    except ValueError as exc:
        raise argparse.ArgumentTypeError("--top must be an integer.") from exc

    if parsed < 1:
        raise argparse.ArgumentTypeError("--top must be greater than or equal to 1.")
    return parsed


if __name__ == "__main__":
    try:
        args = parse_args()
        raise SystemExit(
            main(
                artifact_path=args.artifact,
                output_path=args.output,
                json_output_path=args.json_output,
                top_limit=args.top,
                sort_by=args.sort_by,
                list_artifacts=args.list_artifacts,
            )
        )
    except RuntimeError as exc:
        print(f"Error: {exc}", file=sys.stderr)
        raise SystemExit(1) from None
