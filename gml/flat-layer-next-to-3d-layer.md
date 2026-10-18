# A GML file with one 3D layer cannot be read for its flat layers

Checked on GDAL 3.10.3, PROJ 9.6.0, Python 3.13.5.

## What happens

The writer puts `srsDimension="3"` on the envelope of the whole file as soon as one layer has Z. The flat layer's own `posList` carries no dimension, and the reader then expects three values per vertex. The flat layer yields 0 features and the error "Did not get at least 3 values". The 3D layer reads normally.

## Reproduce

```python
import os, tempfile
from osgeo import gdal, ogr

p = os.path.join(tempfile.mkdtemp(), "t.gml")
ds = ogr.GetDriverByName("GML").CreateDataSource(p)
for name, gt, wkt in (("flat", ogr.wkbLineString, "LINESTRING (1 2, 3 4)"),
                      ("tall", ogr.wkbLineString25D, "LINESTRING Z (1 2 3, 4 5 6)")):
    lyr = ds.CreateLayer(name, geom_type=gt)
    f = ogr.Feature(lyr.GetLayerDefn())
    f.SetGeometry(ogr.CreateGeometryFromWkt(wkt))
    lyr.CreateFeature(f)
ds = lyr = f = None

src = ogr.Open(p)
for lyr in src:
    gdal.ErrorReset()
    n = sum(1 for _ in lyr)
    print(lyr.GetName(), "features read:", n, "| last error:", gdal.GetLastErrorMsg() or "none")
```

Output, as printed (standard output first, then standard error):

```
flat features read: 0 | last error: Geometry of feature 0 flat.0 cannot be parsed: Did not get at least 3 values or invalid number of set of coordinates <gml:posList>1 2 3 4</gml:posList>. You may set the GML_SKIP_CORRUPTED_FEATURES configuration option to YES to skip to the next feature
tall features read: 1 | last error: none
[stderr] ERROR 1: Geometry of feature 0 flat.0 cannot be parsed: Did not get at least 3 values or invalid number of set of coordinates <gml:posList>1 2 3 4</gml:posList>. You may set the GML_SKIP_CORRUPTED_FEATURES configuration option to YES to skip to the next feature
```

## What to do

Keep 2D and 3D layers in separate files. The error text offers `GML_SKIP_CORRUPTED_FEATURES`, which skips the objects and does not repair them.
