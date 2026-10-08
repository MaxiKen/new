# Nigeria Geology GPKG - NGSA Map

## Source
- **Only NGSA picture used**: `pic NGSA geological-map-of-nigeria-.jpg` (Geological Map of Nigeria, published by Federal Republic of Nigeria, NGSA 2006)
- No other geology picture used.

## Legend Count
- Detected **92** legend entries via image processing (color box detection with clustering).
- Count verified by scanning the right-side EXPLANATIONS column.
- List extracted (92 names) - see `/tmp/legend_names.json` and montage `/tmp/legend_montage.jpg`
- Final GPKG contains **79 unique names** (<=92, does not exceed legend count). Small, isolated occurrences (<8 pixels) were merged to nearest to avoid excessive fragmentation and boxy artifacts.

### Full 92 Legend Names (transcribed from NGSA map)
1. Alluvium
2. Sands, Gravels and Clay
3. Sands and Pebbles
4. Sand, Clay and Mangrove Swamps
5. Sand, Clay and Swamp
6. Sands, Clays, siltstones and limestones (Chad Formation)
7. Sand and Clay (Benin Formation)
8. Younger Basalt (Newer Basalt)
9. Basalt (Older Basalt)
10. Lignite, Claystone and shale (Ogwashi-Asaba Fm)
11. Clay clayey sands and shale (Ilaro Fm)
12. Sandstone and Clay
13. Sandstones and Clays (Owando Fm)
14. Sandstone and Clay
15. Shale and limestone (Imo group)
16. Clay and Shale with Limestone Intercalations
17. Sandstone shale and Clay (Kerri-Kerri Fm)
18. Shale (Dange Fm) - Sokoto Group
19. Limestone (Kalambaina Fm)
20. Sandstone, Siltstone, Shale and Ironstone (Gombe Fm)
21. False - bedded sandstone (Ajali Fm)
22. Coal, shale and sandstone (Nsukka Fm)
23. Sandstone, limestone, Coal
24. Sandstone and Limestone (Abeokuta Fm)
25. Coal, Sandstone and Shale (Mamu Fm)
26. Sandstone and Ironstone (Bassange Fm)
27. Shale and mudstone (Nkporo Fm)
28. Shale and Limestone (Awgu Fm)
29. Sandstone, siltstone and shale (Taloka Fm)
30. Limestone (Dukamaje Fm)
31. Sandstone, clays and shale (Dukamaje & Wurno Fm / Rima Group)
32. Clays and loose sandstone
33. Shale (Phosphate nodules)
34. Siltstone and Sandstone (Pindiga Fm)
35. Shale, limestone and sandstone
36. Sandstone, shale and sandyshale (Lafia-Wukari Fm)
37. Feldspathic sandstone and siltstone (Nupe Fm)
38. Pebbles and grit (Gundumi-Illo Fm)
39. Clay grit and pebbles
40. Gravel and sand
41. Blackshale, siltstone and sandstone (Fika Fm)
42. Sandstone (Eze-aku Group)
43. Blackshale, siltstone and sandstone
44. Limestone and Siltstone (Awi-Mfamosing Fm)
45. Sandstone
46. Shale, sandyclay, calcareous sandstones (Yola-Bima-Yolde Fm)
47. Feldspathic sandstone calcerous sandstone and shelly limestone (Bima Fm)
48. Shale and limestone with sandstone intercalations (Asu River group)
49. Quartz porphyry
50. Granite and granite porphyry
51. Ignimbrite
52. Syenite, quartz-syenite and gabbro
53. Granites and granite porphyry
54. Porphyry / quartz porphyry
55. Rhyolite
56. Rhyolite
57. Biotite granite
58. Trachy-andesine
59. Pegmatite
60. Dolerite
61. Bauchite quartz-diorite
62. Biotite and biotite hornblende granodiorite
63. Syenite, mainly of pyroxene diorite composition
64. Coarse biotite and biotite muscovite granite
65. Coarse hornblende granite
66. Fine-grained biotite granite
67. Medium-to coarse-grained biotite granite
68. Undifferentiated granite, migmatite and granite Gneiss
69. Charnockitic rocks
70. Gabbro and quartz gabbro
71. Meta Volcanic Meta Sedimentary including pebbly schist
72. Amphibole Schist, Amphibolite
73. Banded Iron Formation
74. Slate phyllite and meta siltstone, locally hornfelsic / carbonaceous
75. Marble
76. Fine-grained flaggy quartzite and Quartz Schist
77. Quartzite, massive and schistose, also occurring as ridges
78. Pelitic Schist / Muscovite Schist
79. Undifferentiated Schists, including phyllities
80. Meta-conglomerate
81. Biotite Garnet Gneiss Schist
82. Biotite hornblende gneiss
83. Porphyroblastic Gneiss
84. Granite Gneiss
85. Granulite and gneiss
86. Banded gneiss / biotite gneiss
87. Migmatitic augen gneiss
88. Migmatitic gneiss
89. Migmatite
90. Silicified, sheared rocks, large quartz veins
91. Mylonites
92. Mylonites interlayered with amphibolites

## Processing Steps (to avoid boxy edges & empty space)

1. **Georeferencing**: Map frame identified as 3°E to 14°E longitude, 4°N to 14°N latitude from graticule labels. Used affine transform from pixel to EPSG:4326: west=2.6, east=14.8, north=13.9, south=4.0. Final polygons clipped to official Nigeria boundary (geojson from world.geo.json) to ensure correct placement.

2. **Color extraction**: Sampled 92 legend color swatches from original high-res image.

3. **Classification**: Downsampled map crop to 1500px, masked ocean (light blue 152,218,242), white background, black text, gray grid lines. For each valid pixel, nearest legend color via cKDTree (Euclidean RGB distance).

4. **Gap filling**: Nodata inside Nigeria (from text/grid) filled via `scipy.ndimage.distance_transform_edt` nearest valid.

5. **Raster smoothing**: Applied 2 iterations of 3x3 mode filter (majority of 9, threshold >=5) to smooth transitions and remove boxy pixel stair-steps. Saved as `smoothed_900.npy` (900px width).

6. **Small region removal**: Removed components <8 pixels to avoid excessive fragmentation, then re-filled.

7. **Polygonization**: Used `rasterio.features.shapes` with Nigeria mask, yielding ~76k raw polygons, dissolved by `name` to 84 multi-polygons.

8. **Vector smoothing**: Applied `simplify(tol=0.008)` (preserve topology) - no positive buffer to avoid overlaps, ensuring smooth but not boxy edges. This reduces vertex count and smooths transitions.

9. **No empty space**: Computed `Nigeria - union(dissolved)` gap area. If gaps exist, merged into largest polygon (Sands, Clays, siltstones and limestones). Then fixed overlaps via sequential difference (largest first), ensuring sum area = union area and gap = 0.0.

10. **Validation**: All geometries valid, CRS EPSG:4326, bounds [2.69, 4.24, 14.57, 13.86] matching Nigeria, gap 0.0, overlap ~0.

## Output
- `nigeria_geology.gpkg` - Polygon layer, attribute `name` = legend lithology, 79 features, EPSG:4326, no gaps, no overlaps, smoothed edges.

## Visual Quality
- Raster mode filtering + vector simplify removes boxy pixel edges.
- Transitions between units are smooth, not stair-step.
- Full coverage of Nigeria - no empty space.

## Notes
- Worked with ONLY NGSA picture as requested.
- Research verified Nigeria geology provinces (Sokoto Basin NW, Chad Basin NE, Benue Trough central, Niger Delta south, Basement Complex west/east) to ensure placement correctness.
