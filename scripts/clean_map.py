"""Revision 9 cleaning: remove road, railway and river printing from the sheet.

Version 1 of ``NGSA_map_geology_legend_isolated`` is the source photograph whose
mapped area was repainted from a per-pixel palette classification. That repainting
dropped black ink, but three kinds of printing survived it, and the reviewer can
still find them on the map:

``rivers``      river and channel strokes are blue, not black, so they matched
                the mapped-water palette entry and were kept as thin blue
                ribbons (and, where a channel was too faint, as a pale one);
``casing``      the pale fill between a road's two edge lines matched a pale
                sand/clay entry and stayed after the dark lines were healed;
``shading``     ridge hatching, heavy casing and label halos matched the gray
                crystalline entries (dolerite, Bauchite quartz-diorite,
                syenite) which the version-1 legend counts show carry almost no
                real geology.

Cleaning is driven by the derived sheet, because that is what is wrong, and the
source photograph is used only as *evidence* that a thin structure is printing.
Five tests are applied, each of which must also pass a local-width and
long-axis test:

1. dark or neutral pixels that version 1 never repainted at all;
2. thin water ribbons, with the shoreline protected so a lake or the sea is
   never eaten from the edge;
3. thin or tiny parts of the gray crystalline classes;
4. thin ribbons of any unit that agree with their own host on both flanks and
   lie on printed lines, i.e. a road casing wearing a geological colour;
5. the halo of everything above, so the recoloured fringe goes too.

Then the holes are healed from the surrounding geology, and the heal is not
allowed to cross an existing boundary between two units, so a dashed contact
survives as a boundary and never becomes a welded blob. Mapped water can keep
its own pixels but never spreads, which is what stops a drained channel from
widening into a lake.
"""
from pathlib import Path
import argparse, csv, json
import numpy as np
import cv2
from PIL import Image
from scipy import ndimage as ndi
from scipy.cluster.hierarchy import linkage, fcluster
from scipy.spatial import cKDTree

import linework
import sheetgrid

ROOT = Path(__file__).resolve().parents[1]
SOURCE = ROOT / 'pic NGSA geological-map-of-nigeria-.jpg'
SHEET_V1 = ROOT / 'NGSA_map_geology_legend_isolated.png'
LEGEND = ROOT / 'data/map/legend.csv'
OUT = ROOT / 'data/clean'
WORK = ROOT / '.cache/build'
CROP = (190, 190, 4274, 3526)      # mapped area, source-pixel coordinates
SHEET_OFFSET = (120, 96)           # sheet pixel = source pixel - offset
WATER_ID = 95                      # legend row 95: mapped water, not geology
GRAY_CODES = ('D', 'ODh', 'OGS')   # gray entries that printing was matched to
SNAP_TOLERANCE = 14.0              # CIELAB distance to the nearest legend colour
PAPER_ID = 96                      # blank sheet inside the outline: not geology
FRAME_GUARD = 8                    # pixels of the printed neatline kept intact
STROKE_WIDTH = 8.0                 # a structure this narrow is a stroke, not a body
STROKE_LENGTH = 40.0               # ... when it is also this long
BAND_GROW = 1                      # halo, in pixels, around each detected stroke


def log(msg):
    print(msg, flush=True)


def read_legend():
    return [{'id': int(r['id']), 'code': r['code'], 'name': r['name'], 'color': r['color']}
            for r in csv.DictReader(open(LEGEND))]


def palette_of(units):
    return np.array([[int(u['color'][j:j + 2], 16) for j in (1, 3, 5)] for u in units], np.uint8)


def lab(rgb):
    return cv2.cvtColor(rgb.astype(np.float32) / 255, cv2.COLOR_RGB2LAB)


def families(palette, units):
    """Palette entries that are visually indistinguishable in CIELAB.

    Two units that differ by less than a printing tolerance are one *family*
    for the purposes of the flank test: agreeing on both flanks must mean "the
    same ground", not "a colour that happens to look the same".
    """
    plab = lab(palette[None])[0]
    keep = [i for i, u in enumerate(units) if u['id'] < WATER_ID]
    groups = fcluster(linkage(plab[keep], method='complete'), t=3, criterion='distance')
    canonical = np.arange(len(units) + 1, dtype=np.uint8)
    alternatives = {u['id']: [u['id']] for u in units}
    for group in np.unique(groups):
        members = np.array(keep)[groups == group] + 1
        canonical[members] = members[0]
        for m in members:
            alternatives[int(m)] = [int(x) for x in members]
    return canonical, alternatives


