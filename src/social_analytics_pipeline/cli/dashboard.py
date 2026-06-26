import argparse
import datetime as dt
import html
import json
import math
from pathlib import Path
from typing import Any

from social_analytics_pipeline.config import (
    ChannelIdentityConfig,
    load_channel_identity_config,
    match_channel_identity,
)

DEFAULT_DASHBOARD_OUTPUT = Path("data/dashboard/index.html")
DEFAULT_REPORT_JSON_DIR = Path("data/reports/youtube-json")
DEFAULT_REPORT_JSON_DIRS = (
    Path("data/reports/youtube-json"),
    Path("data/reports/instagram-json"),
)
DEFAULT_CHANNELS_CONFIG = Path("config/channels.local.json")


def find_latest_report_json(project_root: Path) -> Path:
    reports = find_report_json_files(project_root)
    if not reports:
        raise RuntimeError("No report JSON artifacts found. Generate a report JSON first.")
    return reports[-1]


def find_report_json_files(project_root: Path) -> list[Path]:
    reports: list[Path] = []
    for report_dir in DEFAULT_REPORT_JSON_DIRS:
        reports.extend((project_root / report_dir).glob("*.json"))
    if reports:
        return sorted(reports)
    return sorted((project_root / DEFAULT_REPORT_JSON_DIR).glob("*.json"))


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

    return (
        f"""<!doctype html>
<html lang="en">
<head>
  <meta charset="utf-8">
  <meta name="viewport" content="width=device-width, initial-scale=1">
  <title>Social Analytics Dashboard</title>
  <style>
    * {{ box-sizing: border-box; }}
    body {{
      background:
        radial-gradient(circle at top left, rgba(30, 234, 216, 0.16), transparent 28rem),
        linear-gradient(135deg, #070813 0%, #101326 52%, #08101f 100%);
      color: #eef8ff;
      font-family: Arial, sans-serif;
      margin: 0;
    }}
    .dashboard-shell {{
      display: grid;
      grid-template-columns: 220px minmax(0, 1fr);
      min-height: 100vh;
    }}
    .sidebar {{
      background: linear-gradient(180deg, #13283a 0%, #0b1024 100%);
      border-right: 1px solid rgba(56, 243, 223, 0.25);
      color: #eef8ff;
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
    .sidebar-note {{
      color: #9da7bc;
      font-size: 0.78rem;
      line-height: 1.45;
      margin: 0;
    }}
    .channel-profile {{
      align-items: center;
      display: flex;
      gap: 0.8rem;
      margin-top: 0.5rem;
      min-width: 0;
    }}
    .channel-image {{
      border: 2px solid rgba(42, 235, 223, 0.8);
      border-radius: 50%;
      flex: 0 0 auto;
      height: 84px;
      object-fit: cover;
      box-shadow: 0 0 26px rgba(26, 220, 214, 0.28);
      width: 84px;
    }}
    .channel-fallback {{
      align-items: center;
      background: radial-gradient(circle at 30% 30%, #1eead8, #1950d1 64%, #182039 65%);
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
    .content {{ display: grid; gap: 1rem; min-width: 0; padding: 1.3rem; }}
    .channel-hero {{
      align-items: center;
      background:
        linear-gradient(135deg, rgba(30, 234, 216, 0.16), transparent 42%),
        linear-gradient(145deg, #11172d 0%, #09101f 100%);
      border: 1px solid rgba(30, 234, 216, 0.32);
      border-radius: 8px;
      box-shadow: 0 22px 46px rgba(0, 0, 0, 0.28);
      display: flex;
      gap: 1rem;
      justify-content: space-between;
      min-width: 0;
      padding: 1.2rem;
    }}
    .hero-identity {{
      align-items: center;
      display: flex;
      gap: 1rem;
      min-width: 0;
    }}
    .hero-copy {{
      display: grid;
      gap: 0.3rem;
      min-width: 0;
    }}
    .hero-copy h1 {{
      color: #eef8ff;
      font-size: 1.8rem;
      line-height: 1.1;
      overflow-wrap: anywhere;
      text-transform: none;
    }}
    .topbar {{
      align-items: center;
      display: flex;
      gap: 1rem;
      justify-content: space-between;
    }}
    h1 {{ font-size: 1.35rem; line-height: 1.2; margin: 0; text-transform: uppercase; }}
    h2 {{ font-size: 0.85rem; letter-spacing: 0; margin: 0; text-transform: uppercase; }}
    .meta {{ color: #9da7bc; line-height: 1.45; margin: 0; overflow-wrap: anywhere; }}
    .channel-select {{
      background: #111428;
      border: 1px solid #2f3654;
      border-radius: 999px;
      color: #eef8f8;
      min-width: 220px;
      padding: 0.55rem 0.75rem;
    }}
    .channel-picker {{
      align-items: end;
      display: grid;
      gap: 0.65rem;
      min-width: 260px;
    }}
    .channel-preview {{
      align-items: center;
      background: rgba(12, 18, 36, 0.78);
      border: 1px solid rgba(30, 234, 216, 0.18);
      border-radius: 8px;
      display: flex;
      gap: 0.7rem;
      min-width: 0;
      padding: 0.65rem;
    }}
    .channel-preview .channel-image {{
      height: 44px;
      width: 44px;
    }}
    .channel-preview-copy {{
      display: grid;
      gap: 0.18rem;
      min-width: 0;
    }}
    .channel-preview-copy strong {{
      color: #eef8ff;
      font-size: 0.84rem;
      overflow-wrap: anywhere;
    }}
    .channel-preview-copy span {{
      color: #9da7bc;
      font-size: 0.74rem;
      overflow-wrap: anywhere;
    }}
    .channel-option-list {{
      display: grid;
      gap: 0.5rem;
      max-height: 10rem;
      overflow-y: auto;
    }}
    .channel-option-card {{
      align-items: center;
      background: rgba(17, 20, 40, 0.88);
      border: 1px solid #2f3654;
      border-radius: 8px;
      color: #eef8ff;
      cursor: pointer;
      display: grid;
      gap: 0.55rem;
      grid-template-columns: auto minmax(0, 1fr);
      padding: 0.55rem;
      text-align: left;
    }}
    .channel-option-card.active {{
      border-color: #1eead8;
      box-shadow: 0 0 0 1px rgba(30, 234, 216, 0.2);
    }}
    .channel-option-card .channel-image {{
      height: 36px;
      width: 36px;
    }}
    .channel-option-copy {{
      display: grid;
      gap: 0.15rem;
      min-width: 0;
    }}
    .channel-option-copy strong {{
      font-size: 0.78rem;
      overflow-wrap: anywhere;
    }}
    .channel-option-copy span {{
      color: #9da7bc;
      font-size: 0.7rem;
      overflow-wrap: anywhere;
    }}
    .hero-grid {{ display: grid; gap: 1rem; grid-template-columns: repeat(4, minmax(0, 1fr)); }}
    .insights-grid {{
      display: grid;
      gap: 0.8rem;
      grid-template-columns: repeat(4, minmax(0, 1fr));
    }}
    .insight-card {{
      background:
        linear-gradient(145deg, rgba(30, 234, 216, 0.08), transparent 52%),
        #0c1224;
      border: 1px solid rgba(30, 234, 216, 0.16);
      border-radius: 8px;
      display: grid;
      gap: 0.35rem;
      min-width: 0;
      overflow: hidden;
      padding: 0.9rem;
      position: relative;
    }}
    .insight-card::before {{
      background: linear-gradient(180deg, #1eead8, #1950d1);
      bottom: 0.85rem;
      content: "";
      left: 0;
      position: absolute;
      top: 0.85rem;
      width: 0.2rem;
    }}
    .insight-card.views::before {{ background: linear-gradient(180deg, #1eead8, #168ac7); }}
    .insight-card.engagement::before {{ background: linear-gradient(180deg, #54ff8a, #1eead8); }}
    .insight-card.activity::before {{ background: linear-gradient(180deg, #1950d1, #54ff8a); }}
    .insight-label {{
      align-items: center;
      color: #9da7bc;
      display: flex;
      font-size: 0.72rem;
      gap: 0.45rem;
      text-transform: uppercase;
    }}
    .insight-marker {{
      align-items: center;
      background: rgba(30, 234, 216, 0.12);
      border: 1px solid rgba(30, 234, 216, 0.22);
      border-radius: 999px;
      color: #85fff4;
      display: inline-flex;
      font-size: 0.68rem;
      font-weight: 800;
      height: 1.35rem;
      justify-content: center;
      width: 1.35rem;
    }}
    .insight-card strong {{
      color: #eef8ff;
      font-size: 0.95rem;
      line-height: 1.25;
      overflow-wrap: anywhere;
    }}
    .card {{
      background: linear-gradient(145deg, #101326 0%, #090b18 100%);
      border: 1px solid #2f3654;
      border-radius: 8px;
      box-shadow: inset 0 0 0 1px rgba(255, 255, 255, 0.02), 0 18px 38px rgba(0, 0, 0, 0.22);
      min-width: 0;
      padding: 1.25rem;
      position: relative;
      overflow: hidden;
    }}
    .metric-card {{
      min-height: 8.6rem;
    }}
    .metric-card::after {{
      display: none;
    }}
    .metric-card::before {{
      background: linear-gradient(90deg, #1eead8, #1950d1, #54ff8a);
      content: "";
      height: 0.28rem;
      left: 1rem;
      position: absolute;
      right: 1rem;
      top: 0;
    }}
    .card::after {{
      background: radial-gradient(circle, rgba(28, 232, 216, 0.18), transparent 62%);
      content: "";
      height: 7rem;
      position: absolute;
      right: 0;
      top: 0;
      transform: translate(45%, -35%);
      width: 7rem;
    }}
    .card.accent {{
      background: linear-gradient(145deg, #12162d 0%, #0a1029 100%);
      border-color: rgba(30, 234, 216, 0.74);
      box-shadow: 0 0 34px rgba(26, 220, 214, 0.18);
      color: #eef8ff;
    }}
    .label {{ color: #9da7bc; font-size: 0.72rem; font-weight: bold; text-transform: uppercase; }}
    .accent .label {{ color: #9af7ee; }}
    .value {{
      color: #27ead8;
      font-size: 1.75rem;
      font-weight: bold;
      line-height: 1.2;
      margin-top: 0.45rem;
      overflow-wrap: anywhere;
    }}
    .metric-spark {{
      align-items: end;
      display: flex;
      gap: 0.25rem;
      height: 1.5rem;
      margin-top: 0.9rem;
      position: relative;
      z-index: 1;
    }}
    .metric-spark span {{
      background: linear-gradient(180deg, #54ff8a, #1eead8 62%, #1950d1);
      border-radius: 999px;
      display: block;
      flex: 1;
      min-width: 0.35rem;
    }}
    .section {{
      background: linear-gradient(145deg, #101326 0%, #090b18 100%);
      border: 1px solid #2f3654;
      border-radius: 8px;
      box-shadow: 0 18px 38px rgba(0, 0, 0, 0.22);
      min-width: 0;
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
      background: rgba(30, 234, 216, 0.12);
      border: 1px solid rgba(30, 234, 216, 0.45);
      border-radius: 999px;
      color: #85fff4;
      font-size: 0.82rem;
      font-weight: bold;
      padding: 0.28rem 0.6rem;
    }}
    .quality-grid {{
      display: grid;
      gap: 0.75rem;
      grid-template-columns: repeat(2, minmax(0, 1fr));
    }}
    .quality-item {{ border-left: 3px solid #1eead8; padding-left: 0.75rem; }}
    .quality-item strong {{ display: block; margin-top: 0.2rem; }}
    .main-grid {{ display: grid; gap: 1rem; grid-template-columns: 1fr 1fr; }}
    .analytics-grid {{ display: grid; gap: 1rem; grid-template-columns: 1.25fr 0.75fr; }}
    .chart-card {{ min-height: 16rem; }}
    .chart-bars {{ display: grid; gap: 0.75rem; }}
    .chart-row {{
      align-items: center;
      display: grid;
      gap: 0.75rem;
      grid-template-columns: minmax(5rem, 0.7fr) minmax(0, 2fr) 4.5rem;
    }}
    .chart-label, .chart-value {{ color: #c8d2e3; font-size: 0.78rem; overflow-wrap: anywhere; }}
    .chart-value {{ text-align: right; }}
    .chart-track {{
      background: #20243b;
      border-radius: 999px;
      height: 0.8rem;
      overflow: hidden;
    }}
    .chart-fill {{
      background: linear-gradient(90deg, #1950d1 0%, #1eead8 72%, #54ff8a 100%);
      border-radius: inherit;
      box-shadow: 0 0 22px rgba(30, 234, 216, 0.48);
      height: 100%;
      min-width: 0.25rem;
    }}
    .donut-grid {{
      display: grid;
      gap: 1rem;
      grid-template-columns: repeat(3, minmax(0, 1fr));
    }}
    .donut {{
      align-items: center;
      display: grid;
      gap: 0.55rem;
      justify-items: center;
      text-align: center;
    }}
    .donut-ring {{
      align-items: center;
      background: conic-gradient(#1eead8 calc(var(--value) * 1%), #24283f 0);
      border-radius: 50%;
      display: flex;
      height: 5rem;
      justify-content: center;
      position: relative;
      width: 5rem;
    }}
    .donut-ring::after {{
      background: #101326;
      border-radius: 50%;
      content: "";
      height: 3.25rem;
      position: absolute;
      width: 3.25rem;
    }}
    .donut-ring strong {{
      color: #eef8ff;
      font-size: 0.9rem;
      position: relative;
      z-index: 1;
    }}
    .donut span {{ color: #9da7bc; font-size: 0.78rem; }}
    .platform-grid {{
      display: grid;
      gap: 1rem;
      grid-template-columns: repeat(3, minmax(0, 1fr));
    }}
    .platform-card {{
      background: #111428;
      border: 1px solid #2f3654;
      border-radius: 8px;
      display: grid;
      gap: 0.65rem;
      min-width: 0;
      padding: 1rem;
    }}
    .platform-card.unavailable {{
      opacity: 0.58;
    }}
    .platform-empty-note {{
      color: #c8d2e3;
      font-size: 0.82rem;
      line-height: 1.45;
      margin: 0;
    }}
    .production-panel {{
      background: #0c1224;
      border: 1px solid rgba(30, 234, 216, 0.16);
      border-radius: 8px;
      overflow-x: auto;
      padding: 1rem;
    }}
    .cadence-grid {{
      display: grid;
      gap: 0.8rem;
      grid-template-columns: repeat(3, minmax(0, 1fr));
      margin-bottom: 1rem;
    }}
    .cadence-card {{
      background:
        linear-gradient(145deg, rgba(84, 255, 138, 0.08), transparent 55%),
        #111428;
      border: 1px solid rgba(84, 255, 138, 0.18);
      border-radius: 8px;
      display: grid;
      gap: 0.35rem;
      min-width: 0;
      overflow: hidden;
      padding: 0.8rem;
      position: relative;
    }}
    .cadence-card::before {{
      background: linear-gradient(180deg, #54ff8a, #1eead8);
      bottom: 0.7rem;
      content: "";
      left: 0;
      position: absolute;
      top: 0.7rem;
      width: 0.2rem;
    }}
    .cadence-card.days::before {{ background: linear-gradient(180deg, #1eead8, #168ac7); }}
    .cadence-card.average::before {{ background: linear-gradient(180deg, #1950d1, #54ff8a); }}
    .cadence-label {{
      align-items: center;
      color: #9da7bc;
      display: flex;
      font-size: 0.72rem;
      gap: 0.45rem;
      text-transform: uppercase;
    }}
    .cadence-marker {{
      align-items: center;
      background: rgba(84, 255, 138, 0.1);
      border: 1px solid rgba(84, 255, 138, 0.22);
      border-radius: 999px;
      color: #b6ffc7;
      display: inline-flex;
      font-size: 0.68rem;
      font-weight: 800;
      height: 1.35rem;
      justify-content: center;
      width: 1.35rem;
    }}
    .cadence-card strong {{
      color: #eef8ff;
      font-size: 1rem;
      overflow-wrap: anywhere;
    }}
    .production-heatmap {{
      display: grid;
      gap: 0.4rem;
      min-width: 760px;
    }}
    .production-months {{
      color: #9da7bc;
      display: grid;
      font-size: 0.78rem;
      grid-template-columns: repeat(6, 1fr);
      padding-left: 1.4rem;
    }}
    .production-grid {{
      display: grid;
      gap: 0.22rem;
      grid-auto-flow: column;
      grid-template-rows: repeat(7, 0.85rem);
      width: max-content;
    }}
    .production-day {{
      background: #20243b;
      border-radius: 3px;
      height: 0.85rem;
      width: 0.85rem;
    }}
    .production-section {{
      border-color: rgba(84, 255, 138, 0.22);
    }}
    .production-day.level-1 {{ background: #1950d1; }}
    .production-day.level-2 {{ background: #168ac7; }}
    .production-day.level-3 {{ background: #1eead8; }}
    .production-day.level-4 {{ background: #54ff8a; }}
    .production-footer {{
      align-items: center;
      color: #9da7bc;
      display: flex;
      font-size: 0.8rem;
      justify-content: space-between;
      margin-top: 0.8rem;
    }}
    .production-legend {{
      align-items: center;
      display: flex;
      gap: 0.35rem;
    }}
    .platform-title {{
      align-items: center;
      display: flex;
      justify-content: space-between;
      gap: 0.75rem;
      text-transform: uppercase;
    }}
    .platform-status {{
      color: #85fff4;
      font-size: 0.7rem;
      font-weight: bold;
    }}
    .platform-content-preview {{
      align-items: center;
      display: flex;
      gap: 0.65rem;
      min-width: 0;
    }}
    .platform-content-preview img {{
      background: #20243b;
      border: 1px solid rgba(30, 234, 216, 0.24);
      border-radius: 6px;
      flex: 0 0 auto;
      height: 2.7rem;
      object-fit: cover;
      width: 4rem;
    }}
    .platform-chart-grid {{
      display: grid;
      gap: 1rem;
      grid-template-columns: repeat(3, minmax(0, 1fr));
      margin-top: 1rem;
    }}
    .platform-chart {{
      background: #0c1224;
      border: 1px solid rgba(30, 234, 216, 0.16);
      border-radius: 8px;
      display: grid;
      gap: 0.65rem;
      padding: 0.85rem;
    }}
    .platform-chart h3 {{
      font-size: 0.76rem;
      margin: 0;
      text-transform: uppercase;
    }}
    .platform-chart-row {{
      align-items: center;
      display: grid;
      gap: 0.55rem;
      grid-template-columns: 4.5rem minmax(0, 1fr) 4.5rem;
    }}
    .platform-chart-label, .platform-chart-value {{
      color: #c8d2e3;
      font-size: 0.74rem;
      overflow-wrap: anywhere;
    }}
    .platform-chart-value {{ text-align: right; }}
    .platform-chart-track {{
      background: #20243b;
      border-radius: 999px;
      height: 0.65rem;
      overflow: hidden;
    }}
    .platform-chart-fill {{
      background: linear-gradient(90deg, #1950d1, #1eead8 70%, #54ff8a);
      border-radius: inherit;
      height: 100%;
      min-width: 0.2rem;
    }}
    .platform-chart-empty {{
      color: #a7c1c8;
      font-size: 0.8rem;
      margin: 0;
    }}
    .table-wrap {{ max-width: 100%; overflow-x: auto; }}
    .supporting-details {{
      background: linear-gradient(145deg, #0c1224 0%, #090b18 100%);
      border-color: rgba(157, 167, 188, 0.2);
    }}
    .supporting-details summary {{
      align-items: center;
      color: #eef8ff;
      cursor: pointer;
      display: flex;
      font-size: 0.86rem;
      font-weight: bold;
      gap: 0.8rem;
      justify-content: space-between;
      list-style: none;
      text-transform: uppercase;
    }}
    .supporting-details summary::-webkit-details-marker {{ display: none; }}
    .supporting-details summary::after {{
      color: #1eead8;
      content: "+";
      font-size: 1.15rem;
      line-height: 1;
    }}
    .supporting-details[open] summary::after {{ content: "-"; }}
    .supporting-details .main-grid,
    .supporting-details .table-wrap {{
      margin-top: 1rem;
    }}
    table {{ border-collapse: collapse; min-width: 680px; width: 100%; }}
    th, td {{
      border-bottom: 1px solid rgba(217, 222, 231, 0.18);
      padding: 0.72rem;
      text-align: left;
    }}
    th {{ background: #111428; color: #9da7bc; font-size: 0.78rem; text-transform: uppercase; }}
    tr:last-child td {{ border-bottom: 0; }}
    tr.winner-row {{
      background: rgba(30, 234, 216, 0.08);
    }}
    tr.winner-row td:first-child {{
      border-left: 3px solid #1eead8;
    }}
    .content-cell {{
      align-items: center;
      display: flex;
      gap: 0.75rem;
      min-width: 18rem;
    }}
    .content-thumb {{
      background: #20243b;
      border: 1px solid rgba(30, 234, 216, 0.2);
      border-radius: 6px;
      flex: 0 0 auto;
      height: 3rem;
      object-fit: cover;
      width: 4.5rem;
    }}
    .content-thumb.fallback {{
      align-items: center;
      color: #85fff4;
      display: flex;
      font-size: 0.72rem;
      font-weight: bold;
      justify-content: center;
      text-transform: uppercase;
    }}
    .content-title {{
      color: #eef8ff;
      display: block;
      font-weight: bold;
      line-height: 1.25;
      overflow-wrap: anywhere;
      text-decoration: none;
    }}
    .content-title:hover {{ color: #27ead8; }}
    .content-meta {{
      color: #9da7bc;
      display: block;
      font-size: 0.74rem;
      margin-top: 0.2rem;
      overflow-wrap: anywhere;
    }}
    .rank-badge {{
      background: linear-gradient(135deg, #1eead8, #1950d1);
      border-radius: 999px;
      color: #eef8ff;
      display: inline-flex;
      font-size: 0.78rem;
      font-weight: 800;
      justify-content: center;
      min-width: 2.4rem;
      padding: 0.28rem 0.55rem;
    }}
    .content-gallery {{
      display: grid;
      gap: 0.9rem;
      grid-template-columns: repeat(3, minmax(0, 1fr));
      margin-bottom: 1rem;
    }}
    .content-card {{
      background: linear-gradient(145deg, #111428 0%, #0b1024 100%);
      border: 1px solid rgba(30, 234, 216, 0.2);
      border-radius: 8px;
      display: grid;
      gap: 0.65rem;
      min-width: 0;
      overflow: hidden;
      padding: 0.8rem;
    }}
    .content-card-media {{
      aspect-ratio: 16 / 9;
      background: #20243b;
      border-radius: 6px;
      overflow: hidden;
      position: relative;
    }}
    .content-card-media img {{
      height: 100%;
      object-fit: cover;
      width: 100%;
    }}
    .content-card-fallback {{
      align-items: center;
      color: #85fff4;
      display: flex;
      font-size: 0.85rem;
      font-weight: bold;
      height: 100%;
      justify-content: center;
      text-transform: uppercase;
    }}
    .content-card-rank {{
      left: 0.55rem;
      position: absolute;
      top: 0.55rem;
    }}
    .content-card-title {{
      color: #eef8ff;
      font-weight: bold;
      line-height: 1.25;
      overflow-wrap: anywhere;
      text-decoration: none;
    }}
    .content-card-title:hover {{ color: #27ead8; }}
    .content-card-meta {{
      color: #9da7bc;
      display: flex;
      flex-wrap: wrap;
      font-size: 0.76rem;
      gap: 0.45rem;
    }}
    .content-card-empty {{
      color: #a7c1c8;
      grid-column: 1 / -1;
      padding: 1rem;
      text-align: center;
    }}
    .empty-row td {{ color: #a7c1c8; padding: 1.25rem 0.72rem; text-align: center; }}
    @media (max-width: 980px) {{
      .dashboard-shell {{ grid-template-columns: 1fr; }}
      .sidebar {{ flex-direction: row; flex-wrap: wrap; align-items: center; }}
      .nav-list {{ display: none; }}
      .hero-grid, .insights-grid, .main-grid, .platform-grid, .analytics-grid,
      .cadence-grid,
      .content-gallery, .platform-chart-grid {{
        grid-template-columns: repeat(2, minmax(0, 1fr));
      }}
    }}
    @media (max-width: 540px) {{
      .content {{ padding: 1rem; }}
      .channel-hero {{ align-items: flex-start; flex-direction: column; }}
      .channel-picker {{ width: 100%; }}
      .channel-select {{ width: 100%; }}
      .hero-grid, .insights-grid, .main-grid, .quality-grid,
      .platform-grid, .analytics-grid, .cadence-grid,
      .donut-grid, .content-gallery, .platform-chart-grid {{ grid-template-columns: 1fr; }}
      .channel-image {{ height: 72px; width: 72px; }}
      .production-heatmap {{ min-width: 0; }}
      .production-months {{
        font-size: 0.72rem;
        padding-left: 0.5rem;
      }}
      .production-grid {{
        gap: 0.1rem;
        grid-template-rows: repeat(7, 0.5rem);
      }}
      .production-day {{
        height: 0.5rem;
        width: 0.5rem;
      }}
      .production-footer {{
        align-items: flex-start;
        flex-direction: column;
        gap: 0.55rem;
      }}
    }}
    .channel-manager {{
      margin: 1rem 0;
      padding: 1rem;
      border: 1px solid #2d3851;
      background: #101827;
    }}
    .channel-manager form, .channel-manager-row, .channel-manager-sources {{
      display: flex;
      align-items: center;
      gap: 0.55rem;
    }}
    .channel-manager form {{ margin-bottom: 0.8rem; flex-wrap: wrap; }}
    .channel-manager label {{ display: grid; gap: 0.3rem; color: #9eabc0; font-size: 0.78rem; }}
    .channel-manager input {{
      min-width: 10rem; padding: 0.45rem; border: 1px solid #33425f;
      background: #0b1220; color: #e6edf7;
    }}
    .channel-manager select {{
      min-width: 7rem; padding: 0.45rem; border: 1px solid #33425f;
      background: #0b1220; color: #e6edf7;
    }}
    .channel-manager button {{
      padding: 0.45rem 0.65rem; border: 1px solid #3a4a68;
      background: #17243a; color: #d9e6f7; cursor: pointer;
    }}
    .channel-manager-row {{
      justify-content: space-between; padding: 0.65rem 0;
      border-top: 1px solid #26334b; flex-wrap: wrap;
    }}
    .channel-manager-row input {{ flex: 1 1 11rem; }}
    .channel-manager-sources {{ flex-wrap: wrap; flex: 1 1 100%; }}
    .channel-manager-sources button {{ text-transform: capitalize; }}
    .channel-manager-source {{
      border: 1px solid #26334b;
      border-radius: 8px;
      display: grid;
      flex: 1 1 14rem;
      gap: 0.45rem;
      min-width: 14rem;
      padding: 0.55rem;
    }}
    .channel-manager-source-header {{
      align-items: center;
      display: flex;
      gap: 0.45rem;
      justify-content: space-between;
    }}
    .channel-manager-source-status {{
      color: #9eabc0;
      font-size: 0.72rem;
      text-transform: uppercase;
    }}
    .channel-manager-source-status.ready {{ color: #54ff8a; }}
    .channel-manager-source-status.pending {{ color: #ffcc66; }}
    .channel-manager-source-detail {{
      color: #9eabc0;
      font-size: 0.72rem;
      line-height: 1.35;
      margin: 0;
      overflow-wrap: anywhere;
    }}
    .channel-manager-source-actions {{
      display: flex;
      gap: 0.45rem;
    }}
    .channel-manager-source-actions input {{ flex: 1 1 auto; min-width: 7rem; }}
    .nav-list .channel-manager-trigger {{
      width: 100%; border: 0; text-align: left; font: inherit;
      color: inherit; background: transparent;
    }}
    .channel-manager-image {{
      width: 2rem; height: 2rem; object-fit: cover; border-radius: 50%;
    }}
  </style>
</head>
<body>
  <main class="dashboard-shell" data-dashboard>
    <aside class="sidebar">
      <h1 class="brand">Social</h1>
      <p class="sidebar-note">Channel-first analytics across connected social sources.</p>
        <div class="nav-list">
          <div class="nav-item"><span class="nav-icon">#</span><span>Overview</span></div>
          <div class="nav-item"><span class="nav-icon">%</span><span>Performance</span></div>
          <div class="nav-item"><span class="nav-icon">*</span><span>Content</span></div>
          <div class="nav-item"><span class="nav-icon">i</span><span>Metadata</span></div>
          <button class="nav-item channel-manager-trigger" type="button" data-channel-manager-open>
            <span class="nav-icon">+</span><span>Manage channels</span>
          </button>
      </div>
    </aside>
    <section class="content">
      <section class="channel-hero" data-visual-dashboard-shell>
        <div class="hero-identity">
          <div data-channel-image>{source_image}</div>
          <div class="hero-copy">
            <h1 data-channel-name>{_text(active["name"])}</h1>
            <p class="channel-provider" data-channel-provider>{_text(active["source_summary"])}</p>
            <p class="meta freshness">
              <span>Data updated</span>
              <strong data-generated-at>{_text(active["generated_at"])}</strong>
            </p>
          </div>
        </div>
        <div class="channel-picker" data-channel-picker>
          <label>
            <span class="label">Channel</span>
            <select class="channel-select" data-channel-select>
              {_channel_options(channels)}
            </select>
          </label>
          <div class="channel-preview" data-channel-preview>
            <div data-channel-preview-image>{source_image}</div>
            <div class="channel-preview-copy">
              <strong data-channel-preview-name>{_text(active["name"])}</strong>
              <span data-channel-preview-meta>{_text(active["source_summary"])}</span>
            </div>
          </div>
          <div class="channel-option-list" data-channel-options>
            {_channel_option_cards(channels)}
          </div>
        </div>
      </section>
      <section class="channel-manager" data-channel-manager hidden>
        <div class="section-header">
          <h2>Managed Channels</h2>
          <button type="button" data-channel-manager-close>Close</button>
        </div>
        <form data-channel-manager-add>
          <label>Channel name<input name="name" required></label>
          <button type="submit">Add channel</button>
        </form>
        <div data-channel-manager-list></div>
        <p data-channel-manager-status></p>
      </section>
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
        {_metric_card("Followers", active["followers"], False, "data-followers")}
      </section>
      <section class="insights-grid" data-channel-insights>
        {_insight_item(
            "Top content",
            active["insight_top_item"],
            "data-insight-top-content",
            "content",
            "T",
        )}
        {_insight_item(
            "Views leader",
            active["insight_top_views_source"],
            "data-insight-views-leader",
            "views",
            "V",
        )}
        {_insight_item(
            "Engagement leader",
            active["insight_top_engagement_source"],
            "data-insight-engagement-leader",
            "engagement",
            "E",
        )}
        {_insight_item(
            "Publishing activity",
            active["production_summary"],
            "data-insight-production-summary",
            "activity",
            "P",
        )}
      </section>
      <section class="analytics-grid">
        <div class="section chart-card">
          <div class="section-header">
            <h2>Top Content Views</h2>
          </div>
          <div data-view-bars>
            {_view_bars(active)}
          </div>
        </div>
        <div class="section chart-card">
          <div class="section-header">
            <h2>Engagement Mix</h2>
          </div>
          <div data-engagement-donuts>
            {_engagement_donuts(active)}
          </div>
        </div>
      </section>
      <section class="section production-section" data-production-panel>
        <div class="section-header">
          <h2>Platform Sources</h2>
          <span class="status-pill" data-platform-coverage>
            {_text(active["platform_coverage"])}
          </span>
        </div>
        <div class="platform-grid" data-platform-sources>
          {_platform_cards(active)}
        </div>
        <div class="platform-chart-grid" data-platform-comparison>
          {_platform_comparison_charts(active)}
        </div>
      </section>
      <section class="section">
        <div class="section-header">
          <div>
            <h2>Production Calendar</h2>
            <p class="meta" data-production-scope>
              {_text(active["production_scope"])}
            </p>
          </div>
          <span class="status-pill" data-production-total>{_text(active["production_total"])}</span>
        </div>
        <div class="cadence-grid" data-cadence-summary>
          {_cadence_item(
              "Productions",
              active["cadence_total"],
              "data-cadence-total",
              "total",
              "P",
          )}
          {_cadence_item(
              "Active days",
              active["cadence_active_days"],
              "data-cadence-active-days",
              "days",
              "D",
          )}
          {_cadence_item(
              "Per active day",
              active["cadence_average_per_active_day"],
              "data-cadence-average",
              "average",
              "A",
          )}
        </div>
        <div class="production-panel" data-production-calendar>
          {_production_calendar(active)}
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
      <section class="section">
        <div class="section-header">
          <h2>Top Content</h2>
          <span class="status-pill" data-top-row-count>{_top_row_count_label(active)}</span>
        </div>
        <div class="content-gallery" data-top-content-gallery>
          {_top_content_gallery(active)}
        </div>
        <details class="supporting-details">
          <summary>
            <span>Detailed ranking table</span>
            <span class="status-pill" data-top-row-count>{_top_row_count_label(active)}</span>
          </summary>
          <div class="table-wrap">
          <table>
            <thead>
              <tr>
                <th>Rank</th><th>Content</th><th>Published</th><th>Views</th><th>Likes</th>
                <th>Comments</th><th>Shares</th>
              </tr>
            </thead>
            <tbody data-top-rows>
              {_channel_table_rows(active)}
            </tbody>
          </table>
          </div>
        </details>
      </section>
      <details class="section supporting-details" data-supporting-details>
        <summary>
          <span>Supporting Details</span>
          <span class="status-pill" data-quality-status>{_text(active["quality_status"])}</span>
        </summary>
        <section class="main-grid">
          <div class="section">
            <div class="section-header">
              <h2>Report Context</h2>
            </div>
            <div class="quality-grid">
              {_metric_item("Report schema", active["schema_version"], "data-schema-version")}
              {_metric_item("Ranking by", active["ranking_metric"], "data-ranking-metric")}
              {_metric_item("Top items limit", active["ranking_limit"], "data-ranking-limit")}
              {_metric_item("Report file", active["source_artifact"], "data-source-artifact")}
            </div>
          </div>
          <div class="section">
            <div class="section-header">
              <h2>Data Quality</h2>
            </div>
            <div class="quality-grid">
              {_metric_item("Engagement data", active["has_engagements"], "data-has-engagements")}
              {_metric_item("Top content", active["top_item"], "data-top-item")}
              {_metric_item(
                  "Views leader",
                  active["top_views_source"],
                  "data-top-views-source",
              )}
              {_metric_item(
                  "Engagement leader",
                  active["top_engagement_source"],
                  "data-top-engagement-source",
              )}
            </div>
          </div>
        </section>
      </details>
    </section>
  </main>
  <script type="application/json" id="dashboard-data">{channels_json}</script>
  <script>
    const channels = JSON.parse(document.getElementById("dashboard-data").textContent);
    const catalogEndpoint = "/api/channels";
    const manager = document.querySelector("[data-channel-manager]");
    const managerList = document.querySelector("[data-channel-manager-list]");
    const managerStatus = document.querySelector("[data-channel-manager-status]");
    const setManagerStatus = (message) => {{ managerStatus.textContent = message; }};
    const catalogAction = async (payload) => {{
      const response = await fetch(catalogEndpoint, {{
        method: "POST",
        headers: {{"Content-Type": "application/json"}},
        body: JSON.stringify(payload),
      }});
      const result = await response.json();
      if (!response.ok) throw new Error(result.error || "Catalog update failed.");
      return result;
    }};
    const renderCatalog = (catalog) => {{
      managerList.replaceChildren(...catalog.map((channel) => {{
        const row = document.createElement("div");
        row.className = "channel-manager-row";
        if (channel.image_url) {{
          const image = document.createElement("img");
          image.className = "channel-manager-image";
          image.src = channel.image_url;
          image.alt = "";
          row.append(image);
        }}
        const name = document.createElement("input");
        name.value = channel.name;
        name.setAttribute("aria-label", `Channel name for ${{channel.name}}`);
        const save = document.createElement("button");
        save.type = "button";
        save.textContent = "Save";
        save.addEventListener("click", async () => {{
          try {{
            await catalogAction({{action: "rename", id: channel.id, name: name.value}});
            await loadCatalog();
          }} catch (error) {{ setManagerStatus(error.message); }}
        }});
        const schedule = document.createElement("select");
        schedule.setAttribute("aria-label", `Collection schedule for ${{channel.name}}`);
        [
          ["", "off"],
          ["daily", "daily"],
          ["weekly", "weekly"],
        ].forEach(([value, label]) => {{
          const option = document.createElement("option");
          option.value = value;
          option.textContent = label;
          option.selected = channel.schedule === value;
          schedule.append(option);
        }});
        schedule.addEventListener("change", async () => {{
          try {{
            await catalogAction({{
              action: "schedule",
              id: channel.id,
              schedule: schedule.value,
            }});
            await loadCatalog();
          }} catch (error) {{ setManagerStatus(error.message); }}
        }});
        const remove = document.createElement("button");
        remove.type = "button";
        remove.textContent = "Remove";
        remove.addEventListener("click", async () => {{
          try {{ await catalogAction({{action: "remove", id: channel.id}}); await loadCatalog(); }}
          catch (error) {{ setManagerStatus(error.message); }}
        }});
        const imageUrl = document.createElement("input");
        imageUrl.value = channel.image_url || "";
        imageUrl.placeholder = "Channel image URL";
        imageUrl.setAttribute("aria-label", `Image URL for ${{channel.name}}`);
        const saveImage = document.createElement("button");
        saveImage.type = "button";
        saveImage.textContent = "Set image";
        saveImage.addEventListener("click", async () => {{
          try {{
            await catalogAction({{
              action: "image",
              id: channel.id,
              image_url: imageUrl.value,
            }});
            await loadCatalog();
          }} catch (error) {{ setManagerStatus(error.message); }}
        }});
        const sources = document.createElement("div");
        sources.className = "channel-manager-sources";
        ["youtube", "instagram", "tiktok"].forEach((provider) => {{
          const platform = channel.platforms[provider] || {{}};
          const enabled = Boolean(platform.enabled);
          const ready = Boolean(platform.ready);
          const source = document.createElement("div");
          source.className = "channel-manager-source";
          const sourceHeader = document.createElement("div");
          sourceHeader.className = "channel-manager-source-header";
          const toggle = document.createElement("button");
          toggle.type = "button";
          toggle.textContent = `${{provider}}: ${{enabled ? "on" : "off"}}`;
          toggle.addEventListener("click", async () => {{
            try {{
              await catalogAction({{
                action: enabled ? "disable" : "enable",
                id: channel.id,
                provider,
              }});
              await loadCatalog();
            }} catch (error) {{ setManagerStatus(error.message); }}
          }});
          const status = document.createElement("span");
          status.className = `channel-manager-source-status ${{ready ? "ready" : "pending"}}`;
          status.textContent = platform.status?.status || (ready ? "ready" : "pending");
          status.title = platform.status?.outcome || "";
          sourceHeader.append(toggle, status);
          const detail = document.createElement("p");
          detail.className = "channel-manager-source-detail";
          const detailParts = [];
          if (platform.status?.outcome) detailParts.push(platform.status.outcome);
          if (platform.status?.loaded_records !== undefined) {{
            detailParts.push(`${{platform.status.loaded_records}} loaded`);
          }}
          if (platform.status?.last_success) {{
            detailParts.push(`last success ${{platform.status.last_success}}`);
          }}
          detail.textContent = detailParts.join(" | ") || "No collection attempt yet";
          const sourceActions = document.createElement("div");
          sourceActions.className = "channel-manager-source-actions";
          const reference = document.createElement("input");
          reference.value = platform.reference || "";
          const referencePlaceholders = {{
            youtube: "YouTube @handle or channel URL",
            instagram: "Instagram handle or profile URL",
            tiktok: "TikTok handle or profile URL",
          }};
          reference.placeholder = referencePlaceholders[provider] || `${{provider}} handle or URL`;
          reference.setAttribute("aria-label", reference.placeholder);
          const saveReference = document.createElement("button");
          saveReference.type = "button";
          saveReference.textContent = "Set";
          saveReference.addEventListener("click", async () => {{
            try {{
              await catalogAction({{
                action: "reference",
                id: channel.id,
                provider,
                reference: reference.value,
              }});
              await loadCatalog();
            }} catch (error) {{ setManagerStatus(error.message); }}
          }});
          sourceActions.append(reference, saveReference);
          source.append(sourceHeader, detail, sourceActions);
          sources.append(source);
        }});
        const collect = document.createElement("button");
        collect.type = "button";
        collect.textContent = "Collect now";
        collect.addEventListener("click", async () => {{
          try {{
            const result = await catalogAction({{action: "collect", id: channel.id}});
            const summary = (result.sources || [])
              .map((source) => {{
                const state = source.collection_status || (
                  source.selected ? "selected" : source.status
                );
                return `${{source.provider}}=${{state}}`;
              }})
              .join(", ");
            setManagerStatus(summary || "No configured sources for this channel.");
            await loadCatalog();
          }} catch (error) {{ setManagerStatus(error.message); }}
        }});
        row.append(name, save, schedule, imageUrl, saveImage, sources, collect, remove);
        managerList.append(row);
      }}));
    }};
    const loadCatalog = async () => {{
      try {{
        const response = await fetch(catalogEndpoint);
        const result = await response.json();
        renderCatalog(result.channels);
        setManagerStatus("");
      }} catch (error) {{ setManagerStatus("Catalog is available only when served locally."); }}
    }};
    document.querySelector("[data-channel-manager-open]").addEventListener("click", () => {{
      manager.hidden = false;
      loadCatalog();
    }});
    document.querySelector("[data-channel-manager-close]").addEventListener("click", () => {{
      manager.hidden = true;
    }});
    document.querySelector("[data-channel-manager-add]").addEventListener(
      "submit",
      async (event) => {{
      event.preventDefault();
      const form = event.currentTarget;
      try {{
        const channelId = form.elements.name.value
          .trim()
          .toLowerCase()
          .normalize("NFD")
          .replace(/[\u0300-\u036f]/g, "")
          .replace(/[^a-z0-9]+/g, "-")
          .replace(/^-+|-+$/g, "");
        await catalogAction({{
          action: "add",
          id: channelId,
          name: form.elements.name.value,
        }});
        form.reset();
        await loadCatalog();
      }} catch (error) {{ setManagerStatus(error.message); }}
      }},
    );
    const channelSelect = document.querySelector("[data-channel-select]");
    const setText = (selector, value) => {{
      document.querySelectorAll(selector).forEach((target) => {{
        target.textContent = value;
      }});
    }};
    const isRenderableImageUrl = (value) => {{
      if (!value) return false;
      try {{
        const url = new URL(value, window.location.href);
        return !["example.com", "example.test"].includes(url.hostname.toLowerCase());
      }} catch {{
        return false;
      }}
    }};
    const contentFallback = (label, className) => {{
      const fallback = document.createElement("div");
      fallback.className = className;
      fallback.textContent = label || "content";
      return fallback;
    }};
    const providerLabel = (provider) => ({{
      youtube: "YouTube",
      tiktok: "TikTok",
      instagram: "Instagram",
    }}[String(provider || "").toLowerCase()] || provider || "Unknown");
    const renderImage = (channel, selector = "[data-channel-image]") => {{
      const target = document.querySelector(selector);
      if (isRenderableImageUrl(channel.image_url)) {{
        const img = document.createElement("img");
        img.className = "channel-image";
        img.src = channel.image_url;
        const altBase = channel.name.toLowerCase().endsWith("channel")
          ? channel.name
          : `${{channel.name}} channel`;
        img.alt = `${{altBase}} image`;
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
      const countLabel = `${{rows.length}} ranked item${{rows.length === 1 ? "" : "s"}}`;
      setText("[data-top-row-count]", countLabel);
      if (!rows.length) {{
        target.innerHTML = (
          '<tr class="empty-row">'
          + '<td colspan="7">No top content rows available for this report.</td>'
          + '</tr>'
        );
        return;
      }}
      target.replaceChildren(...rows.map((row, index) => {{
        const tr = document.createElement("tr");
        if (index === 0) {{
          tr.className = "winner-row";
        }}
        const rank = document.createElement("td");
        const rankBadge = document.createElement("span");
        rankBadge.className = "rank-badge";
        rankBadge.textContent = `#${{index + 1}}`;
        rank.appendChild(rankBadge);
        tr.appendChild(rank);
        tr.appendChild(renderContentCell(row));
        ["published_at", "views", "likes", "comments", "shares"].forEach((key) => {{
          const td = document.createElement("td");
          td.textContent = row[key];
          tr.appendChild(td);
        }});
        return tr;
      }}));
    }};
    const renderContentGallery = (rows) => {{
      const target = document.querySelector("[data-top-content-gallery]");
      if (!rows.length) {{
        const empty = document.createElement("p");
        empty.className = "content-card-empty";
        empty.textContent = "No top content available for this channel.";
        target.replaceChildren(empty);
        return;
      }}
      target.replaceChildren(...rows.slice(0, 3).map((row, index) => {{
        const card = document.createElement("article");
        card.className = "content-card";
        const media = document.createElement("div");
        media.className = "content-card-media";
        const rank = document.createElement("span");
        rank.className = "rank-badge content-card-rank";
        rank.textContent = `#${{index + 1}}`;
        if (isRenderableImageUrl(row.thumbnail_url)) {{
          const img = document.createElement("img");
          img.src = row.thumbnail_url;
          img.alt = `${{row.display_title}} thumbnail`;
          media.appendChild(img);
        }} else {{
          media.appendChild(contentFallback(row.content_type, "content-card-fallback"));
        }}
        media.appendChild(rank);
        const title = document.createElement(row.content_url ? "a" : "span");
        title.className = "content-card-title";
        title.textContent = row.display_title;
        if (row.content_url) {{
          title.href = row.content_url;
          title.target = "_blank";
          title.rel = "noreferrer";
        }}
        const meta = document.createElement("div");
        meta.className = "content-card-meta";
        meta.textContent = [
          row.provider_label || providerLabel(row.provider),
          row.published_at,
          `${{row.views}} views`,
        ]
          .filter(Boolean)
          .join(" | ");
        card.append(media, title, meta);
        return card;
      }}));
    }};
    const renderContentCell = (row) => {{
      const td = document.createElement("td");
      const wrapper = document.createElement("div");
      wrapper.className = "content-cell";
      if (isRenderableImageUrl(row.thumbnail_url)) {{
        const img = document.createElement("img");
        img.className = "content-thumb";
        img.src = row.thumbnail_url;
        img.alt = `${{row.display_title}} thumbnail`;
        wrapper.appendChild(img);
      }} else {{
        wrapper.appendChild(contentFallback(row.content_type, "content-thumb fallback"));
      }}
      const text = document.createElement("div");
      const title = document.createElement(row.content_url ? "a" : "span");
      title.className = "content-title";
      title.textContent = row.display_title;
      if (row.content_url) {{
        title.href = row.content_url;
        title.target = "_blank";
        title.rel = "noreferrer";
      }}
      const meta = document.createElement("span");
      meta.className = "content-meta";
      const metaParts = [];
      if (row.provider) {{
        metaParts.push(`Platform: ${{row.provider_label || providerLabel(row.provider)}}`);
      }}
      meta.textContent = metaParts.join(" | ");
      text.append(title, meta);
      wrapper.appendChild(text);
      td.appendChild(wrapper);
      return td;
    }};
    const renderPlatforms = (platforms) => {{
      const target = document.querySelector("[data-platform-sources]");
      const orderedProviders = ["youtube", "tiktok", "instagram"];
      target.replaceChildren(...orderedProviders.map((provider) => {{
        const platform = platforms.find((item) => item.provider === provider) || {{
          provider,
          provider_label: providerLabel(provider),
          status: "unavailable",
          records: "No data",
          views: "No data",
          views_share: "No data",
          engagements: "No data",
          engagements_share: "No data",
          engagement_rate: "No data",
          top_content: "No data",
          top_content_url: "",
          top_content_thumbnail_url: "",
          top_content_type: "No data",
          top_content_views: "No data",
          top_content_published_at: "No date",
        }};
        const card = document.createElement("article");
        const stateClass = platform.status === "unavailable" ? "unavailable" : "";
        card.className = `platform-card ${{stateClass}}`;
        const title = document.createElement("div");
        title.className = "platform-title";
        const name = document.createElement("strong");
        name.textContent = platform.provider_label || providerLabel(platform.provider);
        const status = document.createElement("span");
        status.className = "platform-status";
        status.textContent = platform.status === "unavailable" ? "No data" : platform.status;
        title.append(name, status);
        card.append(title);
        if (platform.status === "unavailable") {{
          const note = document.createElement("p");
          note.className = "platform-empty-note";
          note.textContent = "No source data for this channel yet.";
          card.append(note);
          return card;
        }}
        if (
          isRenderableImageUrl(platform.top_content_thumbnail_url)
          && platform.top_content !== "unavailable"
        ) {{
          const preview = document.createElement("div");
          preview.className = "platform-content-preview";
          const image = document.createElement("img");
          image.src = platform.top_content_thumbnail_url;
          image.alt = `${{platform.top_content}} thumbnail`;
          preview.appendChild(image);
          card.append(preview);
        }}
        [
          ["Productions", platform.records],
          ["Views", platform.views],
          ["View share", platform.views_share],
          ["Engagements", platform.engagements],
          ["Engagement share", platform.engagements_share],
          ["Performance", platform.engagement_rate],
          ["Top content", platform.top_content],
          ["Top content type", platform.top_content_type],
          ["Top content views", platform.top_content_views],
          ["Top content date", platform.top_content_published_at],
        ].forEach(([label, value]) => {{
          const item = document.createElement("div");
          item.className = "quality-item";
          const itemLabel = document.createElement("span");
          itemLabel.className = "label";
          itemLabel.textContent = label;
          const itemValue = document.createElement("strong");
          if (label === "Top content" && platform.top_content_url && value !== "unavailable") {{
            const link = document.createElement("a");
            link.href = platform.top_content_url;
            link.target = "_blank";
            link.rel = "noreferrer";
            link.textContent = value;
            itemValue.appendChild(link);
          }} else {{
            itemValue.textContent = value;
          }}
          item.append(itemLabel, itemValue);
          card.append(item);
        }});
        return card;
      }}));
    }};
    const numberFromText = (value) => {{
      const parsed = Number(String(value).replace(/[%,$]/g, "").replace(/,/g, ""));
      return Number.isFinite(parsed) ? parsed : 0;
    }};
    const platformMetricRows = (platforms, metric) => {{
      const orderedProviders = ["youtube", "tiktok", "instagram"];
      return orderedProviders.map((provider) => {{
        const platform = platforms.find((item) => item.provider === provider);
        return {{
          provider,
          provider_label: providerLabel(provider),
          value: platform ? numberFromText(platform[metric]) : 0,
          label: platform ? platform[metric] : "No data",
          available: Boolean(platform) && platform.status !== "unavailable",
        }};
      }});
    }};
    const renderPlatformMetricChart = (title, rows) => {{
      const chart = document.createElement("article");
      chart.className = "platform-chart";
      const heading = document.createElement("h3");
      heading.textContent = title;
      chart.appendChild(heading);
      const availableRows = rows.filter((row) => row.available);
      if (!availableRows.length) {{
        const empty = document.createElement("p");
        empty.className = "platform-chart-empty";
        empty.textContent = "No platform metrics available.";
        chart.appendChild(empty);
        return chart;
      }}
      const maxValue = Math.max(...availableRows.map((row) => row.value), 1);
      rows.forEach((row) => {{
        const item = document.createElement("div");
        item.className = "platform-chart-row";
        const label = document.createElement("span");
        label.className = "platform-chart-label";
        label.textContent = row.provider_label || providerLabel(row.provider);
        const track = document.createElement("div");
        track.className = "platform-chart-track";
        const fill = document.createElement("div");
        fill.className = "platform-chart-fill";
        fill.style.width = row.available ? `${{Math.max(4, (row.value / maxValue) * 100)}}%` : "0%";
        track.appendChild(fill);
        const value = document.createElement("span");
        value.className = "platform-chart-value";
        value.textContent = row.label;
        item.append(label, track, value);
        chart.appendChild(item);
      }});
      return chart;
    }};
    const renderPlatformComparison = (platforms) => {{
      const target = document.querySelector("[data-platform-comparison]");
      target.replaceChildren(
        renderPlatformMetricChart("Views", platformMetricRows(platforms, "views")),
        renderPlatformMetricChart("Engagements", platformMetricRows(platforms, "engagements")),
        renderPlatformMetricChart("Productions", platformMetricRows(platforms, "records")),
      );
    }};
    const renderViewBars = (rows) => {{
      const target = document.querySelector("[data-view-bars]");
      if (!rows.length) {{
        target.innerHTML = '<p class="meta">No ranked content available for this chart.</p>';
        return;
      }}
      const maxViews = Math.max(...rows.map((row) => numberFromText(row.views)), 1);
      const chart = document.createElement("div");
      chart.className = "chart-bars";
      rows.slice(0, 6).forEach((row) => {{
        const value = numberFromText(row.views);
        const chartRow = document.createElement("div");
        chartRow.className = "chart-row";
        const label = document.createElement("span");
        label.className = "chart-label";
        label.textContent = row.display_title;
        const track = document.createElement("div");
        track.className = "chart-track";
        const fill = document.createElement("div");
        fill.className = "chart-fill";
        fill.style.width = `${{Math.max(4, (value / maxViews) * 100)}}%`;
        track.appendChild(fill);
        const valueText = document.createElement("span");
        valueText.className = "chart-value";
        valueText.textContent = row.views;
        chartRow.append(label, track, valueText);
        chart.appendChild(chartRow);
      }});
      target.replaceChildren(chart);
    }};
    const renderEngagementDonuts = (channel) => {{
      const target = document.querySelector("[data-engagement-donuts]");
      const metrics = [
        ["Likes", channel.likes_percent],
        ["Comments", channel.comments_percent],
        ["Shares", channel.shares_percent],
      ];
      const grid = document.createElement("div");
      grid.className = "donut-grid";
      metrics.forEach(([label, value]) => {{
        const item = document.createElement("div");
        item.className = "donut";
        const ring = document.createElement("div");
        ring.className = "donut-ring";
        ring.style.setProperty("--value", Math.min(100, numberFromText(value)));
        const strong = document.createElement("strong");
        strong.textContent = value;
        ring.appendChild(strong);
        const caption = document.createElement("span");
        caption.textContent = label;
        item.append(ring, caption);
        grid.appendChild(item);
      }});
      target.replaceChildren(grid);
    }};
    const renderProductionCalendar = (channel) => {{
      const target = document.querySelector("[data-production-calendar]");
      const total = document.querySelector("[data-production-total]");
      total.textContent = channel.production_total;
      if (!channel.production_days.length) {{
        target.innerHTML = '<p class="meta">No publication dates available for this report.</p>';
        return;
      }}
      const wrapper = document.createElement("div");
      wrapper.className = "production-heatmap";
      const months = document.createElement("div");
      months.className = "production-months";
      channel.production_months.forEach((month) => {{
        const item = document.createElement("span");
        item.textContent = month;
        months.appendChild(item);
      }});
      const grid = document.createElement("div");
      grid.className = "production-grid";
      channel.production_days.forEach((day) => {{
        const cell = document.createElement("span");
        cell.className = `production-day level-${{day.level}}`;
        cell.title = `${{day.date}}: ${{day.count}} production(s)`;
        cell.setAttribute("aria-label", cell.title);
        grid.appendChild(cell);
      }});
      const footer = document.createElement("div");
      footer.className = "production-footer";
      const summary = document.createElement("span");
      summary.textContent = channel.production_summary;
      const legend = document.createElement("div");
      legend.className = "production-legend";
      legend.append("Less");
      [0, 1, 2, 3, 4].forEach((level) => {{
        const cell = document.createElement("span");
        cell.className = `production-day level-${{level}}`;
        legend.appendChild(cell);
      }});
      legend.append("More");
      footer.append(summary, legend);
      wrapper.append(months, grid, footer);
      target.replaceChildren(wrapper);
    }};
    const renderChannel = (channel) => {{
      renderImage(channel);
      renderImage(channel, "[data-channel-preview-image]");
      setText("[data-channel-name]", channel.name);
      setText("[data-channel-provider]", channel.source_summary);
      setText("[data-channel-preview-name]", channel.name);
      setText("[data-channel-preview-meta]", channel.source_summary);
      setText("[data-generated-at]", channel.generated_at);
      setText("[data-engagement-rate]", channel.engagement_rate);
      setText("[data-records]", channel.records);
      setText("[data-views]", channel.views);
      setText("[data-engagements]", channel.engagements);
      setText("[data-followers]", channel.followers);
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
      setText("[data-top-views-source]", channel.top_views_source);
      setText("[data-top-engagement-source]", channel.top_engagement_source);
      setText("[data-insight-top-content]", channel.insight_top_item);
      setText("[data-insight-views-leader]", channel.insight_top_views_source);
      setText("[data-insight-engagement-leader]", channel.insight_top_engagement_source);
      setText("[data-insight-production-summary]", channel.production_summary);
      setText("[data-production-scope]", channel.production_scope);
      setText("[data-cadence-total]", channel.cadence_total);
      setText("[data-cadence-active-days]", channel.cadence_active_days);
      setText("[data-cadence-average]", channel.cadence_average_per_active_day);
      setText("[data-platform-coverage]", channel.platform_coverage);
      renderViewBars(channel.top_rows);
      renderEngagementDonuts(channel);
      renderPlatforms(channel.platforms);
      renderPlatformComparison(channel.platforms);
      renderProductionCalendar(channel);
      renderContentGallery(channel.top_rows);
      renderRows(channel.top_rows);
    }};
    const setActiveChannelOption = (index) => {{
      document.querySelectorAll("[data-channel-option]").forEach((button, optionIndex) => {{
        button.classList.toggle("active", optionIndex === index);
      }});
    }};
    const renderChannelAt = (index) => {{
      channelSelect.selectedIndex = index;
      setActiveChannelOption(index);
      renderChannel(channels[index]);
    }};
    channelSelect.addEventListener("change", () => renderChannelAt(channelSelect.selectedIndex));
    document.querySelectorAll("[data-channel-option]").forEach((button) => {{
      button.addEventListener("click", () => renderChannelAt(Number(button.dataset.channelIndex)));
    }});
  </script>
</body>
</html>
"""
    )


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
    channels_config_path = channels_config_path or _default_channels_config_path(root)
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


