"""Continuity-first reconstruction across cartographic overprints.

Never use a dark stroke as a reason to split an already connected color body.
A local repair needs matching reliable colors on BOTH sides of a short masked
band. Different trusted geology, water, and outside-map cells are barriers.
"""
import numpy as np
from scipy import ndimage as ndi
from skimage.measure import label


def repair_annotation_bands(classes, reliable, annotation_band, mask, water,
                            canonical, max_gap=24, observed=None):
    """Return labels and an audit mask; no unrestricted closing or global dissolve.

    reliable: nonzero original-image class seeds, not interpolated labels.
    observed: high-confidence visible source paint before erosion; vetoes
    repairs across narrow real units inside the annotation buffer.
    A pixel changes only in an annotation band bracketed by two same-family
    reliable endpoints. Horizontal/vertical/diagonal disagreements are left untouched.
    Gap limits are Euclidean source-pixel distances, including diagonal rays.
    """
    if observed is None: observed = np.zeros_like(reliable)
    # Original visible paint vetoes interpolation even inside a generously
    # expanded annotation buffer. Erosion-derived cores alone miss thin units.
    evidence_seeds = np.where(reliable > 0, reliable, observed)
    eligible = annotation_band & mask & ~water & (evidence_seeds == 0)
    proposals = np.zeros(classes.shape, dtype=classes.dtype)
    conflict = np.zeros(classes.shape, dtype=bool)
    H, W = classes.shape
    for transpose in (False, True):
        e = eligible.T if transpose else eligible
        seeds = evidence_seeds.T if transpose else evidence_seeds
        width = e.shape[1]
        x = np.arange(width, dtype=np.int32)[None, :]
        left = np.maximum.accumulate(np.where(~e, x, -1), axis=1)
        right = np.minimum.accumulate(np.where(~e, x, width)[:, ::-1], axis=1)[:, ::-1]
        l = np.take_along_axis(seeds, np.maximum(left, 0), axis=1)
        r = np.take_along_axis(seeds, np.minimum(right, width - 1), axis=1)
        match = (e & (left >= 0) & (right < width) & (right-left-1 <= max_gap)
                 & (l > 0) & (r > 0) & (canonical[l] == canonical[r]))
        candidate = np.where(match, l, 0)
        if transpose: candidate = candidate.T
        conflict |= ((proposals > 0) & (candidate > 0)
                     & (canonical[proposals] != canonical[candidate]))
        proposals = np.where((proposals == 0) & (candidate > 0), candidate, proposals)
    # Oblique annotation bands can be physically short but look too wide in
    # both row/column scans. Scan the TWO diagonal axes without resampling the
    # photo or interpolating seed labels. Work a scanline at a time to avoid
    # allocating a padded full-image diagonal transform.
    for mirrored in (False, True):
        e = eligible[:, ::-1] if mirrored else eligible
        seeds = evidence_seeds[:, ::-1] if mirrored else evidence_seeds
        candidate = np.zeros_like(classes)
        target = candidate[:, ::-1] if mirrored else candidate
        for offset in range(1-H, W):
            row0, col0 = max(0, -offset), max(0, offset)
            length = min(H-row0, W-col0)
            if length < 3: continue
            row = e.diagonal(offset)
            if not row.any(): continue
            source = seeds.diagonal(offset)
            x = np.arange(length, dtype=np.int32)
            left = np.maximum.accumulate(np.where(~row, x, -1))
            right = np.minimum.accumulate(np.where(~row, x, length)[::-1])[::-1]
            l = source[np.maximum(left, 0)]
            r = source[np.minimum(right, length-1)]
            match = (row & (left >= 0) & (right < length)
                     & ((right-left-1)*np.sqrt(2) <= max_gap)
                     & (l > 0) & (r > 0) & (canonical[l] == canonical[r]))
            indices = x[match]
            target[row0+indices, col0+indices] = l[match]
        conflict |= ((proposals > 0) & (candidate > 0)
                     & (canonical[proposals] != canonical[candidate]))
        proposals = np.where((proposals == 0) & (candidate > 0), candidate, proposals)
    approved = (proposals > 0) & ~conflict
    # Do not churn between indistinguishable legend IDs; only repair a real
    # classified-family interruption. Its tentative class still needs review.
    changed = approved & (canonical[classes] != canonical[proposals])
    # Matching paint can either reconnect separate interiors OR eliminate an
    # annotation-only halo inside a body already connected around the stroke.
    # The latter must not be preserved as a false geological island.
    before = label(canonical[classes], connectivity=1).astype('int32')
    patches = label(np.where(changed, canonical[proposals], 0), connectivity=1)
    accepted = np.zeros(patches.max()+1, bool)
    for patch_id, sl in enumerate(ndi.find_objects(patches), 1):
        if sl is None: continue
        y = slice(max(0,sl[0].start-1),min(H,sl[0].stop+1))
        x = slice(max(0,sl[1].start-1),min(W,sl[1].stop+1))
        piece = patches[y,x] == patch_id
        family = int(canonical[proposals[y,x][piece][0]])
        rim = ndi.binary_dilation(piece) & ~piece & (canonical[classes[y,x]] == family)
        owners = np.unique(before[y,x][rim]); owners=owners[owners>0]
        accepted[patch_id] = len(owners)>=1
    changed &= accepted[patches]
    result = classes.copy(); result[changed] = proposals[changed]
    # A bridge must not solve one discontinuity by cutting another old body
    # into pieces if that body contains reliable or unmasked geology. Only a
    # completely untrusted, completely masked annotation component may be
    # consumed or broken up. Reject WHOLE patches cutting protected components.
    # Repeat after rejection: two proposed patches can interact. Removing one
    # must not make another remaining patch split an original component.
    evidence = ((evidence_seeds > 0) | ~annotation_band | water) & (before > 0)
    protected = np.zeros(int(before.max())+1, dtype=bool)
    protected[np.unique(before[evidence])] = True
    while changed.any():
        after = label(canonical[result], connectivity=1).astype('int32')
        unchanged_family = (canonical[result] == canonical[classes]) & (before>0)
        stride=int(after.max())+1
        pairs=np.unique(before[unchanged_family].astype(np.int64)*stride+after[unchanged_family])
        pieces_per_old=np.bincount(pairs//stride,minlength=int(before.max())+1)
        cut_components=(pieces_per_old>1) & protected
        bad_patches=np.unique(patches[changed & cut_components[before]])
        if len(bad_patches)==0:break
        accepted[bad_patches]=False
        rejected=changed & ~accepted[patches]
        assert rejected.any(), 'Continuity rejection must make progress'
        conflict |= rejected
        changed &= accepted[patches]
        result=classes.copy();result[changed]=proposals[changed]
    assert not np.any(changed & (~annotation_band | ~mask | water | (evidence_seeds > 0)))
    return result, changed, conflict


def connected_bodies(classes, canonical):
    """One feature seed per connected color region; no dark-contact subdivision.

    Identical colors in DISCONNECTED regions retain different body IDs. No
    proximity-only merge, dilation, buffer-union, or country-wide dissolve.
    """
    ids = label(canonical[classes], connectivity=1).astype('int32')
    nclasses = len(canonical)
    hist = np.bincount(ids.ravel().astype(np.int64)*nclasses + classes.ravel(),
                      minlength=(ids.max()+1)*nclasses).reshape(-1,nclasses)
    dominant = hist.argmax(1)
    table = np.c_[dominant, np.arange(len(dominant)), np.zeros(len(dominant),int)].astype('int32')
    table[0] = 0
    return ids, table
