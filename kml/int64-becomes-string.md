# KML turns a 64-bit integer into a string and trims the trailing space

Kind: format limit

Checked on GDAL 3.10.3, PROJ 9.6.0, Python 3.13.5.

## What happens

An `Integer64` field with 220 is read back as a `String` with `'220'`. A text value `'264 DIVER '` is written with its space (the file shows it) and read back without it. Both changes happen when the file is read. They were seen with the LIBKML driver.

## Reproduce

Snippet file: `int64-becomes-string.py`

```python
import os, tempfile
from osgeo import ogr

p = os.path.join(tempfile.mkdtemp(), "t.kml")
ds = ogr.GetDriverByName("LIBKML").CreateDataSource(p)
lyr = ds.CreateLayer("t", geom_type=ogr.wkbPoint)
lyr.CreateField(ogr.FieldDefn("color", ogr.OFTInteger64))
lyr.CreateField(ogr.FieldDefn("label", ogr.OFTString))
f = ogr.Feature(lyr.GetLayerDefn())
f.SetField("color", 220)
f.SetField("label", "264 DIVER ")
f.SetGeometry(ogr.CreateGeometryFromWkt("POINT (30 50)"))
lyr.CreateFeature(f)
ds = lyr = f = None

print("in the file:", [l.strip() for l in open(p) if "264" in l or "220" in l])
src = ogr.Open(p)
back = src.GetLayer(0)
d = back.GetLayerDefn()
for i in range(d.GetFieldCount()):
    fd = d.GetFieldDefn(i)
    if fd.GetName() in ("color", "label"):
        print(fd.GetName(), "type read:", fd.GetTypeName())
g = next(iter(back))
print("values read:", repr(g.GetField("color")), repr(g.GetField("label")))
```

Output, as printed (standard output first, then standard error):

```
in the file: ['<SimpleData name="color">220</SimpleData>', '<SimpleData name="label">264 DIVER </SimpleData>']
color type read: String
label type read: String
values read: '220' '264 DIVER'
```

## What to do

Convert numbers when you read KML and do not count the missing space as a write error.

## Sources

- [KML reference, Schema](https://developers.google.com/kml/documentation/kmlreference): the type of a `SimpleField` is one of string, int, uint, short, ushort, float, double and bool. There is no 64-bit type. The trailing space is not covered by the reference.
- We did not find a GDAL issue about this.
