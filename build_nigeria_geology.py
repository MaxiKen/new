#!/usr/bin/env python3
"""Build Nigeria geological polygon GPKG - 86 legend units, smooth organic boundaries, no gaps."""
import math, json
import numpy as np
import geopandas as gpd
from shapely.geometry import Point, Polygon, MultiPolygon, LineString
from shapely.ops import unary_union
from scipy.spatial import Voronoi, cKDTree

# ---------------------------------------------------------------- load base
NIGERIA_UNION = "/tmp/nigeria_union.geojson"
OUT_GPKG = "/home/user/new/nigeria_geology_legends.gpkg"
OUT_GEOJSON = "/home/user/new/nigeria_geology_legends.geojson"
OUT_CSV = "/home/user/new/nigeria_geology_legend_count.csv"
OUT_PNG = "/home/user/new/nigeria_geology_preview.png"

gdf_base = gpd.read_file(NIGERIA_UNION)
nigeria = gdf_base.geometry.iloc[0]
print(f"Nigeria base: {nigeria.geom_type}, bounds={nigeria.bounds}, area={nigeria.area:.4f} deg2")
assert nigeria.is_valid

# ------------------------------------------------- 86 legend definitions
# id, clean name, original (image2), NGSA code, formation, age, province, lon, lat
LEGENDS = [
 # --- coastal / delta / recent (A) ---
 ("L36","Alluvium","Alluvium","Al","Sediments (Recent alluvium, river channels, delta)","Recent","Niger Delta / rivers",6.05,4.85),
 ("L26","Sands, Gravels and Clay","Sands, Gravels and Clay","MWS","Meander belt, back swamps, fresh water swamps","Holocene (Neogene)","Niger Delta",5.55,5.35),
 ("L24","Sands and Pebbles","Sands and Pebbles","AB","Abandoned Beach Ridges","Holocene (Neogene)","SW coast (Lagos)",3.60,6.55),
 ("L23","Sand, Clay and Swamp","Sand, Clay and Swamp","SDsm","Sombreiro Deltaic Formation","Pleistocene/Pliocene","SE delta swamp",6.95,4.95),
 ("L22","Sand and Clay","Sand and Clay","Bnst","Benin Formation (coastal plain sands)","Pleistocene/Pliocene","South (Benin Fm, large)",5.95,6.35),
 ("L02","Lignite, Claystone and Shale","Lignite, Claystone and shale","OAlgs","Ogwashi-Asaba Formation","Oligocene/Miocene","South-central (Delta)",6.45,6.55),
 ("L50","Clay Clayey Sands and Shale","Clay clayey sands and shale","Issh","Ilaro Formation","Upper Eocene","SW Dahomey (Ogun)",3.35,6.95),
 ("L51","Clay, Clayey Sands and Shale","Clay, Clayey Sands and Shale","Issh-var","Ilaro Formation lateral (Dahomey Basin)","Upper Eocene","SW Dahomey west",3.05,6.85),
 ("L30","Sandstone and Limestone","Sandstone and Limestone","Asl","Abeokuta Formation (Dahomey Basin)","Coniacian/Maastrichtian","SW Dahomey (Ogun)",3.65,7.35),
 # --- SE Anambra / Lower Benue (C) ---
 ("L60","False-Bedded Sandstone","False - Bedded Sandstone","Ajst","Ajali Formation","Coniacian/Maastrichtian","SE Anambra (Enugu)",7.35,6.75),
 ("L55","Coal, Shale and Sandstone","Coal, Shale and Sandstone","Ncsh","Nsukka Formation","Coniacian/Maastrichtian","SE (Nsukka)",7.65,6.95),
 ("L31","Sandstone, Limestone, Coal","Sandstone, Limestone, Coal","Ncsh","Nsukka Formation lateral","Coniacian/Maastrichtian","SE Anambra",7.05,6.35),
 ("L54","Coal, Sandstone and Shale","Coal, Sandstone and Shale","Mcst","Mamu Formation (coal measures)","Coniacian","SE (Mamu)",7.55,6.45),
 ("L53","Coal Sandstone and Shale","Coal candstone and shale [candstone=sandstone]","Mcst-var","Mamu Formation lateral (coal measures)","Coniacian","SE (Ebonyi)",7.85,6.65),
 ("L75","Shale and Mudstone","Shale and Mudstone","Nsh","Nkporo Formation (incl. Enugu Shale)","Coniacian","SE (Nkporo)",7.90,6.15),
 ("L49","Clay and Shale with Limestone Intercalations","Clay and Shale with Limestone Intercalations","Imsh","Imo Group (Imo Shale)","Lower Eocene","SE (Imo)",7.10,5.75),
 ("L73","Shale and Limestone","Shale and Limestone","Esh/ANsh","Imo Group / Awgu Formation","Lower Eocene / Coniacian","SE (Imo/Awgu)",7.55,5.85),
 ("L74","Shale and Limestone with Sandstone Intercalations","Shale and Limestone with Sandstone Intercalations","Arlsh","Asu River Group","Albian","SE Lower Benue",8.25,6.45),
 ("L27","Sandstone","Sandstone","Ess/Awst","Eze-Aku Group / Awi-Mfamosing Fm","Turonian / Albian-Cenomanian","SE (Cross River)",8.55,6.05),
 ("L46","Blackshale, Siltstone and Sandstone","Blackshale, Siltstone and Sandstone","Esh","Eze-Aku Group (SE variant)","Turonian","SE (Abakaliki)",8.15,6.95),
 # --- Benue Trough + NE (D) ---
 ("L35","Sandstone, Shale and Sandy Shale","Sandstone, shale and sandyshale","Lass","Lafia-Wukari Formation","Turonian pre-Maastrichtian","Middle Benue",9.15,8.35),
 ("L29","Sandstone and Ironstone","Sandstone and Ironstone","Bssf","Bassange Formation","Coniacian","Middle Benue",9.55,8.75),
 ("L62","Feldspathic Sandstone, Calcareous Sandstone and Shelly Limestone","Feldspathic sandstone calcareous sandstone and shelly limestone","Bss","Bima Formation","Albian","Upper Benue (Bima)",11.35,9.55),
 ("L77","Shale, Sandclay, Calcareous Sandstones","Shale, Sandclay, Calcareous sandstones","Yls","Yola-Bima-Yolde Formation","Albian/Cenomanian","Upper Benue (Yola)",12.15,9.15),
 ("L76","Shale, Limestone and Sandstone","Shale, Limestone and Sandstone","Psh","Pindiga Formation","Turonian pre-Maastrichtian","Gongola (Pindiga)",11.15,9.95),
 ("L33","Sandstone, Siltstone, Shale and Ironstone","Sandstone, Siltstone, Shale and Ironstone","Gss","Gombe Formation","Coniacian/Maastrichtian","NE (Gombe)",11.05,10.55),
 ("L45","Black Shale, Siltstone and Sandstone","Black shale, siltstone and sandstone","Fsh","Fika Formation (NE variant)","Turonian pre-Maastrichtian","NE (Fika)",11.65,11.15),
 ("L34","Sandstone, Shale and Clay","Sandstone, shale and clay","Kss","Kerri-Kerri Formation","Palaeocene","NE (Kerri-Kerri, large)",10.65,11.25),
 ("L25","Sands, Clays, Siltstones and Limestones","Sands, Clays, Siltstones and limestones","Cst","Chad Formation","Pleistocene/Pliocene","NE Chad Basin (large)",13.15,12.55),
 # --- Bida/Nupe (E) ---
 ("L61","Feldspathic Sandstone and Siltstone","Feldspathic sandstone and siltstone","NPss","Nupe Formation (Nupe Group)","Turonian pre-Maastrichtian","Bida Basin (large)",6.05,9.15),
 ("L13","Pebbles and Grit","Pebbles and Grit","Glpg","Gundumi-Illo Formation","Turonian pre-Maastrichtian","NW Bida fringe",5.15,10.35),
 ("L48","Clay, Grit and Pebbles","Clay Grit and Pebbles","Glss","Gundumi-Illo Formation","Turonian pre-Maastrichtian","W Bida fringe",4.75,9.85),
 ("L68","Gravel and Sand","Gravel and Sand","Glgss","Gundumi-Illo Formation","Turonian pre-Maastrichtian","S Bida fringe",5.65,8.55),
 # --- Sokoto Basin NW (F) ---
 ("L28","Sandstone and Clay","Sandstone and Clay","Gwss","Gwandu Formation","Middle Eocene","NW Sokoto (large)",5.05,12.45),
 ("L70","Sandstones and Clays","Sandstones and Clays","Glcl","Gwandu/Ilo lateral (Sokoto)","Middle Eocene","NW Sokoto west",4.35,12.15),
 ("L03","Limestone","Limestone","Kls/Glls","Kalambaina / Dukamaje Formation (Sokoto/Rima Group)","Palaeocene / Senonian","NW Sokoto north",5.55,13.15),
 ("L72","Shale (Phosphate Nodules)","Shale (Phosphate nodules)","Wsh","Rima Group (Dukamaje/Wurno)","Senonian","NW Sokoto",5.85,12.75),
 ("L52","Clays and Loose Sandstone","Clays and loose sandstone","Wcs","Rima Group (Dukamaje/Wurno)","Senonian","NW (Kebbi)",4.65,11.55),
 ("L71","Sandstones, Clays and Shale","Sandstones, Clays and Shale","Wss","Rima Group (Dukamaje/Wurno)","Senonian","NW (Zamfara)",5.95,11.65),
 ("L32","Sandstone, Siltstone and Shale","Sandstone, Siltstone and Shale","Tst/Ts","Taloka Formation / Rima Group","Coniacian / Senonian","NW (Zamfara south)",5.35,11.15),
 # --- Jos Younger Granites + volcanics (G) ---
 ("L01","Ignimbrite","Ignimbrite [Ignimbrite]","Myl","Per-Alkaline Younger Granite Series","Jurassic","Jos Plateau",9.15,9.65),
 ("L19","Quartz Porphyry","Quartz porphyry","MyP","Per-Alkaline Younger Granite Series","Jurassic","Jos Plateau",9.35,9.45),
 ("L67","Granite and Granite Porphyry","Granite and Granite Porphyry","MyG/MGp","Per-Alkaline Younger Granite Series","Jurassic","Jos Plateau west",8.95,9.35),
 ("L80","Syenite, Quartz-Syenite and Gabbro","Syenite, Quartz-Syenite and Gabbro","Mys","Per-Alkaline Younger Granite Series","Jurassic","Jos Plateau east",9.55,9.65),
 ("L17","Porphyry / Quartz Porphyry","Porphyry/Quartz Porphyry","MyP","Per-Alkaline Younger Granite Series","Jurassic","Jos Plateau north",9.05,9.85),
 ("L21","Rhyolite","Rhyolite","r/Jyr","Younger Granite volcanics (ring dykes)","Jurassic","Jos Plateau north",9.35,10.05),
 ("L42","Biotite Granite","Biotite Granite","JyG","Younger Granite Series","Jurassic","Jos Plateau SW",8.85,9.05),
 ("L82","Trachy-Andesine","Trachy - andesine","JyA","Younger Granite Series","Jurassic","Jos Plateau SE",9.75,9.25),
 ("L85","Younger Basalt","Younger Basalt","b","Newer Basalt (volcanic plateau)","Tertiary to Recent","Biu Plateau",11.85,10.65),
 ("L40","Basalt","Basalt","bb","Older Basalt (volcanic)","Tertiary to Recent","Jos east / central",9.85,9.85),
 # --- Western schist belts / shear zones (H) ---
 ("L06","Meta-Volcanic and Meta-Sedimentary including Pebbly Schist","Meta Volcanic Meta Sedimentary including pebbly schist","MV","Meta-Sedimentary/Meta-Volcanic Series (schist belt)","Pre-Cambrian","W schist belt north",4.05,10.85),
 ("L37","Amphibole Schist, Amphibolite","Amphibole Schist, Amphibolite","Sa","Meta-Sedimentary/Meta-Volcanic Series","Pre-Cambrian","W schist belt",3.95,10.15),
 ("L39","Banded Iron Formation","Banded Iron Formation","BIF","Meta-Sedimentary/Meta-Volcanic Series (SE of Kabba)","Pre-Cambrian","Kogi (Kabba)",6.35,7.95),
 ("L79","Slate, Phyllite and Meta-Siltstone, locally Hornfelsic/Carbonaceous","Slate phyllite and meta siltstone, locally hornfelstic/carbonaceous","Sp","Meta-Sedimentary/Meta-Volcanic Series","Pre-Cambrian","W (Kwara)",4.15,8.75),
 ("L04","Marble","Marble","m","Meta-Sedimentary/Meta-Volcanic Series (lens)","Pre-Cambrian","W (Igbeti marble)",4.45,8.35),
 ("L64","Fine-Grained Flaggy Quartzite and Quartz Schist","Fine-grained flaggy quartzite and Quartz Schist","Sf","Meta-Sedimentary/Meta-Volcanic Series","Pre-Cambrian","W (Oyo)",3.85,8.15),
 ("L20","Quartzite, Massive and Schistose, also occurring as Ridges","Quartzite, massive and schistose, also occuring as ridges","Qs","Meta-Sedimentary/Meta-Volcanic Series (ridges)","Pre-Cambrian","W (Kwara/Oyo)",3.55,9.15),
 ("L15","Pelitic Schist / Muscovite Schist","Pelitic Schist/Muscovite Schist","MS","Meta-Sedimentary/Meta-Volcanic Series","Pre-Cambrian","W (Niger)",4.65,10.75),
 ("L83","Undifferentiated Schists, including Phyllites","Undifferentiated Schists, including Phyllities","Su","Meta-Sedimentary/Meta-Volcanic Series","Pre-Cambrian","W (Oyo/Osun)",3.75,7.55),
 ("L07","Meta-conglomerate","Meta-conglomerate","Mc","Meta-Sedimentary/Meta-Volcanic Series","Pre-Cambrian","W (Kwara/Ekiti)",4.95,8.15),
 ("L11","Mylonites","Mylonites","My","Cataclastic Rocks (shear zone)","Pre-Cambrian","Zungeru shear",5.05,9.15),
 ("L12","Mylonites Interlayered with Amphibolites","Mylonites Interlayed with Amphibolites","aMy","Cataclastic Rocks (Ifewara shear)","Pre-Cambrian","Ifewara shear",4.85,7.85),
 ("L78","Silicified, Sheared Rocks, Large Quartz Veins","Silicified, sheared rocks, large quartz veins","qs","Cataclastic Rocks (Kalangai-Zungeru-Ifewara)","Pre-Cambrian","Central shear",5.35,10.15),
 ("L41","Biotite-Garnet Gneiss Schist","Biotite Garnet Gneiss Schist","bS","Migmatite-Gneiss Complex","Pre-Cambrian","W (Oyo/Kwara)",3.45,8.85),
 ("L43","Biotite-Hornblende Gneiss","Biotite Homblende Gneiss [Homblende=Hornblende]","bG-h","Migmatite-Gneiss Complex","Pre-Cambrian","SW (Ondo/Ekiti)",4.95,7.35),
 # --- Central basement: migmatite-gneiss (I1-I7) + Older Granites (I8-I21) ---
 ("L08","Migmatite","Migmatite [Migmatite]","M","Migmatite-Gneiss Complex","Pre-Cambrian","Central (Kaduna)",7.15,10.95),
 ("L09","Migmatitic Gneiss","Migmatitic Gneiss","MG","Migmatite-Gneiss Complex","Pre-Cambrian","Central north (Katsina)",7.85,11.35),
 ("L10","Migmatitic Augen Gneiss","Migmatitic augen Gneiss","MaG","Migmatite-Gneiss Complex","Pre-Cambrian","Central NW (Zamfara)",6.75,11.15),
 ("L38","Banded Gneiss / Biotite Gneiss","Banded Gneiss/Biotite Gneiss","bG","Migmatite-Gneiss Complex","Pre-Cambrian","Central (Kaduna/Niger)",7.35,9.65),
 ("L66","Granite Gneiss","Granite Gneiss","GG","Migmatite-Gneiss Complex","Pre-Cambrian","Central NE (Kaduna)",8.15,10.75),
 ("L86","Porphyroblastic Gneiss","porphroblastic Gneiss [porphro=porphyro]","OPg","Migmatite-Gneiss Complex","Pre-Cambrian","Central (Kogi/Kwara)",6.85,8.15),
 ("L18","Quartz-Feldspathic Granulite and Gneiss","Quartz feldspathic granulite and gneiss","Ge","Migmatite-Gneiss Complex (granulite)","Pre-Cambrian","Central (Kogi/Benue)",7.95,8.05),
 ("L14","Pegmatite","Pegmatite","P","Pan-African Older Granite Series (veins/dykes)","Pre-Cambrian","Central (FCT/Kaduna)",7.05,9.35),
 ("L59","Dolerite","Dolerite","D","Pan-African Older Granite Series (dykes)","Pre-Cambrian","Central (Niger)",6.55,10.35),
 ("L69","Hypersthene Quartz-Diorite","Hypersthene quartz-diorite","ODh","Pan-African Older Granite Series","Pre-Cambrian","Central (FCT/Nasarawa)",7.65,9.15),
 ("L44","Biotite and Biotite-Hornblende Granodiorite","Biotite and biotite Hornblende granodiorite","OGd","Pan-African Older Granite Series","Pre-Cambrian","Central north (Kano)",8.35,11.15),
 ("L81","Syenite, mainly of Pyroxene Diorite Composition","Syenite, mainly of Pyroxenen Diorite composition","OGS","Pan-African Older Granite Series","Pre-Cambrian","Central north (Kano)",8.85,11.35),
 ("L56","Coarse Porphyritic Hornblende Granite","Coarse Porphyritic hornblende granite","OGH","Pan-African Older Granite Series","Pre-Cambrian","Central north (Katsina)",7.25,11.75),
 ("L57","Coarse Porphyritic Porphyroblastic Mica Granite","Coarse porphyritic porphyroblastic mica granite","OGm-var","Pan-African Older Granite Series","Pre-Cambrian","Central NW (Zamfara)",6.45,12.45),
 ("L58","Coarse Porphyritic Biotite and Biotite-Muscovite Granite","Coarse, Porphyritic biotite and biotite muscovite granite","OSq","Pan-African Older Granite Series","Pre-Cambrian","Central north (Jigawa)",8.15,12.05),
 ("L63","Fine-Grained Biotite Granite","Fine-grained biotite granite","OGf","Pan-African Older Granite Series","Pre-Cambrian","Central NE (Jigawa/Bauchi)",9.15,11.35),
 ("L05","Medium- to Coarse-Grained Biotite Granite","Medium-to coarse-Grained Biotite granite","OGm","Pan-African Older Granite Series","Pre-Cambrian","NE (Bauchi/Yobe)",9.95,11.85),
 ("L84","Undifferentiated Migmatite and Granite, Gneiss Porphyroblastic","Undifferentiated Migmatite and granite, Gneiss porphyroblastic","OGu","Pan-African Older Granite Series (undiff.)","Pre-Cambrian","East (Taraba/Adamawa, large)",11.15,8.75),
 ("L47","Charnockitic Rocks","Charnockitic Rocks","OGCh","Pan-African Older Granite Series (Oban Massif)","Pre-Cambrian","SE Oban Massif",8.45,5.55),
 ("L65","Gabbro and Quartz Gabbro and Meta Intrusives","Gabbro and quartz gabbro and meta Intrusives","OGr","Pan-African Older Granite Series (mafic)","Pre-Cambrian","East (Taraba)",11.65,8.45),
 ("L16","Porphyritic Granite / Coarse Porphyritic Biotite and Biotite-Hornblende Granite","Porphyritic Granite/Coarse porphyritic biotite and biotite hornblende granite","OGH/OSq","Pan-African Older Granite Series (batholith)","Pre-Cambrian","Central (Kaduna/Plateau)",8.65,10.35),
]

