"""PySide6 desktop window for the FYP risk tool.

    python -m gui.qt_app            # opens the desktop window
    python -m gui.qt_app --smoke F  # headless self-test; writes a JSON result to F and exits

The window hosts the existing offline interface (gui/static, served by gui.api on 127.0.0.1) in Qt
WebEngine, so the desktop app and the browser version are the same tool with the same engine
(app.service.run_case).  Nothing is sent over the network: the server listens on 127.0.0.1 only.
Exports (register.md, CSV, report, case JSON ...) open a normal "Save file" dialog.
"""
from __future__ import annotations

import argparse
import json
import os
import sys
import threading
import urllib.request
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

TITLE = "FYP - Brickwork Delay-Risk Decision Support"


def start_server():
    """Start the local Flask server in a background thread. Returns (server, url)."""
    from werkzeug.serving import make_server

    from gui.__main__ import DEFAULT_PORT, HOST, choose_port
    from gui.api import create_app

    port = choose_port(DEFAULT_PORT)
    server = make_server(HOST, port, create_app(), threaded=True)
    threading.Thread(target=server.serve_forever, name="fyp-server", daemon=True).start()
    return server, f"http://{HOST}:{server.server_port}/"


def main(argv=None) -> int:
    ap = argparse.ArgumentParser(prog="python -m gui.qt_app", description=TITLE)
    ap.add_argument("--smoke", metavar="FILE", help="headless self-test; write the result as JSON to FILE")
    args, qt_argv = ap.parse_known_args(argv)

    if args.smoke:                                   # must be set before Qt starts
        os.environ.setdefault("QT_QPA_PLATFORM", "offscreen")
        os.environ.setdefault("QTWEBENGINE_CHROMIUM_FLAGS", "--disable-gpu --no-sandbox")

    from PySide6.QtCore import QTimer, QUrl
    from PySide6.QtGui import QDesktopServices
    from PySide6.QtWebEngineCore import QWebEnginePage, QWebEngineProfile
    from PySide6.QtWebEngineWidgets import QWebEngineView
    from PySide6.QtWidgets import QApplication, QFileDialog

    server, url = start_server()
    app = QApplication([sys.argv[0], *qt_argv])
    app.setApplicationName("FYP Risk Tool")
    app.aboutToQuit.connect(lambda: threading.Thread(target=server.shutdown, daemon=True).start())

    profile = QWebEngineProfile("fyp-risk-tool")     # named profile: settings (theme etc.) persist between runs
    windows = []

    class Page(QWebEnginePage):
        def acceptNavigationRequest(self, qurl, nav_type, is_main_frame):
            # Anything that is not the local tool opens in the normal browser.
            if qurl.scheme() in ("http", "https") and qurl.host() not in ("127.0.0.1", "localhost"):
                QDesktopServices.openUrl(qurl)
                return False
            return super().acceptNavigationRequest(qurl, nav_type, is_main_frame)

    class View(QWebEngineView):
        def __init__(self):
            super().__init__()
            self.setPage(Page(profile, self))
            self.setWindowTitle(TITLE)
            self.resize(1440, 900)

        def createWindow(self, _window_type):        # target=_blank / window.open
            v = View()
            windows.append(v)
            v.show()
            return v

    def on_download(req):
        suggested = req.suggestedFileName() or "download"
        start_dir = Path.home() / "Downloads"
        start = str((start_dir if start_dir.is_dir() else Path.home()) / suggested)
        path, _ = QFileDialog.getSaveFileName(main_view, "Save file", start)
        if not path:
            req.cancel()
            return
        p = Path(path)
        req.setDownloadDirectory(str(p.parent))
        req.setDownloadFileName(p.name)
        req.accept()

    profile.downloadRequested.connect(on_download)

    main_view = View()
    windows.append(main_view)
    main_view.load(QUrl(url))

    if args.smoke:
        result = {"url": url, "ok": False}

        def finish(code):
            Path(args.smoke).write_text(json.dumps(result, indent=2), encoding="utf-8")
            app.exit(code)

        def check_dom():
            main_view.page().runJavaScript(
                "JSON.stringify({title: document.title, buttons: document.querySelectorAll('button').length,"
                " text: document.body ? document.body.innerText.length : 0})",
                on_dom,
            )

        def on_dom(value):
            try:
                result["dom"] = json.loads(value)
            except Exception as e:                   # noqa: BLE001
                result["dom_error"] = str(e)
            try:
                with urllib.request.urlopen(url + "api/health", timeout=10) as r:
                    result["health"] = json.loads(r.read().decode("utf-8"))
            except Exception as e:                   # noqa: BLE001
                result["health_error"] = str(e)
            dom, health = result.get("dom", {}), result.get("health", {})
            result["ok"] = bool(dom.get("buttons", 0) > 3 and dom.get("text", 0) > 50
                                and health.get("evidence_records", 0) > 0)
            finish(0 if result["ok"] else 1)

        def on_loaded(ok):
            result["load_ok"] = bool(ok)
            if not ok:
                finish(1)
                return
            QTimer.singleShot(4000, check_dom)       # let the single-page app render

        main_view.loadFinished.connect(on_loaded)
        QTimer.singleShot(120_000, lambda: (result.setdefault("error", "timeout"), finish(2)))
    else:
        main_view.show()

    return app.exec()


if __name__ == "__main__":
    sys.exit(main())