def _default_channels_config_path(project_root: Path) -> Path | None:
    candidate = project_root / DEFAULT_CHANNELS_CONFIG
    return candidate if candidate.exists() else None


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
    top_rows = _aggregated_top_rows(payloads)
    production_dates = _aggregated_production_dates(payloads)
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
        "top_content": top_rows[0] if top_rows else _first_dict_value(payloads, "top_content"),
        "production": {
            "period": "latest_6_months",
            "date_source": "all_processed_rows",
            "dates_count": len(production_dates),
        },
        "production_dates": production_dates,
        "top_rows": top_rows,
        "platforms": [_platform_payload_from_report(payload) for payload in payloads],
    }


def _aggregated_production_dates(payloads: list[dict[str, Any]]) -> list[object]:
    return [
        date
        for payload in payloads
        for date in payload.get("production_dates", [])
        if date
    ]


def _aggregated_top_rows(payloads: list[dict[str, Any]]) -> list[dict[str, Any]]:
    rows = [
        _top_row_with_provider(row, payload)
        for payload in payloads
        for row in payload.get("top_rows", [])
        if isinstance(row, dict)
    ]
    metric = _aggregated_ranking_metric(payloads)
    return sorted(rows, key=lambda row: _number(row.get(metric, row.get("views", 0))), reverse=True)