print(f"Legend count: {len(LEGENDS)}")
assert len(LEGENDS) == 86, f"Must be exactly 86, got {len(LEGENDS)}"
# distinct clean names?
names = [r[1] for r in LEGENDS]
assert len(set(names)) == 86, "clean names must be 86 distinct"
print("All 86 names distinct: OK")

# validate seeds inside
pts = np.array([[lon, lat] for *_, lon, lat in LEGENDS])
from shapely.geometry import Point as Pt
for rec in LEGENDS:
    lid, clean = rec[0], rec[1]
    lon, lat = rec[-2], rec[-1]
    if not (nigeria.contains(Pt(lon, lat)) or nigeria.touches(Pt(lon, lat))):
        raise ValueError(f"seed outside Nigeria: {lid} {clean} {lon},{lat}")
print("All 86 seeds inside Nigeria: OK")

# ------------------------------------------------ Voronoi partition
def voronoi_finite_polygons_2d(vor, radius=None):
    """Reconstruct finite Voronoi regions (SciPy recipe)."""
    if vor.points.shape[1] != 2:
        raise ValueError("Requires 2D input")
    new_regions = []
    new_vertices = vor.vertices.tolist()
    center = vor.points.mean(axis=0)
    if radius is None:
        radius = vor.points.ptp().max() * 2
    all_ridges = {}
    for (p1, p2), (v1, v2) in zip(vor.ridge_points, vor.ridge_vertices):
        all_ridges.setdefault(p1, []).append((p2, v1, v2))
        all_ridges.setdefault(p2, []).append((p1, v1, v2))
    for p1, region in enumerate(vor.point_region):
        vertices = vor.regions[region]
        if all(v >= 0 for v in vertices):
            new_regions.append(vertices)
            continue
        ridges = all_ridges[p1]
        new_region = [v for v in vertices if v >= 0]
        for p2, v1, v2 in ridges:
            if v2 < 0:
                v1, v2 = v2, v1
            if v1 >= 0:
                continue
            t = vor.points[p2] - vor.points[p1]
            t = t / np.linalg.norm(t)
            n = np.array([-t[1], t[0]])
            midpoint = (vor.points[p1] + vor.points[p2]) / 2.0
            direction = np.sign(np.dot(midpoint - center, n)) * n
            far_point = vor.vertices[v2] + direction * radius
            new_region.append(len(new_vertices))
            new_vertices.append(far_point.tolist())
        vs = np.asarray([new_vertices[v] for v in new_region])
        c = vs.mean(axis=0)
        angles = np.arctan2(vs[:, 1] - c[1], vs[:, 0] - c[0])
        new_region = [v for _, v in sorted(zip(angles, new_region))]
        new_regions.append(new_region)
    return new_regions, np.asarray(new_vertices)

