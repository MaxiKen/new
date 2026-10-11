#!/usr/bin/env python3
"""Create the block-grid overlay image + georeference world file."""
import numpy as np
from PIL import Image, ImageDraw, ImageFont

PARCH = 328.4
MERX = [288 + i * PARCH for i in range(13)]   # 3E..15E
PARY = [3343 - i * PARCH for i in range(11)]  # 4N..14N

im = Image.open('NGSA_map_geology_legend_isolated_v2.png').convert('RGB')
d = ImageDraw.Draw(im)
try:
    font = ImageFont.truetype('/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf', 30)
    font_s = ImageFont.truetype('/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf', 22)
except Exception:
    font = font_s = ImageFont.load_default()

RED = (255, 0, 0)
# block boundaries = graticule lines; draw on the map panel only
for i, mx in enumerate(MERX[:12]):
    x = int(round(mx))
    d.line([(x, 92), (x, 3342)], fill=RED, width=1)
for j, my in enumerate(PARY):
    y = int(round(my))
    d.line([(69, y), (4152, y)], fill=RED, width=1)
# neatline emphasis
d.rectangle([69, 92, 4152, 3342], outline=RED, width=2)
# column letters (top margin, y 30) and row numbers (left margin x 30)
for ci in range(12):
    cx = int(round((MERX[ci] + MERX[ci + 1]) / 2))
    d.text((cx - 8, 30), chr(65 + ci), fill=RED, font=font)
for ri in range(10):
    ry = int(round((PARY[10 - ri] + PARY[9 - ri]) / 2))
    d.text((28, ry - 14), str(ri + 1), fill=RED, font=font)
# corner labels of graticule values
for i, mx in enumerate(MERX[:12]):
    x = int(round(mx))
    d.text((x - 24, 3348), '%dE' % (3 + i), fill=RED, font=font_s)
for j, my in enumerate(PARY):
    y = int(round(my))
    d.text((60, y - 10), '%dN' % (13 - j), fill=RED, font=font_s)
im.save('NGSA_map_geology_legend_isolated_v2_grid.png')
print('grid overlay saved')

# world file (EPSG:4326, upper-left of the v2 image)
# lon = 3 + (x - 288)/PARCH ; lat = 4 + (3343 - y)/PARCH
A = 1.0 / PARCH          # deg per pixel x
E = -1.0 / PARCH         # deg per pixel y
C = 3 + (0.5 - 288) / PARCH    # lon at x=0.5 (center of first pixel)
F = 4 + (3343 - 0.5) / PARCH   # lat at y=0.5
with open('NGSA_map_geology_legend_isolated_v2.pgw', 'w') as f:
    f.write('%.10f\n0.0000000000\n0.0000000000\n%.10f\n%.10f\n%.10f\n' % (A, E, C, F))
print('world file saved: A=%.8f C=%.6f F=%.6f' % (A, C, F))
