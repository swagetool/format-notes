# format-notes

Traps in geodata formats that we ran into, each one reproduced on a small synthetic file. Every note gives the numbers, a short script that shows the effect, the output of that script as it was printed, and what to do about it.

Written by the Swage team (https://tryswage.com). We convert between GIS and CAD formats and these are the places where data changed without anyone being told.

## What was checked, and on what

Every script was run for these notes on GDAL 3.10.3 (Python bindings), PROJ 9.6.0, Python 3.13.5, in a Debian-based container. No note uses libredwg or any other converter, so no other version is listed. A different GDAL may behave differently. If you see that, please tell us (below).

## How to run a snippet

Each snippet is a complete file. Save it and run `python3 -W ignore snippet.py` where the `osgeo` Python package is installed. The `-W ignore` only hides a Python deprecation notice. Everything else GDAL prints is shown in the note. The snippets write their files into a fresh temporary directory.

## Notes

The strongest come first. Strong here means that the loss is silent or that it looks like something else.

1. [Reprojecting from a feet-based 2D CRS leaves Z in feet](general/z-not-converted-by-reprojection.md)
2. [GDAL reads at most 256 characters of a DXF TEXT, and only the last piece of a split one](dxf/text-longer-than-256-characters.md)
3. [A DXF that declares ANSI_1250 but is written in UTF-8 reads as mojibake](dxf/wrong-declared-codepage.md)
4. [A GML file with one 3D layer cannot be read for its flat layers](gml/flat-layer-next-to-3d-layer.md)
5. [KML loses fields in two situations](kml/fields-lost.md)
6. [The plain KML driver takes features only into the layer created last](kml/layers-created-up-front.md)
7. [Shapefile written without an encoding stores non-Latin text as question marks](shapefile/no-cpg-question-marks.md)
8. [Empty string and NULL are different values, and most formats do not keep both](general/empty-string-and-null.md)
9. [Control characters and U+FFFE in text values are changed or break the file](general/special-characters.md)
10. [GeoPackage silently loses a field named fid or geom](gpkg/fid-and-geom-field-names.md)
11. [MapInfo TAB has no height, and drops Z without a word](mapinfo/no-height.md)
12. [MapInfo TAB moves coordinates by up to about a centimetre](mapinfo/centimetre-grid.md)
13. [MapInfo TAB drops the time zone of a DateTime and keeps the clock time](mapinfo/datetime-zone.md)
14. [The GDAL DXF writer writes UTF-8 text under an ANSI_1252 header](dxf/gdal-writer-header-codepage.md)
15. [GDAL loses the last character of DXF text under ANSI_1255 and ANSI_1258](dxf/hebrew-and-vietnamese-last-letter.md)
16. [GDAL stops reading a DXF block after 10 000 entities](dxf/block-cut-at-10000.md)
17. [The DXF writer drops empty geometries and splits multipolygons](dxf/object-count-changes-on-write.md)
18. [A polygon with all heights 0 or symmetric around 0 comes back from DXF flat](dxf/flat-hatch-reads-without-height.md)
19. [A DXF written by GDAL cannot hold more than one layer set](dxf/only-one-entities-layer.md)
20. [Shapefile cuts field names at 10 bytes, in the middle of a letter](shapefile/field-name-10-bytes.md)
21. [Shapefile text fields hold 254 bytes, not 254 characters](shapefile/text-limit-254-bytes.md)
22. [Shapefile removes spaces from both ends of a text value](shapefile/spaces-stripped.md)
23. [In a 3D Shapefile a flat object gets Z = 0](shapefile/flat-feature-gets-z-zero.md)
24. [The KML driver wraps coordinates it cannot use instead of refusing them](kml/foreign-coordinates.md)
25. [KML turns a 64-bit integer into a string and trims the trailing space](kml/int64-becomes-string.md)
26. [GML rewrites layer and field names and merges layers whose names become equal](gml/names-rewritten-and-merged.md)
27. [FlatGeobuf returns features in spatial-index order, not in write order](flatgeobuf/feature-order.md)
28. [FlatGeobuf turns Date into DateTime and loses Time](flatgeobuf/time-and-date.md)
29. [GDAL gives a GeoJSON without a CRS the CRS EPSG:4326, or EPSG:4979 if any point has Z](geojson/reader-assigns-a-crs.md)
30. [File names inside a ZIP can be in a code page Python does not know about](general/zip-name-codepage.md)

## Licence

The text of the notes is under CC BY 4.0. The code snippets are under the MIT licence. Use them as you like.

## A note is wrong or out of date

Open a GitHub issue on this repository. Say which note, which GDAL version you ran, and paste the output you got.
