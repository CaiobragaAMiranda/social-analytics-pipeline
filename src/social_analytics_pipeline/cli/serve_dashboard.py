import argparse
import functools
import sys
from http.server import SimpleHTTPRequestHandler, ThreadingHTTPServer
from ipaddress import ip_address
from pathlib import Path
from urllib.parse import quote

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
    root = project_root or Path.cwd()
    dashboard_path = output_path if output_path.is_absolute() else root / output_path
    if generate_smoke:
        dashboard_path = run_dashboard_smoke(root, output_path).dashboard_path

    url = dashboard_url(root, dashboard_path, host, port)
    print(f"dashboard_url={url}")
    if not start_server:
        return 0

    print("Press Ctrl+C to stop the dashboard server.")
    try:
        serve_directory(root, host, port)
    except OSError as exc:
        print(f"Error: could not bind dashboard server at {host}:{port}: {exc}", file=sys.stderr)
        return 1
    except KeyboardInterrupt:
        return 0
    return 0


def dashboard_url(project_root: Path, dashboard_path: Path, host: str, port: int) -> str:
    try:
        relative_path = dashboard_path.relative_to(project_root)
    except ValueError:
        relative_path = dashboard_path.name
    path_text = relative_path.as_posix() if isinstance(relative_path, Path) else relative_path
    quoted_path = quote(path_text)
    try:
        display_host = "localhost" if ip_address(host).is_unspecified else host
    except ValueError:
        display_host = host
    return f"http://{display_host}:{port}/{quoted_path}"


def serve_directory(project_root: Path, host: str, port: int) -> None:
    handler = functools.partial(SimpleHTTPRequestHandler, directory=str(project_root))
    with ThreadingHTTPServer((host, port), handler) as server:
        server.serve_forever()


def parse_args(argv: list[str] | None = None) -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Serve the local static dashboard on localhost."
    )
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