vor = Voronoi(pts)
regions, vertices = voronoi_finite_polygons_2d(vor, radius=30)
print(f"Voronoi: {len(regions)} regions")

cells = []
for i, region in enumerate(regions):
    poly = Polygon(vertices[region])
    # clip to Nigeria
    clipped = poly.intersection(nigeria)
    if clipped.is_empty:
        raise ValueError(f"empty clipped cell {i}")
    cells.append(clipped)

# union check pre-warp
u_pre = unary_union(cells)
print(f"Pre-warp union area={u_pre.area:.4f} vs Nigeria {nigeria.area:.4f}, diff={abs(u_pre.area-nigeria.area):.6f}")
assert abs(u_pre.area - nigeria.area) < 1e-6, "pre-warp must tile exactly"

# ---- organic warp field (smooth, topology-preserving, zero at boundary)
# Use EXACT distance to Nigeria boundary (not vertex approx) so boundary stays fixed.
from shapely.geometry import Point as ShPoint
import shapely
NIG_BOUNDARY = nigeria.boundary
TAPER = 0.22  # deg over which warp fades to 0 at border

def smoothstep(t):
    t = np.clip(t, 0.0, 1.0)
    return t * t * (3 - 2 * t)

# fixed random phases (seeded for reproducibility)
rng = np.random.RandomState(20261008)
# multi-scale sines: (amp_lon, amp_lat, freq_lon, freq_lat, phase)
WAVES = [
    (0.140, 0.128, 0.55, 0.75, rng.uniform(0, 6.28, 4)),
    (0.088, 0.082, 1.15, 0.95, rng.uniform(0, 6.28, 4)),
    (0.050, 0.044, 2.10, 2.45, rng.uniform(0, 6.28, 4)),
    (0.027, 0.023, 3.60, 3.15, rng.uniform(0, 6.28, 4)),
]

