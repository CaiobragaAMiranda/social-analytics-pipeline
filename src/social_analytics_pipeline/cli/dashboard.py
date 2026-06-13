import argparse
import datetime as dt
import html
import json
from pathlib import Path
from typing import Any

from social_analytics_pipeline.config import (
    ChannelIdentityConfig,
    load_channel_identity_config,
    match_channel_identity,
)

DEFAULT_DASHBOARD_OUTPUT = Path("data/dashboard/index.html")
DEFAULT_REPORT_JSON_DIR = Path("data/reports/youtube-json")


def find_latest_report_json(project_root: Path) -> Path:
    reports = find_report_json_files(project_root)
    if not reports:
        raise RuntimeError("No report JSON artifacts found. Generate a report JSON first.")
    return reports[-1]


def find_report_json_files(project_root: Path) -> list[Path]:
    report_dir = project_root / DEFAULT_REPORT_JSON_DIR
    return sorted(report_dir.glob("*.json"))


def load_report_payload(report_json_path: Path) -> dict[str, Any]:
    payload = json.loads(report_json_path.read_text(encoding="utf-8"))
    if not isinstance(payload, dict):
        raise RuntimeError("Dashboard report JSON must contain an object.")
    return payload


def load_report_payloads(report_json_paths: list[Path]) -> list[dict[str, Any]]:
    return [load_report_payload(report_json_path) for report_json_path in report_json_paths]


def build_multi_report_dashboard_payload(
    payloads: list[dict[str, Any]],
    channels_config: tuple[ChannelIdentityConfig, ...] = (),
) -> dict[str, Any]:
    grouped: dict[str, list[dict[str, Any]]] = {}
    for payload in payloads:
        payload = _apply_channel_config(payload, channels_config)
        grouped.setdefault(_channel_identity(payload), []).append(payload)

    return {
        "channels": [
            _aggregated_channel_payload(channel_payloads)
            for channel_payloads in grouped.values()
        ]
    }


