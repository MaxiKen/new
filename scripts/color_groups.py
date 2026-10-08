import numpy as np, sys
sys.path.insert(0, '/home/user/work')
from legend_tables import P2_ROWS, P1_LABELS, P2_TO_P1, load_colors
from skimage.color import rgb2lab, deltaE_ciede2000
p2c, p1c = load_colors()
L2 = rgb2lab(np.array(p2c, float)[None] / 255.0)[0]
L1 = rgb2lab(np.array(p1c, float)[None] / 255.0)[0]
def dE(a, b):
    return deltaE_ciede2000(a[None, :], b[None, :])[0] if False else None
from skimage.color import deltaE_ciede2000 as de
def pairwise(L):
    n = len(L)
    M = np.zeros((n, n))
    for i in range(n):
        M[i] = de(np.repeat(L[i][None], n, 0), L)
    return M
M2 = pairwise(L2); M1 = pairwise(L1)
np.save('/home/user/work/M2.npy', M2); np.save('/home/user/work/M1.npy', M1)
print('P2 close pairs (dE00 < 4):')
for i in range(92):
    for j in range(i+1, 92):
        if M2[i, j] < 4:
            ri, rj = P2_ROWS[i], P2_ROWS[j]
            pi, pj = P2_TO_P1.get(i+1), P2_TO_P1.get(j+1)
            d1 = M1[pi-1, pj-1] if (pi and pj) else None
            print('  %2d %-6s %-38s | %2d %-6s %-38s dE2=%.2f  P1:%s/%s dE1=%s' % (
                ri[0], ri[1], ri[2][:38], rj[0], rj[1], rj[2][:38], M2[i, j],
                pi, pj, ('%.1f' % d1) if d1 is not None else '-'))
print('P1 close pairs (dE00 < 4):')
for i in range(86):
    for j in range(i+1, 86):
        if M1[i, j] < 4:
            print('  %2d %-40s | %2d %-40s dE1=%.2f' % (i+1, P1_LABELS[i][:40], j+1, P1_LABELS[j][:40], M1[i, j]))
