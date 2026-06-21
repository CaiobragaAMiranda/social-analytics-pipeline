import argparse
import json
import sys
from http.server import SimpleHTTPRequestHandler, ThreadingHTTPServer
from ipaddress import ip_address
from pathlib import Path
from urllib.parse import quote

from social_analytics_pipeline.cli.channel_catalog import (
    add_channel,
    list_channels,
    remove_channel,
    rename_channel,
    set_platform_enabled,
)
from social_analytics_pipeline.cli.dashboard_smoke import (
    DEFAULT_SMOKE_DASHBOARD_OUTPUT,
    run_dashboard_smoke,
)


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
                        _channel_payload(channel) for channel in list_channels(catalog_path)
                    ]
                },
            )

        def do_POST(self) -> None:
            if self.path != "/api/channels":
                self._send_json(404, {"error": "Unknown API endpoint."})
                return
            try:
                payload = json.loads(self.rfile.read(int(self.headers.get("Content-Length", "0"))))
                result = _apply_catalog_action(catalog_path, payload)
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


def _apply_catalog_action(catalog_path: Path, payload: object) -> dict:
    if not isinstance(payload, dict):
        raise ValueError("Catalog request must contain an object.")
    action = payload.get("action")
    channel_id = str(payload.get("id", ""))
    if action == "add":
        add_channel(catalog_path, channel_id, str(payload.get("name", "")))
    elif action == "rename":
        rename_channel(catalog_path, channel_id, str(payload.get("name", "")))
    elif action == "remove":
        remove_channel(catalog_path, channel_id)
    elif action in {"enable", "disable"}:
        set_platform_enabled(
            catalog_path, channel_id, str(payload.get("provider", "")), action == "enable"
        )
    else:
        raise ValueError("Unsupported catalog action.")
    return {"channels": [_channel_payload(channel) for channel in list_channels(catalog_path)]}


def _channel_payload(channel) -> dict:
    return {
        "id": channel.channel_id,
        "name": channel.display_name,
        "image_url": channel.image_url,
        "platforms": {
            platform.provider: {"enabled": platform.enabled} for platform in channel.platforms
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
