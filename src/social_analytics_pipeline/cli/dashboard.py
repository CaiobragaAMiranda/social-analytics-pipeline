import argparse
import html
import json
from pathlib import Path
from typing import Any

DEFAULT_DASHBOARD_OUTPUT = Path("data/dashboard/index.html")
DEFAULT_REPORT_JSON_DIR = Path("data/reports/youtube-json")


def find_latest_report_json(project_root: Path) -> Path:
    report_dir = project_root / DEFAULT_REPORT_JSON_DIR
    reports = sorted(report_dir.glob("*.json"))
    if not reports:
        raise RuntimeError("No report JSON artifacts found. Generate a report JSON first.")
    return reports[-1]


def load_report_payload(report_json_path: Path) -> dict[str, Any]:
    payload = json.loads(report_json_path.read_text(encoding="utf-8"))
    if not isinstance(payload, dict):
        raise RuntimeError("Dashboard report JSON must contain an object.")
    return payload


def build_dashboard_html(payload: dict[str, Any]) -> str:
    source = payload.get("source", {})
    totals = payload.get("totals", {})
    data_quality = payload.get("data_quality", {})
    top_content = payload.get("top_content", {})
    rows = payload.get("top_rows", [])
    if not isinstance(rows, list):
        rows = []

    provider = _text(source.get("provider", "unknown"))
    generated_at = _text(payload.get("generated_at", "unknown"))
    source_image = _source_image(source)
    body_rows = "\n".join(_table_row(row) for row in rows) or (
        "<tr><td>&lt;none&gt;</td><td>0</td><td>0</td><td>0</td><td>0</td></tr>"
    )

    return f"""<!doctype html>
<html lang="en">
<head>
  <meta charset="utf-8">
  <meta name="viewport" content="width=device-width, initial-scale=1">
  <title>Social Analytics Dashboard</title>
  <style>
    * {{ box-sizing: border-box; }}
    body {{
      background: #f6f7f9;
      color: #17202a;
      font-family: Arial, sans-serif;
      margin: 0;
    }}
    main {{ max-width: 1120px; margin: 0 auto; padding: 2rem; }}
    .dashboard-shell {{ display: grid; gap: 1.25rem; }}
    header {{
      align-items: center;
      background: #ffffff;
      border: 1px solid #d9dee7;
      border-radius: 8px;
      display: flex;
      gap: 1rem;
      padding: 1.25rem;
    }}
    .channel-image {{
      border: 1px solid #ccd3df;
      border-radius: 50%;
      flex: 0 0 auto;
      height: 72px;
      object-fit: cover;
      width: 72px;
    }}
    .channel-fallback {{
      align-items: center;
      background: #243447;
      color: #fff;
      display: flex;
      font-size: 1.8rem;
      font-weight: bold;
      justify-content: center;
    }}
    .title-block {{ min-width: 0; }}
    h1 {{ font-size: 1.7rem; line-height: 1.2; margin: 0 0 0.35rem; }}
    h2 {{ font-size: 1rem; margin: 0; }}
    .meta {{ color: #5f6f82; line-height: 1.45; margin: 0; overflow-wrap: anywhere; }}
    .provider-pill {{
      background: #e8f3ef;
      border: 1px solid #bad8cd;
      border-radius: 999px;
      color: #17634d;
      display: inline-block;
      font-size: 0.78rem;
      font-weight: bold;
      margin-bottom: 0.45rem;
      padding: 0.22rem 0.55rem;
      text-transform: uppercase;
    }}
    .cards {{ display: grid; gap: 1rem; grid-template-columns: repeat(4, minmax(0, 1fr)); }}
    .card {{
      background: #ffffff;
      border: 1px solid #d9dee7;
      border-radius: 8px;
      min-width: 0;
      padding: 1rem;
    }}
    .card:nth-child(1) {{ border-top: 4px solid #2f6fed; }}
    .card:nth-child(2) {{ border-top: 4px solid #15a085; }}
    .card:nth-child(3) {{ border-top: 4px solid #d68910; }}
    .card:nth-child(4) {{ border-top: 4px solid #8e5bbf; }}
    .label {{ color: #5f6f82; font-size: 0.78rem; font-weight: bold; text-transform: uppercase; }}
    .value {{
      font-size: 1.55rem;
      font-weight: bold;
      line-height: 1.2;
      margin-top: 0.45rem;
      overflow-wrap: anywhere;
    }}
    .section {{
      background: #ffffff;
      border: 1px solid #d9dee7;
      border-radius: 8px;
      padding: 1rem;
    }}
    .section-header {{
      align-items: center;
      display: flex;
      justify-content: space-between;
      gap: 1rem;
      margin-bottom: 0.85rem;
    }}
    .status-pill {{
      background: #edf6ee;
      border: 1px solid #c8e4cc;
      border-radius: 999px;
      color: #25662d;
      font-size: 0.82rem;
      font-weight: bold;
      padding: 0.28rem 0.6rem;
    }}
    .quality-grid {{
      display: grid;
      gap: 0.75rem;
      grid-template-columns: repeat(2, minmax(0, 1fr));
    }}
    .quality-item {{ border-left: 3px solid #15a085; padding-left: 0.75rem; }}
    .quality-item strong {{ display: block; margin-top: 0.2rem; }}
    .table-wrap {{ overflow-x: auto; }}
    table {{ border-collapse: collapse; min-width: 680px; width: 100%; }}
    th, td {{ border-bottom: 1px solid #d9dee7; padding: 0.72rem; text-align: left; }}
    th {{ background: #f0f3f7; color: #344256; font-size: 0.78rem; text-transform: uppercase; }}
    tr:last-child td {{ border-bottom: 0; }}
    @media (max-width: 820px) {{
      main {{ padding: 1rem; }}
      .cards {{ grid-template-columns: repeat(2, minmax(0, 1fr)); }}
      header {{ align-items: flex-start; }}
    }}
    @media (max-width: 540px) {{
      .cards, .quality-grid {{ grid-template-columns: 1fr; }}
      header {{ flex-direction: column; }}
      .channel-image {{ height: 64px; width: 64px; }}
    }}
  </style>
</head>
<body>
  <main class="dashboard-shell">
    <header>
      {source_image}
      <div class="title-block">
        <span class="provider-pill">{provider}</span>
        <h1>Social Analytics Dashboard</h1>
        <p class="meta">Generated: {generated_at}</p>
      </div>
    </header>
    <section class="cards">
      {_card("Records", payload.get("records", 0))}
      {_card("Views", totals.get("views", 0))}
      {_card("Engagements", totals.get("engagements", 0))}
      {_card("Engagement Rate", f"{_number(totals.get('engagement_rate_percent', 0.0)):.2f}%")}
    </section>
    <section class="section">
      <div class="section-header">
        <h2>Data Quality</h2>
        <span class="status-pill">{_text(data_quality.get("status", "unknown"))}</span>
      </div>
      <div class="quality-grid">
        <div class="quality-item">
          <span class="label">Has engagements</span>
          <strong>{_yes_no(data_quality.get("has_engagements", False))}</strong>
        </div>
        <div class="quality-item">
          <span class="label">Top item</span>
          <strong>{_text(top_content.get("content_id", "<none>"))}</strong>
        </div>
      </div>
    </section>
    <section class="section">
      <div class="section-header">
        <h2>Top Content</h2>
      </div>
      <div class="table-wrap">
        <table>
          <thead>
            <tr><th>Content ID</th><th>Views</th><th>Likes</th><th>Comments</th><th>Shares</th></tr>
          </thead>
          <tbody>
            {body_rows}
          </tbody>
        </table>
      </div>
    </section>
  </main>
</body>
</html>
"""


