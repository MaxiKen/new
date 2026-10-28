NIGERIA - GEOLOGY + MINERALS LAYERS

Read PLAIN_ANSWER.md first. Summary of what is here and how far to trust it.

Geology_Georeferenced.tif
  The complete 2011 NGSA geological sheet, 2 px per PDF point, registered on its own printed
  graticule. NO correction was applied, because none is justified: three independent feature
  classes on the sheet (state boundaries, rivers, coastline) all sit within 1-3 km of modern
  reference data, and the best-controlled two agree with each other at +0.2 km east and
  +0.9 km north - less than 1.5 map pixels. Applying that would be fitting noise.
  Residual accuracy: 1-2 km. Datum not stated on the sheet.

Combined_Map_v2.png
  The geology sheet in full, unmodified colour, with the 1,323 re-registered mineral symbols
  drawn on top as vector markers coloured by commodity class. Replaces the earlier 62/38
  colour blend, which destroyed the geology colours and both legends.

Minerals_Symbol_Points_CORRECTED.csv / .geojson
  1,323 printed mineral symbols, each at the centre of its printed glyph, with commodity name,
  class and confidence tier. The original extraction computed their coordinates on the 2023
  sheet's PRINTED graticule, which is 0.172 degrees (about 19 km) west of the frame the sheet
  was actually drawn in. They are corrected here (+18.5 to +19.1 km east). Proof: the sheet's
  own vector international border matches modern data to 0.5-1.1 km in the embedded frame but
  is 12.9 km out in the printed frame. Old coordinates are kept in lon_printed/lat_printed and
  lon_was/lat_was.

Geology_Alignment_Test.png / .json
  The evidence that the geology sheet needs no shift: per-feature-class best-fit translations
  with bootstrap error bars.

WHAT IS NOT KNOWN
  * No datum is established for either sheet. EPSG:4326 is written into the TIFF only so GIS
    software will display it on a basemap. It is not a verified statement about the source.
    Nigeria's own datum (Minna) would move the country about 90 m, well below what these
    sheets can resolve.
  * Commodity names are about 81% correct per point (leave-one-out). Per-mineral totals are
    NOT reliable; use the tier and confidence columns for each point.
  * Neither sheet's legend is digitised; read the original PDFs for geology units and symbols.

NOT SUITABLE FOR
  Exploration decisions, licensing, legal boundaries, navigation, or site-scale work.
  These are 1:2,000,000 regional maps with 1-2 km accuracy.
