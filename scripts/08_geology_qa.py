"""Geology QA plots: whole-country render + detail overlay on source JPG."""
import sys, json
sys.path.insert(0,"scripts")
import numpy as np
import geopandas as gpd
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
from PIL import Image

g=gpd.read_file("output/02_Shapefiles/Geology_Rocks.shp")
bnd=gpd.read_file("output/02_Shapefiles/Nigeria_Boundary.shp")
fig,ax=plt.subplots(figsize=(11,10))
g.plot(ax=ax, color=g["HEX"], linewidth=0)
bnd.boundary.plot(ax=ax, color="black", linewidth=0.7)
ax.set_title(f"Geology_Rocks — {len(g)} polygons, {g['UNIT_IDX'].nunique()} units, area {g['AREA_KM2'].sum():,.0f} km2")
ax.set_xlabel("Longitude (WGS84)"); ax.set_ylabel("Latitude (WGS84)")
fig.tight_layout(); fig.savefig("output/03_QA_Check_Plots/QA_Geology_WholeCountry.png", dpi=110)
print("whole country saved")

# detail: Keffi-Lafia area lon 7.6-8.7, lat 8.3-9.2 over JPG
gj=json.load(open("work/georef_geology.json"))
print("georef keys:", list(gj.keys())[:8])
# lon = a*u+b with u=px+0.5 (session-derived); recover coeffs from json if present else defaults
a_lon=gj.get("lon_coef",[0.0030454997,1.75445908])[0]; b_lon=gj.get("lon_coef",[0.0030454997,1.75445908])[1]
a_lat=gj.get("lat_coef",[-0.0030457553,14.47736835])[0]; b_lat=gj.get("lat_coef",[-0.0030457553,14.47736835])[1]
def px_of(lon,lat):
    return (lon-b_lon)/a_lon-0.5, (lat-b_lat)/a_lat-0.5
lon0,lon1,lat0,lat1=7.55,8.75,8.25,9.25
x0,y1_=px_of(lon0,lat1); x1,y0_=px_of(lon1,lat0)
img=Image.open("pic NGSA geological-map-of-nigeria-.jpg")
crop=img.crop((int(x0),int(y1_),int(x1),int(y0_)))
sub=g.cx[lon0:lon1, lat0:lat1]
fig,axes=plt.subplots(1,2,figsize=(15,7))
axes[0].imshow(crop, extent=[lon0,lon1,lat0,lat1], aspect="auto")
axes[0].set_title("Source JPG (NGSA geological map) — Keffi-Lafia")
sub.plot(ax=axes[1], color=sub["HEX"], linewidth=0.25, edgecolor="#333333")
axes[1].set_xlim(lon0,lon1); axes[1].set_ylim(lat0,lat1)
axes[1].set_title("Geology_Rocks polygons (same extent)")
fig.tight_layout(); fig.savefig("output/03_QA_Check_Plots/QA_Geology_Detail_Keffi.png", dpi=110)
print("detail saved, sub polys:", len(sub))
# NW detail (Sokoto, regularized West strip check): lon 4.6-6.2 lat 11.8-13.2
lon0,lon1,lat0,lat1=4.55,6.25,11.75,13.25
x0,y1_=px_of(lon0,lat1); x1,y0_=px_of(lon1,lat0)
crop=img.crop((int(x0),int(y1_),int(x1),int(y0_)))
sub=g.cx[lon0:lon1, lat0:lat1]
fig,axes=plt.subplots(1,2,figsize=(15,7))
axes[0].imshow(crop, extent=[lon0,lon1,lat0,lat1], aspect="auto"); axes[0].set_title("Source JPG — Sokoto (NW)")
sub.plot(ax=axes[1], color=sub["HEX"], linewidth=0.25, edgecolor="#333333")
axes[1].set_xlim(lon0,lon1); axes[1].set_ylim(lat0,lat1); axes[1].set_title("Geology_Rocks polygons (same extent)")
fig.tight_layout(); fig.savefig("output/03_QA_Check_Plots/QA_Geology_Detail_Sokoto.png", dpi=110)
print("Sokoto saved, sub polys:", len(sub))
