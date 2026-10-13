#!/usr/bin/env python3
"""Serve this folder locally so offline map images can be sampled safely."""
from functools import partial
from http.server import SimpleHTTPRequestHandler, ThreadingHTTPServer
from pathlib import Path
import threading
import webbrowser

HOST = "127.0.0.1"
PORT = 8765
ROOT = Path(__file__).resolve().parent


def main() -> None:
    handler = partial(SimpleHTTPRequestHandler, directory=str(ROOT))
    try:
        server = ThreadingHTTPServer((HOST, PORT), handler)
    except OSError as error:
        raise SystemExit(
            f"Could not start the offline launcher on port {PORT}: {error}\n"
            "Close the other app using that port, then try again. The fixed port keeps your local notes on the same browser origin."
        ) from error

    url = f"http://{HOST}:{PORT}/"
    print(f"Offline Field Notes is ready at {url}")
    print("Keep this window open while using the app. Press Ctrl+C to stop.")
    threading.Timer(0.6, lambda: webbrowser.open(url, new=2)).start()
    try:
        server.serve_forever()
    except KeyboardInterrupt:
        print("\nStopping the local server…")
    finally:
        server.server_close()


if __name__ == "__main__":
    main()