def map_area():
    """The mapped area in sheet coordinates."""
    return (CROP[0] - SHEET_OFFSET[0], CROP[1] - SHEET_OFFSET[1],
            CROP[2] - SHEET_OFFSET[0], CROP[3] - SHEET_OFFSET[1])


def load_pair():
    """The whole sheet, the sheet's mapped area, and the aligned photograph.

    ``SHEET_OFFSET`` is what makes the last two refer to the same ground: the
    published sheet is the photograph cropped by (120, 96), so no resampling
    and no fitting is involved.
    """
    sheet = np.array(Image.open(SHEET_V1).convert('RGB'))
    source = np.array(Image.open(SOURCE).convert('RGB'))
    x0, y0, x1, y1 = map_area()
    cut = sheet[y0:y1, x0:x1]
    src = source[CROP[1]:CROP[3], CROP[0]:CROP[2]]
    if cut.shape != src.shape:
        raise SystemExit('sheet/photo crop mismatch: %s vs %s' % (cut.shape, src.shape))
    return sheet, cut, src


def snap(rgb, palette, tolerance=SNAP_TOLERANCE):
    """Legend unit per pixel by nearest CIELAB colour; 0 where nothing matches.

    The sheet was painted with these colours, so this recovers version 1
    exactly. The tolerance is what keeps the open sea, the paper and the gray
    ink out of the geological classes instead of inventing a unit for them.
    """
    target = lab(rgb).reshape(-1, 3).astype(np.float32)
    ref = lab(palette[None])[0].astype(np.float32)
    dist, nearest = cKDTree(ref).query(target, k=1)
    ids = np.where(dist <= tolerance, nearest + 1, 0).astype(np.int16)
    return ids.reshape(rgb.shape[:2]), dist.reshape(rgb.shape[:2])


