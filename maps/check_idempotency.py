#!/usr/bin/env python3
"""Run the repair pipeline twice and prove it changes nothing the second time.

A repair that is not idempotent is a repair that keeps editing the data, and one
of these was not: `state_agree` was *converted* rather than computed, so the
second run read the stored 0/1 and turned every True into False. The column
stayed a BOOLEAN, its NULL count stayed plausible and every type check passed -
29,470 values were simply gone. This script is the check that would have caught
it: fingerprint every row of every layer, run the pipeline, fingerprint again,
and fail if anything but the timestamps moved.

Run:  python check_idempotency.py      (writes idempotency_check.json, exits 1 on a diff)
"""
import hashlib
import json
import pathlib
import subprocess
import sys

HERE = pathlib.Path(__file__).parent
GPKG = HERE / "Nigeria_Geology_Minerals_4326.gpkg"
OUT = HERE / "idempotency_check.json"
PIPELINE = ["normalise_nulls.py", "repair_layers.py", "describe_layers.py",
            "fix_gpkg_hygiene.py"]


def fingerprint():
    """sha256 of every row of every table, timestamps aside."""
    import sqlite3
    con = sqlite3.connect(GPKG)
    tables = [r[0] for r in con.execute(
        "SELECT table_name FROM gpkg_contents ORDER BY 1")]
    prints = {}
    for t in tables:
        h = hashlib.sha256()
        for row in con.execute(f'SELECT * FROM "{t}" ORDER BY rowid'):
            h.update(repr(tuple(row)).encode())
        prints[t] = h.hexdigest()[:16]
    con.close()
    return prints


before = fingerprint()
for script in PIPELINE:
    subprocess.run([sys.executable, str(HERE / script)], check=True,
                   stdout=subprocess.DEVNULL)
after = fingerprint()

changed = {t: [before[t], after.get(t)] for t in before if before[t] != after.get(t)}
result = {"rows_fingerprinted": len(before), "changed": changed,
          "pipeline": PIPELINE, "idempotent": not changed}
json.dump(result, open(OUT, "w"), indent=1)

print(f"{len(before)} tables fingerprinted, {len(changed)} changed by a second run")
for t, (a, b) in changed.items():
    print(f"  ! {t}: {a} -> {b}")
print("\nidempotent" if not changed else "\nNOT idempotent")
sys.exit(1 if changed else 0)
