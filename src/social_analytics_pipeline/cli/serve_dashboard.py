import argparse
import datetime as dt
import json
import sys
from http.server import SimpleHTTPRequestHandler, ThreadingHTTPServer
from ipaddress import ip_address
from pathlib import Path
from urllib.parse import quote

from social_analytics_pipeline.cli.channel_catalog import (
    add_channel,
    collection_plan,
    list_channels,
    load_collection_status,
    record_collection_status,
    remove_channel,
    rename_channel,
    set_channel_image,
    set_channel_schedule,
    set_platform_enabled,
    set_platform_reference,
)
from social_analytics_pipeline.cli.dashboard_smoke import (
    DEFAULT_SMOKE_DASHBOARD_OUTPUT,
    run_dashboard_smoke,
)
from social_analytics_pipeline.cli.instagram_local_pipeline import (
    resolve_instagram_interval,
    run_instagram_local_pipeline,
)
from social_analytics_pipeline.cli.youtube_local_pipeline import run_youtube_local_pipeline
from social_analytics_pipeline.cli.youtube_smoke import build_runtime_env, resolve_backfill_interval
from social_analytics_pipeline.providers import (
    InstagramApiConfig,
    InstagramGraphApiProvider,
    YouTubeApiConfig,
    YouTubeDataApiProvider,
)

DEFAULT_COLLECTION_LOOKBACK_DAYS = 180


def main(
    project_root: Path | None = None,
    output_path: Path = DEFAULT_SMOKE_DASHBOARD_OUTPUT,
    host: str = "127.0.0.1",
    port: int = 8000,
    generate_smoke: bool = True,
    start_server: bool = True,
) -> int:
    root = (project_root or Path.cwd()).resolve()
    dashboard_path = (output_path if output_path.is_absolute() else root / output_path).resolve()
    if not _is_inside_project_root(root, dashboard_path):
        print("Error: dashboard output must be inside the project root.", file=sys.stderr)
        return 1
    if generate_smoke:
        dashboard_path = run_dashboard_smoke(root, output_path).dashboard_path
    elif not dashboard_path.is_file():
        print(
            f"Error: dashboard output not found: {_display_dashboard_path(root, dashboard_path)}",
            file=sys.stderr,
        )
        return 1

    url = dashboard_url(root, dashboard_path, host, port)
    print(f"dashboard_url={url}")
    if not start_server:
        return 0

    print("Press Ctrl+C to stop the dashboard server.")
    try:
        serve_directory(root, host, port, root / "config" / "channels.local.json")
    except OSError as exc:
        print(f"Error: could not bind dashboard server at {host}:{port}: {exc}", file=sys.stderr)
        return 1
    except KeyboardInterrupt:
        return 0
    return 0


def dashboard_url(project_root: Path, dashboard_path: Path, host: str, port: int) -> str:
    quoted_path = quote(_display_dashboard_path(project_root, dashboard_path))
    try:
        address = ip_address(host)
        if address.is_unspecified:
            display_host = "localhost"
        elif address.version == 6:
            display_host = f"[{host}]"
        else:
            display_host = host
    except ValueError:
        display_host = host
    return f"http://{display_host}:{port}/{quoted_path}"


def _display_dashboard_path(project_root: Path, dashboard_path: Path) -> str:
    try:
        relative_path = dashboard_path.relative_to(project_root)
    except ValueError:
        relative_path = dashboard_path.name
    return relative_path.as_posix() if isinstance(relative_path, Path) else relative_path


def _is_inside_project_root(project_root: Path, dashboard_path: Path) -> bool:
    try:
        dashboard_path.relative_to(project_root)
    except ValueError:
        return False
    return True


def serve_directory(
    project_root: Path,
    host: str,
    port: int,
    catalog_path: Path,
) -> None:
    handler = _dashboard_handler(project_root, catalog_path)
    with ThreadingHTTPServer((host, port), handler) as server:
        server.serve_forever()