def _top_row_with_provider(row: dict[str, Any], payload: dict[str, Any]) -> dict[str, Any]:
    if row.get("provider"):
        return row
    source = _source_object(payload)
    provider = source.get("provider") or payload.get("provider")
    return {**row, "provider": provider} if provider else row


def _aggregated_ranking_metric(payloads: list[dict[str, Any]]) -> str:
    ranking = _first_dict_value(payloads, "ranking")
    metric = ranking.get("metric", "views")
    return str(metric) if metric else "views"


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
        "has_followers": bool(data_quality.get("has_followers", False)),
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
    ]
    for candidate in candidates:
        if candidate:
            return str(candidate)
    return _provider_channel_label(source.get("provider", payload.get("provider", "unknown")))


def _provider_channel_label(provider: object) -> str:
    provider_name = str(provider or "unknown").strip()
    if not provider_name or provider_name == "unknown":
        return "Unknown channel"
    display_names = {
        "youtube": "YouTube",
        "tiktok": "TikTok",
        "instagram": "Instagram",
    }
    return f"{display_names.get(provider_name.lower(), provider_name.title())} channel"


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
        platforms = _platform_share_models(platforms, totals)
    data_quality = payload.get("data_quality", {})
    if not isinstance(data_quality, dict):
        data_quality = {}
    top_content = payload.get("top_content", {})
    ranking = payload.get("ranking", {})
    engagement_breakdown = payload.get("engagement_breakdown", {})
    production = payload.get("production", {})
    if not isinstance(production, dict):
        production = {}
    rows = payload.get("top_rows", [])
    if not isinstance(rows, list):
        rows = []
    production_source = payload.get("production_dates", rows)
    if not isinstance(production_source, list):
        production_source = rows

    provider = source.get("provider", payload.get("provider", "unknown"))
    name = (
        source.get("name")
        or source.get("channel_name")
        or source.get("channel_handle")
        or _provider_channel_label(provider)
    )
    image_url = source.get("image_url") or source.get("channel_image_url")
    channel_name = str(name or "unknown")
    top_item = _top_content_label(top_content, escape=False)
    top_views_source = _top_platform_source(platforms, "views")
    top_engagement_source = _top_platform_source(platforms, "engagements")
    production_summary = _production_summary(production_source)
    cadence = _production_cadence(production_source)

    return {
        "name": channel_name,
        "provider": str(provider or "unknown"),
        "source_summary": _channel_source_summary(provider, platforms),
        "initial": channel_name[:1].upper() if channel_name else "?",
        "image_url": str(image_url) if image_url else "",
        "generated_at": _format_generated_at(payload.get("generated_at", "unknown"), escape=False),
        "records": _display_number(payload.get("records", 0)),
        "views": _display_number(totals.get("views", 0)),
        "engagements": _display_number(totals.get("engagements", 0)),
        "followers": _display_number(totals.get("max_followers", 0))
        if (totals.get("has_followers") or data_quality.get("has_followers"))
        else "Unavailable",
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
        "quality_status": _quality_status_label(data_quality.get("status", "unknown")),
        "has_engagements": _availability_label(data_quality.get("has_engagements", False)),
        "top_item": top_item,
        "top_views_source": top_views_source,
        "top_engagement_source": top_engagement_source,
        "insight_top_item": _insight_empty_state(top_item, "No top content yet"),
        "insight_top_views_source": _insight_empty_state(
            top_views_source,
            "No views leader yet",
        ),
        "insight_top_engagement_source": _insight_empty_state(
            top_engagement_source,
            "No engagement leader yet",
        ),
        "top_rows": [_row_model(row) for row in rows],
        "production_total": _production_total(production_source),
        "production_summary": production_summary,
        "production_scope": _production_scope_label(production),
        "cadence_total": cadence["total"],
        "cadence_active_days": cadence["active_days"],
        "cadence_average_per_active_day": cadence["average_per_active_day"],
        "production_months": _production_months(production_source),
        "production_days": _production_days(production_source),
        "platform_coverage": _platform_coverage(platforms),
        "platforms": _platforms_with_top_content(platforms, rows),
    }


