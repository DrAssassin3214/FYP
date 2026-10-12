"""Start the local GUI:  python -m gui  [--port 8765] [--no-browser] [--verbose]

Serves on 127.0.0.1 only (never on the network), picks the next free port if the preferred one is
busy, opens the default browser and shuts down cleanly on Ctrl+C.
"""
from __future__ import annotations

import argparse
import logging
import signal
import socket
import sys
import threading
import webbrowser
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

HOST = "127.0.0.1"
DEFAULT_PORT = 8765


def _port_free(port: int) -> bool:
    """True if nothing listens on the port and it can be bound exclusively.
    (On Windows SO_REUSEADDR lets a second server bind a busy port, so probe explicitly.)"""
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
        s.settimeout(0.3)
        if s.connect_ex((HOST, port)) == 0:
            return False
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
        if hasattr(socket, "SO_EXCLUSIVEADDRUSE"):
            s.setsockopt(socket.SOL_SOCKET, socket.SO_EXCLUSIVEADDRUSE, 1)
        try:
            s.bind((HOST, port))
            return True
        except OSError:
            return False


def choose_port(preferred: int) -> int:
    for p in range(preferred, preferred + 20):
        if _port_free(p):
            return p
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:     # let the OS pick one
        s.bind((HOST, 0))
        return s.getsockname()[1]


def _interrupt(signum, frame):
    raise KeyboardInterrupt


def main(argv=None) -> int:
    ap = argparse.ArgumentParser(prog="python -m gui", description="Brick-masonry delay-risk decision support (local GUI)")
    ap.add_argument("--port", type=int, default=DEFAULT_PORT, help=f"preferred port (default {DEFAULT_PORT}; next free port is used if busy)")
    ap.add_argument("--no-browser", action="store_true", help="do not open the browser automatically")
    ap.add_argument("--verbose", action="store_true", help="log every HTTP request")
    a = ap.parse_args(argv)

    from werkzeug.serving import make_server

    from gui import __version__
    from gui.api import ai_status, create_app

    logging.basicConfig(level=logging.INFO, format="%(levelname)s %(name)s: %(message)s")
    logging.getLogger("werkzeug").setLevel(logging.INFO if a.verbose else logging.WARNING)

    app = create_app()
    port = choose_port(a.port)
    server = make_server(HOST, port, app, threaded=True)
    url = f"http://{HOST}:{server.server_port}/"

    signal.signal(signal.SIGINT, _interrupt)
    if hasattr(signal, "SIGBREAK"):                  # Ctrl+Break on Windows consoles
        signal.signal(signal.SIGBREAK, _interrupt)

    print(f"Masonry delay-risk decision support GUI v{__version__}")
    print(f"  Serving on {url}  (this computer only)")
    if server.server_port != a.port:
        print(f"  Port {a.port} was busy; using {server.server_port}.")
    print(f"  {ai_status()['label']}")
    print("  Press Ctrl+C to stop.", flush=True)
    if not a.no_browser:
        threading.Timer(0.6, lambda: webbrowser.open(url)).start()
    try:
        server.serve_forever()
    except KeyboardInterrupt:
        print("\nShutting down...", flush=True)
    finally:
        server.server_close()
    print("Server stopped.", flush=True)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