def _dashboard_handler(project_root: Path, catalog_path: Path):
    status_path = catalog_path.with_name("collection_status.local.json")

    class DashboardHandler(SimpleHTTPRequestHandler):
        def __init__(self, *args, **kwargs):
            super().__init__(*args, directory=str(project_root), **kwargs)

        def do_GET(self) -> None:
            if self.path != "/api/channels":
                super().do_GET()
                return
            self._send_json(
                200,
                {
                    "channels": [
                        _channel_payload(channel, status_path)
                        for channel in list_channels(catalog_path)
                    ]
                },
            )

        def do_POST(self) -> None:
            if self.path != "/api/channels":
                self._send_json(404, {"error": "Unknown API endpoint."})
                return
            try:
                payload = json.loads(self.rfile.read(int(self.headers.get("Content-Length", "0"))))
                result = _apply_catalog_action(catalog_path, payload, project_root)
            except (RuntimeError, ValueError, json.JSONDecodeError) as exc:
                self._send_json(400, {"error": str(exc)})
                return
            self._send_json(200, result)

        def _send_json(self, status: int, payload: dict) -> None:
            body = json.dumps(payload).encode("utf-8")
            self.send_response(status)
            self.send_header("Content-Type", "application/json")
            self.send_header("Content-Length", str(len(body)))
            self.end_headers()
            self.wfile.write(body)

    return DashboardHandler


def _apply_catalog_action(
    catalog_path: Path,
    payload: object,
    project_root: Path | None = None,
) -> dict:
    if not isinstance(payload, dict):
        raise ValueError("Catalog request must contain an object.")
    action = payload.get("action")
    channel_id = str(payload.get("id", ""))
    if action == "add":
        add_channel(catalog_path, channel_id, str(payload.get("name", "")))
    elif action == "rename":
        rename_channel(catalog_path, channel_id, str(payload.get("name", "")))
    elif action == "image":
        set_channel_image(catalog_path, channel_id, str(payload.get("image_url", "")))
    elif action == "remove":
        remove_channel(catalog_path, channel_id)
    elif action in {"enable", "disable"}:
        set_platform_enabled(
            catalog_path, channel_id, str(payload.get("provider", "")), action == "enable"
        )
    elif action == "schedule":
        set_channel_schedule(catalog_path, channel_id, str(payload.get("schedule", "")))
    elif action == "reference":
        set_platform_reference(
            catalog_path,
            channel_id,
            str(payload.get("provider", "")),
            str(payload.get("reference", "")),
        )
    elif action == "collect":
        plan = collection_plan(catalog_path, channel_id)
        collection_results = _collect_ready_sources(project_root or catalog_path.parent, plan)
        status = record_collection_status(
            catalog_path.with_name("collection_status.local.json"),
            channel_id,
            collection_results,
        )
        return {
            "channel_id": channel_id,
            "sources": list(collection_results),
            "status": status["channels"].get(channel_id, {}),
        }
    else:
        raise ValueError("Unsupported catalog action.")
    status_path = catalog_path.with_name("collection_status.local.json")
    return {
        "channels": [
            _channel_payload(channel, status_path) for channel in list_channels(catalog_path)
        ]
    }


def _collect_ready_sources(
    project_root: Path,
    plan: tuple[dict[str, object], ...],
) -> tuple[dict[str, object], ...]:
    return tuple(_collect_ready_source(project_root, source) for source in plan)


def _collect_ready_source(project_root: Path, source: dict[str, object]) -> dict[str, object]:
    result = dict(source)
    if not source.get("selected"):
        result["collection_status"] = "pending"
        result["outcome"] = "Missing enabled public source reference"
        return result

    provider = str(source.get("provider", ""))
    if provider == "instagram":
        try:
            summary = _run_instagram_catalog_collection(project_root)
        except RuntimeError as exc:
            result["collection_status"] = "failed"
            result["outcome"] = _safe_collection_error(exc)
            return result

        result["collection_status"] = "ok"
        result["outcome"] = "Instagram collection completed"
        result["loaded_records"] = summary.result.loaded_records
        return result

    if provider != "youtube":
        result["collection_status"] = "failed"
        result["outcome"] = "Provider dispatch is not implemented yet"
        return result

    try:
        summary = _run_youtube_catalog_collection(project_root, str(source.get("reference", "")))
    except RuntimeError as exc:
        result["collection_status"] = "failed"
        result["outcome"] = _safe_collection_error(exc)
        return result

    result["collection_status"] = "ok"
    result["outcome"] = "YouTube collection completed"
    result["loaded_records"] = summary.result.loaded_records
    return result