def build_dashboard_html(payload: dict[str, Any]) -> str:
    channels = _dashboard_channels(payload)
    channels_json = _json_script_payload(channels)
    active = channels[0]
    source_image = _channel_image_markup(active)

    return f"""<!doctype html>
<html lang="en">
<head>
  <meta charset="utf-8">
  <meta name="viewport" content="width=device-width, initial-scale=1">
  <title>Social Analytics Dashboard</title>
  <style>
    * {{ box-sizing: border-box; }}
    body {{
      background: #1f3c46;
      color: #eef8f8;
      font-family: Arial, sans-serif;
      margin: 0;
    }}
    .dashboard-shell {{
      display: grid;
      grid-template-columns: 250px minmax(0, 1fr);
      min-height: 100vh;
    }}
    .sidebar {{
      background: #12d8bd;
      color: #14343d;
      display: flex;
      flex-direction: column;
      gap: 1.4rem;
      padding: 1.6rem;
    }}
    .brand {{
      font-size: 2rem;
      font-weight: normal;
      letter-spacing: 0;
      margin: 0;
      text-transform: uppercase;
    }}
    .channel-profile {{
      align-items: center;
      display: flex;
      gap: 0.8rem;
      margin-top: 0.5rem;
      min-width: 0;
    }}
    .channel-image {{
      border: 2px solid rgba(20, 52, 61, 0.28);
      border-radius: 50%;
      flex: 0 0 auto;
      height: 64px;
      object-fit: cover;
      width: 64px;
    }}
    .channel-fallback {{
      align-items: center;
      background: #254a55;
      color: #fff;
      display: flex;
      font-size: 1.6rem;
      font-weight: bold;
      justify-content: center;
    }}
    .channel-name {{
      font-size: 0.95rem;
      font-weight: bold;
      margin: 0 0 0.15rem;
      overflow-wrap: anywhere;
    }}
    .channel-provider {{ font-size: 0.8rem; margin: 0; opacity: 0.78; }}
    .nav-list {{ display: grid; gap: 0.8rem; margin-top: 1rem; }}
    .nav-item {{
      align-items: center;
      display: flex;
      gap: 0.65rem;
      font-size: 0.78rem;
      font-weight: bold;
      opacity: 0.82;
      text-transform: uppercase;
    }}
    .nav-icon {{ font-size: 1rem; width: 1.2rem; }}
    .content {{ display: grid; gap: 1rem; padding: 1.6rem; }}
    .topbar {{
      align-items: center;
      display: flex;
      gap: 1rem;
      justify-content: space-between;
    }}
    h1 {{ font-size: 1.35rem; line-height: 1.2; margin: 0; text-transform: uppercase; }}
    h2 {{ font-size: 0.85rem; letter-spacing: 0; margin: 0; text-transform: uppercase; }}
    .meta {{ color: #a7c1c8; line-height: 1.45; margin: 0; overflow-wrap: anywhere; }}
    .channel-select {{
      background: #284b57;
      border: 1px solid #4e7480;
      border-radius: 999px;
      color: #eef8f8;
      min-width: 220px;
      padding: 0.55rem 0.75rem;
    }}
    .hero-grid {{ display: grid; gap: 1rem; grid-template-columns: repeat(4, minmax(0, 1fr)); }}
    .card {{
      background: #294b57;
      border: 1px solid rgba(136, 181, 190, 0.18);
      border-radius: 4px;
      min-width: 0;
      padding: 1.25rem;
    }}
    .card.accent {{ background: #0dd7bf; color: #153942; }}
    .label {{ color: #a9c2c9; font-size: 0.72rem; font-weight: bold; text-transform: uppercase; }}
    .accent .label {{ color: #16434b; }}
    .value {{
      font-size: 1.75rem;
      font-weight: bold;
      line-height: 1.2;
      margin-top: 0.45rem;
      overflow-wrap: anywhere;
    }}
    .section {{
      background: #294b57;
      border: 1px solid rgba(136, 181, 190, 0.18);
      border-radius: 4px;
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
      background: rgba(13, 215, 191, 0.16);
      border: 1px solid rgba(13, 215, 191, 0.45);
      border-radius: 999px;
      color: #89f4e7;
      font-size: 0.82rem;
      font-weight: bold;
      padding: 0.28rem 0.6rem;
    }}
    .quality-grid {{
      display: grid;
      gap: 0.75rem;
      grid-template-columns: repeat(2, minmax(0, 1fr));
    }}
    .quality-item {{ border-left: 3px solid #0dd7bf; padding-left: 0.75rem; }}
    .quality-item strong {{ display: block; margin-top: 0.2rem; }}
    .main-grid {{ display: grid; gap: 1rem; grid-template-columns: 1fr 1fr; }}
    .platform-grid {{
      display: grid;
      gap: 1rem;
      grid-template-columns: repeat(3, minmax(0, 1fr));
    }}
    .platform-card {{
      background: #203d47;
      border: 1px solid rgba(136, 181, 190, 0.18);
      border-radius: 4px;
      display: grid;
      gap: 0.65rem;
      min-width: 0;
      padding: 1rem;
    }}
    .platform-card.unavailable {{
      opacity: 0.58;
    }}
    .platform-title {{
      align-items: center;
      display: flex;
      justify-content: space-between;
      gap: 0.75rem;
      text-transform: uppercase;
    }}
    .platform-status {{
      color: #89f4e7;
      font-size: 0.7rem;
      font-weight: bold;
    }}
    .table-wrap {{ overflow-x: auto; }}
    table {{ border-collapse: collapse; min-width: 680px; width: 100%; }}
    th, td {{
      border-bottom: 1px solid rgba(217, 222, 231, 0.18);
      padding: 0.72rem;
      text-align: left;
    }}
    th {{ background: #203d47; color: #a7c1c8; font-size: 0.78rem; text-transform: uppercase; }}
    tr:last-child td {{ border-bottom: 0; }}
    .empty-row td {{ color: #a7c1c8; padding: 1.25rem 0.72rem; text-align: center; }}
    @media (max-width: 980px) {{
      .dashboard-shell {{ grid-template-columns: 1fr; }}
      .sidebar {{ flex-direction: row; flex-wrap: wrap; align-items: center; }}
      .nav-list {{ display: none; }}
      .hero-grid, .main-grid, .platform-grid {{
        grid-template-columns: repeat(2, minmax(0, 1fr));
      }}
    }}
    @media (max-width: 540px) {{
      .content {{ padding: 1rem; }}
      .topbar {{ align-items: flex-start; flex-direction: column; }}
      .channel-select {{ width: 100%; }}
      .hero-grid, .main-grid, .quality-grid, .platform-grid {{ grid-template-columns: 1fr; }}
      .channel-image {{ height: 64px; width: 64px; }}
    }}
  </style>
</head>
<body>
  <main class="dashboard-shell" data-dashboard>
    <aside class="sidebar">
      <h1 class="brand">Social</h1>
      <div class="channel-profile">
        <div data-channel-image>{source_image}</div>
        <div>
          <p class="channel-name" data-channel-name>{_text(active["name"])}</p>
          <p class="channel-provider" data-channel-provider>{_text(active["provider"])}</p>
        </div>
      </div>
      <div class="nav-list">
        <div class="nav-item"><span class="nav-icon">#</span><span>Overview</span></div>
        <div class="nav-item"><span class="nav-icon">%</span><span>Performance</span></div>
        <div class="nav-item"><span class="nav-icon">*</span><span>Content</span></div>
        <div class="nav-item"><span class="nav-icon">i</span><span>Metadata</span></div>
      </div>
    </aside>
    <section class="content">
      <div class="topbar">
        <div>
          <h1>Channel Analytics</h1>
          <p class="meta">
            Generated: <span data-generated-at>{_text(active["generated_at"])}</span>
          </p>
        </div>
        <label>
          <span class="label">Channel</span>
          <select class="channel-select" data-channel-select>
            {_channel_options(channels)}
          </select>
        </label>
      </div>
      <section class="hero-grid">
        {_metric_card(
            "Semiannual Performance",
            active["engagement_rate"],
            True,
            "data-engagement-rate",
        )}
        {_metric_card("Productions", active["records"], False, "data-records")}
        {_metric_card("Total Views", active["views"], False, "data-views")}
        {_metric_card("Total Engagements", active["engagements"], False, "data-engagements")}
      </section>
      <section class="section">
        <div class="section-header">
          <h2>Platform Sources</h2>
        </div>
        <div class="platform-grid" data-platform-sources>
          {_platform_cards(active)}
        </div>
      </section>
      <section class="main-grid">
        <div class="section">
          <div class="section-header">
            <h2>Engagement Breakdown</h2>
          </div>
          <div class="quality-grid">
            {_metric_item("Likes", active["likes_percent"], "data-likes-percent")}
            {_metric_item("Comments", active["comments_percent"], "data-comments-percent")}
            {_metric_item("Shares", active["shares_percent"], "data-shares-percent")}
          </div>
        </div>
        <div class="section">
          <div class="section-header">
            <h2>Per-Record Averages</h2>
          </div>
          <div class="quality-grid">
            {_metric_item("Views", active["average_views"], "data-average-views")}
            {_metric_item("Engagements", active["average_engagements"], "data-average-engagements")}
            {_metric_item("Likes", active["average_likes"], "data-average-likes")}
            {_metric_item("Comments", active["average_comments"], "data-average-comments")}
          </div>
        </div>
      </section>
      <section class="main-grid">
        <div class="section">
          <div class="section-header">
            <h2>Report Metadata</h2>
          </div>
          <div class="quality-grid">
            {_metric_item("Schema version", active["schema_version"], "data-schema-version")}
            {_metric_item("Ranking metric", active["ranking_metric"], "data-ranking-metric")}
            {_metric_item("Ranking limit", active["ranking_limit"], "data-ranking-limit")}
            {_metric_item("Source artifact", active["source_artifact"], "data-source-artifact")}
          </div>
        </div>
        <div class="section">
          <div class="section-header">
            <h2>Data Quality</h2>
            <span class="status-pill" data-quality-status>{_text(active["quality_status"])}</span>
          </div>
          <div class="quality-grid">
            {_metric_item("Has engagements", active["has_engagements"], "data-has-engagements")}
            {_metric_item("Top item", active["top_item"], "data-top-item")}
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
              <tr>
                <th>Content ID</th><th>Views</th><th>Likes</th>
                <th>Comments</th><th>Shares</th>
              </tr>
            </thead>
            <tbody data-top-rows>
              {_channel_table_rows(active)}
            </tbody>
          </table>
        </div>
      </section>
    </section>
  </main>
  <script type="application/json" id="dashboard-data">{channels_json}</script>
  <script>
    const channels = JSON.parse(document.getElementById("dashboard-data").textContent);
    const select = document.querySelector("[data-channel-select]");
    const setText = (selector, value) => {{
      document.querySelector(selector).textContent = value;
    }};
    const renderImage = (channel) => {{
      const target = document.querySelector("[data-channel-image]");
      if (channel.image_url) {{
        const img = document.createElement("img");
        img.className = "channel-image";
        img.src = channel.image_url;
        img.alt = `${{channel.name}} channel image`;
        target.replaceChildren(img);
        return;
      }}
      const fallback = document.createElement("div");
      fallback.className = "channel-image channel-fallback";
      fallback.setAttribute("aria-label", "Channel image");
      fallback.textContent = channel.initial;
      target.replaceChildren(fallback);
    }};
    const renderRows = (rows) => {{
      const target = document.querySelector("[data-top-rows]");
      if (!rows.length) {{
        target.innerHTML = (
          '<tr class="empty-row">'
          + '<td colspan="5">No top content rows available for this report.</td>'
          + '</tr>'
        );
        return;
      }}
      target.replaceChildren(...rows.map((row) => {{
        const tr = document.createElement("tr");
        ["content_id", "views", "likes", "comments", "shares"].forEach((key) => {{
          const td = document.createElement("td");
          td.textContent = row[key];
          tr.appendChild(td);
        }});
        return tr;
      }}));
    }};
    const renderPlatforms = (platforms) => {{
      const target = document.querySelector("[data-platform-sources]");
      const orderedProviders = ["youtube", "tiktok", "instagram"];
      target.replaceChildren(...orderedProviders.map((provider) => {{
        const platform = platforms.find((item) => item.provider === provider) || {{
          provider,
          status: "unavailable",
          records: "unavailable",
          views: "unavailable",
          engagements: "unavailable",
          engagement_rate: "unavailable",
        }};
        const card = document.createElement("article");
        const stateClass = platform.status === "unavailable" ? "unavailable" : "";
        card.className = `platform-card ${{stateClass}}`;
        const title = document.createElement("div");
        title.className = "platform-title";
        const name = document.createElement("strong");
        name.textContent = platform.provider;
        const status = document.createElement("span");
        status.className = "platform-status";
        status.textContent = platform.status;
        title.append(name, status);
        card.append(title);
        [
          ["Productions", platform.records],
          ["Views", platform.views],
          ["Engagements", platform.engagements],
          ["Performance", platform.engagement_rate],
        ].forEach(([label, value]) => {{
          const item = document.createElement("div");
          item.className = "quality-item";
          const itemLabel = document.createElement("span");
          itemLabel.className = "label";
          itemLabel.textContent = label;
          const itemValue = document.createElement("strong");
          itemValue.textContent = value;
          item.append(itemLabel, itemValue);
          card.append(item);
        }});
        return card;
      }}));
    }};
    const renderChannel = (channel) => {{
      renderImage(channel);
      setText("[data-channel-name]", channel.name);
      setText("[data-channel-provider]", channel.provider);
      setText("[data-generated-at]", channel.generated_at);
      setText("[data-engagement-rate]", channel.engagement_rate);
      setText("[data-records]", channel.records);
      setText("[data-views]", channel.views);
      setText("[data-engagements]", channel.engagements);
      setText("[data-likes-percent]", channel.likes_percent);
      setText("[data-comments-percent]", channel.comments_percent);
      setText("[data-shares-percent]", channel.shares_percent);
      setText("[data-average-views]", channel.average_views);
      setText("[data-average-engagements]", channel.average_engagements);
      setText("[data-average-likes]", channel.average_likes);
      setText("[data-average-comments]", channel.average_comments);
      setText("[data-schema-version]", channel.schema_version);
      setText("[data-ranking-metric]", channel.ranking_metric);
      setText("[data-ranking-limit]", channel.ranking_limit);
      setText("[data-source-artifact]", channel.source_artifact);
      setText("[data-quality-status]", channel.quality_status);
      setText("[data-has-engagements]", channel.has_engagements);
      setText("[data-top-item]", channel.top_item);
      renderPlatforms(channel.platforms);
      renderRows(channel.top_rows);
    }};
    select.addEventListener("change", () => renderChannel(channels[select.selectedIndex]));
  </script>
</body>
</html>
"""


