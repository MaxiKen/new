import sys, csv, numpy as np, geopandas as gpd
sys.path.insert(0, '/home/user/work')
from legend_tables import P2_ROWS, P1_LABELS, P2_TO_P1, load_colors
p2c, p1c = load_colors()
EXTRA = {41: [45], 43: [45], 11: [51], 25: [53], 61: [69]}
gdf = gpd.read_file('/home/user/work/out/nigeria_geology.gpkg', layer='nigeria_geology')
names = set(gdf.name)
A = np.load('/home/user/work/cluster_assign.npz'); gid1 = A['gid1']
out = '/home/user/work/out/'
with open(out + 'legend_p2_crosswalk.csv', 'w', newline='') as f:
    w = csv.writer(f)
    w.writerow(['p2_row', 'code', 'legend_label', 'colour_hex', 'p1_entry', 'p1_entry_label', 'p1_extra_entries', 'label_has_polygon'])
    for r, code, lab in P2_ROWS:
        p1 = P2_TO_P1.get(r)
        w.writerow([r, code, lab, '#%02x%02x%02x' % tuple(int(v) for v in p2c[r - 1]), p1 or '', P1_LABELS[p1 - 1] if p1 else '', ';'.join(str(e) for e in EXTRA.get(r, [])), 'yes' if lab in names else 'no'])
inv = {}
for r, j in P2_TO_P1.items(): inv.setdefault(j, []).append(r)
for r, js in EXTRA.items():
    for j in js: inv.setdefault(j, []).append(r)
with open(out + 'legend_p1_crosswalk.csv', 'w', newline='') as f:
    w = csv.writer(f)
    w.writerow(['p1_entry', 'p1_label', 'colour_hex', 'colour_group', 'mapped_p2_rows'])
    for j in range(1, 87):
        w.writerow([j, P1_LABELS[j - 1], '#%02x%02x%02x' % tuple(int(v) for v in p1c[j - 1]), int(gid1[j - 1]) + 1, ';'.join(str(r) for r in sorted(set(inv.get(j, []))))])
print('tables written')
