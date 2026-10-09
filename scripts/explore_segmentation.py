from pathlib import Path
from PIL import Image
import numpy as np
from scipy import ndimage as ndi
from skimage.color import rgb2lab

ROOT = Path(__file__).resolve().parents[1]
im = np.asarray(Image.open(ROOT / "pic geology of nigeria.png").convert("RGB"))
# Twelve swatch colours, sampled from the solid interiors of the legend chips.
palette = np.array([
    [143, 211, 206],  # cyan
    [255, 255, 176],  # pale yellow
    [188, 189, 219],  # lavender
    [255, 125, 110],  # coral
    [127, 177, 212],  # blue
    [255, 178,  98],  # orange
    [179, 221, 112],  # green
    [255, 203, 227],  # pink
    [217, 217, 219],  # grey
    [190, 128, 188],  # purple
    [202, 236, 201],  # pale green
    [254, 236, 113],  # yellow
], dtype=np.uint8)
# Map frame (inclusive inside border), established from 4/8/12 E and 14/10/6 N gridlines.
x0, x1, y0, y1 = 34, 704, 33, 581
rgb = im[y0:y1, x0:x1]
lab = rgb2lab(rgb / 255.0)
plab = rgb2lab(palette[:, None, :] / 255.0)[:, 0, :]
d = np.linalg.norm(lab[:, :, None, :] - plab[None, None, :, :], axis=3)
label = d.argmin(2).astype(np.uint8)
mind = d.min(2)
print('distance percentiles', np.percentile(mind, [1,5,10,25,50,75,90,95,99]))
for t in [3,5,8,10,12,15,20,25,30]:
    cand = mind < t
    labcc,n=ndi.label(cand)
    sizes=np.bincount(labcc.ravel()); largest=sizes[1:].max() if n else 0
    print(t, cand.sum(), cand.mean(), 'cc',n,'largest',largest)
# Strong non-grey palette pixels define the country. Excluding grey prevents the
# printed graticule/frame from entering the mask. Close linework interruptions,
# retain the country component, and fill enclosed grey units and cartographic ink.
seed = (mind < 12) & (label != 8)
seed = ndi.binary_closing(seed, structure=np.ones((5,5), bool), iterations=2)
cc,n=ndi.label(seed)
sizes=np.bincount(cc.ravel()); keep=np.argmax(sizes[1:])+1
mask = cc == keep
mask = ndi.binary_closing(mask, structure=np.ones((7,7), bool), iterations=2)
mask = ndi.binary_fill_holes(mask)
mask = ndi.binary_opening(mask, structure=np.ones((3,3), bool))
ys, xs = np.where(mask)
print('mask pixels',mask.sum(),'bbox',(ys.min(), ys.max(), xs.min(), xs.max()))
# Fill unreliable cartographic text/linework from the closest reliable geology.
reliable = (mind < 13) & mask
_, inds = ndi.distance_transform_edt(~reliable, return_indices=True)
filled = label.copy()
filled[mask & ~reliable] = label[tuple(inds[:, mask & ~reliable])]

# The grey graticule can otherwise be mistaken for the grey legend colour.
# Inpaint all known grid strips with a local two-dimensional categorical
# interpolation. A Gaussian vote follows surrounding contacts and avoids both
# a straight grey line and square-ended nearest-neighbour blocks.
grid = np.zeros(mask.shape, dtype=bool)
for global_y, width in ((254, 4), (474, 3)):
    cy = global_y - y0
    grid[max(0, cy - width):cy + width + 1, :] = True
for global_x in (127, 345, 563):
    cx = global_x - x0
    grid[:, max(0, cx - 2):cx + 3] = True
grid &= mask
known = mask & ~grid
votes = []
for k in range(12):
    support = ((filled == k) & known).astype(np.float32)
    votes.append(ndi.gaussian_filter(support, sigma=4.0, mode="nearest"))
votes = np.stack(votes)
filled[grid] = votes[:, grid].argmax(axis=0).astype(np.uint8)
# Small majority pass only where isolated speckle differs from a strong neighbourhood majority.
for _ in range(2):
    onehot = np.stack([filled == k for k in range(12)])
    counts = np.stack([ndi.uniform_filter(x.astype(float), size=3, mode='nearest') for x in onehot])
    winner = counts.argmax(0).astype(np.uint8)
    certainty = counts.max(0)
    change = mask & (winner != filled) & (certainty >= 5/9)
    filled[change] = winner[change]
# Diagnostic rendering.
out = np.full(rgb.shape, 255, np.uint8)
out[mask] = palette[filled[mask]]
Image.fromarray(out).save(ROOT / 'segmentation_preview.png')
Image.fromarray((mask*255).astype(np.uint8)).save(ROOT / 'mask_preview.png')
np.savez_compressed(ROOT / 'segmentation.npz', labels=filled, mask=mask, palette=palette, frame=np.array([x0,x1,y0,y1]))