def write_dashboard_html(payload: dict[str, Any], output_path: Path) -> Path:
    output_path.parent.mkdir(parents=True, exist_ok=True)
    output_path.write_text(build_dashboard_html(payload), encoding="utf-8")
    return output_path


def main(
    report_json_path: Path | list[Path] | None = None,
    output_path: Path = DEFAULT_DASHBOARD_OUTPUT,
    project_root: Path | None = None,
    all_reports: bool = False,
    channels_config_path: Path | None = None,
) -> int:
    root = project_root or Path.cwd()
    target_reports = _dashboard_report_paths(report_json_path, root, all_reports)
    channels_config = (
        load_channel_identity_config(channels_config_path) if channels_config_path else ()
    )
    payloads = load_report_payloads(target_reports)
    payload = (
        build_multi_report_dashboard_payload(payloads, channels_config)
        if len(payloads) > 1
        else _apply_channel_config(payloads[0], channels_config)
    )
    dashboard_path = write_dashboard_html(payload, output_path)
    print("report_json_paths=" + ",".join(path.as_posix() for path in target_reports))
    print(f"dashboard_path={dashboard_path.as_posix()}")
    return 0


def parse_args(argv: list[str] | None = None) -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Build a local static dashboard from report JSON artifacts."
    )
    parser.add_argument(
        "--report-json",
        action="append",
        type=Path,
        help=(
            "Report JSON artifact to render. Can be provided more than once. "
            "Defaults to the latest local YouTube report JSON."
        ),
    )
    parser.add_argument(
        "--all-reports",
        action="store_true",
        help="Render all local report JSON artifacts from the default report directory.",
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
    parser.add_argument(
        "--channels-config",
        type=Path,
        help="Optional local channel identity config JSON with public placeholders only.",
    )
    args = parser.parse_args(argv)
    if args.all_reports and args.report_json:
        parser.error("--all-reports cannot be used with --report-json.")
    return args


def cli_entrypoint() -> int:
    args = parse_args()
    return main(
        args.report_json,
        args.output,
        args.project_root,
        args.all_reports,
        args.channels_config,
    )


def _dashboard_report_paths(
    report_json_path: Path | list[Path] | None,
    project_root: Path,
    all_reports: bool,
) -> list[Path]:
    if all_reports:
        reports = find_report_json_files(project_root)
        if not reports:
            raise RuntimeError("No report JSON artifacts found. Generate a report JSON first.")
        return reports
    if isinstance(report_json_path, list):
        if not report_json_path:
            return [find_latest_report_json(project_root)]
        return report_json_path
    if report_json_path is not None:
        return [report_json_path]
    return [find_latest_report_json(project_root)]


def _apply_channel_config(
    payload: dict[str, Any],
    channels_config: tuple[ChannelIdentityConfig, ...],
) -> dict[str, Any]:
    channel_config = match_channel_identity(payload, channels_config)
    if channel_config is None:
        return payload

    source = _source_object(payload).copy()
    source["channel_id"] = channel_config.channel_id
    source["channel_name"] = channel_config.display_name
    if channel_config.image_url:
        source["image_url"] = channel_config.image_url
    return {**payload, "source": source}


def _channel_identity(payload: dict[str, Any]) -> str:
    source = payload.get("source", {})
    if not isinstance(source, dict):
        source = {}
    candidates = [
        source.get("channel_id"),
        source.get("channel_handle"),
        source.get("channel_name"),
        source.get("name"),
        payload.get("channel_id"),
        payload.get("channel_handle"),
        payload.get("channel_name"),
        source.get("provider"),
        payload.get("provider"),
    ]
    for candidate in candidates:
        if candidate:
            return str(candidate).strip().lower()
    return "unknown"


def _aggregated_channel_payload(payloads: list[dict[str, Any]]) -> dict[str, Any]:
    first_payload = payloads[0] if payloads else {}
    source = _source_object(first_payload)
    channel_name = _channel_display_name(first_payload)
    return {
        "generated_at": _latest_generated_at(payloads),
        "source": {
            "provider": "multi-platform",
            "channel_name": channel_name,
            "image_url": source.get("image_url") or source.get("channel_image_url") or "",
        },
        "report_schema_version": first_payload.get("report_schema_version", "unknown"),
        "records": sum(_number(payload.get("records", 0)) for payload in payloads),
        "ranking": _first_dict_value(payloads, "ranking"),
        "data_quality": _aggregated_data_quality(payloads),
        "top_content": _first_dict_value(payloads, "top_content"),
        "top_rows": [
            row
            for payload in payloads
            for row in payload.get("top_rows", [])
            if isinstance(row, dict)
        ],
        "platforms": [_platform_payload_from_report(payload) for payload in payloads],
    }


def _platform_payload_from_report(payload: dict[str, Any]) -> dict[str, Any]:
    source = _source_object(payload)
    data_quality = payload.get("data_quality", {})
    if not isinstance(data_quality, dict):
        data_quality = {}
    totals = payload.get("totals", {})
    if not isinstance(totals, dict):
        totals = {}
    return {
        "provider": str(source.get("provider", payload.get("provider", "unknown"))),
        "status": str(data_quality.get("status", "available")),
        "records": payload.get("records", 0),
        "totals": totals,
    }


def _source_object(payload: dict[str, Any]) -> dict[str, Any]:
    source = payload.get("source", {})
    return source if isinstance(source, dict) else {}


def _channel_display_name(payload: dict[str, Any]) -> str:
    source = _source_object(payload)
    candidates = [
        source.get("channel_name"),
        source.get("name"),
        payload.get("channel_name"),
        payload.get("channel_handle"),
        source.get("channel_handle"),
        source.get("provider"),
        payload.get("provider"),
    ]
    for candidate in candidates:
        if candidate:
            return str(candidate)
    return "unknown"


def _latest_generated_at(payloads: list[dict[str, Any]]) -> str:
    generated = [
        str(payload.get("generated_at"))
        for payload in payloads
        if payload.get("generated_at")
    ]
    return sorted(generated)[-1] if generated else "unknown"


def _first_dict_value(payloads: list[dict[str, Any]], key: str) -> dict[str, Any]:
    for payload in payloads:
        value = payload.get(key)
        if isinstance(value, dict):
            return value
    return {}


def _aggregated_data_quality(payloads: list[dict[str, Any]]) -> dict[str, Any]:
    records = sum(_number(payload.get("records", 0)) for payload in payloads)
    has_engagements = any(
        bool(payload.get("data_quality", {}).get("has_engagements", False))
        for payload in payloads
        if isinstance(payload.get("data_quality", {}), dict)
    )
    return {"status": "ok" if records else "empty", "has_engagements": has_engagements}


def _dashboard_channels(payload: dict[str, Any]) -> list[dict[str, Any]]:
    raw_channels = payload.get("channels")
    if isinstance(raw_channels, list) and raw_channels:
        channels = [
            _channel_model(channel) for channel in raw_channels if isinstance(channel, dict)
        ]
        return channels or [_channel_model(payload)]
    return [_channel_model(payload)]


def _channel_model(payload: dict[str, Any]) -> dict[str, Any]:
    source = payload.get("source", {})
    if not isinstance(source, dict):
        source = {}
    platforms = _platform_models(payload.get("platforms", []))
    totals = payload.get("totals", {})
    if not isinstance(totals, dict):
        totals = {}
    if platforms:
        totals = _consolidated_platform_totals(platforms, totals)
    data_quality = payload.get("data_quality", {})
    if not isinstance(data_quality, dict):
        data_quality = {}
    top_content = payload.get("top_content", {})
    ranking = payload.get("ranking", {})
    engagement_breakdown = payload.get("engagement_breakdown", {})
    rows = payload.get("top_rows", [])
    if not isinstance(rows, list):
        rows = []

    provider = source.get("provider", payload.get("provider", "unknown"))
    name = source.get("name") or source.get("channel_name") or provider
    image_url = source.get("image_url") or source.get("channel_image_url")
    channel_name = str(name or "unknown")

    return {
        "name": channel_name,
        "provider": str(provider or "unknown"),
        "initial": channel_name[:1].upper() if channel_name else "?",
        "image_url": str(image_url) if image_url else "",
        "generated_at": _format_generated_at(payload.get("generated_at", "unknown"), escape=False),
        "records": _display_number(payload.get("records", 0)),
        "views": _display_number(totals.get("views", 0)),
        "engagements": _display_number(totals.get("engagements", 0)),
        "engagement_rate": f"{_number(totals.get('engagement_rate_percent', 0.0)):.2f}%",
        "likes_percent": _breakdown_percent(engagement_breakdown, "likes_percent"),
        "comments_percent": _breakdown_percent(engagement_breakdown, "comments_percent"),
        "shares_percent": _breakdown_percent(engagement_breakdown, "shares_percent"),
        "average_views": _average_value(totals, "average_views_per_record"),
        "average_engagements": _average_value(totals, "average_engagements_per_record"),
        "average_likes": _average_value(totals, "average_likes_per_record"),
        "average_comments": _average_value(totals, "average_comments_per_record"),
        "average_shares": _average_value(totals, "average_shares_per_record"),
        "schema_version": str(payload.get("report_schema_version", "unknown")),
        "ranking_metric": _ranking_value(ranking, "metric", escape=False),
        "ranking_limit": _ranking_value(ranking, "limit", escape=False),
        "source_artifact": _source_artifact(payload, source, escape=False),
        "quality_status": str(data_quality.get("status", "unknown")),
        "has_engagements": _yes_no(data_quality.get("has_engagements", False)),
        "top_item": _top_content_label(top_content, escape=False),
        "top_rows": [_row_model(row) for row in rows],
        "platforms": platforms,
    }


def _platform_models(platforms: object) -> list[dict[str, Any]]:
    if not isinstance(platforms, list):
        return []
    return [_platform_model(platform) for platform in platforms if isinstance(platform, dict)]


def _platform_model(platform: dict[str, Any]) -> dict[str, Any]:
    totals = platform.get("totals", {})
    if not isinstance(totals, dict):
        totals = {}
    return {
        "provider": str(platform.get("provider", "unknown")),
        "status": str(platform.get("status", "available")),
        "records": _display_number(platform.get("records", 0)),
        "views": _display_number(totals.get("views", 0)),
        "engagements": _display_number(totals.get("engagements", 0)),
        "engagement_rate": f"{_number(totals.get('engagement_rate_percent', 0.0)):.2f}%",
    }


def _consolidated_platform_totals(
    platforms: list[dict[str, Any]],
    fallback_totals: dict[str, Any],
) -> dict[str, Any]:
    total_views = sum(_plain_number(platform["views"]) for platform in platforms)
    total_engagements = sum(_plain_number(platform["engagements"]) for platform in platforms)
    engagement_rate_percent = (
        (total_engagements / total_views) * 100 if total_views else 0.0
    )
    return {
        **fallback_totals,
        "views": total_views,
        "engagements": total_engagements,
        "engagement_rate_percent": engagement_rate_percent,
    }


def _row_model(row: object) -> dict[str, str]:
    if not isinstance(row, dict):
        row = {}
    return {
        "content_id": str(row.get("content_id", "<none>")),
        "views": str(row.get("views", 0)),
        "likes": str(row.get("likes", 0)),
        "comments": str(row.get("comments", 0)),
        "shares": str(row.get("shares", 0)),
    }


def _json_script_payload(channels: list[dict[str, Any]]) -> str:
    payload = json.dumps(channels, ensure_ascii=True)
    return (
        payload.replace("&", "\\u0026")
        .replace("<", "\\u003c")
        .replace(">", "\\u003e")
        .replace("</", "<\\/")
    )


def _channel_image_markup(channel: dict[str, Any]) -> str:
    image_url = channel.get("image_url")
    name = channel.get("name", "unknown")
    if image_url:
        return (
            f'<img class="channel-image" src="{_text(image_url)}" '
            f'alt="{_text(name)} channel image">'
        )
    initial = _text(channel.get("initial", "?"))
    return f'<div class="channel-image channel-fallback" aria-label="Channel image">{initial}</div>'


def _channel_options(channels: list[dict[str, Any]]) -> str:
    return "\n".join(
        f'<option value="{index}">{_text(channel["name"])}</option>'
        for index, channel in enumerate(channels)
    )


def _metric_card(label: str, value: object, accent: bool, data_attr: str) -> str:
    accent_class = " accent" if accent else ""
    return (
        f'<article class="card{accent_class}">'
        f'<div class="label">{_text(label)}</div>'
        f'<div class="value" {data_attr}>{_text(value)}</div>'
        "</article>"
    )


def _metric_item(label: str, value: object, data_attr: str) -> str:
    return (
        '<div class="quality-item">'
        f'<span class="label">{_text(label)}</span>'
        f'<strong {data_attr}>{_text(value)}</strong>'
        "</div>"
    )


def _channel_table_rows(channel: dict[str, Any]) -> str:
    rows = channel.get("top_rows", [])
    if not isinstance(rows, list) or not rows:
        return _empty_table_row()
    return "\n".join(_table_row(row) for row in rows)


def _platform_cards(channel: dict[str, Any]) -> str:
    platforms = channel.get("platforms", [])
    if not isinstance(platforms, list):
        platforms = []
    by_provider = {
        platform["provider"]: platform
        for platform in platforms
        if isinstance(platform, dict) and "provider" in platform
    }
    return "\n".join(
        _platform_card(
            by_provider.get(
                provider,
                {
                    "provider": provider,
                    "status": "unavailable",
                    "records": "unavailable",
                    "views": "unavailable",
                    "engagements": "unavailable",
                    "engagement_rate": "unavailable",
                },
            )
        )
        for provider in ("youtube", "tiktok", "instagram")
    )


def _platform_card(platform: dict[str, Any]) -> str:
    unavailable = " unavailable" if platform.get("status") == "unavailable" else ""
    return f"""<article class="platform-card{unavailable}">
  <div class="platform-title">
    <strong>{_text(platform.get("provider", "unknown"))}</strong>
    <span class="platform-status">{_text(platform.get("status", "unknown"))}</span>
  </div>
  {_metric_item("Productions", platform.get("records", "unavailable"), "")}
  {_metric_item("Views", platform.get("views", "unavailable"), "")}
  {_metric_item("Engagements", platform.get("engagements", "unavailable"), "")}
  {_metric_item("Performance", platform.get("engagement_rate", "unavailable"), "")}
</article>"""


def _display_number(value: object) -> str:
    number = _number(value)
    if number.is_integer():
        return f"{int(number):,}"
    return f"{number:,.2f}"


def _plain_number(value: object) -> float:
    if isinstance(value, str):
        value = value.replace(",", "")
    return _number(value)


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


def _empty_table_row() -> str:
    return (
        '<tr class="empty-row">'
        '<td colspan="5">No top content rows available for this report.</td>'
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


def _source_artifact(payload: dict[str, Any], source: object, escape: bool = True) -> str:
    if isinstance(source, dict):
        artifact = source.get("artifact")
        if artifact not in (None, ""):
            return _text(artifact) if escape else str(artifact)
    artifact = payload.get("artifact")
    if artifact in (None, ""):
        return "unknown"
    return _text(artifact) if escape else str(artifact)


def _top_content_label(top_content: object, escape: bool = True) -> str:
    if not isinstance(top_content, dict):
        return "No top content available"
    content_id = top_content.get("content_id")
    if content_id in (None, "", "<none>"):
        return "No top content available"
    return _text(content_id) if escape else str(content_id)


def _ranking_value(ranking: object, key: str, escape: bool = True) -> str:
    if not isinstance(ranking, dict):
        return "unknown"
    value = ranking.get(key, "unknown")
    if value in (None, ""):
        return "unknown"
    return _text(value) if escape else str(value)


def _breakdown_percent(engagement_breakdown: object, key: str) -> str:
    if not isinstance(engagement_breakdown, dict):
        return "0.00%"
    return f"{_number(engagement_breakdown.get(key, 0.0)):.2f}%"


def _average_value(totals: object, key: str) -> str:
    if not isinstance(totals, dict):
        return "0.00"
    return f"{_number(totals.get(key, 0.0)):.2f}"


def _format_generated_at(value: object, escape: bool = True) -> str:
    raw_value = str(value)
    if raw_value.endswith("Z"):
        raw_value = f"{raw_value[:-1]}+00:00"
    try:
        generated_at = dt.datetime.fromisoformat(raw_value)
    except ValueError:
        return _text(value) if escape else str(value)
    suffix = " UTC" if generated_at.tzinfo is dt.UTC else ""
    formatted = f"{generated_at:%Y-%m-%d %H:%M}{suffix}"
    return _text(formatted) if escape else formatted


def _text(value: object) -> str:
    return html.escape(str(value), quote=True)


def _number(value: object) -> float:
    if isinstance(value, int | float):
        return float(value)
    if isinstance(value, str):
        try:
            return float(value)
        except ValueError:
            return 0.0
    return 0.0


def _yes_no(value: object) -> str:
    return "yes" if value is True else "no"


if __name__ == "__main__":
    raise SystemExit(cli_entrypoint())
