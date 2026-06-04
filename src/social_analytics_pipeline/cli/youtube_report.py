import json
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
    top_row = max(rows, key=lambda row: _metric_value(row, "views"), default=None)

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
    )


def main(project_root: Path | None = None, artifact_path: Path | None = None) -> int:
    root = project_root or Path.cwd()
    target = artifact_path or find_latest_youtube_processed_artifact(root)
    summary = build_youtube_report_summary(target)

    print("YouTube report summary")
    print(f"artifact_path={summary.artifact_path.relative_to(root).as_posix()}")
    print(f"records={summary.records}")
    print(f"total_views={summary.total_views}")
    print(f"total_likes={summary.total_likes}")
    print(f"total_comments={summary.total_comments}")
    print(f"total_shares={summary.total_shares}")
    print(f"max_followers={summary.max_followers}")
    print(f"top_content_id={summary.top_content_id or '<none>'}")
    print(f"top_views={summary.top_views}")
    return 0


def _metric_value(row: dict[str, Any] | None, field: str) -> int:
    if not row:
        return 0
    value = row.get(field, 0)
    if isinstance(value, int):
        return value
    return 0


if __name__ == "__main__":
    try:
        raise SystemExit(main())
    except RuntimeError as exc:
        print(f"Error: {exc}", file=sys.stderr)
        raise SystemExit(1) from None
