# The KML driver wraps coordinates it cannot use instead of refusing them

Kind: documented driver behaviour

Checked on GDAL 3.10.3, PROJ 9.6.0, Python 3.13.5.

## What happens

KML stores longitude and latitude only. Writing projected metres without a CRS does not fail. The longitude is wrapped into the range -180 to 180, so 500123.5 becomes 83.5, and the latitude 4500000 is written as is, although it is far outside the valid range. GDAL prints a warning for each of them once. The LIBKML driver refused the same point with "Invalid longitude".

## Reproduce

Snippet file: `foreign-coordinates.py`

```python
import os, tempfile
from osgeo import ogr

p = os.path.join(tempfile.mkdtemp(), "t.kml")
ds = ogr.GetDriverByName("KML").CreateDataSource(p)
lyr = ds.CreateLayer("t", geom_type=ogr.wkbPoint)          # no CRS given
f = ogr.Feature(lyr.GetLayerDefn())
f.SetGeometry(ogr.CreateGeometryFromWkt("POINT (500123.5 4500000)"))   # UTM metres
lyr.CreateFeature(f)
ds = lyr = f = None

print("in the file:", [l.strip() for l in open(p) if "<coordinates>" in l])
src = ogr.Open(p)
for g in src.GetLayer(0):
    print("written: POINT (500123.5 4500000)")
    print("read:   ", g.GetGeometryRef().ExportToWkt())
```

Output, as printed (standard output first, then standard error):

```
in the file: ['<Point><coordinates>83.5,4500000.0</coordinates></Point>']
written: POINT (500123.5 4500000)
read:    POINT (83.5 4500000.0)
[stderr] ERROR 1: Latitude 4500000.000000 is invalid. Valid range is [-90,90]. This warning will not be issued any more
Warning 1: Longitude 500123.500000 has been modified to fit into range [-180,180]. This warning will not be issued any more
```

## What to do

Reproject to EPSG:4326 before writing KML and check the range of the result.

## Sources

- [GDAL KML driver page](https://gdal.org/en/stable/drivers/vector/kml.html): "KML by specification uses only a single projection, EPSG:4326. All OGR KML output will be presented in EPSG:4326. As such OGR will create layers in the correct coordinate system and transform any geometries." With no CRS on the layer there is nothing to transform from, which is the case in this note.
- We did not find a GDAL issue about this.
