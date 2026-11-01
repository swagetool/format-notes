# A geometry kind the format does not know is kept, changed, lost or refused, depending on the format

Kind: undocumented driver behaviour

Checked on GDAL 3.10.3, PROJ 9.6.0, Python 3.13.5.

## What happens

The snippet writes one `POLYHEDRALSURFACE Z` with two faces to ten drivers and reads each file back. The answers are different, and the write call is not a reliable sign of what happened.

- Kept as it was: GeoPackage (with a warning about a non-standard extension), GML, FlatGeobuf, CSV with WKT.
- Changed: Shapefile reads it back as a TIN with 2 parts.
- Lost without a word: MapInfo returns 0 from the write, prints nothing, and the record has no geometry on reading.
- Lost with a message: plain KML and GeoJSON return 0 from the write and print one message. The record has no geometry on reading.
- Refused: LIBKML and DXF return 6 from the write and print a message.

Three of ten formats return success and leave a record with no geometry. The count of objects does not change, so a count check does not see it.

## Reproduce

Snippet file: `geometry-kind-the-format-does-not-know.py`

```python
import os, tempfile
from osgeo import gdal, ogr

WKT = "POLYHEDRALSURFACE Z (((0 0 0,1 0 0,1 1 0,0 0 0)),((0 0 0,1 0 0,1 0 1,0 0 0)))"
os.chdir(tempfile.mkdtemp())
for driver, ext in (("ESRI Shapefile", "shp"), ("MapInfo File", "tab"), ("KML", "kml"), ("LIBKML", "kml"),
                    ("DXF", "dxf"), ("GeoJSON", "geojson"), ("GPKG", "gpkg"), ("GML", "gml"),
                    ("FlatGeobuf", "fgb"), ("CSV", "csv")):
    msgs = []
    gdal.PushErrorHandler(lambda c, n, m: msgs.append(" ".join(m.split())))
    name = "t." + ext
    ds = ogr.GetDriverByName(driver).CreateDataSource(name)
    lyr = ds.CreateLayer("t", geom_type=ogr.wkbUnknown if driver == "DXF" else ogr.wkbPolyhedralSurfaceZ,
                         options=["GEOMETRY=AS_WKT"] if driver == "CSV" else [])
    if driver != "DXF":
        lyr.CreateField(ogr.FieldDefn("id", ogr.OFTInteger))
    f = ogr.Feature(lyr.GetLayerDefn())
    f.SetGeometry(ogr.CreateGeometryFromWkt(WKT))
    written = lyr.CreateFeature(f)
    ds = lyr = f = None
    back = ogr.Open(name)
    lyr = back.GetLayer(0)
    kinds = []
    for g in (x.GetGeometryRef() for x in lyr):
        kinds.append("no geometry" if g is None else "%s with %d parts" % (g.GetGeometryName(), g.GetGeometryCount()))
    gdal.PopErrorHandler()
    print("%s: write returned %d, read back %d feature(s): %s" % (driver, written, lyr.GetFeatureCount(), kinds))
    for m in msgs:
        print("    message:", m)
    back = lyr = None
```

Output, as printed (standard output first, then standard error):

```
ESRI Shapefile: write returned 0, read back 1 feature(s): ['TIN with 2 parts']
MapInfo File: write returned 0, read back 1 feature(s): ['no geometry']
KML: write returned 0, read back 1 feature(s): ['no geometry']
    message: Export of geometry to KML failed
LIBKML: write returned 6, read back 0 feature(s): []
    message: Cannot translate feature: OGRFeature(t):-1 POLYHEDRALSURFACE Z (((0 0 0,1 0 0,1 1 0,0 0 0)),((0 0 0,1 0 0,1 0 1,0 0 0)))
DXF: write returned 6, read back 0 feature(s): []
    message: No known way to write feature with geometry 'PolyhedralSurface'.
GeoJSON: write returned 0, read back 1 feature(s): ['no geometry']
    message: OGR geometry type unsupported as a GeoJSON geometry detected. Feature gets NULL geometry assigned.
GPKG: write returned 0, read back 1 feature(s): ['POLYHEDRALSURFACE with 2 parts']
    message: Registering non-standard gpkg_geom_POLYHEDRALSURFACE extension
GML: write returned 0, read back 1 feature(s): ['POLYHEDRALSURFACE with 2 parts']
FlatGeobuf: write returned 0, read back 1 feature(s): ['POLYHEDRALSURFACE with 2 parts']
CSV: write returned 0, read back 1 feature(s): ['POLYHEDRALSURFACE with 2 parts']
```

## What to do

Find out which geometry kinds are in the data before choosing a target. If the target does not know a kind, convert it yourself (for a surface, to its faces as polygons) and tell the user, or pick a format that keeps it. After writing, count the objects that have a geometry, not only the objects.

## Sources

- No link. The driver pages do not list which geometry kinds a driver cannot write. The table above is the output of the snippet.
- We did not find a GDAL issue about this.
