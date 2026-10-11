import json, csv, math
d=json.load(open('work/report.json'))
units=[tuple(u) for u in d['units']]; K=len(units)
rows=d['rows']; NC,NR=d['grid']; CW,CH=d['cw'],d['ch']; H,W=d['shape']
def U(k): return f'U{k+1:02d}'
def hexc(c): return '#%02X%02X%02X'%tuple(c)

tot=sum(r['n'] for r in rows)
geo=sum(r['geopx'] for r in rows); nod=sum(r['nodata'] for r in rows)
chg=sum(r['chg'] for r in rows); ov=sum(r['ov'] for r in rows); gp=sum(r['gp'] for r in rows)
ag=sum(r['ag'] for r in rows); tt=sum(r['tot'] for r in rows)
fp=sum(r['fp'] for r in rows); fn=sum(r['fn'] for r in rows)

L=[]
L.append('# NGSA geological map — v1 → v2 cell-by-cell comparison atlas')
L.append('')
L.append('**Grid:** columns **A–L** (12), rows **1–7** (7) — 84 cells, Excel style, applied over the full')
L.append(f'**{W} × {H}** px canvas. Cell size **{CW:.1f} × {CH:.1f} px**.')
L.append('')
L.append('Because `pic NGSA geological-map-of-nigeria-.jpg` is the *same* rendering, merely cropped at')
L.append('offset **(dx = +120, dy = +96)**, the NGSA reference was cropped to that identical frame')
L.append('(`pic_NGSA_grid.png`) so that **cell A1 means the same pixels in all three pictures**.')
L.append('')
L.append('## What v2 changes')
L.append('')
L.append('| item | value |')
L.append('|---|---|')
L.append(f'| geology (mapped) pixels | {geo:,} ({100*geo/tot:.2f}%) |')
L.append(f'| no-data (unmapped / non-geology sheet area) | {nod:,} ({100*nod/tot:.2f}%) |')
L.append(f'| overlay removed (graticule, labels, roads, edge fringe) | {ov:,} ({100*ov/tot:.2f}%) |')
L.append(f'| interior gaps filled | {gp:,} ({100*gp/tot:.2f}%) |')
L.append(f'| total pixels changed vs v1 | {chg:,} ({100*chg/tot:.2f}%) |')
L.append(f'| structural agreement v2 ↔ NGSA | **{100*ag/tt:.2f}%** |')
L.append(f'| v2 shows geology where NGSA does not | {fp:,} px (½-res) |')
L.append(f'| NGSA shows geology where v2 does not | {fn:,} px (½-res) |')
L.append('')
L.append('**Legend for the per-cell connection lines**')
L.append('')
L.append('- `aligned` — a unit sits on *both* sides of the shared cell edge at the *same* place:')
L.append('  the feature is continuous across the border → **connection established**. Length in px of the shared edge segment.')
L.append('- `offset` — the unit occurs on both sides of the border but not opposite itself: same unit continues')
L.append('  into the neighbour, displaced. Check the neighbour to confirm.')
L.append('- `ends` — the unit reaches the border of this cell but is **absent from the neighbour entirely**:')
L.append('  the feature genuinely terminates at the cell edge.')
L.append('')
L.append('---')
L.append('')
L.append('## Unit palette (canonical flat colours taken from the map, ranked by area)')
L.append('')
L.append('| id | colour | swatch | % of map area |')
L.append('|---|---|---|---|')
for k,c in enumerate(units):
    L.append(f'| {U(k)} | `rgb{c}` | {hexc(c)} | — |')
L.append('')

