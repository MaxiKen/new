"""Refine v2->JPG affine: guided SIFT (using ICP init) + ECC. Pick best by independent contour metric."""
import json
import numpy as np, cv2
from PIL import Image
from scipy.spatial import cKDTree
Image.MAX_IMAGE_PIXELS=None

A0 = np.array(json.load(open("work/register_v2_contour.json"))["A"])
print("init A0:\n", A0)
jpg = cv2.imread("pic NGSA geological-map-of-nigeria-.jpg")
v2rgb = np.array(Image.open("NGSA_map_geology_legend_isolated_v2.png").convert("RGB"))
v2 = cv2.cvtColor(v2rgb, cv2.COLOR_RGB2BGR)
gj_full = cv2.cvtColor(jpg, cv2.COLOR_BGR2GRAY)
gv_full = cv2.cvtColor(v2, cv2.COLOR_BGR2GRAY)

def affine_apply(A,P): return (A[:,:2]@P.T).T+A[:,2]
Pv = np.load("work/contour_v2.npy"); Pj = np.load("work/contour_jpg.npy")
tree = cKDTree(Pj)
def contour_metrics(A, tag):
    d,_ = tree.query(affine_apply(A,Pv))
    print(f"{tag}: contour dist jpg-px median={np.median(d):.2f} mean={d.mean():.2f} rms={np.sqrt(np.mean(d**2)):.2f} p90={np.percentile(d,90):.2f}")
    return float(np.median(d)), float(np.sqrt(np.mean(d**2)))
contour_metrics(A0, "A0 ICP")

# ---- Guided SIFT at moderate scale ----
s_j, s_v = 0.6, 0.3
gj = cv2.resize(gj_full, None, fx=s_j, fy=s_j, interpolation=cv2.INTER_AREA)
gv = cv2.resize(gv_full, None, fx=s_v, fy=s_v, interpolation=cv2.INTER_AREA)
# mask JPG to map frame area only (in small coords): x<4313*s, y in frame
mask_j = np.zeros(gj.shape, np.uint8); mask_j[int(188*s_j):int(3525*s_j), int(187*s_j):int(4313*s_j)]=255
sift = cv2.SIFT_create(nfeatures=12000, contrastThreshold=0.02)
kp_v, des_v = sift.detectAndCompute(gv, None)
kp_j, des_j = sift.detectAndCompute(gj, mask_j)
print(f"SIFT kp v2={len(kp_v)} jpg(frame)={len(kp_j)}")
bf = cv2.BFMatcher()
matches = bf.knnMatch(des_v, des_j, k=2)
cand=[]
for mn in matches:
    if len(mn)!=2: continue
    m,n = mn
    if m.distance < 0.78*n.distance: cand.append(m)
print(f"ratio-pass matches: {len(cand)}")
# guide: predicted jpg_full via A0 must be within 30 jpg-full px
src=[]; dst=[]
for m in cand:
    pv = np.array(kp_v[m.queryIdx].pt)/s_v
    pj = np.array(kp_j[m.trainIdx].pt)/s_j
    pred = affine_apply(A0, pv[None,:])[0]
    if np.hypot(*(pred-pj)) < 30:
        src.append(pv); dst.append(pj)
src=np.array(src); dst=np.array(dst)
print(f"guided-consistent matches: {len(src)}")
A_sift=None
if len(src)>=12:
    M, inl = cv2.estimateAffine2D(src, dst, method=cv2.RANSAC, ransacReprojThreshold=3.0, maxIters=8000, confidence=0.999)
    inl = inl.ravel().astype(bool)
    pred = affine_apply(M, src); res=np.linalg.norm(pred-dst,axis=1)
    print(f"SIFT affine inliers {inl.sum()}/{len(src)} median resid={np.median(res[inl]):.2f} jpg-px p90={np.percentile(res[inl],90):.2f}")
    print(M)
    A_sift=M
    contour_metrics(M, "A_sift")
    # spatial spread of inliers
    print("inlier src bbox:", src[inl].min(axis=0).round(0), src[inl].max(axis=0).round(0))

