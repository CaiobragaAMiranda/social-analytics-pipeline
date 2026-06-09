import argparse
import json
import os
import sys
from dataclasses import dataclass
from pathlib import Path
from typing import Any


@dataclass(frozen=True)
class YouTubeReportSummary:
    artifact_path: Path
    records: int
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
    rows = load_youtube_report_rows(artifact_path)
    top_rows = sorted(rows, key=lambda row: _metric_value(row, "views"), reverse=True)[:5]
    top_row = top_rows[0] if top_rows else None

    return YouTubeReportSummary(
        artifact_path=artifact_path,
        records=len(rows),
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
        "",
        "## Top Content by Views",
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


def main(
    project_root: Path | None = None,
    artifact_path: Path | None = None,
    output_path: Path | None = None,
) -> int:
    root = project_root or Path.cwd()
    target = artifact_path or find_latest_youtube_processed_artifact(root)
    summary = build_youtube_report_summary(target)
    report_path = write_youtube_report_markdown(summary, root, output_path)

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
    print(f"report_path={_display_path(report_path, root)}")
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
    return parser.parse_args(argv)


def _metric_value(row: dict[str, Any] | None, field: str) -> int:
    if not row:
        return 0
    value = row.get(field, 0)
    if isinstance(value, int):
        return value
    return 0


def _display_path(path: Path, project_root: Path) -> str:
    try:
        return path.relative_to(project_root).as_posix()
    except ValueError:
        try:
            return Path(os.path.relpath(path, project_root)).as_posix()
        except ValueError:
            return path.as_posix()


if __name__ == "__main__":
    try:
        args = parse_args()
        raise SystemExit(main(artifact_path=args.artifact, output_path=args.output))
    except RuntimeError as exc:
        print(f"Error: {exc}", file=sys.stderr)
        raise SystemExit(1) from None
