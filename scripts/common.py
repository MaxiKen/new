"""Shared georeferencing constants/fits for NGSA Geology + Mineral maps."""
import numpy as np

# ---- MINERAL PDF (vector graticule, exact) ----
# Graticule line positions in PDF points (from vector drawings)
MIN_LON_X = np.array([341.4, 656.6, 971.8, 1287.0, 1602.2, 1917.4])  # -> 4,6,8,10,12,14 E
MIN_LON_V = np.array([4., 6., 8., 10., 12., 14.])
MIN_LAT_Y = np.array([523.5, 838.7, 1153.9, 1469.1, 1784.3])          # -> 13,11,9,7,5 N
MIN_LAT_V = np.array([13., 11., 9., 7., 5.])
MIN_FRAME = (74.2397, 358.7239, 2051.8313, 1968.6611)  # x0,y0,x1,y1 PDF pt

def _fit(x, v):
    A = np.vstack([x, np.ones_like(x)]).T
    coef, *_ = np.linalg.lstsq(A, v, rcond=None)
    pred = coef[0]*x + coef[1]
    resid = v - pred
    return coef, resid

MIN_LON_COEF, MIN_LON_RES = _fit(MIN_LON_X, MIN_LON_V)  # lon = a*x+b
MIN_LAT_COEF, MIN_LAT_RES = _fit(MIN_LAT_Y, MIN_LAT_V)  # lat = a*y+b (a<0)

def mineral_pdf_to_lonlat(x, y):
    lon = MIN_LON_COEF[0]*np.asarray(x, dtype=float) + MIN_LON_COEF[1]
    lat = MIN_LAT_COEF[0]*np.asarray(y, dtype=float) + MIN_LAT_COEF[1]
    return lon, lat

def mineral_lonlat_to_pdf(lon, lat):
    x = (np.asarray(lon, dtype=float) - MIN_LON_COEF[1]) / MIN_LON_COEF[0]
    y = (np.asarray(lat, dtype=float) - MIN_LAT_COEF[1]) / MIN_LAT_COEF[0]
    return x, y

# Native raster canvas (stitched strips): 2060 x 1677, px/pt = 2060/1977.5917
MIN_NATIVE_PXPT = 2060.0 / (2051.8313 - 74.2397)
MIN_NATIVE_W, MIN_NATIVE_H = 2060, 1677
def mineral_native_to_pdf(col, row):
    x = MIN_FRAME[0] + (np.asarray(col, dtype=float) + 0.5) / MIN_NATIVE_PXPT
    y = MIN_FRAME[1] + (np.asarray(row, dtype=float) + 0.5) / MIN_NATIVE_PXPT
    return x, y
def mineral_native_to_lonlat(col, row):
    x, y = mineral_native_to_pdf(col, row)
    return mineral_pdf_to_lonlat(x, y)

# Salmon zone dividers (PDF pt)
ZONE_V1, ZONE_V2 = 777.3, 1411.5
ZONE_H_A, ZONE_H_E, ZONE_H_F = 826.4, 996.0, 1306.9
def mineral_zone_of(x, y):
    if x < ZONE_V1:
        return "A" if y < ZONE_H_A else ("D" if y < ZONE_H_F else "F")
    if y < ZONE_H_E:
        return "B" if x < ZONE_V2 else "C"
    return "E" if y < ZONE_H_F else "G"

# ---- GEOLOGY JPG (grid peaks, refined in 01_georef.py; defaults from peak detection) ----
GEO_LON_X = np.array([408, 737, 1065, 1394, 1722, 2050, 2378, 2707, 3036, 3364, 3692, 4020], dtype=float)
GEO_LON_V = np.arange(3., 15.)
GEO_LAT_Y = np.array([485, 813, 1141, 1470, 1798, 2126, 2454, 2783, 3111, 3440], dtype=float)
GEO_LAT_V = np.arange(13., 3., -1.)
GEO_LON_COEF, GEO_LON_RES = _fit(GEO_LON_X, GEO_LON_V)
GEO_LAT_COEF, GEO_LAT_RES = _fit(GEO_LAT_Y, GEO_LAT_V)
def geology_px_to_lonlat(col, row):
    """col,row = pixel indices (centres at col,row). Uses separable fit on line-centre coords."""
    lon = GEO_LON_COEF[0]*np.asarray(col, dtype=float) + GEO_LON_COEF[1]
    lat = GEO_LAT_COEF[0]*np.asarray(row, dtype=float) + GEO_LAT_COEF[1]
    return lon, lat

if __name__ == "__main__":
    print("Mineral lon coef", MIN_LON_COEF, "resid deg", MIN_LON_RES, "max|res| pt-equiv", np.abs(MIN_LON_RES).max()/MIN_LON_COEF[0])
    print("Mineral lat coef", MIN_LAT_COEF, "resid deg", MIN_LAT_RES, "max|res| pt-equiv", np.abs(MIN_LAT_RES).max()/abs(MIN_LAT_COEF[0]))
    print("Mineral frame lonlat corners:", mineral_pdf_to_lonlat(MIN_FRAME[0], MIN_FRAME[1]), mineral_pdf_to_lonlat(MIN_FRAME[2], MIN_FRAME[3]))
    print("Geology lon coef", GEO_LON_COEF, "resid px", GEO_LON_RES/GEO_LON_COEF[0])
    print("Geology lat coef", GEO_LAT_COEF, "resid px", GEO_LAT_RES/GEO_LAT_COEF[0])

# ---- Mineral absolute (WGS84) correction (see 03e-03g; border Chamfer optimum) ----
MIN_CORR_DX, MIN_CORR_DY = 0.162, -0.002  # degrees, added to as-printed-graticule lon/lat
def mineral_pdf_to_lonlat_corr(x, y):
    lon, lat = mineral_pdf_to_lonlat(x, y)
    return lon + MIN_CORR_DX, lat + MIN_CORR_DY
def mineral_native_to_lonlat_corr(col, row):
    lon, lat = mineral_native_to_lonlat(col, row)
    return lon + MIN_CORR_DX, lat + MIN_CORR_DY
