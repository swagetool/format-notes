# Control characters and U+FFFE in text values are changed or break the file

Checked on GDAL 3.10.3, PROJ 9.6.0, Python 3.13.5.

## What happens

Three values were written into one text field of each format and read back. In the output below `kept` means the value came back unchanged.

- A carriage return became a line feed in GML, KML and CSV.
- Control character 0x01 is dropped by GML, and a KML file with it will not open at all.
- U+FFFE makes the KML file unreadable, and the GML file opens with zero features and an XML error.
- GeoJSON and GeoPackage kept all three.

The snippet silences GDAL messages so the table stays short.

## Reproduce

```python
import os, tempfile
from osgeo import gdal, ogr

values = {"carriage return": "a\rb", "control char 0x01": "a\x01b", "U+FFFE": "a\ufffeb"}
formats = [("GML", "t.gml"), ("LIBKML", "t.kml"), ("CSV", "t.csv"),
           ("GeoJSON", "t.geojson"), ("GPKG", "t.gpkg")]

gdal.PushErrorHandler("CPLQuietErrorHandler")
for drv, name in formats:
    out = []
    for label, v in values.items():
        p = os.path.join(tempfile.mkdtemp(), name)
        ds = ogr.GetDriverByName(drv).CreateDataSource(p)
        lyr = ds.CreateLayer("t", geom_type=ogr.wkbPoint)
        lyr.CreateField(ogr.FieldDefn("v", ogr.OFTString))
        f = ogr.Feature(lyr.GetLayerDefn())
        f.SetField("v", v)
        f.SetGeometry(ogr.CreateGeometryFromWkt("POINT (1 2)"))
        lyr.CreateFeature(f)
        ds = lyr = f = None
        gdal.ErrorReset()
        src = ogr.Open(p)
        if src is None:
            out.append("%s: FILE WILL NOT OPEN" % label)
            continue
        got = [r.GetField("v") for r in src.GetLayer(0)]
        why = " (" + gdal.GetLastErrorMsg()[:40] + ")" if not got else ""
        out.append("%s: %s%s" % (label, "kept" if got == [v] else repr(got), why))
    print(drv.ljust(8), " | ".join(out))
```

Output, as printed (standard output first, then standard error):

```
GML      carriage return: ['a\nb'] | control char 0x01: ['ab'] | U+FFFE: [] (XML parsing of GML file failed : not wel)
LIBKML   carriage return: ['a\nb'] | control char 0x01: FILE WILL NOT OPEN | U+FFFE: FILE WILL NOT OPEN
CSV      carriage return: ['a\nb'] | control char 0x01: kept | U+FFFE: kept
GeoJSON  carriage return: kept | control char 0x01: kept | U+FFFE: kept
GPKG     carriage return: kept | control char 0x01: kept | U+FFFE: kept
```

## What to do

Remove control characters and U+FFFE from text before writing to XML formats. Read a sample back from the written file.