def _platform_models(platforms: object) -> list[dict[str, Any]]:
    if not isinstance(platforms, list):
        return []
    return [_platform_model(platform) for platform in platforms if isinstance(platform, dict)]


def _platform_coverage(platforms: list[dict[str, Any]]) -> str:
    available = sum(
        1 for platform in platforms if platform.get("status", "available") != "unavailable"
    )
    return f"{available}/3 available"


def _channel_source_summary(provider: object, platforms: list[dict[str, Any]]) -> str:
    if platforms:
        return f"{_platform_coverage(platforms)} sources"
    return str(provider or "unknown")


def _top_platform_source(platforms: list[dict[str, Any]], metric: str) -> str:
    available = [
        platform
        for platform in platforms
        if platform.get("status", "available") != "unavailable"
    ]
    if not available:
        return "unavailable"
    top_platform = max(available, key=lambda platform: _plain_number(platform.get(metric, 0)))
    provider = _provider_label(top_platform.get("provider", "unknown"))
    value = str(top_platform.get(metric, "0"))
    return f"{provider} ({value})"


def _insight_empty_state(value: object, empty_label: str) -> str:
    text = str(value)
    if text.lower() in {"", "unavailable", "unknown", "no top content available"}:
        return empty_label
    return text


def _platform_share_models(
    platforms: list[dict[str, Any]],
    totals: dict[str, Any],
) -> list[dict[str, Any]]:
    total_views = _number(totals.get("views", 0))
    total_engagements = _number(totals.get("engagements", 0))
    return [
        {
            **platform,
            "views_share": _share_percent(platform["views"], total_views),
            "engagements_share": _share_percent(
                platform["engagements"],
                total_engagements,
            ),
        }
        for platform in platforms
    ]


