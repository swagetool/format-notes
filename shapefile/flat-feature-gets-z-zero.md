# In a 3D Shapefile a flat object gets Z = 0

Kind: format limit

Checked on GDAL 3.10.3, PROJ 9.6.0, Python 3.13.5.

## What happens

Dimension belongs to the layer in a Shapefile. A flat `POINT (3 4)` written to a 3D layer is read back as `POINT Z (3 4 0)`. A zero invented this way cannot be told apart from a real height of 0.

## Reproduce

Snippet file: `flat-feature-gets-z-zero.py`

```python
import os, tempfile
from osgeo import ogr

wkts = ("POINT Z (1 2 5)", "POINT (3 4)")
p = os.path.join(tempfile.mkdtemp(), "t.shp")
ds = ogr.GetDriverByName("ESRI Shapefile").CreateDataSource(p)
lyr = ds.CreateLayer("t", geom_type=ogr.wkbPoint25D)
for wkt in wkts:
    f = ogr.Feature(lyr.GetLayerDefn())
    f.SetGeometry(ogr.CreateGeometryFromWkt(wkt))
    lyr.CreateFeature(f)
ds = lyr = f = None

src = ogr.Open(p)
for wkt, f in zip(wkts, src.GetLayer(0)):
    print("written:", wkt.ljust(16), "read:", f.GetGeometryRef().ExportToIsoWkt())
```

Output, as printed (standard output first, then standard error):

```
written: POINT Z (1 2 5)  read: POINT Z (1 2 5)
written: POINT (3 4)      read: POINT Z (3 4 0)
```

## What to do

Decide your policy before writing. Losing the height of some objects and saying how many is more honest than giving the others a made-up zero.

## Sources

- [GDAL Shapefile driver page](https://gdal.org/en/stable/drivers/vector/shapefile.html): "ESRI shapefiles can only store one kind of geometry per layer", and the layer creation option `SHPT` takes POINT, ARC, POLYGON, MULTIPOINT for 2D and POINTZ, ARCZ, POLYGONZ, MULTIPOINTZ or MULTIPATCH for 3D. The kind, and so the dimension, belongs to the layer.
- We did not find a GDAL issue about this.
