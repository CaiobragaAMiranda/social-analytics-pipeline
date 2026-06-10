import argparse
import json
import os
import sys
from dataclasses import dataclass
from pathlib import Path
from typing import Any

DEFAULT_TOP_LIMIT = 5
DEFAULT_SORT_BY = "views"
DEFAULT_JSON_INDENT = 2
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
    total_engagements: int
    max_followers: int
    top_content_id: str | None
    top_views: int
    top_metric_value: int
    top_rows: list[dict[str, Any]]


def list_youtube_processed_artifacts(project_root: Path) -> list[Path]:
    artifact_dir = project_root / "data" / "processed" / "youtube"
    return sorted(artifact_dir.glob("youtube-*.json"))


def build_youtube_artifact_listing(project_root: Path) -> list[str]:
    return [
        _display_path(path, project_root)
        for path in list_youtube_processed_artifacts(project_root)
    ]


def build_latest_youtube_artifact_listing(project_root: Path) -> str:
    return _display_path(find_latest_youtube_processed_artifact(project_root), project_root)


def count_youtube_processed_artifacts(project_root: Path) -> int:
    return len(list_youtube_processed_artifacts(project_root))


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
    total_likes = sum(_metric_value(row, "likes") for row in rows)
    total_comments = sum(_metric_value(row, "comments") for row in rows)
    total_shares = sum(_metric_value(row, "shares") for row in rows)

    return YouTubeReportSummary(
        artifact_path=artifact_path,
        records=len(rows),
        sort_by=sort_by,
        total_views=sum(_metric_value(row, "views") for row in rows),
        total_likes=total_likes,
        total_comments=total_comments,
        total_shares=total_shares,
        total_engagements=total_likes + total_comments + total_shares,
        max_followers=max((_metric_value(row, "followers") for row in rows), default=0),
        top_content_id=top_row.get("content_id") if top_row else None,
        top_views=_metric_value(top_row, "views") if top_row else 0,
        top_metric_value=_metric_value(top_row, sort_by) if top_row else 0,
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
        f"- Total engagements: `{summary.total_engagements}`",
        f"- Max followers: `{summary.max_followers}`",
        f"- Top content: `{summary.top_content_id or '<none>'}`",
        f"- Top views: `{summary.top_views}`",
        f"- Ranking metric: `{summary.sort_by}`",
        f"- Top {_metric_label(summary.sort_by).lower()}: `{summary.top_metric_value}`",
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


def build_youtube_report_output_path_in_dir(output_dir: Path, artifact_path: Path) -> Path:
    return output_dir / f"{artifact_path.stem}.md"


def resolve_youtube_report_markdown_output_path(
    project_root: Path,
    artifact_path: Path,
    output_path: Path | None = None,
    output_dir: Path | None = None,
) -> Path:
    if output_dir:
        return build_youtube_report_output_path_in_dir(output_dir, artifact_path)
    return output_path or build_youtube_report_output_path(project_root, artifact_path)


def build_youtube_report_json_output_path_in_dir(
    output_dir: Path,
    artifact_path: Path,
) -> Path:
    return output_dir / f"{artifact_path.stem}.json"


def resolve_youtube_report_json_output_path(
    artifact_path: Path,
    json_output_path: Path | None = None,
    json_output_dir: Path | None = None,
) -> Path | None:
    if json_output_dir:
        return build_youtube_report_json_output_path_in_dir(json_output_dir, artifact_path)
    return json_output_path


def write_youtube_report_markdown(
    summary: YouTubeReportSummary,
    project_root: Path,
    output_path: Path | None = None,
) -> Path:
    target = resolve_youtube_report_markdown_output_path(
        project_root,
        summary.artifact_path,
        output_path,
    )
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
            "engagements": summary.total_engagements,
            "max_followers": summary.max_followers,
        },
        "top_content": {
            "content_id": summary.top_content_id,
            "views": summary.top_views,
            "metric": summary.sort_by,
            "metric_value": summary.top_metric_value,
        },
        "top_rows": [_report_row(row) for row in summary.top_rows],
    }


