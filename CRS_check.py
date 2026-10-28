#!/usr/bin/env python3
"""Inspect the two map PDFs and recompute the two alternative registrations.

Requires PyMuPDF: python -m pip install pymupdf
Run from this directory: python CRS_check.py
This is a numerical diagnostic, NOT a datum transformation or a GIS overlay.
"""
import csv
import hashlib
import math
import re
import statistics
from pathlib import Path

import pymupdf

ROOT = Path(__file__).resolve().parent
FILES = ['Geological_Map_of_Nigeria.pdf', 'Mineral_Resources_Map_of_Nigeria_2023.pdf']


def array(text, name):
    match = re.search(r'/' + name + r'\s*\[([^\]]+)\]', text, re.S)
    if not match:
        raise ValueError('Missing ' + name)
    return [float(s) for s in match.group(1).split()]


def km(lon1, lat1, lon2, lat2):
    h = (math.sin(math.radians(lat2 - lat1) / 2) ** 2 +
         math.cos(math.radians(lat1)) * math.cos(math.radians(lat2)) *
         math.sin(math.radians(lon2 - lon1) / 2) ** 2)
    return 12742.0176 * math.asin(min(1, math.sqrt(h)))


def main():
    docs = []
    for name in FILES:
        path = ROOT / name
        doc = pymupdf.open(path)
        docs.append(doc)
        page = doc[0]
        data = path.read_bytes()
        print('\n' + name, '\n SHA256', hashlib.sha256(data).hexdigest())
        print(' creator:', doc.metadata.get('creator'), 'page:', page.rect)
        print(' page dictionary:', doc.xref_object(page.xref))
        for i in range(1, doc.xref_length()):
            obj = doc.xref_object(i)
            if '/Subtype /GEO' in obj or '/Type /GEOGCS' in obj:
                print(' xref', i, obj)

    doc = docs[1]
    page = doc[0]
    page_obj = doc.xref_object(page.xref)
    bbox = array(page_obj, 'BBox')
    measure_refs = re.findall(r'/Measure\s+(\d+)\s+\d+\s+R', page_obj)
    if len(measure_refs) != 1:
        raise ValueError('Expected one indirect geographic Measure')
    measure = doc.xref_object(int(measure_refs[0]))
    gpts, lpts = array(measure, 'GPTS'), array(measure, 'LPTS')
    # Guard against silently using the wrong coordinate order or viewport.
    if len(bbox) != 4 or len(gpts) != 8 or lpts != [0, 1, 0, 0, 1, 0, 1, 1]:
        raise ValueError('Unexpected viewport / tie-point arrangement')
    if not (gpts[0] == gpts[6] and gpts[2] == gpts[4] and
            gpts[1] == gpts[3] and gpts[5] == gpts[7]):
        raise ValueError('Unexpected geographic control point arrangement')
    # Esri's viewport BBox here has upper y before lower y. Page coordinates
    # below are PyMuPDF top-left coordinates; GeoPDF GPTS pairs are lat, lon.
    xleft, yhigh_pdf, xright, ylow_pdf = bbox
    top = page.rect.height - yhigh_pdf
    bottom = page.rect.height - ylow_pdf
    south, west, north, east = gpts[0], gpts[1], gpts[2], gpts[5]

    def embedded(x, y):
        return (west + (x - xleft) * (east - west) / (xright - xleft),
                north - (y - top) * (north - south) / (bottom - top))

    print('\nPrinted mineral meridians compared with embedded measure:')
    for deg in (4, 6, 8, 10, 12, 14):
        x = 157.5987 * deg - 288.95
        print(f' {deg}°E, x={x:.3f} pt: embedded longitude {embedded(x, top)[0]:.6f}°E')

    with (ROOT / 'Town_comparison_three_sources.csv').open(newline='', encoding='utf-8') as f:
        rows = list(csv.DictReader(f))
    checked = [r for r in rows if r['review_status'].startswith('visually')]
    print('\nVisually checked sample (positions still approximate):')
    distances = []
    for r in checked:
        x = float(r['minerals_estimated_marker_lon']) * 157.5987 - 288.95
        y = 2572.35 - float(r['minerals_estimated_marker_lat']) * 157.6015
        lon, lat = embedded(x, y)
        separation = km(float(r['geology_lon']), float(r['geology_lat']), lon, lat)
        distances.append(separation)
        print(f" {r['map_town_name']}: embedded raw ({lon:.5f}, {lat:.5f}); "
              f"to geology {separation:.2f} km; graticule-based {r['geology_vs_minerals_km']} km")
    if distances:
        print(' sample median, embedded raw:', round(statistics.median(distances), 2), 'km')
    print('\nThese are numerical comparisons, not validated CRS transformations.')


if __name__ == '__main__':
    main()
