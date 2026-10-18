# FlatGeobuf returns features in spatial-index order, not in write order

Checked on GDAL 3.10.3, PROJ 9.6.0, Python 3.13.5.

## What happens

Five points written in the order 0 to 4 are read back as 3, 1, 2, 4, 0. Comparing by position in the file reports a difference for nearly every object.

## Reproduce

```python
import os, tempfile
from osgeo import ogr

pts = [(0, 0), (90, 90), (10, 80), (80, 10), (45, 45)]
p = os.path.join(tempfile.mkdtemp(), "t.fgb")
ds = ogr.GetDriverByName("FlatGeobuf").CreateDataSource(p)
lyr = ds.CreateLayer("t", geom_type=ogr.wkbPoint)
lyr.CreateField(ogr.FieldDefn("seq", ogr.OFTInteger))
for i, (x, y) in enumerate(pts):
    f = ogr.Feature(lyr.GetLayerDefn())
    f.SetField("seq", i)
    f.SetGeometry(ogr.CreateGeometryFromWkt("POINT (%d %d)" % (x, y)))
    lyr.CreateFeature(f)
ds = lyr = f = None

print("written order:", list(range(len(pts))))
back = ogr.Open(p)
print("read order:   ", [r.GetField("seq") for r in back.GetLayer(0)])
```

Output, as printed (standard output first, then standard error):

```
written order: [0, 1, 2, 3, 4]
read order:    [3, 1, 2, 4, 0]
```

## What to do

Write a key attribute and match objects by it. Do not promise the user an unchanged order.