L.append('---')
L.append('')
L.append('## Cells, in working order (A1 → B1 → C1 … → L7)')
L.append('')
for r in rows:
    c=r['cell']
    L.append(f"### {c}  —  x {r['x0']}–{r['x1']}, y {r['y0']}–{r['y1']}")
    L.append('')
    gpct=100*r['geopx']/r['n']; ndct=100*r['nodata']/r['n']
    if r['geopx']==0:
        L.append('**Empty cell** — no mapped geology. Entirely sheet / legend / unmapped area; filled with the no-data tone.')
        L.append('')
        continue
    L.append(f"- mapped geology **{gpct:.1f}%**, no-data **{ndct:.1f}%**, distinct units **{len(r['polys'])}**")
    L.append(f"- v1 → v2: **{r['chg']:,} px** changed (overlay removed {r['ov']:,}, gaps filled {r['gp']:,})")
    L.append(f"- agreement with NGSA reference: **{100*r['ag']/max(r['tot'],1):.1f}%**")
    L.append('')
    L.append('| unit | colour | area px | % cell | polygons ≥200 px | largest |')
    L.append('|---|---|---|---|---|---|')
    items=sorted(((int(k),v) for k,v in r['polys'].items()), key=lambda t:-t[1][0])
    for k,(area,npoly,big) in items[:14]:
        L.append(f'| {U(k)} | {hexc(units[k])} `rgb{units[k]}` | {area:,} | {100*area/r["n"]:.2f}% | {npoly} | {big:,} |')
    L.append('')
    for cn in r['conn']:
        L.append(f"- **{cn['dir']} → {cn['nb']}**")
        if cn.get('corner'):
            of=', '.join(U(int(k)) for k in cn['offset'][:10])
            tm=', '.join(U(int(k)) for k in cn['term'][:10])
            L.append(f"  - *corner contact only (no shared edge)*")
            L.append(f"  - unit also present in the {cn['nb']} corner: {of if of else '— none —'}")
            if tm: L.append(f"  - not carried into {cn['nb']} corner: {tm}")
            continue
        al=', '.join(f'{U(int(k))} {v}px' for k,v in sorted(cn['aligned'].items(), key=lambda t:-int(t[1]))[:6])
        of=', '.join(U(int(k)) for k in cn['offset'][:8])
        tm=', '.join(U(int(k)) for k in cn['term'][:8])
        L.append(f"  - aligned (continuous): {al if al else '— none —'}")
        if of: L.append(f"  - offset (same unit, displaced): {of}")
        if tm: L.append(f"  - ends at edge (absent from {cn['nb']}): {tm}")
    L.append('')
L.append('---')
L.append('')
L.append('## Summary matrix — mapped-geology coverage (%)')
L.append('')
def cell_at(i,j): return [x for x in rows if x['cell']==f'{chr(65+i)}{j+1}'][0]
L.append('| | ' + ' | '.join(chr(65+i) for i in range(NC)) + ' |')
L.append('|' + '---|'*(NC+1))
for j in range(NR):
    L.append('| **%d** | '%(j+1) + ' | '.join(f"{100*cell_at(i,j)['geopx']/cell_at(i,j)['n']:.0f}" for i in range(NC)) + ' |')
L.append('')
L.append('## Summary matrix — agreement with NGSA (%)')
L.append('')
L.append('| | ' + ' | '.join(chr(65+i) for i in range(NC)) + ' |')
L.append('|' + '---|'*(NC+1))
for j in range(NR):
    parts=[]
    for i in range(NC):
        rr=cell_at(i,j)
        parts.append(f"{100*rr['ag']/rr['tot']:.0f}" if rr['tot']>200 else '—')
    L.append('| **%d** | '%(j+1) + ' | '.join(parts) + ' |')
L.append('')
open('CELL_BY_CELL_REPORT.md','w').write('\n'.join(L))
print('cells',len(rows),'lines',len(L))

with open('cell_inventory.csv','w',newline='') as fh:
    wtr=csv.writer(fh)
    wtr.writerow(['cell','x0','x1','y0','y1','geology_px','nodata_px','units','changed_vs_v1','overlay_removed','gaps_filled','agree_with_NGSA_pct'])
    for r in rows:
        wtr.writerow([r['cell'],r['x0'],r['x1'],r['y0'],r['y1'],r['geopx'],r['nodata'],len(r['polys']),r['chg'],r['ov'],r['gp'],round(100*r['ag']/max(r['tot'],1),2)])
print('csv written')
