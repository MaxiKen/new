"""Register NGSA_map_geology_legend_isolated_v2.png to geology JPG (full-sheet px) via SIFT+RANSAC, ECC refine."""
import json, sys
import numpy as np, cv2
from PIL import Image
Image.MAX_IMAGE_PIXELS = None

print("loading...")
jpg = cv2.imread("pic NGSA geological-map-of-nigeria-.jpg")
print("jpg", jpg.shape)
v2pil = Image.open("NGSA_map_geology_legend_isolated_v2.png")
v2rgb = np.array(v2pil.convert("RGB"))
print("v2", v2rgb.shape)
v2 = cv2.cvtColor(v2rgb, cv2.COLOR_RGB2BGR)

# Work at scale s for matching (relative to full res of each image)
s_jpg, s_v2 = 0.5, 0.25  # jpg 3300x1837, v2 1930x1607 - comparable ground sampling
def prep(img, s):
    small = cv2.resize(img, None, fx=s, fy=s, interpolation=cv2.INTER_AREA)
    g = cv2.cvtColor(small, cv2.COLOR_BGR2GRAY)
    # edge-enhanced: blur+edges blended helps match flat-fill vs scanned map
    e = cv2.Canny(cv2.GaussianBlur(g,(5,5),0), 60, 150)
    return g, e
gj, ej = prep(jpg, s_jpg)
gv, ev = prep(v2, s_v2)
print("small jpg", gj.shape, "small v2", gv.shape)
cv2.imwrite("work/reg_jpg_edges.png", ej); cv2.imwrite("work/reg_v2_edges.png", ev)

sift = cv2.SIFT_create(nfeatures=8000)
kp1, des1 = sift.detectAndCompute(ev, None)
kp2, des2 = sift.detectAndCompute(ej, None)
print(f"SIFT kp v2={len(kp1)} jpg={len(kp2)}")
bf = cv2.BFMatcher()
matches = bf.knnMatch(des1, des2, k=2)
good=[]
for m_n in matches:
    if len(m_n)!=2: continue
    m,n = m_n
    if m.distance < 0.75*n.distance: good.append(m)
good.sort(key=lambda m:m.distance)
print(f"good matches: {len(good)}")
src = np.array([kp1[m.queryIdx].pt for m in good], dtype=np.float64)  # v2 small coords
dst = np.array([kp2[m.trainIdx].pt for m in good], dtype=np.float64)  # jpg small coords
# to full-res coords
srcF = src / s_v2; dstF = dst / s_jpg
M, inliers = cv2.estimateAffine2D(srcF, dstF, method=cv2.RANSAC, ransacReprojThreshold=6.0, maxIters=5000, confidence=0.999)
print("Affine v2_full -> jpg_full:\n", M)
inl = inliers.ravel().astype(bool)
print(f"inliers {inl.sum()}/{len(good)}")
pred = (M[:,:2] @ srcF.T).T + M[:,2]
res = np.linalg.norm(pred-dstF, axis=1)
print(f"RANSAC inlier residuals (jpg px): median={np.median(res[inl]):.2f} mean={res[inl].mean():.2f} p90={np.percentile(res[inl],90):.2f} max={res[inl].max():.2f}")
print(f"all matches median residual: {np.median(res):.2f} px")
# scale/rotation decomposition
sx = np.hypot(M[0,0], M[1,0]); sy = np.hypot(M[0,1], M[1,1]); rot = np.degrees(np.arctan2(M[1,0], M[0,0]))
print(f"scale x={sx:.5f} y={sy:.5f} rotation={rot:.4f} deg translation={M[:,2]}")
json.dump(dict(M=M.tolist(), n_good=len(good), n_inliers=int(inl.sum()),
               resid_median_jpgpx=float(np.median(res[inl])), resid_p90_jpgpx=float(np.percentile(res[inl],90)),
               scale=[float(sx),float(sy)], rotation_deg=float(rot),
               inlier_src=srcF[inl].tolist(), inlier_dst=dstF[inl].tolist()),
          open("work/register_v2_sift.json","w"))
# QA overlay: warp v2 (small) onto jpg (small) with M scaled
Ms = M.copy()
# v2small->jpgfull: scale src by 1/s_v2 handled: jpg_small = s_jpg * (M @ (v2_small/s_v2))
A = np.zeros((2,3)); A[:,:2] = M[:,:2]*(s_jpg/s_v2); A[:,2] = M[:,2]*s_jpg
warped = cv2.warpAffine(gv, A, (gj.shape[1], gj.shape[0]), flags=cv2.INTER_LINEAR, borderValue=0)
mask = cv2.warpAffine(np.full(gv.shape,255,np.uint8), A, (gj.shape[1], gj.shape[0]), borderValue=0)
blend = gj.copy()
blend[mask>0] = (0.5*gj[mask>0].astype(float)+0.5*warped[mask>0].astype(float)).astype(np.uint8)
cv2.imwrite("work/reg_overlay_gray.png", blend)
# contour overlay in color
jpg_s = cv2.resize(jpg, None, fx=s_jpg, fy=s_jpg, interpolation=cv2.INTER_AREA)
v2mask_small = (cv2.resize(v2rgb[:,:,0], None, fx=s_v2, fy=s_v2, interpolation=cv2.INTER_AREA) < 250) | (cv2.resize(v2rgb[:,:,1], None, fx=s_v2, fy=s_v2, interpolation=cv2.INTER_AREA) < 250)
# simpler: v2 fg from non-white in gv? gv gray of white bg=255
fg = (gv < 252).astype(np.uint8)*255
cnts,_ = cv2.findContours(fg, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_NONE)
cnt = max(cnts, key=cv2.contourArea)
pts = cnt.reshape(-1,2).astype(np.float64)
pts_w = (A[:,:2] @ pts.T).T + A[:,2]
overlay = jpg_s.copy()
cv2.polylines(overlay, [pts_w.astype(np.int32).reshape(-1,1,2)], True, (0,0,255), 2)
cv2.imwrite("work/reg_overlay_contour.png", overlay)
print("wrote QA overlays")
