"""Side-by-side inspection of version 1 and the cleaned result, plus the erase mask."""
import sys
from pathlib import Path
import numpy as np
from PIL import Image

sys.path.insert(0, str(Path(__file__).resolve().parent))
import clean_map as cm

d = np.load(cm.WORK / 'r9.npz')
before, after, mask, erase = d['before'], d['after'], d['mask'], d['erase']
units = cm.read_legend()
palette = cm.palette_of(units)
sheet, base, src = cm.load_pair()


def paint(ids):
    out = np.full(ids.shape + (3,), 255, np.uint8)
    good = (ids > 0) & (ids <= len(palette))
    out[good] = palette[ids[good] - 1]
    out[~good] = base[~good]
    return out


B = paint(after)
A = paint(before)
windows = [('Niger - Benue valley', 1500, 1450), ('Niger delta and coast', 500, 2500),
           ('Jos plateau', 1850, 850), ('Sokoto basin', 250, 450),
           ('Katsina / Hadejia', 2350, 350), ('Cross river / SE', 2900, 2100)]
W, H = 900, 560
rows = []
for name, x, y in windows:
    x1, y1 = min(x + W, A.shape[1]), min(y + H, A.shape[0])
    a, b = A[y:y1, x:x1], B[y:y1, x:x1]
    ov = a.copy()
    ov[erase[y:y1, x:x1]] = (255, 0, 0)
    s = src[y:y1, x:x1]
    rows.append(np.concatenate([s, a, b, ov], 1))
img = np.concatenate(rows, 0)
Image.fromarray(img).save(cm.ROOT / '.cache/prev/compare.png')
sc = 2
Image.fromarray(img).resize((img.shape[1] * sc // 2, img.shape[0] * sc // 2),
                            Image.LANCZOS).save(cm.ROOT / '.cache/prev/compare_small.png')
print('columns: source | version 1 | cleaned | erased(red)')
print(img.shape)
