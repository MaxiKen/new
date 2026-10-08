import numpy as np, json
from PIL import Image
im = np.asarray(Image.open('/home/user/new/pic geology of nigeria.png').convert('RGB')).astype(int)
def detect(x0, x1, y0, y1):
    sub = im[y0:y1, x0:x1]
    med = np.median(sub, axis=1)
    rowstd = sub.std(axis=1).mean(axis=1)
    sat = med.max(axis=1) - med.min(axis=1)
    colored = (rowstd < 12) & ((med.mean(axis=1) < 246) | (sat > 10))
    idx = np.where(colored)[0]
    res = []
    if idx.size:
        s = p = idx[0]
        runs = []
        for v in idx[1:]:
            if v != p + 1:
                runs.append((s, p)); s = v
            p = v
        runs.append((s, p))
        for a, b in runs:
            if b - a + 1 >= 8:
                c = np.median(sub[a:b + 1, 4:-4].reshape(-1, 3), axis=0)
                res.append({'y0': int(a + y0), 'y1': int(b + y0), 'rgb': [int(v) for v in c]})
    return res
out = {
    'TR_left': detect(770, 806, 0, 700),
    'TR_right': detect(1306, 1332, 0, 640),
    'BOT_left': detect(44, 82, 600, 1210),
    'BOT_mid': detect(499, 532, 600, 1210),
    'BOT_right': detect(1101, 1132, 600, 1210),
}
for k, v in out.items():
    print(k, len(v))
    for r in v:
        print('   ', r['y0'], r['y1'], r['rgb'])
json.dump(out, open('/home/user/work/p1_swatches.json', 'w'), indent=1)
