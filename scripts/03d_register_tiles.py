"""Tile-wise ECC translations to test if affine suffices or distortion field exists."""
import json
import numpy as np, cv2
from PIL import Image
Image.MAX_IMAGE_PIXELS=None
A_best = np.array(json.load(open("work/register_v2_final.json"))["A"])
print("A_best:\n", A_best)
jpg = cv2.imread("pic NGSA geological-map-of-nigeria-.jpg", cv2.IMREAD_GRAYSCALE)
v2g = cv2.cvtColor(np.array(Image.open("NGSA_map_geology_legend_isolated_v2.png").convert("RGB")), cv2.COLOR_RGB2GRAY)
# Downscale factor for field measurement
s = 0.5
inp = cv2.resize(jpg, None, fx=s, fy=s, interpolation=cv2.INTER_AREA)
# Warp v2 into jpg-small coords: As maps v2full->jpgsmall
As = A_best.copy(); As[:,:2]*=s; As[:,2]*=s
warped = cv2.warpAffine(v2g, As.astype(np.float32), (inp.shape[1], inp.shape[0]), flags=cv2.INTER_LINEAR, borderValue=255)
mask = cv2.warpAffine(np.full(v2g.shape,255,np.uint8), As.astype(np.float32), (inp.shape[1], inp.shape[0]), borderValue=0)
# Tiles over map frame small coords: frame (187..4313,188..3525)*s
fx0,fy0,fx1,fy1 = int(187*s),int(188*s),int(4313*s),int(3525*s)
cols, rows = 4, 3
tw, th = (fx1-fx0)//cols, (fy1-fy0)//rows
results=[]
for r in range(rows):
    for c in range(cols):
        x0,y0 = fx0+c*tw, fy0+r*th
        # expand tile by margin for ECC stability, evaluate shift at centre
        m=30
        xs,ys = max(0,x0-m), max(0,y0-m)
        xe,ye = min(inp.shape[1],x0+tw+m), min(inp.shape[0],y0+th+m)
        t_inp = inp[ys:ye, xs:xe].astype(np.float32)/255.0
        t_tpl = warped[ys:ye, xs:xe].astype(np.float32)/255.0
        t_msk = cv2.erode(mask[ys:ye, xs:xe], np.ones((9,9),np.uint8))
        frac = (t_msk>0).mean()
        if frac<0.35:
            print(f"tile r{r}c{c}: skip mask frac {frac:.2f}"); continue
        warp = np.eye(2,3,dtype=np.float32)
        crit=(cv2.TERM_CRITERIA_EPS|cv2.TERM_CRITERIA_COUNT,120,1e-7)
        try:
            cc, warp = cv2.findTransformECC(t_tpl, t_inp, warp, cv2.MOTION_TRANSLATION, crit, t_msk, 5)
        except Exception as e:
            print(f"tile r{r}c{c}: ECC fail {e}"); continue
        # warp maps inp->tpl coords per docs; shift of tpl relative to inp = ? Report raw; centre in full px:
        cx_full, cy_full = (x0+tw/2)/s, (y0+th/2)/s
        # Convert small-px translation to full jpg px
        dx_full, dy_full = warp[0,2]/s, warp[1,2]/s
        print(f"tile r{r}c{c} centre_full=({cx_full:.0f},{cy_full:.0f}) cc={cc:.4f} warp_t_small=({warp[0,2]:+.2f},{warp[1,2]:+.2f}) -> full ({dx_full:+.2f},{dy_full:+.2f}) jpg-px maskfrac={frac:.2f}")
        results.append(dict(r=r,c=c,cx=float(cx_full),cy=float(cy_full),cc=float(cc),tx_small=float(warp[0,2]),ty_small=float(warp[1,2])))
json.dump(results, open("work/register_tiles.json","w"), indent=1)
if results:
    tx=np.array([r["tx_small"] for r in results])/s; ty=np.array([r["ty_small"] for r in results])/s
    print(f"\nTile translations (full jpg px): dx median={np.median(tx):+.2f} range[{tx.min():+.2f},{tx.max():+.2f}] | dy median={np.median(ty):+.2f} range[{ty.min():+.2f},{ty.max():+.2f}]")
    print(f"Spread (std) dx={tx.std():.2f} dy={ty.std():.2f} px; |shift| median={np.median(np.hypot(tx,ty)):.2f} px")
