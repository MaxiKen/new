#!/usr/bin/env python3
"""
Fetch the pinned source extraction that build_combined.py reads.

Why this exists
---------------
This repository's own PDFs are drawings, not data: they carry no attribute
tables, so unit codes, ages and mineral names have to be reconstructed from
layer names, the legend and in-polygon labels.  That reconstruction was done
once, in the sibling repository MaxiKen/site, and published as

    nigeria_maps.gpkg   (40+ layers, 21 MB)

build_combined.py consumes that file rather than doing the extraction again.
To keep the build reproducible, the source is pinned to one commit and its
checksum is verified here.

Usage
    python fetch_source.py [--dest ./source_extraction]

Then
    python build_combined.py            # defaults to ./source_extraction/nigeria_maps.gpkg
    python anchor_to_icons.py
    python render_combined.py
"""
import argparse
import hashlib
import pathlib
import subprocess
import sys

REPO = "https://github.com/MaxiKen/site.git"
COMMIT = "138e9619fb8c1fad257f8cdefd3d03c51f6fb5c6"
FILE = "nigeria_maps.gpkg"
SHA256 = "7f5e05799981da54a133c646c86967ca8b623d5cddd78924d4f1ee48056a18da"

HERE = pathlib.Path(__file__).parent


def sha256(path):
    h = hashlib.sha256()
    with open(path, "rb") as f:
        for chunk in iter(lambda: f.read(1 << 20), b""):
            h.update(chunk)
    return h.hexdigest()


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--dest", default=str(HERE / "source_extraction"))
    ap.add_argument("--force", action="store_true")
    args = ap.parse_args()

    dest = pathlib.Path(args.dest)
    dest.mkdir(parents=True, exist_ok=True)
    target = dest / FILE

    if target.exists() and not args.force:
        got = sha256(target)
        if got == SHA256:
            print(f"already present and verified: {target}")
            return 0
        print(f"checksum mismatch on existing file ({got[:16]}...), re-fetching")

    with subprocess.Popen(["git", "clone", "--filter=blob:none", "--no-checkout", REPO, str(dest / "_repo")],
                          stdout=subprocess.PIPE, stderr=subprocess.STDOUT, text=True) as p:
        for line in p.stdout:
            print("   ", line.rstrip())

    subprocess.run(["git", "fetch", "--depth", "1", "origin", COMMIT],
                   cwd=dest / "_repo", check=True)
    out = subprocess.run(["git", "show", f"{COMMIT}:{FILE}"],
                         cwd=dest / "_repo", check=True, capture_output=True)
    target.write_bytes(out.stdout)

    got = sha256(target)
    if got != SHA256:
        print(f"ERROR: checksum mismatch\n  expected {SHA256}\n  got      {got}")
        return 1
    print(f"fetched and verified {target}  ({target.stat().st_size / 1e6:.1f} MB)")
    print(f"  repo {REPO} @ {COMMIT[:12]}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
