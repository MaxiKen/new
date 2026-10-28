#!/usr/bin/env python3
"""Reproduce the seven-place Natural Earth diagnostic, not a CRS identification."""
import csv, math, statistics
from pathlib import Path

F = Path(__file__).resolve().parent / 'Natural_Earth_town_comparison.csv'
names = {'Bama', 'Biu', 'Idah', 'Iseyin', 'Nguru', 'Ogbomosho', 'Orlu'}
with F.open(newline='', encoding='utf-8') as f:
    rows = [r for r in csv.DictReader(f) if r['map_name'] in names]
if len(rows) != 7:
    raise ValueError('Expected the seven reviewed candidate rows')

def distance(x, y, u, v):
    h = math.sin(math.radians(v-y)/2)**2 + math.cos(math.radians(y))*math.cos(math.radians(v))*math.sin(math.radians(u-x)/2)**2
    return 12742.0176*math.asin(min(1, math.sqrt(h)))

print('Selected:', ', '.join(r['map_name'] for r in rows))
for col in ('geology_vs_NE_km','minerals_grid_vs_NE_km','minerals_embedded_vs_NE_km','maps_embedded_vs_geology_km'):
    print(col, 'median km:', round(statistics.median(float(r[col]) for r in rows), 2))
for prefix in ('geology_grid','minerals_grid','minerals_embedded_raw'):
    residuals=[]
    for held in rows:
        training=[r for r in rows if r is not held]
        dx=statistics.median(float(r['ne_lon'])-float(r[prefix+'_lon']) for r in training)
        dy=statistics.median(float(r['ne_lat'])-float(r[prefix+'_lat']) for r in training)
        residuals.append(distance(float(held[prefix+'_lon'])+dx,float(held[prefix+'_lat'])+dy,float(held['ne_lon']),float(held['ne_lat'])))
    print(prefix, 'leave-one-out translation residual median, max km:', round(statistics.median(residuals),2), round(max(residuals),2))
print('Caution: seven candidates, approximate markers, selected by name and proximity; not a verified CRS or correction.')
