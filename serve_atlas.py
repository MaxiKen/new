#!/usr/bin/env python3
"""Live preview server for the Nigeria geology and minerals atlas.

Serves the comparison viewer, and on request renders a fresh high-zoom crop of the original
sheet around any coordinate, so the page compares a picture of the printed map with the
digitised result at the same spot, live.

    python3 serve_atlas.py            # http://0.0.0.0:8080

Endpoints
  /                     the viewer
  /data/*               exported layers, sheet renders, statistics
  /api/crop             ?lon=&lat=&r=&src=minerals|geology  -> PNG with a crosshair
  /api/health           liveness + asset report
"""
import io, json, os
from http.server import SimpleHTTPRequestHandler, ThreadingHTTPServer
from pathlib import Path
from urllib.parse import urlparse, parse_qs

import pymupdf
from PIL import Image, ImageDraw

ROOT = Path(__file__).resolve().parent
WEB = ROOT / "web"
PORT = int(os.environ.get("PORT", "8080"))

PDFS = {
    "minerals": ROOT / "Mineral_Resources_Map_of_Nigeria_2023.pdf",
    "geology": ROOT / "Geological_Map_of_Nigeria.pdf",
}


def ll_to_page(lon, lat, src):
    """lon/lat -> page points, using the registration each sheet was digitised with."""
    if src == "geology":
        return lon * 157.593 - 276.36, 2281.63 - lat * 157.586
    return (74.23969 + (lon - 2.47619) / 12.54519 * 1976.9518,
            358.7239 + (14.04668 - lat) / 10.20997 * 1608.9773)


_DOCS = {}


def crop_png(lon, lat, radius_pt, src, zoom):
    doc = _DOCS.get(src)
    if doc is None:
        doc = _DOCS[src] = pymupdf.open(PDFS[src])
    page = doc[0]
    x, y = ll_to_page(lon, lat, src)
    clip = pymupdf.Rect(x - radius_pt, y - radius_pt, x + radius_pt, y + radius_pt)
    pix = page.get_pixmap(matrix=pymupdf.Matrix(zoom, zoom), clip=clip, alpha=False)
    im = Image.frombytes("RGB", (pix.width, pix.height), pix.samples)
    d = ImageDraw.Draw(im)
    cx, cy = pix.width / 2, pix.height / 2
    arm = pix.width * 0.28
    # crosshair with a gap in the middle, so the symbol under it stays visible
    for dx0, dy0, dx1, dy1 in ((-arm, 0, -6, 0), (6, 0, arm, 0), (0, -arm, 0, -6), (0, 6, 0, arm)):
        d.line([(cx + dx0, cy + dy0), (cx + dx1, cy + dy1)], fill=(255, 0, 220), width=2)
    d.ellipse([cx - 5, cy - 5, cx + 5, cy + 5], outline=(255, 0, 220), width=2)
    buf = io.BytesIO()
    im.save(buf, "PNG", optimize=True)
    return buf.getvalue()


class Handler(SimpleHTTPRequestHandler):
    def __init__(self, *a, **kw):
        super().__init__(*a, directory=str(WEB), **kw)

    def log_message(self, fmt, *args):
        print("%s - %s" % (self.address_string(), fmt % args), flush=True)

    def _json(self, obj, code=200):
        body = json.dumps(obj).encode()
        self.send_response(code)
        self.send_header("Content-Type", "application/json")
        self.send_header("Content-Length", str(len(body)))
        self.send_header("Cache-Control", "no-store")
        self.end_headers()
        self.wfile.write(body)

    def do_GET(self):
        u = urlparse(self.path)
        if u.path == "/api/health":
            data = WEB / "data"
            files = {p.name: p.stat().st_size for p in sorted(data.glob("*"))} if data.exists() else {}
            return self._json({"ok": True, "port": PORT, "assets": files,
                               "pdfs": {k: v.exists() for k, v in PDFS.items()}})
        if u.path == "/api/crop":
            q = parse_qs(u.query)
            try:
                lon = float(q.get("lon", ["8"])[0])
                lat = float(q.get("lat", ["9"])[0])
                r = max(4.0, min(40.0, float(q.get("r", ["16"])[0])))
                zoom = max(3.0, min(14.0, float(q.get("zoom", ["8"])[0])))
                src = q.get("src", ["minerals"])[0]
                if src not in PDFS:
                    return self._json({"error": "unknown src"}, 400)
                png = crop_png(lon, lat, r, src, zoom)
            except Exception as exc:                      # noqa: BLE001 - report, do not die
                return self._json({"error": str(exc)}, 400)
            self.send_response(200)
            self.send_header("Content-Type", "image/png")
            self.send_header("Content-Length", str(len(png)))
            self.send_header("Cache-Control", "no-store")
            self.end_headers()
            self.wfile.write(png)
            return
        if u.path in ("", "/"):
            self.path = "/index.html"
        return super().do_GET()


if __name__ == "__main__":
    print(f"atlas viewer on http://0.0.0.0:{PORT}  (serving {WEB})", flush=True)
    ThreadingHTTPServer(("0.0.0.0", PORT), Handler).serve_forever()