def build_youtube_report_json_text(
    summary: YouTubeReportSummary,
    project_root: Path,
    indent: int = DEFAULT_JSON_INDENT,
) -> str:
    json_indent = None if indent == 0 else indent
    return (
        json.dumps(
            build_youtube_report_json_payload(summary, project_root),
            indent=json_indent,
            sort_keys=True,
        )
        + "\n"
    )


def write_youtube_report_json(
    summary: YouTubeReportSummary,
    project_root: Path,
    output_path: Path,
    indent: int = DEFAULT_JSON_INDENT,
) -> Path:
    output_path.parent.mkdir(parents=True, exist_ok=True)
    output_path.write_text(
        build_youtube_report_json_text(summary, project_root, indent),
        encoding="utf-8",
    )
    return output_path


def main(
    project_root: Path | None = None,
    artifact_path: Path | None = None,
    output_path: Path | None = None,
    json_output_path: Path | None = None,
    json_output_dir: Path | None = None,
    no_markdown: bool = False,
    quiet: bool = False,
    output_dir: Path | None = None,
    json_indent: int = DEFAULT_JSON_INDENT,
    print_json: bool = False,
    dry_run: bool = False,
    fail_if_empty: bool = False,
    min_records: int = 0,
    top_limit: int = DEFAULT_TOP_LIMIT,
    sort_by: str = DEFAULT_SORT_BY,
    list_artifacts: bool = False,
    latest_artifact: bool = False,
    count_artifacts: bool = False,
    fail_if_missing: bool = False,
) -> int:
    root = project_root or Path.cwd()

    if count_artifacts:
        artifact_count = count_youtube_processed_artifacts(root)
        print(artifact_count)
        return 1 if fail_if_missing and artifact_count == 0 else 0

    if latest_artifact:
        print(build_latest_youtube_artifact_listing(root))
        return 0

    if list_artifacts:
        artifacts = build_youtube_artifact_listing(root)
        if not artifacts:
            print("No processed YouTube artifacts found.")
            return 1 if fail_if_missing else 0

        for artifact in artifacts:
            print(artifact)
        return 0

    target = artifact_path or find_latest_youtube_processed_artifact(root)
    summary = build_youtube_report_summary_with_options(target, top_limit, sort_by)
    required_records = max(min_records, 1 if fail_if_empty else 0)
    if summary.records < required_records:
        if not quiet:
            print(
                "Selected YouTube artifact has "
                f"{summary.records} records; required at least {required_records}."
            )
        return 1

    if no_markdown and not (json_output_path or json_output_dir or print_json):
        raise RuntimeError(
            "--no-markdown requires --json-output, --json-output-dir or --print-json."
        )
    if output_path and output_dir:
        raise RuntimeError("--output and --output-dir cannot be used together.")
    if json_output_path and json_output_dir:
        raise RuntimeError("--json-output and --json-output-dir cannot be used together.")

    markdown_output_path = resolve_youtube_report_markdown_output_path(
        root,
        target,
        output_path,
        output_dir,
    )
    json_report_output_path = resolve_youtube_report_json_output_path(
        target,
        json_output_path,
        json_output_dir,
    )

    if dry_run:
        if not quiet:
            json_output_display = (
                "<none>"
                if not json_report_output_path
                else _display_path(json_report_output_path, root)
            )
            print("YouTube report dry run")
            print(f"artifact_path={_display_path(summary.artifact_path, root)}")
            print(f"records={summary.records}")
            print(f"sort_by={summary.sort_by}")
            print(
                "markdown_output_path="
                f"{'<none>' if no_markdown else _display_path(markdown_output_path, root)}"
            )
            print(f"json_output_path={json_output_display}")
        return 0

    report_path = (
        None
        if no_markdown
        else write_youtube_report_markdown(summary, root, markdown_output_path)
    )
    json_report_path = (
        write_youtube_report_json(
            summary,
            root,
            json_report_output_path,
            indent=json_indent,
        )
        if json_report_output_path
        else None
    )

    if not quiet:
        print("YouTube report summary")
        print(f"artifact_path={_display_path(summary.artifact_path, root)}")
        print(f"records={summary.records}")
        print(f"total_views={summary.total_views}")
        print(f"total_likes={summary.total_likes}")
        print(f"total_comments={summary.total_comments}")
        print(f"total_shares={summary.total_shares}")
        print(f"total_engagements={summary.total_engagements}")
        print(f"max_followers={summary.max_followers}")
        print(f"top_content_id={summary.top_content_id or '<none>'}")
        print(f"top_views={summary.top_views}")
        print(f"sort_by={summary.sort_by}")
        print(f"top_metric_value={summary.top_metric_value}")
        if report_path:
            print(f"report_path={_display_path(report_path, root)}")
        if json_report_path:
            print(f"json_report_path={_display_path(json_report_path, root)}")
    if print_json:
        print(build_youtube_report_json_text(summary, root, json_indent), end="")
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
        "--output-dir",
        type=Path,
        help="Markdown output directory. Uses the artifact stem as the file name.",
    )
    parser.add_argument(
        "--json-output",
        type=Path,
        help="Optional JSON summary output path.",
    )
    parser.add_argument(
        "--json-output-dir",
        type=Path,
        help="JSON summary output directory. Uses the artifact stem as the file name.",
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
    parser.add_argument(
        "--no-markdown",
        action="store_true",
        help="Skip markdown output. Requires a JSON file destination or --print-json.",
    )
    parser.add_argument(
        "--quiet",
        action="store_true",
        help="Suppress report-generation summary output.",
    )
    parser.add_argument(
        "--print-json",
        action="store_true",
        help="Print the JSON summary payload to stdout.",
    )
    parser.add_argument(
        "--dry-run",
        action="store_true",
        help="Validate inputs and print planned report outputs without writing files.",
    )
    list_mode = parser.add_mutually_exclusive_group()
    list_mode.add_argument(
        "--list-artifacts",
        action="store_true",
        help="List processed YouTube artifacts and exit without writing reports.",
    )
    list_mode.add_argument(
        "--latest-artifact",
        action="store_true",
        help="Print the latest processed YouTube artifact and exit without writing reports.",
    )
    list_mode.add_argument(
        "--count-artifacts",
        action="store_true",
        help="Print the processed YouTube artifact count and exit without writing reports.",
    )
    parser.add_argument(
        "--fail-if-missing",
        action="store_true",
        help="Exit with failure when list-only mode finds no processed artifacts.",
    )
    parser.add_argument(
        "--fail-if-empty",
        action="store_true",
        help="Exit with failure when the selected processed artifact has no records.",
    )
    parser.add_argument(
        "--min-records",
        type=_non_negative_int("--min-records"),
        default=0,
        help="Minimum records required in the selected processed artifact.",
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
    args = parser.parse_args(argv)
    if args.no_markdown and not (
        args.json_output or args.json_output_dir or args.print_json
    ):
        parser.error(
            "--no-markdown requires --json-output, --json-output-dir or --print-json."
        )
    if args.output and args.output_dir:
        parser.error("--output and --output-dir cannot be used together.")
    if args.json_output and args.json_output_dir:
        parser.error("--json-output and --json-output-dir cannot be used together.")
    return args


def cli_entrypoint() -> int:
    try:
        args = parse_args()
        return main(
            artifact_path=args.artifact,
            output_path=args.output,
            output_dir=args.output_dir,
            json_output_path=args.json_output,
            json_output_dir=args.json_output_dir,
            no_markdown=args.no_markdown,
            quiet=args.quiet,
            top_limit=args.top,
            json_indent=args.json_indent,
            print_json=args.print_json,
            dry_run=args.dry_run,
            fail_if_empty=args.fail_if_empty,
            min_records=args.min_records,
            sort_by=args.sort_by,
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


def _non_negative_int(option_name: str) -> Any:
    def parse(value: str) -> int:
        try:
            parsed = int(value)
        except ValueError as exc:
            raise argparse.ArgumentTypeError(
                f"{option_name} must be an integer."
            ) from exc

        if parsed < 0:
            raise argparse.ArgumentTypeError(
                f"{option_name} must be greater than or equal to 0."
            )
        return parsed

    return parse


if __name__ == "__main__":
    raise SystemExit(cli_entrypoint())