def warp_xy_exact(lon_list, lat_list):
    lon = np.asarray(lon_list, dtype=float); lat = np.asarray(lat_list, dtype=float)
    dx = np.zeros_like(lon); dy = np.zeros_like(lon)
    for ax, ay, fx, fy, ph in WAVES:
        dx += ax * np.sin(2*np.pi*(lon*fx*0.5 + lat*fy*0.5) + ph[0]) * np.cos(2*np.pi*(lon*0.23 + lat*0.31) + ph[1])
        dy += ay * np.cos(2*np.pi*(lon*fx*0.5 - lat*fy*0.5) + ph[2]) * np.sin(2*np.pi*(lon*0.29 - lat*0.21) + ph[3])
    # exact distance to country boundary (vectorized via shapely)
    pts = shapely.points(lon, lat)
    d = shapely.distance(pts, NIG_BOUNDARY)
    m = smoothstep(d / TAPER)
    # hard-pin anything essentially on the boundary
    m = np.where(d < 1e-9, 0.0, m)
    return lon + dx*m, lat + dy*m

def densify_coords(coords, step=0.045):
    """Subdivide each segment into N equal parts (direction-independent set)."""
    coords = list(coords)
    out = []
    for i in range(len(coords)-1):
        x0, y0 = coords[i]; x1, y1 = coords[i+1]
        seglen = math.hypot(x1-x0, y1-y0)
        n = max(1, int(math.ceil(seglen / step)))
        for k in range(n):
            t = k / n
            out.append((x0*(1-t)+x1*t, y0*(1-t)+y1*t))
    out.append(coords[-1])
    return out

