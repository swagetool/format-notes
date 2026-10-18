# The DXF writer drops empty geometries and splits multipolygons

Checked on GDAL 3.10.3, PROJ 9.6.0, Python 3.13.5.

## What happens

Two ways the count differs after writing to DXF.

1. A feature with `POLYGON EMPTY` is accepted (`CreateFeature` returns 0) and nothing is written. Three written, two read back.
2. A multipolygon with three parts becomes three DXF entities, so one object is read back as three.

## Reproduce

```python
import os, tempfile
from osgeo import ogr

p = os.path.join(tempfile.mkdtemp(), "empty.dxf")
ds = ogr.GetDriverByName("DXF").CreateDataSource(p)
lyr = ds.CreateLayer("entities", geom_type=ogr.wkbPolygon)
for wkt in ("POLYGON ((0 0, 1 0, 1 1, 0 0))", "POLYGON EMPTY", "POLYGON ((5 5, 6 5, 6 6, 5 5))"):
    f = ogr.Feature(lyr.GetLayerDefn())
    f.SetGeometry(ogr.CreateGeometryFromWkt(wkt))
    print(wkt.ljust(34), "CreateFeature returned", lyr.CreateFeature(f))
ds = lyr = f = None

n = sum(l.GetFeatureCount() for l in ogr.Open(p))
print("features written: 3, read back:", n)
```

Output, as printed (standard output first, then standard error):

```
POLYGON ((0 0, 1 0, 1 1, 0 0))     CreateFeature returned 0
POLYGON EMPTY                      CreateFeature returned 0
POLYGON ((5 5, 6 5, 6 6, 5 5))     CreateFeature returned 0
features written: 3, read back: 2
```

```python
import os, tempfile
from osgeo import ogr

p = os.path.join(tempfile.mkdtemp(), "multi.dxf")
ds = ogr.GetDriverByName("DXF").CreateDataSource(p)
lyr = ds.CreateLayer("entities", geom_type=ogr.wkbMultiPolygon)
f = ogr.Feature(lyr.GetLayerDefn())
f.SetGeometry(ogr.CreateGeometryFromWkt(
    "MULTIPOLYGON (((0 0, 1 0, 1 1, 0 0)), ((5 5, 6 5, 6 6, 5 5)), ((9 9, 10 9, 10 10, 9 9)))"))
lyr.CreateFeature(f)
ds = lyr = f = None

back = ogr.Open(p)
lyr = back.GetLayer(0)
print("features written: 1, features read back:", lyr.GetFeatureCount())
```

Output, as printed (standard output first, then standard error):

```
features written: 1, features read back: 3
```

## What to do

Filter empty geometries yourself and say how many were left out. When you compare counts after a DXF round trip, expect more objects than you wrote for multi-part geometry and group the parts back by their source object.