def _share_percent(value: object, total: float) -> str:
    if total <= 0:
        return "0.00%"
    return f"{(_plain_number(value) / total) * 100:.2f}%"


def _platforms_with_top_content(
    platforms: list[dict[str, Any]],
    rows: list[object],
) -> list[dict[str, Any]]:
    return [
        {
            **platform,
            "top_content": _top_content_for_provider(rows, platform["provider"]),
            "top_content_url": _top_content_url_for_provider(rows, platform["provider"]),
            "top_content_thumbnail_url": _top_content_thumbnail_for_provider(
                rows,
                platform["provider"],
            ),
            "top_content_type": _top_content_type_for_provider(
                rows,
                platform["provider"],
            ),
            "top_content_views": _top_content_views_for_provider(
                rows,
                platform["provider"],
            ),
            "top_content_published_at": _top_content_date_for_provider(
                rows,
                platform["provider"],
            ),
        }
        for platform in platforms
    ]


def _top_content_for_provider(rows: list[object], provider: object) -> str:
    row = _top_row_for_provider(rows, provider)
    return _content_display_title(row) if row else "unavailable"


def _top_content_date_for_provider(rows: list[object], provider: object) -> str:
    row = _top_row_for_provider(rows, provider)
    if not row:
        return "No date"
    published_at = _optional_text(row.get("published_at"))
    return _format_content_date(published_at) or "No date"


