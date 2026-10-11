"""Cartographic-linework evidence: road, railway and river printing.

This module supplies *evidence*, not decisions. The map is cleaned by looking
at the derived sheet, because that is what the reviewer sees; the source
photograph is used only to confirm that a thin structure on the sheet sits on
printing. Black ink alone was never the whole problem, because printing
survives a repaint in three ways:

``recoloured``   a thin blue river stroke was matched to the nearest palette
                 entry, so the river stayed on the map as a thin blue ribbon;
``casing``       the pale fill between a road's two edge lines survived as a
                 pale sand/clay ribbon once the dark lines were healed;
``shaded``       ridge hatching and heavy road casing survived as the gray
                 crystalline legend entries (dolerite, Bauchite, syenite).

Two helpers carry the geometric judgements:

``stroke_metrics``   local width, long axis and flank agreement per connected
                     part. Width is measured locally with a distance transform,
                     because roads, railways, lettering and dashed contacts all
                     touch each other: a single network would be judged by its
                     thickest and thinnest parts together, so a global width
                     test either rejects everything or accepts everything;
``body_shield``      the outer band of every fat object. The shore of a lake,
                     lagoon or sea is thin in exactly the way a channel stroke
                     is, so without this a shoreline would be deleted and the
                     geology next to it would spread into the water.

Nothing here dissolves polygons by colour, and nothing here decides that two
different units are the same unit.
"""
import numpy as np
import cv2
from scipy import ndimage as ndi

WATER_RGB = (153, 216, 235)          # mapped water on the sheet
SEA_RGB = (152, 218, 242)            # open water on the sheet
OFFSETS = ((0, 1), (1, 0), (1, 1), (1, -1))


def _shift(img, dy, dx, fill=0):
    h, w = img.shape
    out = np.full_like(img, fill)
    y0, x0 = max(0, dy), max(0, dx)
    y1, x1 = h + min(0, dy), w + min(0, dx)
    sy, sx = max(0, -dy), max(0, -dx)
    out[y0:y1, x0:x1] = img[sy:sy + y1 - y0, sx:sx + x1 - x0]
    return out


def flank_agreement(family, probe=3, offsets=OFFSETS):
    """Per-pixel count of scan directions in which both flanks hold one unit.

    An overprint drawn on top of uniform geology agrees on both sides for most
    of its length; a printed contact between two units disagrees for all of it.
    Directions with water, blank paper or nothing to compare do not vote.
    """
    fam = np.asarray(family).astype(np.int32)
    same = np.zeros(fam.shape, np.float32)
    valid = np.zeros(fam.shape, np.float32)
    for dy, dx in offsets:
        a = _shift(fam, dy * probe, dx * probe)
        b = _shift(fam, -dy * probe, -dx * probe)
        ok = (a > 0) & (b > 0)
        valid += ok
        same += ok & (a == b)
    return same, valid


def body_shield(mask, probe=3):
    """Everything within a few pixels of the interior of a fat object."""
    disk = cv2.getStructuringElement(cv2.MORPH_ELLIPSE, (2 * probe + 1, 2 * probe + 1))
    inner = ndi.binary_erosion(mask, disk)
    return ndi.binary_dilation(inner, iterations=probe + 1)


def stroke_metrics(mask, same, valid, max_width):
    """Length, width and flank agreement per thin connected part of ``mask``.

    ``max_width`` narrows the mask first: only pixels no more than half that
    far from an edge survive, which is what isolates strokes inside a network.
    """
    edt = ndi.distance_transform_edt(mask).astype(np.float32)
    thin = mask & (2.0 * edt <= max_width)
    if not thin.any():
        return thin, None
    n, labels, stats, _ = cv2.connectedComponentsWithStats(thin.astype(np.uint8), 8)
    flat = labels.ravel()
    area = np.bincount(flat, minlength=n)[1:].astype(np.float64)
    width_sum = np.bincount(flat, weights=edt.ravel(), minlength=n)[1:]
    mean_w = 2.0 * np.divide(width_sum, np.maximum(area, 1))
    peak = np.zeros(n, np.float32)
    np.maximum.at(peak, flat, edt.ravel())
    length = np.divide(area, np.maximum(mean_w, 0.75))
    votes = np.bincount(flat, weights=valid.ravel(), minlength=n)[1:]
    agree = np.bincount(flat, weights=same.ravel(), minlength=n)[1:]
    share = np.divide(agree, np.maximum(votes, 1), out=np.ones(len(area)), where=votes >= 6)
    share[votes < 6] = 1.0        # nothing on either flank: nothing to protect
    return thin, dict(area=area, mean_w=mean_w, max_w=2.0 * peak[1:], length=length,
                      share=share, votes=votes, labels=labels, n=n)


