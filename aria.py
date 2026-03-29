"""
ARIA — Launcher
Run:  python aria.py
      Opens the browser dashboard automatically.
"""

import sys
import os
import subprocess
import socket

# ── Auto-install required packages if missing ─────────────────────────────────
REQUIRED = ["fastapi", "uvicorn", "httpx", "pydantic"]

def ensure_packages():
    missing = []
    for pkg in REQUIRED:
        try:
            __import__(pkg)
        except ImportError:
            missing.append(pkg)
    if missing:
        print(f"[ARIA] Installing missing packages: {', '.join(missing)}")
        subprocess.check_call(
            [sys.executable, "-m", "pip", "install"] + missing,
            stdout=subprocess.DEVNULL,
            stderr=subprocess.DEVNULL,
        )
        print("[ARIA] Packages installed.\n")

ensure_packages()

# ── Now safe to import everything ─────────────────────────────────────────────
import argparse
import threading
import time
import platform

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

import uvicorn
from server import app
import config as _cfg


# ══════════════════════════════════════════════════════════════════════════════
# FREE PORT FINDER
# ══════════════════════════════════════════════════════════════════════════════

def find_free_port(start: int = 8000, end: int = 8020) -> int:
    """Try ports from start to end, return the first one that is free."""
    for port in range(start, end):
        with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
            s.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
            try:
                s.bind(("127.0.0.1", port))
                return port          # port is free
            except OSError:
                continue             # port in use, try next
    raise RuntimeError(f"No free port found between {start} and {end}. "
                       "Close other applications and try again.")


# ══════════════════════════════════════════════════════════════════════════════
# BROWSER OPENER  — silent on Windows (no CMD flash)
# ══════════════════════════════════════════════════════════════════════════════

def open_browser(url: str, delay: float = 1.5):
    def _go():
        time.sleep(delay)
        system = platform.system()
        try:
            if system == "Windows":
                os.startfile(url)
            elif system == "Darwin":
                subprocess.Popen(["open", url],
                                 stdout=subprocess.DEVNULL,
                                 stderr=subprocess.DEVNULL)
            else:
                subprocess.Popen(["xdg-open", url],
                                 stdout=subprocess.DEVNULL,
                                 stderr=subprocess.DEVNULL)
        except Exception:
            import webbrowser
            webbrowser.open(url)
    threading.Thread(target=_go, daemon=True).start()


# ══════════════════════════════════════════════════════════════════════════════
# ENTRY POINT
# ══════════════════════════════════════════════════════════════════════════════

def main():
    parser = argparse.ArgumentParser(description="ARIA — Autonomous Revenue Intelligence Agent")
    parser.add_argument("--host",       default="127.0.0.1", help="Bind host  (default: 127.0.0.1)")
    parser.add_argument("--port",       default=None, type=int, help="Port (default: auto-detect free port)")
    parser.add_argument("--no-browser", action="store_true",   help="Don't auto-open the browser")
    args = parser.parse_args()

    host = args.host

    # Auto-find a free port if not specified or if specified port is busy
    if args.port:
        # Check if user-specified port is free
        with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
            try:
                s.bind((host, args.port))
                port = args.port
            except OSError:
                print(f"[ARIA] Port {args.port} is in use. Finding a free port...")
                port = find_free_port()
                print(f"[ARIA] Using port {port} instead.\n")
    else:
        port = find_free_port()

    url = f"http://{host}:{port}"

    print(f"""
+----------------------------------------------------------+
|   ARIA  -  Autonomous Revenue Intelligence Agent         |
+----------------------------------------------------------+

  Dashboard  ->  {url}
  API docs   ->  {url}/docs
  Health     ->  {url}/health

  Provider   :  Groq
  Model      :  {_cfg.MODEL_NAME}

  Opening browser UI...
  Press Ctrl+C to stop.
+----------------------------------------------------------+
""")

    if not args.no_browser:
        open_browser(url)

    uvicorn.run(
        "server:app",
        host=host,
        port=port,
        reload=False,
        log_level="warning",
    )


if __name__ == "__main__":
    main()