def _top_content_url_for_provider(rows: list[object], provider: object) -> str:
    row = _top_row_for_provider(rows, provider)
    if not row:
        return ""
    return _optional_text(row.get("content_url") or row.get("permalink"))


def _top_content_thumbnail_for_provider(rows: list[object], provider: object) -> str:
    row = _top_row_for_provider(rows, provider)
    if not row:
        return ""
    return _optional_text(row.get("thumbnail_url") or row.get("image_url"))


def _top_content_views_for_provider(rows: list[object], provider: object) -> str:
    row = _top_row_for_provider(rows, provider)
    if not row:
        return "unavailable"
    views = row.get("views")
    if views in (None, "", "<none>"):
        return "unavailable"
    return _display_number(views)


def _top_content_type_for_provider(rows: list[object], provider: object) -> str:
    row = _top_row_for_provider(rows, provider)
    if not row:
        return "unavailable"
    content_type = _optional_text(row.get("content_type") or row.get("media_type"))
    return content_type or "unavailable"


def _top_row_for_provider(rows: list[object], provider: object) -> dict[str, Any] | None:
    provider_key = str(provider).strip().lower()
    for row in rows:
        if not isinstance(row, dict):
            continue
        row_provider = str(row.get("provider", "")).strip().lower()
        if row_provider == provider_key:
            return row
    return None


def _platform_model(platform: dict[str, Any]) -> dict[str, Any]:
    totals = platform.get("totals", {})
    if not isinstance(totals, dict):
        totals = {}
    provider = str(platform.get("provider", "unknown"))
    return {
        "provider": provider,
        "provider_label": _provider_label(provider),
        "status": str(platform.get("status", "available")),
        "records": _display_number(platform.get("records", 0)),
        "views": _display_number(totals.get("views", 0)),
        "views_share": "0.00%",
        "engagements": _display_number(totals.get("engagements", 0)),
        "engagements_share": "0.00%",
        "engagement_rate": f"{_number(totals.get('engagement_rate_percent', 0.0)):.2f}%",
        "followers": _display_number(totals.get("max_followers", 0)),
        "has_followers": bool(platform.get("has_followers", False)),
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
        "max_followers": max(
            (
                _plain_number(platform.get("followers", 0))
                for platform in platforms
                if platform.get("has_followers")
            ),
            default=0,
        ),
        "has_followers": any(platform.get("has_followers") for platform in platforms),
    }