def select_strokes(m, min_length=40.0, min_area=8, same_side_share=0.6,
                   require_agreement=True, extra=None):
    """Which thin parts are printing rather than geology."""
    chosen = (m['length'] >= min_length) & (m['area'] >= min_area)
    if require_agreement:
        chosen &= m['share'] >= same_side_share
    if extra is not None:
        chosen &= extra
    return chosen


def mask_of(m, chosen):
    return np.isin(m['labels'], np.flatnonzero(chosen) + 1)


def hydrography_mask(rgb):
    """Blue printing used for water: rivers, channels, lakes, open sea."""
    a = rgb.astype(np.int32)
    blue = (a[:, :, 2] - a[:, :, 0] > 14) & (a[:, :, 2] > 130) & (a.max(2) < 252)
    near = np.zeros(a.shape[:2], bool)
    for ref in (WATER_RGB, SEA_RGB):
        near |= np.abs(a - np.array(ref, np.int32)).sum(2) <= 46
    return blue | near


def ink_mask(rgb, bright_limit=226, neutral_limit=16, dark_limit=150):
    """Dark or neutral printing: ink, casings, hatching, lettering."""
    a = rgb.astype(np.int32)
    mx, mn = a.max(2), a.min(2)
    return (mx < dark_limit) | ((mx - mn <= neutral_limit) & (mx < bright_limit))


def pale_casing_mask(rgb):
    """Near-white fill held between a road's or railway's paired edge lines."""
    a = rgb.astype(np.int32)
    mx, mn = a.max(2), a.min(2)
    return (mn > 200) & (mx - mn <= 30) & (mx < 253)


def printing_evidence(rgb, footprint, probe=3, water_width=10.0, ink_width=11.0,
                      casing_width=7.0):
    """Where the source photograph shows cartographic printing.

    Returned masks already exclude the interior band of water bodies and the
    surroundings of a preserved contact, so they can be used as evidence about
    a thin structure without deleting a shoreline or a boundary between units.
    """
    neutral = np.zeros(footprint.shape, np.float32)
    hydro_all = hydrography_mask(rgb) & footprint
    water = hydro_all & ~body_shield(hydro_all, probe)
    n, m = stroke_metrics(water, neutral, neutral, water_width)
    rivers = mask_of(m, select_strokes(m, min_length=10, min_area=5,
                                      require_agreement=False)) if m is not None else np.zeros_like(water)
    ink = ink_mask(rgb) & footprint & ~hydro_all
    n2, m2 = stroke_metrics(ink, neutral, neutral, ink_width)
    lines = mask_of(m2, select_strokes(m2, min_length=12, min_area=5,
                                      require_agreement=False)) if m2 is not None else np.zeros_like(ink)
    casing = pale_casing_mask(rgb) & footprint & ~hydro_all
    n3, m3 = stroke_metrics(casing, neutral, neutral, casing_width)
    pale = mask_of(m3, select_strokes(m3, min_length=45, min_area=8,
                                     require_agreement=False)) if m3 is not None else np.zeros_like(casing)
    evidence = np.zeros(rgb.shape[:2], bool)
    for part in (rivers, lines, pale):
        evidence |= cv2.dilate(part.astype(np.uint8), np.ones((3, 3), np.uint8)).astype(bool)
    return dict(rivers=rivers, lines=lines, pale=pale, evidence=evidence & footprint,
                hydrography=hydro_all, ink=ink, casing=casing,
                counts=dict(rivers=int(rivers.sum()), lines=int(lines.sum()),
                            pale=int(pale.sum()), evidence=int(evidence.sum())))