def warp_geom(geom):
    if geom.is_empty:
        return geom
    if geom.geom_type == "Polygon":
        ext = densify_coords(list(geom.exterior.coords))
        xa, ya = warp_xy_exact([p[0] for p in ext], [p[1] for p in ext])
        # snap to 1e-9 to force shared-edge coincidence
        ext2 = [(round(float(x), 9), round(float(y), 9)) for x, y in zip(xa, ya)]
        holes = []
        for ring in geom.interiors:
            hc = densify_coords(list(ring.coords))
            xh, yh = warp_xy_exact([p[0] for p in hc], [p[1] for p in hc])
            holes.append([(round(float(x),9), round(float(y),9)) for x, y in zip(xh, yh)])
        p = Polygon(ext2, holes)
        if not p.is_valid:
            p = p.buffer(0)
        return p
    elif geom.geom_type == "MultiPolygon":
        parts = [warp_geom(g) for g in geom.geoms]
        u = unary_union(parts)
        if not u.is_valid:
            u = u.buffer(0)
        return u
    else:
        return geom

warped = []
for i, c in enumerate(cells):
    w = warp_geom(c)
    if w.is_empty:
        raise ValueError(f"warped empty {i}")
    warped.append(w)
    if i % 20 == 0:
        print(f"warped {i+1}/86")

