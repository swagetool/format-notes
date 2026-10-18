# MapInfo TAB drops the time zone of a DateTime and keeps the clock time

Checked on GDAL 3.10.3, PROJ 9.6.0, Python 3.13.5.

## What happens

`2026-10-18 12:00:00+03` is read back as `2026/10/18 12:00:00`. The zone is gone and the hour is unchanged, so the instant is now wrong by three hours if anyone reads it as UTC. GeoPackage keeps `+03` in the same test. GDAL also prints a "non-conformant content" warning during the run, but it does not mention the zone being dropped.

## Reproduce

```python
import os, tempfile
from osgeo import ogr

def run(driver, name):
    p = os.path.join(tempfile.mkdtemp(), name)
    ds = ogr.GetDriverByName(driver).CreateDataSource(p)
    lyr = ds.CreateLayer("t", geom_type=ogr.wkbPoint)
    lyr.CreateField(ogr.FieldDefn("when", ogr.OFTDateTime))
    f = ogr.Feature(lyr.GetLayerDefn())
    f.SetField("when", 2026, 10, 18, 12, 0, 0, 112)    # flag 112 = UTC+03:00
    f.SetGeometry(ogr.CreateGeometryFromWkt("POINT (1 2)"))
    lyr.CreateFeature(f)
    ds = lyr = f = None
    if driver == "MapInfo File":
        p = os.path.join(p, "t.tab")
    src = ogr.Open(p)
    g = next(iter(src.GetLayer(0)))
    print(driver.ljust(13), g.GetFieldAsString("when"))

print("written:      2026-10-18 12:00:00+03")
run("MapInfo File", "mi")
run("GPKG", "t.gpkg")
```

Output, as printed (standard output first, then standard error):

```
written:      2026-10-18 12:00:00+03
MapInfo File  2026/10/18 12:00:00
GPKG          2026/10/18 12:00:00+03
[stderr] Warning 1: Non-conformant content for record 1 in column when, 2026-10-18T12:00:00.000+03:00, successfully parsed
```

## What to do

Convert DateTime fields to UTC before writing to MapInfo, or store the offset in a separate attribute.
