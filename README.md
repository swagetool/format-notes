# format-notes

Traps in geodata formats that we ran into, each one reproduced on a small synthetic file. Every note gives the numbers, a short script that shows the effect, the output of that script as it was printed, and what to do about it.

Written by the Swage team (https://tryswage.com). We convert between GIS and CAD formats and these are the places where data changed or got lost while the conversion went on.

## What was checked, and on what

The output stored in every note was printed by GDAL 3.10.3 (Python bindings), PROJ 9.6.0, Python 3.13.5, in a Debian-based container. No note uses libredwg or any other converter, so no other version is listed. A GitHub Actions workflow runs every snippet again on GDAL 3.8.5, 3.10.3 and 3.13.3 and reports where the output differs from the note (see "Other GDAL versions" below). A different GDAL may behave differently. If you see that, please tell us (below).

## How to run a snippet

Each snippet is a complete file, stored next to its note with the same name (`dxf/block-cut-at-10000.py`). The note shows the same code. Run `python3 -W ignore snippet.py` where the `osgeo` Python package is installed. The `-W ignore` only hides a Python deprecation notice. Everything else GDAL prints is shown in the note. The snippets write their files into a fresh temporary directory.

## Notes

The strongest come first. Strong here means that the data changes while the call succeeds, or that the result looks like something else. GDAL does print a warning in some of these cases, and each note says whether it does.

Every note starts with a `Kind:` line, so you can see whose behaviour it is:

- `format limit`: the format itself cannot hold it.
- `documented driver behaviour`: a GDAL driver page describes it.
- `driver bug`: GDAL 3.10.3 does something its own documentation or its own message does not account for. Some notes carry this label for an undocumented limitation of a driver, and say so in the Sources section.
- `undocumented driver behaviour`: the driver page does not mention it, and it is not clearly a bug. Linux telling letter case apart in file names is an example.
- `PROJ behaviour`: it comes from PROJ.

Each note ends with a Sources section. A link is there only where the page says what the note claims. Where we found no page or issue, the note says that.

1. [Reprojecting from a feet-based 2D CRS leaves Z in feet](general/z-not-converted-by-reprojection.md)
2. [GDAL reads at most 256 characters of a DXF TEXT, and only the last piece of a split one](dxf/text-longer-than-256-characters.md)
3. [A DXF that declares ANSI_1250 but is written in UTF-8 reads as mojibake](dxf/wrong-declared-codepage.md)
4. [A GML file with one 3D layer cannot be read for its flat layers](gml/flat-layer-next-to-3d-layer.md)
5. [KML loses fields in two situations](kml/fields-lost.md)
6. [The plain KML driver takes features only into the layer created last](kml/layers-created-up-front.md)
7. [Shapefile written without an encoding stores non-Latin text as question marks](shapefile/no-cpg-question-marks.md)
8. [Empty string and NULL are different values, and most formats do not keep both](general/empty-string-and-null.md)
9. [Control characters and U+FFFE in text values are changed or break the file](general/special-characters.md)
10. [GeoPackage does not keep a field named fid or geom](gpkg/fid-and-geom-field-names.md)
11. [MapInfo TAB has no height, and drops Z with no message about it](mapinfo/no-height.md)
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
31. [File Geodatabase in its default layout breaks a time of day and changes four other value types](filegdb/default-layout-types.md)
32. [File Geodatabase gives a date and time without a zone the zone UTC](filegdb/time-without-zone-marked-utc.md)
33. [File Geodatabase stores coordinates on a grid and moves a vertex by up to half a step](filegdb/coordinate-grid.md)
34. [A DXF hatch with several separate boundaries is read as one polygon with holes outside it](dxf/hatch-boundaries-merge-into-one-polygon.md)
35. [GDAL ignores the GML attribute-fields option once it has written a .gfs file](gml/gfs-file-hides-attribute-fields.md)
36. [An ISO 19139 metadata file opens as GML with no layers](gml/iso-19139-metadata-opens-as-gml.md)
37. [MIF writes a newline in a value as backslash and n, and reads it back that way](mapinfo/mif-newline-in-value.md)
38. [A MIF table with no fields is written and cannot be opened](mapinfo/mif-table-without-fields.md)
39. [A Shapefile .prj with a different letter case is not found on Linux](shapefile/prj-name-case-on-linux.md)
40. [A KML written with a quote, ampersand or less-than sign in a field name cannot be opened](kml/field-name-breaks-the-file.md)
41. [The GDAL DXF writer declares inches over data in metres](dxf/writer-declares-inches.md)
42. [A VRT whose source cannot be reached opens fine and has no features](vrt/unreachable-source-opens-empty.md)
43. [A GML with a topology edge that has no geometry stops reading at the first such object](gml/topology-edge-stops-reading.md)
44. [SQLite does not create a layer with a field named geometry, and drops a text field named OGC_FID](sqlite/geometry-and-ogc-fid-fields.md)
45. [DXF objects on a layout sheet come in the same layer as the model](dxf/paper-space-objects-in-the-same-layer.md)
46. [GDAL does not open a MapInfo table whose header says Type NativeX](mapinfo/native-x-not-recognized.md)
47. [A geometry kind the format does not know is kept, changed, lost or refused, depending on the format](general/geometry-kind-the-format-does-not-know.md)

## What each format loses or changes

| Format | What changes | Notes |
|---|---|---|
| Shapefile | field names cut at 10 bytes, text cut at 254 bytes, non-Latin text becomes `?` without an encoding, spaces removed at both ends, flat objects get Z = 0 in a 3D layer, a `.prj` with another letter case is not found on Linux | [names](shapefile/field-name-10-bytes.md), [text](shapefile/text-limit-254-bytes.md), [encoding](shapefile/no-cpg-question-marks.md), [spaces](shapefile/spaces-stripped.md), [Z = 0](shapefile/flat-feature-gets-z-zero.md), [.prj case](shapefile/prj-name-case-on-linux.md) |
| MapInfo TAB | a table of type NativeX is not recognized, Z dropped, coordinates move by up to about a centimetre, time zone of DateTime dropped, MIF: newline in a value comes back as backslash and n, a table with no fields cannot be opened | [NativeX](mapinfo/native-x-not-recognized.md), [Z](mapinfo/no-height.md), [grid](mapinfo/centimetre-grid.md), [zone](mapinfo/datetime-zone.md), [MIF newline](mapinfo/mif-newline-in-value.md), [MIF no fields](mapinfo/mif-table-without-fields.md) |
| KML | a quote, ampersand or less-than sign in a field name makes the file unreadable, fields lost when all are empty or when a name is one the reader uses, features lost in layers created up front (plain KML driver), foreign coordinates wrapped, 64-bit integer becomes a string | [field name](kml/field-name-breaks-the-file.md), [fields](kml/fields-lost.md), [layers](kml/layers-created-up-front.md), [coordinates](kml/foreign-coordinates.md), [Int64](kml/int64-becomes-string.md) |
| GML | a topology edge without geometry stops the read, file unreadable for flat layers next to a 3D layer, names rewritten and layers merged, empty string read as NULL, attribute fields hidden by a .gfs file, metadata XML opens with no layers | [topology](gml/topology-edge-stops-reading.md), [3D](gml/flat-layer-next-to-3d-layer.md), [names](gml/names-rewritten-and-merged.md), [empty string](general/empty-string-and-null.md), [.gfs](gml/gfs-file-hides-attribute-fields.md), [metadata](gml/iso-19139-metadata-opens-as-gml.md) |
| DXF | header declares inches over data in metres, sheet objects in the same layer as the model, text cut at 256 characters, wrong or ignored code page, last character lost on two code pages, block cut at 10 000 entities, empty geometry dropped and multipolygon split, polygon with Z around 0 read flat, one layer set only, hatch with several boundaries read as one polygon with holes | [units](dxf/writer-declares-inches.md), [sheets](dxf/paper-space-objects-in-the-same-layer.md), [text](dxf/text-longer-than-256-characters.md), [declared page](dxf/wrong-declared-codepage.md), [writer header](dxf/gdal-writer-header-codepage.md), [1255 and 1258](dxf/hebrew-and-vietnamese-last-letter.md), [block](dxf/block-cut-at-10000.md), [counts](dxf/object-count-changes-on-write.md), [hatch](dxf/flat-hatch-reads-without-height.md), [layers](dxf/only-one-entities-layer.md), [hatch boundaries](dxf/hatch-boundaries-merge-into-one-polygon.md) |
| SQLite | a field named `geometry` stops the layer from being created, a text field named `OGC_FID` is dropped | [fields](sqlite/geometry-and-ogc-fid-fields.md) |
| VRT | a source that cannot be reached opens as an empty layer | [source](vrt/unreachable-source-opens-empty.md) |
| GeoPackage | field named `fid` or `geom` not kept, a repeated integer `fid` loses an object | [fid and geom](gpkg/fid-and-geom-field-names.md) |
| FlatGeobuf | feature order changes, Date becomes DateTime, Time lost | [order](flatgeobuf/feature-order.md), [types](flatgeobuf/time-and-date.md) |
| GeoJSON | a CRS that nobody wrote is reported on reading | [CRS](geojson/reader-assigns-a-crs.md) |
| File Geodatabase | in the default layout a 64-bit integer becomes a real, a time of day is lost, a zoned time is moved to UTC, a fraction of a second is cut, a time without a zone comes back marked UTC, coordinates move to a grid of 0.0001 unit or 0.000000001 degree | [layout](filegdb/default-layout-types.md), [UTC](filegdb/time-without-zone-marked-utc.md), [grid](filegdb/coordinate-grid.md) |
| Several | empty string against NULL, control characters, carriage return and U+FFFE in text, a geometry kind the format does not know | [empty string](general/empty-string-and-null.md), [special characters](general/special-characters.md), [geometry kind](general/geometry-kind-the-format-does-not-know.md) |
| Not a format | Z stays in feet when a 2D CRS is reprojected (PROJ), file names in a ZIP in another code page | [Z](general/z-not-converted-by-reprojection.md), [ZIP](general/zip-name-codepage.md) |

## Other GDAL versions

`.github/workflows/notes.yml` runs every snippet in the official images `ghcr.io/osgeo/gdal:ubuntu-full-3.8.5`, `ubuntu-full-3.10.3` and `ubuntu-full-3.13.3` (3.13.3 was the newest release when this was written). `ci/check_notes.py` compares what each snippet prints with the output stored in its note and uploads a report per image. A difference is information about another version, not a failed build.

## Licence

The text of the notes is under CC BY 4.0. The code snippets are under the MIT licence. Use them as you like.

## A note is wrong or out of date

Open a GitHub issue on this repository (see [CONTRIBUTING.md](CONTRIBUTING.md) for what to include). Say which note, which GDAL version you ran, and paste the output you got.