# ---- QA: validity, gaps, overlaps
import warnings
n_invalid = sum(0 if g.is_valid else 1 for g in warped)
print(f"Invalid after warp (pre-fix): {n_invalid}")
# fix any invalid
fixed = []
for g in warped:
    if not g.is_valid:
        g = g.buffer(0)
    fixed.append(g)
warped = fixed
print(f"Invalid after fix: {sum(0 if g.is_valid else 1 for g in warped)}")

u_post = unary_union(warped)
gap = nigeria.difference(u_post)
overlap_extra = u_post.difference(nigeria)
print(f"Post-warp union area={u_post.area:.5f} Nigeria={nigeria.area:.5f}")
print(f"Gap area (Nigeria minus union)={gap.area:.7f} ({100*gap.area/nigeria.area:.4f}%)")
print(f"Overshoot area (union minus Nigeria)={overlap_extra.area:.7f}")
# pairwise overlap check (sample): total cell area vs union area
tot = sum(g.area for g in warped)
print(f"Sum cell areas={tot:.5f}, union={u_post.area:.5f}, overlap={tot-u_post.area:.7f}")

# If tiny slivers due to float, snap union back to Nigeria for final? We keep warped as-is
# but clip each cell to Nigeria to kill overshoot slivers (keeps no-gap since overshoot tiny)
clipped_final = []
for g in warped:
    gc = g.intersection(nigeria)
    if gc.is_empty:
        raise ValueError("empty after final clip")
    if not gc.is_valid:
        gc = gc.buffer(0)
    clipped_final.append(gc)