def footprint_of(ids, water):
    """The mapped area: the outline of everything painted, holes included."""
    solid = ((ids > 0) & ~water).astype(np.uint8)
    solid = cv2.morphologyEx(solid, cv2.MORPH_CLOSE, np.ones((9, 9), np.uint8))
    contours, _ = cv2.findContours(solid, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
    mask = np.zeros(ids.shape, np.uint8)
    cv2.drawContours(mask, [max(contours, key=cv2.contourArea)], -1, 1, -1)
    return ndi.binary_fill_holes(mask.astype(bool))


def unit_boundary(family):
    """Existing contacts: the heal may not cross one, so they cannot be welded."""
    edge = np.zeros(family.shape, bool)
    for dy, dx in ((0, 1), (1, 0), (1, 1), (1, -1)):
        a = linework._shift(family, dy, dx)
        b = linework._shift(family, -dy, -dx)
        edge |= (a > 0) & (b > 0) & (a != b)
    return edge


def thin_parts(base, max_width=STROKE_WIDTH, min_length=STROKE_LENGTH, min_area=6,
               same=None, valid=None, require_agreement=False, same_side_share=0.6,
               protect_bodies=True, probe=3):
    """Thin, long connected parts of ``base``, grown back to their full width."""
    if same is None:
        same = np.zeros(base.shape, np.float32)
        valid = np.zeros(base.shape, np.float32)
    thin, m = linework.stroke_metrics(base, same, valid, max_width)
    if m is None:
        return np.zeros(base.shape, bool), 0, dict(candidates=0, medianWidth=0.0, medianLength=0.0)
    if protect_bodies:
        kept = thin & ~linework.body_shield(base, probe)
        if not kept.any():
            return kept, 0, dict(candidates=0, medianWidth=0.0, medianLength=0.0)
        m = linework.stroke_metrics(kept, same, valid, max_width)[1]
        if m is None:
            return kept, 0, dict(candidates=0, medianWidth=0.0, medianLength=0.0)
    chosen = linework.select_strokes(m, min_length=min_length, min_area=min_area,
                                     require_agreement=require_agreement,
                                     same_side_share=same_side_share)
    picked = linework.mask_of(m, chosen)
    grown = cv2.dilate(picked.astype(np.uint8), np.ones((3, 3), np.uint8)).astype(bool) & base
    info = dict(candidates=int(chosen.sum()),
                medianWidth=round(float(np.median(m['mean_w'][chosen])), 2) if chosen.any() else 0.0,
                medianLength=round(float(np.median(m['length'][chosen])), 1) if chosen.any() else 0.0)
    return grown, int(picked.sum()), info


def small_parts(base, size=260):
    """Tiny connected parts of ``base``: speckle, dot glyphs, hachure ends."""
    n, labels, stats, _ = cv2.connectedComponentsWithStats(base.astype(np.uint8), 8)
    if n <= 1:
        return np.zeros(base.shape, bool)
    area = stats[1:, cv2.CC_STAT_AREA]
    return np.isin(labels, np.flatnonzero(area < size) + 1)


def heal(seeds, fill, barriers=None, rounds=48, no_spread=None, donor=None):
    """Grow trusted labels into the cells listed in ``fill``, and nowhere else.

    Only the pixels this build judged to be printing are touched, so the blank
    sea, the paper and any unmapped ground inside the outline of the map are
    never painted with invented geology. Propagation is local and barrier
    aware: a nearest-seed transform would happily weld two units that a
    preserved contact separates, so each round a cell takes a label from an
    already-filled 4-neighbour unless a barrier lies between them.
    ``no_spread`` lists labels that may keep their own pixels but never grow
    into a hole, which is what stops a drained channel from becoming a lake.
    Cells a barrier fully encloses fall back to the nearest trusted seed.
    """
    out = seeds.copy()
    if donor is None:
        donor = (seeds > 0) & ~fill
    else:
        donor = donor & ~fill
    spreadable = np.ones(out.shape, bool)
    if no_spread is not None and len(no_spread):
        spreadable = ~np.isin(out, np.asarray(no_spread))
    pending = fill.copy()
    if not pending.any():
        return out
    for _ in range(rounds):
        source_ready = donor & spreadable
        taken = np.zeros(out.shape, bool)
        for dy, dx in ((-1, 0), (1, 0), (0, -1), (0, 1)):
            src = linework._shift(out, dy, dx)
            d = linework._shift(source_ready.astype(np.uint8), dy, dx).astype(bool)
            if barriers is not None:
                d &= ~linework._shift(barriers.astype(np.uint8), dy, dx).astype(bool)
            take = pending & d & ~taken
            out[take] = src[take]
            donor[take] = True
            taken |= take
        if not taken.any():
            break
        pending &= ~taken
    if pending.any():
        if donor.any():
            _, indices = ndi.distance_transform_edt(~donor, return_indices=True)
            out[pending] = out[indices[0][pending], indices[1][pending]]
    return out


def build(write=True, debug_dir=None):
    WORK.mkdir(parents=True, exist_ok=True)
    OUT.mkdir(parents=True, exist_ok=True)
    units = read_legend()
    palette = palette_of(units)
    canonical, alternatives = families(palette, units)
    gray_ids = np.array([u['id'] for u in units if u['code'] in GRAY_CODES], np.int16)
    sheet, base, src = load_pair()

    v1_ids, _ = snap(base, palette)
    water = (v1_ids == WATER_ID)
    footprint = footprint_of(v1_ids, water)
    # The sheet is cleaned across its whole map area, including the unmapped
    # neighbouring countries, because a road printed in Benin is still a road.
    # The frame itself is guarded so the neatline stays as printed.
    zone = np.ones(v1_ids.shape, bool)
    zone[:FRAME_GUARD, :] = False; zone[-FRAME_GUARD:, :] = False
    zone[:, :FRAME_GUARD] = False; zone[:, -FRAME_GUARD:] = False
    # Blank paper is not a hole to be filled with invented geology: it is the
    # sheet background, and it heals as itself. Giving it a class of its own is
    # what lets the cleaning run over the sea and foreign ground at all.
    a0 = base.astype(np.int32)
    # Blank sheet, i.e. paper: bright *and* colourless. A pale blue wash is a
    # river drawn on that paper, and must stay visible to the tests below.
    paper = zone & (v1_ids == 0) & (a0.min(2) > 232) & ((a0.max(2) - a0.min(2)) <= 18)
    v1_ids = np.where(paper, PAPER_ID, v1_ids)
    # Only ground version 1 mapped holds a *recoloured* print; elsewhere the
    # cleaning is limited to ink and water that survive on the sheet.
    painted = footprint & (v1_ids > 0) & (v1_ids != WATER_ID) & (v1_ids != PAPER_ID)
    mask = ndi.binary_closing(painted, np.ones((25, 25), bool)) & footprint & zone
    recovered = mask & (v1_ids > 0) & (v1_ids != PAPER_ID)
    log('cleaning zone %d px, mapped footprint %d px; version-1 colour recovered on '
        '%.2f%% of it' % (zone.sum(), mask.sum(), 100 * recovered.sum() / mask.sum()))

    ids_safe = v1_ids.astype(np.int32).clip(0, len(canonical) - 1)
    family = np.where(zone & (v1_ids < len(canonical)), canonical[ids_safe], v1_ids).astype(np.int32)
    family[~zone] = 0
    same, valid = linework.flank_agreement(family, probe=3)
    evidence = linework.printing_evidence(src, zone)
    log('photographic printing evidence: %s' % evidence['counts'])

    # 1. printing version 1 never repainted. A *thin* unpainted sliver is a road,
    # a railway, a label or the casing round either; fat unpainted ground is real
    # unmapped country or open water, and is left exactly as printed.
    leftover = zone & (v1_ids == 0)
    s1, k1, i1 = thin_parts(leftover, max_width=12.0, min_length=6.0, min_area=3)
    s1 |= small_parts(leftover, size=260) & zone
    i1['darkPixels'] = int((leftover & ((a0.max(2) < 226) &
                                        ((a0.max(2) - a0.min(2)) <= 20))).sum())

    # 2. thin water ribbons: channels, not lakes or the sea. Inside the mapped
    # footprint every thin channel is print; outside it a channel is only print
    # when it does not fringe a body of open water, so the coastline and Lake
    # Chad keep their shape.
    water_mask = (v1_ids == WATER_ID) & zone
    open_sea = linework.body_shield((v1_ids == WATER_ID), probe=6)
    s2in, k2, i2 = thin_parts(water_mask & mask, max_width=10.0, min_length=6.0, min_area=5)
    s2in |= small_parts(water_mask & mask, size=420)
    s2out = thin_parts(water_mask & ~mask, max_width=10.0, min_length=6.0, min_area=5)[0]
    s2out |= small_parts(water_mask & ~mask, size=420)
    s2out &= ~ndi.binary_dilation(open_sea, np.ones((9, 9), bool))
    # A thin blue thread that is *surrounded* by water is a label or a current
    # arrow drawn on the sea, not a channel cut in ground; leave the sheet alone.
    s2 = (s2in | s2out) & zone & ndi.binary_dilation((v1_ids != WATER_ID), np.ones((5, 5), bool))
    # 2b. a channel the sheet drew in a blue that is not the legend's water
    # colour: foreign rivers and the coastline hatching. Same thinness test, and
    # the same rule that a body of open water is geography and stays.
    hydro = linework.hydrography_mask(base) & zone & (v1_ids == 0)
    s2b, k2b, i2b = thin_parts(hydro, max_width=6.0, min_length=12.0, min_area=4)
    s2b |= small_parts(hydro & ~ndi.binary_dilation(open_sea, np.ones((9, 9), bool)), size=200)
    s2b &= ~ndi.binary_dilation(open_sea, np.ones((9, 9), bool))
    s2b &= ndi.binary_dilation((v1_ids != WATER_ID), np.ones((5, 5), bool))
    s2 |= s2b
    i2['hydroHairlines'] = int(s2b.sum())
    i2['outsideFootprint'] = int(s2out.sum())

    # 3. the gray crystalline classes are almost entirely hatching and casing
    gray_mask = np.isin(v1_ids, gray_ids) & mask
    s3, k3, i3 = thin_parts(gray_mask, max_width=8.0, min_length=14.0, min_area=5)
    s3 |= small_parts(gray_mask, size=260) & mask

    # 4. a thin ribbon of any unit that agrees with its host on both flanks and
    #    sits on printed lines: a road casing wearing a geological colour. A
    #    genuine contact disagrees on its flanks, so this cannot erase one.
    geology = mask & (v1_ids > 0) & (v1_ids != WATER_ID) & (v1_ids != PAPER_ID)
    s4, k4, i4 = thin_parts(geology, max_width=STROKE_WIDTH, min_length=STROKE_LENGTH,
                            min_area=8, same=same, valid=valid, require_agreement=True,
                            same_side_share=0.6)
    s4 &= ndi.binary_dilation(evidence['lines'] | evidence['pale'], iterations=BAND_GROW)
    s4 &= ~unit_boundary(family)          # never a contact between two units

    # 5. the printed line work itself. A road, railway or track is a thin dark
    #    continuous line in the photograph that runs *through* the interior of a
    #    unit, so its flanks carry the same sheet colour; a geological contact has
    #    different colours on the two sides. That single test separates them, which
    #    is why the photograph can be trusted here and nowhere else. Its pale
    #    casing is taken with it, but never across a contact.
    boundary = unit_boundary(family)
    off_contact = ~ndi.binary_dilation(boundary, np.ones((3, 3), bool))
    ink = evidence['ink'] & zone & off_contact
    s5, k5, i5 = thin_parts(ink, max_width=14.0, min_length=25.0, min_area=6,
                            same=same, valid=valid, require_agreement=True,
                            same_side_share=0.55)
    s5 &= zone
    s5 |= (ndi.binary_dilation(s5, np.ones((11, 11), bool)) & zone &
           evidence['casing'] & off_contact)
    i5['casingPixels'] = int(s5.sum())

    erase = (s1 | s2 | s3 | s4 | s5) & zone
    halo = cv2.dilate(erase.astype(np.uint8), np.ones((3, 3), np.uint8)).astype(bool)
    barriers = boundary & ~erase
    band = ndi.binary_dilation(erase, np.ones((7, 7), bool)) & zone
    log('erase %d px (%.2f%% of the zone): leftover ink %d, water %d, gray %d, '
        'ribbon on printing %d, printed line work %d; band %d px'
        % (erase.sum(), 100 * erase.sum() / zone.sum(), s1.sum(), s2.sum(), s3.sum(),
           s4.sum(), s5.sum(), band.sum()))

    seeds = np.where(v1_ids > 0, v1_ids, 0).astype(np.int16)
    seeds[erase] = 0
    # Only the detected printing is refilled; class barriers stop a healed river
    # in the sea from dragging geology inland with it.
    # Mapped water and the gray crystalline classes may keep their own pixels
    # but never grow: otherwise a healed channel widens into a lake and a
    # healed hatching speck smears into a dolerite sheet.
    no_grow = np.concatenate([[WATER_ID, PAPER_ID], gray_ids])
    healed = heal(seeds, erase & (seeds == 0), barriers=barriers, no_spread=no_grow,
                  donor=(seeds > 0))
    healed = np.asarray(polish(healed, band, zone, gray_ids=gray_ids), np.int16)
    # A healed gray body keeps frayed single-pixel arms, which read as hatching.
    for _ in range(3):
        gray_now = np.isin(healed, gray_ids) & mask
        stray = small_parts(gray_now, size=140) & mask
        if not stray.any():
            break
        seeds_g = np.where(gray_now & ~stray, healed, 0).astype(np.int16)
        seeds_g[~mask] = 0
        filled = heal(np.where(stray, 0, healed), stray, barriers=barriers,
                      no_spread=no_grow, donor=(seeds_g > 0))
        healed = np.where(stray & (filled > 0), filled, healed)
    changed = (healed != v1_ids) & zone
    log('changed %d px (%.2f%% of the zone)'
        % (changed.sum(), 100 * changed.sum() / max(zone.sum(), 1)))

    qa = dict(revision=10, base=SHEET_V1.name, sourceCrop=list(CROP), sheetOffset=list(SHEET_OFFSET),
              paperPixels=int(((healed == PAPER_ID) & zone).sum()),
              frameGuardPixels=FRAME_GUARD,
              mappedAreaBox=list(map_area()), snapTolerance=SNAP_TOLERANCE,
              strokeWidth=STROKE_WIDTH, strokeLength=STROKE_LENGTH,
              zonePixels=int(zone.sum()), footprintPixels=int(mask.sum()),
              recoveredSheetColourPixels=int(recovered.sum()),
              photographicEvidence=evidence['counts'],
              tests=dict(leftoverInk=dict(strokes=k1, **i1, pixels=int(s1.sum())),
                         waterRibbon=dict(strokes=k2, **i2, pixels=int(s2.sum())),
                         grayShading=dict(strokes=k3, **i3, pixels=int(s3.sum())),
                         recolouredRibbon=dict(strokes=k4, **i4, pixels=int(s4.sum())),
                         printedLineWork=dict(strokes=k5, **i5, pixels=int(s5.sum()))),
              erase=dict(pixels=int(erase.sum()), bandPixels=int(band.sum()),
                         shareOfZone=round(float(100 * erase.sum() / zone.sum()), 3),
                         shareOfMappedArea=round(float(100 * (erase & mask).sum() / mask.sum()), 3)),
              healedPixels=int(changed.sum()),
              boundaryPixels=int(boundary.sum()),
              residualBefore=residual_report(v1_ids, zone, gray_ids),
              residualAfter=residual_report(healed, zone, gray_ids, keep_water=water_mask),
              legend=[dict(id=u['id'], code=u['code'], name=u['name'], color=u['color'],
                           pixels=int(((healed == u['id']) & mask).sum()),
                           before=int(((v1_ids == u['id']) & mask).sum())) for u in units])
    if write:
        np.savez_compressed(WORK / 'r9.npz', before=v1_ids, after=healed, mask=mask,
                            zone=zone, erase=erase, band=band, barriers=barriers,
                            water=water_mask, canonical=canonical, gray_ids=gray_ids)
        np.savez_compressed(WORK / 'r9_geom.npz', meridian_x=np.array(sheetgrid.MERIDIAN_X),
                            parallel_y=np.array(sheetgrid.PARALLEL_Y), crop=np.array(CROP),
                            offset=np.array(SHEET_OFFSET), mapArea=np.array(map_area()))
        (OUT / 'qa.json').write_text(json.dumps(qa, indent=2))
        log(json.dumps({k: qa[k] for k in ('photographicEvidence', 'tests', 'erase',
                                           'healedPixels', 'residualBefore', 'residualAfter')},
                       indent=2))
    if debug_dir:
        write_debug(debug_dir, base, src, zone, erase, s1, s2, s3, s4, s5, evidence, healed,
                    v1_ids, palette)
    return dict(sheet=sheet, base=base, src=src, ids=v1_ids, healed=healed, mask=mask,
                zone=zone, erase=erase, palette=palette, canonical=canonical,
                alternatives=alternatives, units=units, qa=qa)


def polish(ids, band, mask, size=12, gray_ids=()):
    """Remove the speckle a fill leaves behind, inside the repair band only."""
    out = ids.copy()
    holes = small_parts(out > 0, size=size) & band
    if not holes.any():
        return out
    seeds = np.where((out > 0) & ~holes, out, 0).astype(out.dtype)
    filled = heal(seeds, holes, barriers=None, rounds=24,
                  no_spread=np.concatenate([[WATER_ID], gray_ids]), donor=(seeds > 0))
    return np.where(holes & (filled > 0), filled, out)


def residual_report(ids, mask, gray_ids, keep_water=None):
    """How much printing-looking geometry the map still shows.

    ``keep_water`` marks the water bodies that were already there, so a retained
    shoreline never counts as a surviving river.
    """
    water = (ids == WATER_ID) & mask
    if keep_water is not None:
        water &= ~ndi.binary_dilation(keep_water, iterations=4)
    gray = np.isin(ids, gray_ids) & mask
    w, wn, _ = thin_parts(water, max_width=10.0, min_length=6.0, min_area=5)
    g, gn, _ = thin_parts(gray, max_width=8.0, min_length=14.0, min_area=5)
    dark = mask & (ids == 0)
    return dict(waterStrokeComponents=int(wn), waterStrokePixels=int(w.sum()),
                grayStrokeComponents=int(gn), grayStrokePixels=int(g.sum()),
                unpaintedPixels=int(dark.sum()), waterPixels=int(((ids == WATER_ID) & mask).sum()),
                grayPixels=int(gray.sum()))


def write_debug(debug_dir, base, src, mask, erase, s1, s2, s3, s4, s5, evidence, healed, v1_ids,
               palette):
    """Diagnostic render only: paints the cleaning result and each test's hits."""
    d = Path(debug_dir)
    d.mkdir(parents=True, exist_ok=True)

    def paint(ids):
        out = np.full(ids.shape + (3,), 255, np.uint8)
        good = (ids > 0) & (ids <= len(palette))
        out[good] = palette[ids[good] - 1]
        out[ids == PAPER_ID] = 255
        return out

    Image.fromarray(paint(healed)).save(d / 'after.png')
    Image.fromarray(paint(v1_ids)).save(d / 'before.png')
    overlay = base.copy()
    overlay[erase] = (255, 0, 0)
    Image.fromarray(overlay).save(d / 'erase_overlay.png')
    for name, m in (('test1_leftover_ink', s1), ('test2_water_ribbon', s2),
                    ('test3_gray_shading', s3), ('test4_recoloured_ribbon', s4),
                    ('photo_evidence', evidence['evidence'])):
        Image.fromarray((m.astype(np.uint8)) * 255).save(d / (name + '.png'))


if __name__ == '__main__':
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument('--dry-run', action='store_true')
    ap.add_argument('--debug', default=None, help='write diagnostic masks here')
    args = ap.parse_args()
    build(write=not args.dry_run, debug_dir=args.debug)