# ---- ECC refine from best init ----
def ecc_refine(A_init, scale=0.30, iters=200):
    # Work in JPG-full*scale canvas. Template=v2 gray scaled so its px correspond via warp.
    # Build: input = gj_full downscaled; template = gv_full warped? OpenCV ECC aligns template to input with warp mapping input->template? 
    # Safer iterative approach: warp v2 into JPG canvas with A_init, then ECC estimates small correction warp (input=jpg canvas, template=warped v2).
    inp = cv2.resize(gj_full, None, fx=scale, fy=scale, interpolation=cv2.INTER_AREA).astype(np.float32)/255.0
    # warp v2 full -> jpg full canvas then downscale (warp at full is heavy: do scaled warp directly)
    # v2_small coords = v2_full * kv ; jpg_small = scale*(A@v2_full) => A_s = scale * A * diag(1/kv) with kv chosen = scale/ (scale factor of A ~0.508) -> use kv=scale/0.508 approx 0.59
    kv = scale/0.508
    gv_s = cv2.resize(gv_full, None, fx=kv, fy=kv, interpolation=cv2.INTER_AREA)
    As = A_init.copy().astype(np.float32)
    As[:,:2] = A_init[:,:2]*(scale/kv); As[:,2] = A_init[:,2]*scale
    tpl = cv2.warpAffine(gv_s, As, (inp.shape[1], inp.shape[0]), flags=cv2.INTER_LINEAR, borderValue=255).astype(np.float32)/255.0
    msk = cv2.warpAffine(np.full(gv_s.shape,255,np.uint8), As, (inp.shape[1], inp.shape[0]), borderValue=0)
    # erode mask to avoid border effects
    msk = cv2.erode(msk, np.ones((9,9),np.uint8))
    warp = np.eye(2,3,dtype=np.float32)
    criteria = (cv2.TERM_CRITERIA_EPS|cv2.TERM_CRITERIA_COUNT, iters, 1e-7)
    try:
        cc, warp = cv2.findTransformECC(tpl, inp, warp, cv2.MOTION_AFFINE, criteria, msk, 5)
        print(f"ECC cc={cc:.5f} correction warp (small coords):\n{warp}")
    except Exception as e:
        print("ECC failed:", e); return A_init, None
    # findTransformECC returns warp that maps input(inp) coords to template? Documentation: template is warped to input... warpMatrix transforms point in inputImage to templateImage?
    # Empirical: correction should be near identity. Compose both ways and pick better by contour metric after converting to full coords.
    W = warp.astype(np.float64)
    # Candidate 1: jpg_corrected_point = W^{-1} applied? Build full-res candidates:
    # Small-coord mapping v2s->jpgs is As. If ECC warp W maps inp->tpl coordinates (i.e. tpl(W(x))=inp(x)), then improved mapping = W^{-1} o As ... test both + identity.
    def to_full(Asmall):
        Af = np.zeros((2,3)); Af[:,:2]=Asmall[:,:2]*(kv/scale); Af[:,2]=Asmall[:,2]/scale; return Af
    def compose(P,Q): # apply Q then P: P(Q(x))
        R=np.zeros((2,3)); R[:,:2]=P[:,:2]@Q[:,:2]; R[:,2]=P[:,:2]@Q[:,2]+P[:,2]; return R
    def inv_aff(P):
        Ai=np.linalg.inv(P[:,:2]); R=np.zeros((2,3)); R[:,:2]=Ai; R[:,2]=-Ai@P[:,2]; return R
    cands = {"W_o_As": compose(W, As.astype(np.float64)), "Winv_o_As": compose(inv_aff(W), As.astype(np.float64)), "As_only": As.astype(np.float64)}
    best=None
    for k,v in cands.items():
        Af = to_full(v)
        med,rms = contour_metrics(Af, f"ECCcand {k}")
        if best is None or med<best[1]: best=(k,med,Af)
    print("ECC best:", best[0])
    return best[2], cc

A_cur = A_sift if A_sift is not None else A0
A_ecc, cc = ecc_refine(A_cur)
# Final choice: compare contour medians
cands_final = [("ICP",A0)]
if A_sift is not None: cands_final.append(("SIFT",A_sift))
if A_ecc is not None: cands_final.append(("ECC",A_ecc))
results=[]
for tag,A in cands_final:
    med,rms = contour_metrics(A, f"FINAL? {tag}")
    results.append((med,rms,tag,A))
results.sort(key=lambda r:r[0])
med,rms,tag,A_best = results[0]
print(f"\nCHOSEN: {tag} median={med:.2f} jpg-px")
print(A_best)
json.dump(dict(A=A_best.tolist(), method=tag, contour_median_jpgpx=med, contour_rms_jpgpx=rms,
               A_ICP=A0.tolist(), A_SIFT=(A_sift.tolist() if A_sift is not None else None),
               A_ECC=(A_ecc.tolist() if A_ecc is not None else None)),
          open("work/register_v2_final.json","w"), indent=1)
# QA overlays: full + 3 zooms (NW Sokoto, Jos centre, Niger Delta coast)
s=0.5
ov = cv2.resize(jpg, None, fx=s, fy=s, interpolation=cv2.INTER_AREA)
Pw = affine_apply(A_best, Pv)
cv2.polylines(ov, [(Pw*s).astype(np.int32).reshape(-1,1,2)], True, (0,0,255), 2)
cv2.imwrite("work/reg_overlay_final.png", ov)
# zoom crops with warped v2 edges in red over jpg
v2_warped = cv2.warpAffine(gv_full, A_best.astype(np.float32), (gj_full.shape[1], gj_full.shape[0]), flags=cv2.INTER_LINEAR, borderValue=255)
edges_w = cv2.Canny(v2_warped, 60, 150)
for name,(cx,cy,half) in {"NW_Sokoto":(900,700,450), "Centre_Jos":(2600,1800,450), "Delta_coast":(1500,3100,450), "NE_Borno":(3600,600,450)}.items():
    crop = jpg[cy-half:cy+half, cx-half:cx+half].copy()
    ew = edges_w[cy-half:cy+half, cx-half:cx+half]
    crop[ew>0] = (0,0,255)
    cv2.imwrite(f"work/reg_zoom_{name}.png", crop)
    print("zoom", name)
print("DONE 03c")