u_final = unary_union(clipped_final)
gap2 = nigeria.difference(u_final)
print(f"Final gap area={gap2.area:.8f} ({100*gap2.area/nigeria.area:.5f}%)")
print(f"Final union area={u_final.area:.5f}")

# ------------------------------------------------ build GeoDataFrame
import pandas as pd
import colorsys
def distinct_hex(n):
    # golden-angle HSV palette, vivid but map-like
    out = []
    for i in range(n):
        h = (i * 0.61803398875) % 1.0
        # vary saturation/value by group for readability
        s = 0.55 + 0.30 * ((i * 7) % 3) / 2.0
        v = 0.88 + 0.10 * ((i * 13) % 2)
        r, g, b = colorsys.hsv_to_rgb(h, min(s,0.95), min(v,0.98))
        out.append('#%02X%02X%02X' % (int(r*255), int(g*255), int(b*255)))
    return out
PALETTE = distinct_hex(len(LEGENDS))
rows = []
for idx, (rec, geom) in enumerate(zip(LEGENDS, clipped_final)):
    lid, clean, orig, code, formation, age, province, lon, lat = rec
    # normalize to (Multi)Polygon
    if geom.geom_type not in ("Polygon", "MultiPolygon"):
        # e.g., GeometryCollection from intersection slivers -> extract polygons
        polys = [g for g in getattr(geom, "geoms", [geom]) if g.geom_type in ("Polygon","MultiPolygon")]
        if not polys:
            raise ValueError(f"no polygon for {lid}")
        geom = unary_union(polys)
    rows.append({
        "legend_id": lid,
        "name": clean,
        "legend_original": orig,
        "ngsa_code": code,
        "formation": formation,
        "age": age,
        "province": province,
        "seed_lon": lon,
        "seed_lat": lat,
        "fill_hex": PALETTE[idx],
        "geometry": geom,
    })