def _row_model(row: object) -> dict[str, str]:
    if not isinstance(row, dict):
        row = {}
    display_title = _content_display_title(row)
    provider = _optional_text(row.get("provider") or row.get("source_provider"))
    return {
        "content_id": str(row.get("content_id", "<none>")),
        "display_title": display_title,
        "thumbnail_url": _optional_text(row.get("thumbnail_url") or row.get("image_url")),
        "content_url": _optional_text(row.get("content_url") or row.get("permalink")),
        "content_type": _optional_text(row.get("content_type") or row.get("type")) or "content",
        "provider": provider,
        "provider_label": _provider_label(provider) if provider else "",
        "published_at": _format_content_date(row.get("published_at")),
        "views": str(row.get("views", 0)),
        "likes": str(row.get("likes", 0)),
        "comments": str(row.get("comments", 0)),
        "shares": str(row.get("shares", 0)),
    }


def _production_total(rows: list[object]) -> str:
    dates = _published_dates(rows)
    if not dates:
        return "No dates"
    return f"{len(dates)} productions"


def _production_scope_label(production: dict[str, Any]) -> str:
    period = _production_period_label(production.get("period"))
    source = _production_source_label(production.get("date_source"))
    dates_count = int(_number(production.get("dates_count", 0)))
    if dates_count:
        return f"{period} from {source} ({dates_count} dated item(s))"
    return f"{period} from {source}"


def _production_period_label(period: object) -> str:
    labels = {"latest_6_months": "Latest 6 months"}
    value = str(period or "").strip()
    return labels.get(value, "Available production window")


def _production_source_label(source: object) -> str:
    labels = {"all_processed_rows": "all processed content"}
    value = str(source or "").strip()
    return labels.get(value, "available content dates")


def _production_summary(rows: list[object]) -> str:
    dates = _published_dates(rows)
    if not dates:
        return "Publication dates unavailable"
    unique_days = len(set(dates))
    return f"{len(dates)} productions across {unique_days} day(s)"


def _production_cadence(rows: list[object]) -> dict[str, str]:
    dates = _published_dates(rows)
    if not dates:
        return {
            "total": "No dates",
            "active_days": "No dates",
            "average_per_active_day": "No dates",
        }
    active_days = len(set(dates))
    return {
        "total": _display_number(len(dates)),
        "active_days": _display_number(active_days),
        "average_per_active_day": f"{len(dates) / active_days:.2f}",
    }


def _production_months(rows: list[object]) -> list[str]:
    dates = _published_dates(rows)
    if not dates:
        return []
    start_day, end_day = _production_window(dates)
    month_names: list[str] = []
    current = dt.date(start_day.year, start_day.month, 1)
    while current <= end_day:
        month_names.append(current.strftime("%b"))
        if current.month == 12:
            current = dt.date(current.year + 1, 1, 1)
        else:
            current = dt.date(current.year, current.month + 1, 1)
    return month_names[-6:]


def _production_days(rows: list[object]) -> list[dict[str, str | int]]:
    dates = _published_dates(rows)
    if not dates:
        return []
    counts: dict[dt.date, int] = {}
    for date in dates:
        counts[date] = counts.get(date, 0) + 1
    start_day, end_day = _production_window(dates)
    max_count = max(counts.values(), default=0)
    days = []
    current = start_day
    while current <= end_day:
        count = counts.get(current, 0)
        days.append(
            {
                "date": current.isoformat(),
                "count": count,
                "level": _production_level(count, max_count),
            }
        )
        current += dt.timedelta(days=1)
    return days


def _published_dates(rows: list[object]) -> list[dt.date]:
    dates = []
    for row in rows:
        if isinstance(row, str):
            date = _parse_date(row)
            if date:
                dates.append(date)
            continue
        if not isinstance(row, dict):
            continue
        value = row.get("published_at")
        if not value:
            continue
        date = _parse_date(value)
        if date:
            dates.append(date)
    return dates


def _parse_date(value: object) -> dt.date | None:
    try:
        return dt.datetime.fromisoformat(str(value).replace("Z", "+00:00")).date()
    except ValueError:
        return None


def _production_window(dates: list[dt.date]) -> tuple[dt.date, dt.date]:
    end_day = max(dates)
    start_day = end_day - dt.timedelta(days=181)
    start_day -= dt.timedelta(days=start_day.weekday())
    return start_day, end_day


def _production_level(count: int, max_count: int) -> int:
    if count < 1 or max_count < 1:
        return 0
    return min(4, max(1, math.ceil((count / max_count) * 4)))


def _json_script_payload(channels: list[dict[str, Any]]) -> str:
    payload = json.dumps(channels, ensure_ascii=True)
    return (
        payload.replace("&", "\\u0026")
        .replace("<", "\\u003c")
        .replace(">", "\\u003e")
        .replace("</", "<\\/")
    )


def _channel_image_markup(channel: dict[str, Any]) -> str:
    image_url = _renderable_image_url(channel.get("image_url"))
    name = channel.get("name", "unknown")
    if image_url:
        alt_name = str(name)
        if not alt_name.lower().endswith("channel"):
            alt_name = f"{alt_name} channel"
        return (
            f'<img class="channel-image" src="{_text(image_url)}" '
            f'alt="{_text(alt_name)} image">'
        )
    initial = _text(channel.get("initial", "?"))
    return f'<div class="channel-image channel-fallback" aria-label="Channel image">{initial}</div>'


def _channel_options(channels: list[dict[str, Any]]) -> str:
    return "\n".join(
        f'<option value="{index}">{_text(channel["name"])}</option>'
        for index, channel in enumerate(channels)
    )


def _channel_option_cards(channels: list[dict[str, Any]]) -> str:
    return "\n".join(
        _channel_option_card(index, channel) for index, channel in enumerate(channels)
    )


def _channel_option_card(index: int, channel: dict[str, Any]) -> str:
    active_class = " active" if index == 0 else ""
    return f"""
<button class="channel-option-card{active_class}" type="button"
  data-channel-option data-channel-index="{index}">
  {_channel_image_markup(channel)}
  <span class="channel-option-copy">
    <strong>{_text(channel["name"])}</strong>
    <span>{_text(channel["source_summary"])}</span>
  </span>
</button>"""


def _metric_card(label: str, value: object, accent: bool, data_attr: str) -> str:
    accent_class = " accent" if accent else ""
    return (
        f'<article class="card metric-card{accent_class}">'
        f'<div class="label">{_text(label)}</div>'
        f'<div class="value" {data_attr}>{_text(value)}</div>'
        '<div class="metric-spark" aria-hidden="true">'
        '<span style="height: 45%"></span>'
        '<span style="height: 72%"></span>'
        '<span style="height: 56%"></span>'
        '<span style="height: 88%"></span>'
        "</div>"
        "</article>"
    )


def _metric_item(label: str, value: object, data_attr: str) -> str:
    return (
        '<div class="quality-item">'
        f'<span class="label">{_text(label)}</span>'
        f'<strong {data_attr}>{_text(value)}</strong>'
        "</div>"
    )


def _insight_item(
    label: str,
    value: object,
    data_attr: str,
    variant: str,
    marker: str,
) -> str:
    return (
        f'<article class="insight-card {_text(variant)}">'
        '<span class="insight-label">'
        f'<span class="insight-marker" aria-hidden="true">{_text(marker)}</span>'
        f"{_text(label)}"
        "</span>"
        f"<strong {data_attr}>{_text(value)}</strong>"
        "</article>"
    )


def _cadence_item(
    label: str,
    value: object,
    data_attr: str,
    variant: str,
    marker: str,
) -> str:
    return (
        f'<article class="cadence-card {_text(variant)}">'
        '<span class="cadence-label">'
        f'<span class="cadence-marker" aria-hidden="true">{_text(marker)}</span>'
        f"{_text(label)}"
        "</span>"
        f"<strong {data_attr}>{_text(value)}</strong>"
        "</article>"
    )


def _channel_table_rows(channel: dict[str, Any]) -> str:
    rows = channel.get("top_rows", [])
    if not isinstance(rows, list) or not rows:
        return _empty_table_row()
    return "\n".join(_table_row(index, row) for index, row in enumerate(rows, start=1))


def _top_content_gallery(channel: dict[str, Any]) -> str:
    rows = channel.get("top_rows", [])
    if not isinstance(rows, list) or not rows:
        return '<p class="content-card-empty">No top content available for this channel.</p>'
    return "".join(_top_content_card(index, row) for index, row in enumerate(rows[:3], start=1))


def _top_content_card(rank: int, row: object) -> str:
    if not isinstance(row, dict):
        row = {}
    title = _text(row.get("display_title", "<none>"))
    url = _optional_text(row.get("content_url"))
    thumbnail_url = _renderable_image_url(row.get("thumbnail_url"))
    content_type = _text(row.get("content_type", "content"))
    media = (
        f'<img src="{_text(thumbnail_url)}" alt="{title} thumbnail">'
        if thumbnail_url
        else f'<div class="content-card-fallback">{content_type}</div>'
    )
    title_markup = (
        f'<a class="content-card-title" href="{_text(url)}" target="_blank" '
        f'rel="noreferrer">{title}</a>'
        if url
        else f'<span class="content-card-title">{title}</span>'
    )
    meta_parts = [
        str(value)
        for value in (
            row.get("provider_label") or _provider_label(row.get("provider")),
            row.get("published_at"),
            f'{row.get("views", 0)} views',
        )
        if value
    ]
    return (
        '<article class="content-card">'
        '<div class="content-card-media">'
        f"{media}"
        f'<span class="rank-badge content-card-rank">#{_text(rank)}</span>'
        "</div>"
        f"{title_markup}"
        f'<div class="content-card-meta">{_text(" | ".join(meta_parts))}</div>'
        "</article>"
    )


def _top_row_count_label(channel: dict[str, Any]) -> str:
    rows = channel.get("top_rows", [])
    count = len(rows) if isinstance(rows, list) else 0
    suffix = "" if count == 1 else "s"
    return f"{count} ranked item{suffix}"


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
                    "provider_label": _provider_label(provider),
                    "status": "unavailable",
                    "records": "No data",
                    "views": "No data",
                    "views_share": "No data",
                    "engagements": "No data",
                    "engagements_share": "No data",
                    "engagement_rate": "No data",
                    "top_content": "No data",
                    "top_content_url": "",
                    "top_content_thumbnail_url": "",
                    "top_content_type": "No data",
                    "top_content_views": "No data",
                    "top_content_published_at": "No date",
                },
            )
        )
        for provider in ("youtube", "tiktok", "instagram")
    )


def _platform_comparison_charts(channel: dict[str, Any]) -> str:
    platforms = channel.get("platforms", [])
    if not isinstance(platforms, list):
        platforms = []
    return "".join(
        [
            _platform_metric_chart("Views", platforms, "views"),
            _platform_metric_chart("Engagements", platforms, "engagements"),
            _platform_metric_chart("Productions", platforms, "records"),
        ]
    )


def _platform_metric_chart(title: str, platforms: list[object], metric: str) -> str:
    rows = _platform_metric_rows(platforms, metric)
    available_rows = [row for row in rows if row["available"]]
    if not available_rows:
        body = '<p class="platform-chart-empty">No platform metrics available.</p>'
    else:
        max_value = max((row["value"] for row in available_rows), default=1)
        body = "".join(_platform_metric_row(row, max_value) for row in rows)
    return f'<article class="platform-chart"><h3>{_text(title)}</h3>{body}</article>'


def _platform_metric_rows(platforms: list[object], metric: str) -> list[dict[str, object]]:
    available = {
        platform.get("provider"): platform
        for platform in platforms
        if isinstance(platform, dict) and platform.get("status", "available") != "unavailable"
    }
    rows = []
    for provider in ("youtube", "tiktok", "instagram"):
        platform = available.get(provider)
        value = _plain_number(platform.get(metric, 0)) if platform else 0
        rows.append(
            {
                "provider": provider,
                "provider_label": _provider_label(provider),
                "value": value,
                "label": str(platform.get(metric, "No data")) if platform else "No data",
                "available": platform is not None,
            }
        )
    return rows


