"""Register v2 to JPG via Nigeria outer-contour ICP (affine)."""
import json
import numpy as np, cv2
from PIL import Image
from scipy.spatial import cKDTree
Image.MAX_IMAGE_PIXELS=None

jpg = cv2.imread("pic NGSA geological-map-of-nigeria-.jpg")  # BGR
H,W = jpg.shape[:2]
# --- JPG Nigeria mask inside map frame ---
x0,y0,x1,y1 = 187,188,4313,3525
frame = jpg[y0:y1+1, x0:x1+1].copy()
print("frame", frame.shape)
sea_sample = np.median(frame[3000:3250, 100:600].reshape(-1,3), axis=0)  # Gulf of Guinea BGR
print("sea BGR sample:", sea_sample)
f = frame.astype(np.int16)
dist_sea = np.sqrt(((f - sea_sample.astype(np.int16))**2).sum(axis=2))
whiteish = (frame[:,:,0]>238)&(frame[:,:,1]>238)&(frame[:,:,2]>238)
fg = ((~whiteish) & (dist_sea>42)).astype(np.uint8)
# clean: close small gaps (roads/text), open specks
fg = cv2.morphologyEx(fg, cv2.MORPH_CLOSE, np.ones((7,7),np.uint8))
fg = cv2.morphologyEx(fg, cv2.MORPH_OPEN, np.ones((3,3),np.uint8))
n, lab, stats, cent = cv2.connectedComponentsWithStats(fg, 8)
largest = 1+np.argmax(stats[1:, cv2.CC_STAT_AREA])
mask_j = (lab==largest).astype(np.uint8)
print(f"JPG components={n} largest area={stats[largest, cv2.CC_STAT_AREA]} frac={mask_j.mean():.3f}")
# fill holes in largest
cnts,_ = cv2.findContours(mask_j, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_NONE)
filled = np.zeros_like(mask_j); cv2.drawContours(filled, cnts, -1, 1, -1)
mask_j = filled
cv2.imwrite("work/reg_jpg_nigeria_mask.png", (mask_j*255).astype(np.uint8))
cnt_j = max(cnts, key=cv2.contourArea).reshape(-1,2).astype(np.float64)
cnt_j[:,0]+=x0; cnt_j[:,1]+=y0  # full-sheet coords
print(f"JPG contour pts={len(cnt_j)} bbox x[{cnt_j[:,0].min():.0f},{cnt_j[:,0].max():.0f}] y[{cnt_j[:,1].min():.0f},{cnt_j[:,1].max():.0f}]")

# --- v2 mask/contour ---
v2pil = Image.open("NGSA_map_geology_legend_isolated_v2.png")
idx = np.array(v2pil)
mask_v = (idx!=0).astype(np.uint8)
cnts_v,_ = cv2.findContours(mask_v, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_NONE)
cnt_v = max(cnts_v, key=cv2.contourArea).reshape(-1,2).astype(np.float64)
print(f"v2 contour pts={len(cnt_v)} bbox x[{cnt_v[:,0].min():.0f},{cnt_v[:,0].max():.0f}] y[{cnt_v[:,1].min():.0f},{cnt_v[:,1].max():.0f}]")

def resample(pts, n=3000):
    # uniform by index after approx (contour already dense & ordered); use arc-length
    d = np.r_[0, np.cumsum(np.hypot(np.diff(pts[:,0]), np.diff(pts[:,1])))]
    total = d[-1] + np.hypot(pts[0,0]-pts[-1,0], pts[0,1]-pts[-1,1])
    t = np.linspace(0, d[-1], n)
    return np.column_stack([np.interp(t, d, pts[:,0]), np.interp(t, d, pts[:,1])])
Pv = resample(cnt_v, 3000); Pj = resample(cnt_j, 3000)
np.save("work/contour_v2.npy", Pv); np.save("work/contour_jpg.npy", Pj)

# --- initial affine from bboxes ---
def bbox_affine(src, dst):
    s_min, s_max = src.min(axis=0), src.max(axis=0)
    d_min, d_max = dst.min(axis=0), dst.max(axis=0)
    sc = (d_max-d_min)/(s_max-s_min)
    A = np.array([[sc[0],0,d_min[0]-sc[0]*s_min[0]],[0,sc[1],d_min[1]-sc[1]*s_min[1]]])
    return A
A = bbox_affine(Pv, Pj)
print("init bbox affine:\n", A)
def applyA(A,P): return (A[:,:2]@P.T).T + A[:,2]
def solve_affine(src, dst):
    # least squares affine src->dst
    X = np.column_stack([src, np.ones(len(src))])
    coef, *_ = np.linalg.lstsq(X, dst, rcond=None)  # 3x2
    return coef.T  # 2x3
tree = cKDTree(Pj)
for it in range(60):
    Pw = applyA(A, Pv)
    dist, ind = tree.query(Pw, k=1)
    # robust trim: keep best 92%
    thr = np.percentile(dist, 92)
    keep = dist<=thr
    A_new = solve_affine(Pv[keep], Pj[ind[keep]])
    delta = np.abs(A_new-A).max()
    A = A_new
    if it%10==0 or delta<1e-4:
        print(f" iter {it}: median dist={np.median(dist):.3f} jpg-px, p90={np.percentile(dist,90):.2f}, rms={np.sqrt(np.mean(dist**2)):.2f}, kept={keep.sum()}, dA={delta:.5f}")
    if delta<1e-4: break
Pw = applyA(A,Pv); dist, ind = tree.query(Pw)
print("FINAL affine v2->jpg:\n", A)
print(f"contour dist jpg-px: median={np.median(dist):.3f} mean={dist.mean():.3f} rms={np.sqrt(np.mean(dist**2)):.3f} p90={np.percentile(dist,90):.2f} p99={np.percentile(dist,99):.2f} max={dist.max():.2f}")
sx=np.hypot(A[0,0],A[1,0]); sy=np.hypot(A[0,1],A[1,1]); rot=np.degrees(np.arctan2(A[1,0],A[0,0]))
print(f"scale x={sx:.6f} y={sy:.6f} rot={rot:.4f}deg trans={A[:,2]}")
json.dump(dict(A=A.tolist(), contour_median_jpgpx=float(np.median(dist)), contour_rms_jpgpx=float(np.sqrt(np.mean(dist**2))),
               contour_p90_jpgpx=float(np.percentile(dist,90)), scale=[float(sx),float(sy)], rotation_deg=float(rot)),
          open("work/register_v2_contour.json","w"), indent=1)
# QA overlay at half scale
s=0.5
ov = cv2.resize(jpg, None, fx=s, fy=s, interpolation=cv2.INTER_AREA)
pts = (Pw*s).astype(np.int32).reshape(-1,1,2)
cv2.polylines(ov, [pts], True, (0,0,255), 2)
cv2.imwrite("work/reg_overlay_contour_ICP.png", ov)
print("wrote work/reg_overlay_contour_ICP.png")
