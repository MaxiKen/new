import numpy as np, sys, time
sys.path.insert(0, '/home/user/work')
from collections import defaultdict
from skimage.color import rgb2lab
from scipy.cluster.hierarchy import linkage, fcluster
from legend_tables import P2_ROWS, P1_LABELS, P2_TO_P1, load_colors, norm_label
# name-based extra links found by checking unmatched picture-1 entries against picture-2 names (1-based P1 index)
EXTRA_P1 = {41: [45], 43: [45], 11: [51], 25: [53], 61: [69]}
t0 = time.time()
p2c, p1c = load_colors()
L2s = rgb2lab(np.array(p2c, float)[None] / 255.0)[0]
L1s = rgb2lab(np.array(p1c, float)[None] / 255.0)[0]
d = np.load('/home/user/work/samples_p2grid.npz')
c2 = d['c2']; c1 = d['c1']; d1 = d['d1']; i1 = d['i1']
N = c2.shape[0]
# ---- P2 colour bins (4-level) -> clusters by average-linkage on Lab (dE 3.5)
q = (c2 // 4).astype(np.int32)
key = q[:, 0] * 10000 + q[:, 1] * 100 + q[:, 2]
ukeys, inv, cnts = np.unique(key, return_inverse=True, return_counts=True)
keep = cnts >= 1
rgbs = np.stack([ukeys // 10000, (ukeys // 100) % 100, ukeys % 100], 1) * 4 + 2
Lb = rgb2lab(rgbs[None].astype(float) / 255.0)[0]
print('bins', len(ukeys), 'time', round(time.time() - t0, 1))
core = np.where(cnts >= 30)[0]
print('core bins', core.size)
Z = linkage(Lb[core], method='average', metric='euclidean')
lab_core = fcluster(Z, t=3.5, criterion='distance') - 1
ncore = lab_core.max() + 1
# centroids of core clusters (count weighted)
cent = np.zeros((ncore, 3))
for k in range(ncore):
    m = core[lab_core == k]
    cent[k] = (Lb[m] * cnts[m, None]).sum(0) / cnts[m].sum()
# assign every bin to nearest centroid if within 6 dE, else -1
dmat = np.sqrt(((Lb[:, None, :] - cent[None, :, :]) ** 2).sum(-1))
nn = dmat.argmin(1); nd = dmat.min(1)
cl_of_bin = np.where(nd < 6.0, nn, -1)
# remap so clusters are 0..ncl-1, -1 kept as unassigned cluster
ncl = ncore
cl_of_sample = cl_of_bin[inv]
ok_s = cl_of_sample >= 0
n_k = np.bincount(cl_of_sample[ok_s], minlength=ncl)
w = cnts.astype(float)
Lk = np.zeros((ncl, 3)); Rk = np.zeros((ncl, 3))
for k in range(ncl):
    m = cl_of_bin == k
    Lk[k] = (Lb[m] * w[m, None]).sum(0) / w[m].sum()
    Rk[k] = (rgbs[m] * w[m, None]).sum(0) / w[m].sum()
order = np.argsort(-n_k)
print('P2 clusters', ncl, 'top sizes', n_k[order[:10]].tolist(), 'time', round(time.time() - t0, 1))
# ---- P1 colour groups (rows with dE<3 are the same colour)
from skimage.color import deltaE_ciede2000
M1 = np.load('/home/user/work/M1.npy')
gid1 = -np.ones(86, int); g = 0
for j in range(86):
    if gid1[j] >= 0: continue
    stack = [j]; gid1[j] = g
    while stack:
        a = stack.pop()
        for b in np.where((M1[a] < 3.0) & (gid1 < 0))[0]:
            gid1[b] = g; stack.append(b)
    g += 1
print('P1 colour groups', g)
# ---- per-sample P1 group votes
valid1 = d1 < 6
g1 = np.where(valid1, gid1[np.clip(i1, 0, 85)], -1)
# fraction of votes per (cluster, group)
G = g
cnt_kg = np.zeros((ncl, G))
sel = valid1 & ok_s
np.add.at(cnt_kg, (cl_of_sample[sel], g1[sel]), 1)
nvalid = cnt_kg.sum(1)
frac_kg = cnt_kg / np.maximum(nvalid[:, None], 1)
# ---- label-level info
labels = []
lab_index = {}
for r, code, lab in P2_ROWS:
    nl = norm_label(lab)
    if nl not in lab_index:
        lab_index[nl] = len(labels); labels.append({'name': lab, 'rows': [], 'p1': set()})
    labels[lab_index[nl]]['rows'].append(r)
    if P2_TO_P1.get(r): labels[lab_index[nl]]['p1'].add(P2_TO_P1[r] - 1)
    for j1 in EXTRA_P1.get(r, []): labels[lab_index[nl]]['p1'].add(j1 - 1)
for L in labels:
    L['groups'] = sorted(set(int(gid1[j]) for j in L['p1'])) if L['p1'] else None
print('distinct labels', len(labels))
rowcol = {r: Rk for r in []}
R2 = np.array(p2c, float); L2 = L2s
# cost matrix for the big clusters
def cost(k, li):
    """Joint cost: colour distance to legend swatch (capped) + picture-1 disagreement.
    Exact colour matches (dE<=4) keep picture 2 in charge; far (shifted) colours rely on picture 1."""
    L = labels[li]
    dE2 = min(np.sqrt(((Lk[k] - L2[r - 1]) ** 2).sum()) for r in L['rows'])
    w = 1.0 + 2.0 * min(1.0, max(0.0, (dE2 - 4.0) / 4.0))
    if L['groups'] is None or nvalid[k] < 30:
        pen = 0.9 * w   # no picture-1 evidence: neutral (not a bonus), so it cannot act as a default sink
    else:
        f = sum(frac_kg[k, gg] for gg in L['groups'])
        pen = w * (1 - min(1.0, f))
    return min(dE2, 8.0) / 6.0 + 0.02 * dE2 + pen, dE2, pen
best = np.full(ncl, -1); bestc = np.full(ncl, np.inf)
for k in range(ncl):
    if n_k[k] < 50:
        continue
    cs = [cost(k, li)[0] for li in range(len(labels))]
    li = int(np.argmin(cs)); best[k] = li; bestc[k] = cs[li]
np.savez('/home/user/work/cluster_assign.npz', Lk=Lk, Rk=Rk, n_k=n_k, best=best, bestc=bestc, cl_of_bin=cl_of_bin, ukeys=ukeys, gid1=gid1, frac_kg=frac_kg, nvalid=nvalid)
import pickle
pickle.dump({'labels': labels}, open('/home/user/work/labels.pkl', 'wb'))
print('--- top clusters (n, RGB, assigned label, cost, dE2, penalty, top P1 groups) ---')
for k in order[:90]:
    if n_k[k] < 50: break
    li = best[k]
    if li < 0: continue
    c, dE2, pen = cost(k, li)
    top = np.argsort(-frac_kg[k])[:2]
    tg = ', '.join('g%d:%.2f' % (t, frac_kg[k, t]) for t in top if frac_kg[k, t] > 0.05)
    print('k%4d n=%7d rgb=%-15s -> %-38s cost=%.2f dE2=%5.1f pen=%.2f | %s' % (k, n_k[k], tuple(Rk[k].round().astype(int)), labels[li]['name'][:38], c, dE2, pen, tg))
print('time', round(time.time() - t0, 1))
