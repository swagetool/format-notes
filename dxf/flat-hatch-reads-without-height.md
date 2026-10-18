# A polygon with all heights 0 or symmetric around 0 comes back from DXF flat

Checked on GDAL 3.10.3, PROJ 9.6.0, Python 3.13.5.

## What happens

GDAL writes a polygon as a hatch, which carries a single elevation. Reading it back, a polygon whose Z values are all 0 loses its Z. So does one with Z of -1, 1, -1. A polygon at constant height 5 keeps it. The second case is consistent with the writer storing the mid-height between lowest and highest, which is 0 for -1 and 1, but we did not read the writer source to confirm that.

## Reproduce

```python
import os, tempfile
from osgeo import ogr

p = os.path.join(tempfile.mkdtemp(), "hatch.dxf")
ds = ogr.GetDriverByName("DXF").CreateDataSource(p)
lyr = ds.CreateLayer("entities", geom_type=ogr.wkbPolygon25D)
wkts = ["POLYGON Z ((0 0 0, 1 0 0, 1 1 0, 0 0 0))",
        "POLYGON Z ((0 0 -1, 1 0 1, 1 1 -1, 0 0 -1))",
        "POLYGON Z ((0 0 5, 1 0 5, 1 1 5, 0 0 5))"]
for w in wkts:
    f = ogr.Feature(lyr.GetLayerDefn())
    f.SetGeometry(ogr.CreateGeometryFromWkt(w))
    lyr.CreateFeature(f)
ds = lyr = f = None

back = ogr.Open(p)
for (w, f) in zip(wkts, back.GetLayer(0)):
    print("written:", w)
    print("read:   ", f.GetGeometryRef().ExportToIsoWkt())
```

Output, as printed (standard output first, then standard error):

```
written: POLYGON Z ((0 0 0, 1 0 0, 1 1 0, 0 0 0))
read:    POLYGON ((0 0,1 0,1 1,0 0))
written: POLYGON Z ((0 0 -1, 1 0 1, 1 1 -1, 0 0 -1))
read:    POLYGON ((0 0,1 0,1 1,0 0))
written: POLYGON Z ((0 0 5, 1 0 5, 1 1 5, 0 0 5))
read:    POLYGON Z ((0 0 5,1 0 5,1 1 5,0 0 5))
```

## What to do

If Z of polygons matters, check it after writing. A flat result for a polygon you wrote with a height of 0 is the same as a polygon that never had a height, so decide how you want to report that.