def _run_youtube_catalog_collection(project_root: Path, reference: str):
    runtime_env = build_runtime_env(None, project_root / ".env")
    provider = YouTubeDataApiProvider(YouTubeApiConfig.from_env(runtime_env))
    channel_id = provider.resolve_channel_reference(reference)
    interval = resolve_backfill_interval(runtime_env)
    if interval:
        start_at, end_at = interval
    else:
        lookback_days = _collection_lookback_days(runtime_env)
        end_at = dt.datetime.now(dt.UTC)
        start_at = end_at - dt.timedelta(days=lookback_days)
    return run_youtube_local_pipeline(
        provider=provider,
        channel_id=channel_id,
        start_at=start_at,
        end_at=end_at,
        project_root=project_root,
    )


def _run_instagram_catalog_collection(project_root: Path):
    runtime_env = build_runtime_env(None, project_root / ".env")
    provider = InstagramGraphApiProvider(InstagramApiConfig.from_env(runtime_env))
    start_at, end_at = resolve_instagram_interval(runtime_env)
    return run_instagram_local_pipeline(
        provider=provider,
        account_id=provider.config.account_id,
        start_at=start_at,
        end_at=end_at,
        project_root=project_root,
    )


def _collection_lookback_days(runtime_env: dict[str, str]) -> int:
    raw_value = runtime_env.get(
        "CATALOG_COLLECTION_LOOKBACK_DAYS",
        runtime_env.get("YOUTUBE_SMOKE_LOOKBACK_DAYS", str(DEFAULT_COLLECTION_LOOKBACK_DAYS)),
    )
    try:
        value = int(raw_value)
    except ValueError as exc:
        raise RuntimeError("CATALOG_COLLECTION_LOOKBACK_DAYS must be an integer.") from exc
    if value < 1:
        raise RuntimeError("CATALOG_COLLECTION_LOOKBACK_DAYS must be greater than or equal to 1.")
    return value


def _safe_collection_error(exc: RuntimeError) -> str:
    message = str(exc)
    if "YOUTUBE_API_KEY" in message:
        return "YouTube credentials are missing or invalid"
    if "INSTAGRAM_ACCESS_TOKEN" in message or "INSTAGRAM_USER_ID" in message:
        return "Instagram credentials are missing or invalid"
    return message


def _channel_payload(channel, status_path: Path | None = None) -> dict:
    status_payload = load_collection_status(status_path) if status_path else {"channels": {}}
    channel_status = status_payload.get("channels", {}).get(channel.channel_id, {})
    source_statuses = channel_status.get("sources", {})
    return {
        "id": channel.channel_id,
        "name": channel.display_name,
        "image_url": channel.image_url,
        "schedule": channel.schedule,
        "platforms": {
            platform.provider: {
                "enabled": platform.enabled,
                "ready": bool(platform.enabled and platform.handle),
                "reference": platform.handle,
                "status": source_statuses.get(platform.provider, {}),
            }
            for platform in channel.platforms
        },
    }


def parse_args(argv: list[str] | None = None) -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Serve the local static dashboard on localhost.")
    parser.add_argument(
        "--project-root",
        type=Path,
        default=Path.cwd(),
        help="Project root to serve. Defaults to the current directory.",
    )
    parser.add_argument(
        "--output",
        type=Path,
        default=DEFAULT_SMOKE_DASHBOARD_OUTPUT,
        help=f"Dashboard output path. Defaults to {DEFAULT_SMOKE_DASHBOARD_OUTPUT}.",
    )
    parser.add_argument("--host", default="127.0.0.1", help="Host to bind.")
    parser.add_argument("--port", type=int, default=8000, help="Port to bind.")
    parser.add_argument(
        "--no-smoke",
        action="store_true",
        help="Serve the existing dashboard output without regenerating smoke data.",
    )
    return parser.parse_args(argv)


def cli_entrypoint() -> int:
    args = parse_args()
    return main(
        project_root=args.project_root,
        output_path=args.output,
        host=args.host,
        port=args.port,
        generate_smoke=not args.no_smoke,
    )


if __name__ == "__main__":
    raise SystemExit(cli_entrypoint())