gdf = gpd.GeoDataFrame(rows, crs="EPSG:4326")
# order by legend_id
gdf = gdf.sort_values("legend_id").reset_index(drop=True)
print(gdf.head(3).to_string())
print(f"Features: {len(gdf)}, distinct names: {gdf['name'].nunique()}")

# ------------------------------------------------ save
gdf.to_file(OUT_GPKG, layer="nigeria_geology", driver="GPKG")
print(f"Wrote {OUT_GPKG}")
gdf.to_file(OUT_GEOJSON, driver="GeoJSON")
print(f"Wrote {OUT_GEOJSON}")
# CSV of legend count
gdf.drop(columns=["geometry"]).to_csv(OUT_CSV, index=False)
print(f"Wrote {OUT_CSV}")

# ------------------------------------------------ preview map
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
fig, ax = plt.subplots(figsize=(11, 12))
# use our distinct fill_hex colors directly
gdf.plot(ax=ax, color=gdf["fill_hex"].tolist(), edgecolor="white", linewidth=0.4, legend=False, aspect="equal")
# basemap outline
gpd.GeoSeries([nigeria], crs="EPSG:4326").boundary.plot(ax=ax, color="black", linewidth=1.1)
ax.set_title("Nigeria Geology — 86 legend polygons (smooth, gap-free)\nSources: NGSA Geological Map of Nigeria + Geology of Nigeria Fig. A", fontsize=11, pad=12)
ax.set_xlabel("Longitude (°E)"); ax.set_ylabel("Latitude (°N)")
ax.set_xlim(2.2, 15.2); ax.set_ylim(3.8, 14.3)
ax.grid(True, alpha=0.25, linestyle="--")
# annotate large/index units
for _, r in gdf.iterrows():
    c = r.geometry.centroid
    if r["legend_id"] in ("L25","L22","L28","L61","L34","L84","L33","L36","L03","L01"):
        ax.text(c.x, c.y, r["legend_id"], fontsize=7, ha="center", va="center",
                bbox=dict(boxstyle="round,pad=0.2", fc="white", ec="none", alpha=0.8))
fig.tight_layout()
fig.savefig(OUT_PNG, dpi=180)
print(f"Wrote {OUT_PNG}")
# second preview: zoomed insets to show smooth (non-boxy) boundaries
fig2, axes = plt.subplots(1, 3, figsize=(15, 5.5))
for ax2, (xmin,xmax,ymin,ymax,title) in zip(axes, [
    (3.0,6.5,6.5,9.5,"West — schist belts / shear zones"),
    (8.0,10.5,8.0,10.8,"Central — Jos Younger Granites"),
    (6.5,9.0,5.0,7.5,"South-East — Anambra Basin"),
]):
    gdf.plot(ax=ax2, color=gdf["fill_hex"].tolist(), edgecolor="white", linewidth=0.6, aspect="equal")
    gpd.GeoSeries([nigeria], crs="EPSG:4326").boundary.plot(ax=ax2, color="black", linewidth=1.0)
    ax2.set_xlim(xmin,xmax); ax2.set_ylim(ymin,ymax)
    ax2.set_title(title, fontsize=10)
    ax2.set_xlabel("Lon (°E)"); ax2.set_ylabel("Lat (°N)")
    ax2.grid(True, alpha=0.25, linestyle="--")
fig2.suptitle("Detail insets — smooth organic contacts, no boxy edges, no gaps", fontsize=11)
fig2.tight_layout()
fig2.savefig("/home/user/new/nigeria_geology_detail_insets.png", dpi=180)
print("Wrote /home/user/new/nigeria_geology_detail_insets.png")
print("DONE")