def _platform_metric_row(row: dict[str, object], max_value: float) -> str:
    width = 0 if not row["available"] else max(4, (_number(row["value"]) / max(max_value, 1)) * 100)
    return (
        '<div class="platform-chart-row">'
        f'<span class="platform-chart-label">{_text(row["provider_label"])}</span>'
        '<div class="platform-chart-track">'
        f'<div class="platform-chart-fill" style="width: {width:.2f}%"></div>'
        "</div>"
        f'<span class="platform-chart-value">{_text(row["label"])}</span>'
        "</div>"
    )


def _view_bars(channel: dict[str, Any]) -> str:
    rows = channel.get("top_rows", [])
    if not isinstance(rows, list) or not rows:
        return '<p class="meta">No ranked content available for this chart.</p>'
    max_views = max(
        (_plain_number(row.get("views", 0)) for row in rows if isinstance(row, dict)),
        default=1,
    )
    max_views = max(max_views, 1)
    bars = []
    for row in rows[:6]:
        if not isinstance(row, dict):
            continue
        views = _plain_number(row.get("views", 0))
        width = max(4, (views / max_views) * 100)
        bars.append(
            '<div class="chart-row">'
            f'<span class="chart-label">{_text(row.get("display_title", "<none>"))}</span>'
            '<div class="chart-track">'
            f'<div class="chart-fill" style="width: {width:.2f}%"></div>'
            "</div>"
            f'<span class="chart-value">{_text(row.get("views", 0))}</span>'
            "</div>"
        )
    return '<div class="chart-bars">' + "".join(bars) + "</div>"


def _engagement_donuts(channel: dict[str, Any]) -> str:
    metrics = [
        ("Likes", channel.get("likes_percent", "0.00%")),
        ("Comments", channel.get("comments_percent", "0.00%")),
        ("Shares", channel.get("shares_percent", "0.00%")),
    ]
    items = []
    for label, value in metrics:
        percent = min(100, _percent_number(value))
        items.append(
            '<div class="donut">'
            f'<div class="donut-ring" style="--value: {percent:.2f}">'
            f"<strong>{_text(value)}</strong>"
            "</div>"
            f"<span>{_text(label)}</span>"
            "</div>"
        )
    return '<div class="donut-grid">' + "".join(items) + "</div>"


def _production_calendar(channel: dict[str, Any]) -> str:
    days = channel.get("production_days", [])
    if not isinstance(days, list) or not days:
        return '<p class="meta">No publication dates available for this report.</p>'
    months = channel.get("production_months", [])
    if not isinstance(months, list):
        months = []
    month_markup = "".join(f"<span>{_text(month)}</span>" for month in months)
    day_markup = "".join(
        (
            f'<span class="production-day level-{_text(day.get("level", 0))}" '
            f'title="{_text(day.get("date", "unknown"))}: '
            f'{_text(day.get("count", 0))} production(s)" '
            f'aria-label="{_text(day.get("date", "unknown"))}: '
            f'{_text(day.get("count", 0))} production(s)"></span>'
        )
        for day in days
        if isinstance(day, dict)
    )
    return f"""<div class="production-heatmap">
  <div class="production-months">{month_markup}</div>
  <div class="production-grid">{day_markup}</div>
  <div class="production-footer">
    <span>{_text(channel.get("production_summary", ""))}</span>
    <div class="production-legend">
      <span>Less</span>
      <span class="production-day level-0"></span>
      <span class="production-day level-1"></span>
      <span class="production-day level-2"></span>
      <span class="production-day level-3"></span>
      <span class="production-day level-4"></span>
      <span>More</span>
    </div>
  </div>
</div>"""


def _platform_card(platform: dict[str, Any]) -> str:
    unavailable = " unavailable" if platform.get("status") == "unavailable" else ""
    provider_label = _provider_label(platform.get("provider", "unknown"))
    status_label = "No data" if platform.get("status") == "unavailable" else platform.get(
        "status",
        "unknown",
    )
    if platform.get("status") == "unavailable":
        return f"""<article class="platform-card{unavailable}">
  <div class="platform-title">
    <strong>{_text(provider_label)}</strong>
    <span class="platform-status">{_text(status_label)}</span>
  </div>
  <p class="platform-empty-note">No source data for this channel yet.</p>
</article>"""
    return f"""<article class="platform-card{unavailable}">
  <div class="platform-title">
    <strong>{_text(provider_label)}</strong>
    <span class="platform-status">{_text(status_label)}</span>
  </div>
  {_metric_item("Productions", platform.get("records", "unavailable"), "")}
  {_metric_item("Views", platform.get("views", "unavailable"), "")}
  {_metric_item("View share", platform.get("views_share", "unavailable"), "")}
  {_metric_item("Engagements", platform.get("engagements", "unavailable"), "")}
  {_metric_item("Engagement share", platform.get("engagements_share", "unavailable"), "")}
  {_metric_item("Performance", platform.get("engagement_rate", "unavailable"), "")}
  {_platform_top_content_thumbnail(platform)}
  {_platform_top_content_item(platform)}
  {_metric_item("Top content type", platform.get("top_content_type", "unavailable"), "")}
  {_metric_item("Top content views", platform.get("top_content_views", "unavailable"), "")}
  {_metric_item(
        "Top content date",
        platform.get("top_content_published_at", "unavailable"),
        "",
    )}
</article>"""


def _platform_top_content_thumbnail(platform: dict[str, Any]) -> str:
    value = str(platform.get("top_content", "unavailable"))
    thumbnail_url = _renderable_image_url(platform.get("top_content_thumbnail_url"))
    if not thumbnail_url or value == "unavailable":
        return ""
    return (
        '<div class="platform-content-preview">'
        f'<img src="{_text(thumbnail_url)}" alt="{_text(value)} thumbnail">'
        "</div>"
    )


def _platform_top_content_item(platform: dict[str, Any]) -> str:
    value = str(platform.get("top_content", "unavailable"))
    url = _optional_text(platform.get("top_content_url"))
    if url and value != "unavailable":
        content = (
            f'<a href="{_text(url)}" target="_blank" rel="noreferrer">'
            f"{_text(value)}</a>"
        )
    else:
        content = _text(value)
    return (
        '<div class="quality-item">'
        '<span class="label">Top content</span>'
        f"<strong>{content}</strong>"
        "</div>"
    )


def _display_number(value: object) -> str:
    number = _number(value)
    if number.is_integer():
        return f"{int(number):,}"
    return f"{number:,.2f}"


def _plain_number(value: object) -> float:
    if isinstance(value, str):
        value = value.replace(",", "")
    return _number(value)


def _percent_number(value: object) -> float:
    if isinstance(value, str):
        value = value.replace("%", "")
    return _plain_number(value)


def _card(label: str, value: object) -> str:
    return (
        '<article class="card">'
        f'<div class="label">{_text(label)}</div>'
        f'<div class="value">{_text(value)}</div>'
        "</article>"
    )


def _table_row(rank: int, row: object) -> str:
    if not isinstance(row, dict):
        row = {}
    row_class = ' class="winner-row"' if rank == 1 else ""
    return (
        f"<tr{row_class}>"
        f'<td><span class="rank-badge">#{_text(rank)}</span></td>'
        f"<td>{_content_cell(row)}</td>"
        f"<td>{_text(row.get('published_at', ''))}</td>"
        f"<td>{_text(row.get('views', 0))}</td>"
        f"<td>{_text(row.get('likes', 0))}</td>"
        f"<td>{_text(row.get('comments', 0))}</td>"
        f"<td>{_text(row.get('shares', 0))}</td>"
        "</tr>"
    )


def _empty_table_row() -> str:
    return (
        '<tr class="empty-row">'
        '<td colspan="7">No top content rows available for this report.</td>'
        "</tr>"
    )


def _source_image(source: object) -> str:
    if not isinstance(source, dict):
        source = {}
    image_url = _renderable_image_url(source.get("image_url") or source.get("channel_image_url"))
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
            return _safe_artifact_label(artifact, escape=escape)
    artifact = payload.get("artifact")
    if artifact in (None, ""):
        return "unknown"
    return _safe_artifact_label(artifact, escape=escape)


def _safe_artifact_label(value: object, escape: bool = True) -> str:
    label = str(value).replace("\\", "/").rstrip("/").split("/")[-1]
    if not label:
        label = "unknown"
    return _text(label) if escape else label


def _top_content_label(top_content: object, escape: bool = True) -> str:
    if not isinstance(top_content, dict):
        return "No top content available"
    title = _content_display_title(top_content)
    if title in ("", "<none>"):
        return "No top content available"
    return _text(title) if escape else title


def _content_cell(row: dict[str, Any]) -> str:
    title = _content_display_title(row)
    url = _optional_text(row.get("content_url") or row.get("permalink"))
    thumbnail_url = _renderable_image_url(row.get("thumbnail_url") or row.get("image_url"))
    content_type = _optional_text(row.get("content_type") or row.get("type")) or "content"
    provider = _optional_text(row.get("provider") or row.get("source_provider"))
    thumb = (
        f'<img class="content-thumb" src="{_text(thumbnail_url)}" '
        f'alt="{_text(title)} thumbnail">'
        if thumbnail_url
        else f'<div class="content-thumb fallback">{_text(content_type)}</div>'
    )
    title_markup = (
        f'<a class="content-title" href="{_text(url)}" target="_blank" '
        f'rel="noreferrer">{_text(title)}</a>'
        if url
        else f'<span class="content-title">{_text(title)}</span>'
    )
    meta_parts = []
    if provider:
        meta_parts.append(f"Platform: {_provider_label(provider)}")
    meta = (
        f'<span class="content-meta">{_text(" | ".join(meta_parts))}</span>'
        if meta_parts
        else ""
    )
    return f'<div class="content-cell">{thumb}<div>{title_markup}{meta}</div></div>'


def _renderable_image_url(value: object) -> str:
    image_url = _optional_text(value)
    if not image_url:
        return ""
    lowered = image_url.lower()
    if "://example.com/" in lowered or "://example.test/" in lowered:
        return ""
    return image_url


def _content_display_title(row: dict[str, Any]) -> str:
    for key in ("display_title", "title", "content_title", "name", "caption"):
        value = row.get(key)
        if value not in (None, "", "<none>"):
            return str(value)
    content_id = row.get("content_id")
    return str(content_id) if content_id not in (None, "", "<none>") else "<none>"


def _optional_text(value: object) -> str:
    return "" if value in (None, "", "<none>") else str(value)


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


def _provider_label(provider: object) -> str:
    provider_name = str(provider or "").strip()
    if not provider_name:
        return ""
    labels = {
        "youtube": "YouTube",
        "tiktok": "TikTok",
        "instagram": "Instagram",
        "multi-platform": "Multi-platform",
    }
    return labels.get(provider_name.lower(), provider_name.title())


def _format_content_date(value: object) -> str:
    raw_value = _optional_text(value)
    if not raw_value:
        return ""
    normalized = raw_value[:-1] + "+00:00" if raw_value.endswith("Z") else raw_value
    try:
        published_at = dt.datetime.fromisoformat(normalized)
    except ValueError:
        return raw_value
    return f"{published_at:%b} {published_at.day}, {published_at:%Y}"


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


def _quality_status_label(value: object) -> str:
    labels = {
        "ok": "Ready",
        "empty": "No records",
        "unknown": "Unknown",
    }
    return labels.get(str(value).lower(), str(value))


def _availability_label(value: object) -> str:
    return "Available" if value is True else "Missing"


if __name__ == "__main__":
    raise SystemExit(cli_entrypoint())
