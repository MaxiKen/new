"""Final transforms (verified 2026-10-19). All axis-aligned, EPSG:4326.
Geology: printed-graticule affine from previous extraction, VERIFIED against Nigeria boundary (median 1.24 km, no systematic shift).
  Page coords = PDF points, PyMuPDF top-left origin. Previous json used bottom-origin page_y: lat = 0.00634488747510426*yb + 3.2845481786541253, yb=1764-yt.
  => lat = -0.00634488747510426*yt + 14.476866...
Mineral: publisher /VP extent transform (= graticule-line affine +0.1723 deg longitude). Printed longitude graticule is displaced; do NOT use it.
  Frame (neatline) page rect x 74.23969..2051.1915, ytop 358.72388..1967.70117 maps to lon 2.47619..15.02138, lat 14.04668..3.83671.
"""
# Geology page (3168 x 1764 pt), native image 6600x3675 px covering full page.
GEO_LON0 = 1.7544578039042098          # lon at page_x=0
GEO_DLDX = 0.006344690965581331        # deg per pt
GEO_LAT_TOP = 0.00634488747510426*1764 + 3.2845481786541253  # lat at yt=0
GEO_DLADY = -0.00634488747510426       # deg per pt (yt down)
def geo_page_to_lonlat(x_pt, ytop_pt):
    return (GEO_LON0 + GEO_DLDX*x_pt, GEO_LAT_TOP + GEO_DLADY*ytop_pt)
# Mineral page (3960 x 2160 pt)
MIN_FRAME = (74.23969, 358.72388, 2051.1915, 1967.70117)  # x0,ytop0,x1,ytop1
MIN_LON = (2.47619, 15.02138); MIN_LAT = (14.04668, 3.83671)  # at ytop0, ytop1
MIN_DLDX = (MIN_LON[1]-MIN_LON[0])/(MIN_FRAME[2]-MIN_FRAME[0])
MIN_DLADY = (MIN_LAT[1]-MIN_LAT[0])/(MIN_FRAME[3]-MIN_FRAME[1])
MIN_LON0 = MIN_LON[0] - MIN_DLDX*MIN_FRAME[0]
MIN_LAT0 = MIN_LAT[0] - MIN_DLADY*MIN_FRAME[1]
def min_page_to_lonlat(x_pt, ytop_pt):
    return (MIN_LON0 + MIN_DLDX*x_pt, MIN_LAT0 + MIN_DLADY*ytop_pt)
def min_lonlat_to_page(lon, lat):
    return ((lon-MIN_LON0)/MIN_DLDX, (lat-MIN_LAT0)/MIN_DLADY)
def min_basepx_to_lonlat(px, py):
    """Base raster 2060x1677 px covering x 74.23969..2051.83130 pt, ytop 358.72388..1968.66113 pt. Pixel-centre aware: px is continuous pixel coordinate with pixel (0,0) centre at (0,0)? 
    Existing mineral px_x/px_y are in image pixel index coords (bbox centres like 784.0). Treat px as index coordinate where edge of image = -0.5. Page x = x0 + (px+0.5)*(Wpt/Wpx)."""
    x_pt = 74.23969 + (px+0.5)*(1977.59161/2060.0)
    y_pt = 358.72388 + (py+0.5)*(1609.93725/1677.0)
    return min_page_to_lonlat(x_pt, y_pt)
def min_lonlat_to_basepx(lon, lat):
    x_pt, y_pt = min_lonlat_to_page(lon, lat)
    return ((x_pt-74.23969)/(1977.59161/2060.0)-0.5, (y_pt-358.72388)/(1609.93725/1677.0)-0.5)
# Old boundary-fit (for remapping old BF vectors to VP): old lonlat -> base px via inverse BF, then VP.
def bf_page_to_lonlat(x_pt, ytop_pt):
    yb = 2160 - ytop_pt
    return (8.999624062683695 + 6.3408036208710055*(x_pt-1104.0922160059586)/1000.0,
            10.488502044741583 + 6.350936179071387*(yb-1241.0996111966826)/1000.0)
def bf_lonlat_to_vp_lonlat(lon, lat):
    x_pt = 1104.0922160059586 + (lon-8.999624062683695)*1000.0/6.3408036208710055
    yb = 1241.0996111966826 + (lat-10.488502044741583)*1000.0/6.350936179071387
    return min_page_to_lonlat(x_pt, 2160-yb)
if __name__ == "__main__":
    print("GEO lat top", GEO_LAT_TOP)
    print("GEO corners TL", geo_page_to_lonlat(0,0), "BR", geo_page_to_lonlat(3168,1764))
    print("MIN dldx", MIN_DLDX, "pt/deg", 1/MIN_DLDX, "dlady", MIN_DLADY, 1/abs(MIN_DLADY))
    print("MIN frame TL", min_page_to_lonlat(*MIN_FRAME[:2]), "BR", min_page_to_lonlat(MIN_FRAME[2],MIN_FRAME[3]))
    print("MIN page corners TL", min_page_to_lonlat(0,0), "BR", min_page_to_lonlat(3960,2160))
    print("base px (0,0)", min_basepx_to_lonlat(0,0), "(2059,1676)", min_basepx_to_lonlat(2059,1676))
    # roundtrip
    print("roundtrip", min_lonlat_to_basepx(*min_basepx_to_lonlat(1000.3, 800.7)))
