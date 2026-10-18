# FlatGeobuf turns Date into DateTime and loses Time

Checked on GDAL 3.10.3, PROJ 9.6.0, Python 3.13.5.

## What happens

A `Date` field is read back as `DateTime` (`2026/10/18 00:00:00`). A `Time` field is read back as `DateTime` too, and the value is empty.

## Reproduce

```python
import os, tempfile
from osgeo import ogr

p = os.path.join(tempfile.mkdtemp(), "t.fgb")
ds = ogr.GetDriverByName("FlatGeobuf").CreateDataSource(p)
lyr = ds.CreateLayer("t", geom_type=ogr.wkbPoint)
lyr.CreateField(ogr.FieldDefn("d", ogr.OFTDate))
lyr.CreateField(ogr.FieldDefn("t", ogr.OFTTime))
f = ogr.Feature(lyr.GetLayerDefn())
f.SetField("d", 2026, 10, 18, 0, 0, 0, 0)
f.SetField("t", 0, 0, 0, 13, 45, 30, 0)
f.SetGeometry(ogr.CreateGeometryFromWkt("POINT (1 2)"))
lyr.CreateFeature(f)
ds = lyr = f = None

src = ogr.Open(p)
back = src.GetLayer(0)
d = back.GetLayerDefn()
print("types read:", [(d.GetFieldDefn(i).GetName(), d.GetFieldDefn(i).GetTypeName()) for i in range(d.GetFieldCount())])
g = next(iter(back))
print("written: d=2026-10-18 t=13:45:30")
print("read:   ", "d =", g.GetFieldAsString("d"), "| t =", g.GetFieldAsString("t"))
```

Output, as printed (standard output first, then standard error):

```
types read: [('d', 'DateTime'), ('t', 'DateTime')]
written: d=2026-10-18 t=13:45:30
read:    d = 2026/10/18 00:00:00 | t = 
```

## What to do

Store time of day as text or as seconds. Treat the date type change as a change of type in your report.