def write_dashboard_html(payload: dict[str, Any], output_path: Path) -> Path:
    output_path.parent.mkdir(parents=True, exist_ok=True)
    output_path.write_text(build_dashboard_html(payload), encoding="utf-8")
    return output_path


def main(
    report_json_path: Path | None = None,
    output_path: Path = DEFAULT_DASHBOARD_OUTPUT,
    project_root: Path | None = None,
) -> int:
    root = project_root or Path.cwd()
    target_report = report_json_path or find_latest_report_json(root)
    payload = load_report_payload(target_report)
    dashboard_path = write_dashboard_html(payload, output_path)
    print(f"report_json_path={target_report.as_posix()}")
    print(f"dashboard_path={dashboard_path.as_posix()}")
    return 0


def parse_args(argv: list[str] | None = None) -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Build a local static dashboard from report JSON artifacts."
    )
    parser.add_argument(
        "--report-json",
        type=Path,
        help="Report JSON artifact to render. Defaults to the latest local YouTube report JSON.",
    )
    parser.add_argument(
        "--output",
        default=DEFAULT_DASHBOARD_OUTPUT,
        type=Path,
        help="Dashboard HTML output path.",
    )
    parser.add_argument(
        "--project-root",
        type=Path,
        help=(
            "Project root used to discover the latest report JSON. "
            "Defaults to the current directory."
        ),
    )
    return parser.parse_args(argv)


def cli_entrypoint() -> int:
    args = parse_args()
    return main(args.report_json, args.output, args.project_root)


def _card(label: str, value: object) -> str:
    return (
        '<article class="card">'
        f'<div class="label">{_text(label)}</div>'
        f'<div class="value">{_text(value)}</div>'
        "</article>"
    )


def _table_row(row: object) -> str:
    if not isinstance(row, dict):
        row = {}
    return (
        "<tr>"
        f"<td>{_text(row.get('content_id', '<none>'))}</td>"
        f"<td>{_text(row.get('views', 0))}</td>"
        f"<td>{_text(row.get('likes', 0))}</td>"
        f"<td>{_text(row.get('comments', 0))}</td>"
        f"<td>{_text(row.get('shares', 0))}</td>"
        "</tr>"
    )


def _source_image(source: object) -> str:
    if not isinstance(source, dict):
        source = {}
    image_url = source.get("image_url") or source.get("channel_image_url")
    provider = str(source.get("provider", "?"))
    if image_url:
        return (
            f'<img class="channel-image" src="{_text(image_url)}" '
            f'alt="{_text(provider)} channel image">'
        )
    initial = _text(provider[:1].upper() if provider else "?")
    return f'<div class="channel-image channel-fallback" aria-label="Channel image">{initial}</div>'


def _text(value: object) -> str:
    return html.escape(str(value), quote=True)


def _number(value: object) -> float:
    if isinstance(value, int | float):
        return float(value)
    return 0.0


def _yes_no(value: object) -> str:
    return "yes" if value is True else "no"


if __name__ == "__main__":
    raise SystemExit(cli_entrypoint())
