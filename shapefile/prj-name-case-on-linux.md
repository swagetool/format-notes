# A Shapefile .prj with a different letter case is not found on Linux

Kind: undocumented driver behaviour

Checked on GDAL 3.10.3, PROJ 9.6.0, Python 3.13.5.

## What happens

On a case-sensitive file system GDAL looks for the `.prj` next to `Road.shp` under a name that matches the `.shp` base name. A file `road.prj` next to `Road.shp`, as can come out of a Windows folder, is not found. The layer is read with no CRS and GDAL prints no message. In the snippet the layer reports EPSG:32633 with `Road.prj` and `None` after the rename to `road.prj`.

The coordinates are unchanged, so the file looks fine until you reproject or overlay it.

## Reproduce

Snippet file: `prj-name-case-on-linux.py`

```python
import os, tempfile
from osgeo import ogr, osr

d = tempfile.mkdtemp()
p = os.path.join(d, "Road.shp")
srs = osr.SpatialReference()
srs.ImportFromEPSG(32633)
ds = ogr.GetDriverByName("ESRI Shapefile").CreateDataSource(p)
lyr = ds.CreateLayer("Road", srs=srs, geom_type=ogr.wkbPoint)
f = ogr.Feature(lyr.GetLayerDefn())
f.SetGeometry(ogr.CreateGeometryFromWkt("POINT (500000 5000000)"))
lyr.CreateFeature(f)
ds = lyr = f = None

def crs():
    src = ogr.Open(p)
    s = src.GetLayer(0).GetSpatialRef()
    return s.GetAuthorityCode(None) if s else None

print("Road.prj:", crs())
os.rename(os.path.join(d, "Road.prj"), os.path.join(d, "road.prj"))
print("road.prj:", crs())
```

Output, as printed (standard output first, then standard error):

```
Road.prj: 32633
road.prj: None
```

## What to do

Before reading a Shapefile on Linux, look for companion files whose names differ from the `.shp` only by letter case. Rename them to match and tell the user you did. Always report a layer that has no CRS.

## Sources

- The [GDAL Shapefile driver page](https://gdal.org/en/stable/drivers/vector/shapefile.html) says that a `.prj` file in old Arc/Info style or in ESRI WKT style "will be read". It says nothing about letter case in the name, so the label is ours.
- We did not find a GDAL issue about this.
