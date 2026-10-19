import pymupdf
from PIL import Image, ImageDraw
import numpy as np, geopandas as gpd
d=pymupdf.open('Mineral_Resources_Map_of_Nigeria_2023 (2).pdf'); p=d[0]
# Render legend column clip at 200dpi (zoom 2.777)
zoom=200/72
clip=pymupdf.Rect(2075,320,2300,1400)
pix=p.get_pixmap(matrix=pymupdf.Matrix(zoom,zoom), clip=clip)
pix.save("work/mineral_legend_render.png")
print("legend render", pix.width, pix.height)
# Transform for img19/21 placement
for xref in [19,21]:
    info=[x for x in p.get_image_info(xrefs=True) if x.get('xref')==xref][0]
    print(xref, info)
# Overlay QA: base raster crops with existing points
base=Image.open("work/mineral_base_2060x1677.png").convert("RGB")
minr=gpd.read_file("shapefile_results/minerals/nigeria_mineral_symbols.shp")
def crop_with_points(name, x0,y0,x1,y1, scale=3):
    c=base.crop((x0,y0,x1,y1)).resize(((x1-x0)*scale,(y1-y0)*scale), Image.NEAREST)
    dr=ImageDraw.Draw(c)
    sel=minr[(minr.px_x>=x0)&(minr.px_x<x1)&(minr.px_y>=y0)&(minr.px_y<y1)]
    for _,r in sel.iterrows():
        cx,cy=(r.px_x-x0)*scale,(r.px_y-y0)*scale
        dr.ellipse([cx-7,cy-7,cx+7,cy+7], outline=(255,0,255), width=2)
        dr.line([cx-10,cy,cx+10,cy], fill=(255,0,255), width=1)
        dr.line([cx,cy-10,cx,cy+10], fill=(255,0,255), width=1)
        dr.text((cx+8,cy-6), str(int(r.fid)), fill=(255,0,255))
    c.save(name)
    print(name, f"points={len(sel)}")
# Dense Jos Plateau cluster around px (950-1150, 600-780)? find densest cell
pts=minr[['px_x','px_y']].values
H,_,_=np.histogram2d(pts[:,0],pts[:,1],bins=[np.arange(0,2100,200),np.arange(0,1750,200)])
print("densest 200px cells:", np.dstack(np.unravel_index(np.argsort(H.ravel())[::-1][:5], H.shape))[0], np.sort(H.ravel())[::-1][:5])
crop_with_points("work/qa_overlay_dense.png", 800,600,1100,850)
crop_with_points("work/qa_overlay_NE.png", 1400,150,1750,450)
crop_with_points("work/qa_overlay_SWdense.png", 150,950,450,1200)
crop_with_points("work/qa_overlay_sparse_north.png", 300,80,650,330)
# Symbol size: crop single isolated points enlarged
from scipy.spatial import cKDTree
tree=cKDTree(pts); dd,_=tree.query(pts,k=2); nn=dd[:,1]
iso=minr[nn>40].head(12)
for _,r in iso.iterrows():
    x,y=int(r.px_x),int(r.py_y) if hasattr(r,'py_y') else int(r.px_y)
    c=base.crop((x-14,y-14,x+15,y+15)).resize((290,290), Image.NEAREST)
    c.save(f"work/sym_fid{int(r.fid)}_{r.mineral.replace(' ','_')}.png")
    print("isolated", int(r.fid), r.mineral, x,y)
