# File Geodatabase gives a date and time without a zone the zone UTC

Kind: driver bug

Checked on GDAL 3.10.3, PROJ 9.6.0, Python 3.13.5.

## What happens

`2024/01/05 10:20:30` written with no time zone comes back as `2024/01/05 10:20:30+00`. The clock time is the same, but the value now claims to be UTC, which nobody wrote. It happens in the default layout and with `TARGET_ARCGIS_VERSION=ARCGIS_PRO_3_2_OR_LATER` alike. GDAL prints nothing.

## Reproduce

Snippet file: `time-without-zone-marked-utc.py`

```python
import os, tempfile
from osgeo import ogr

for options in ([], ["TARGET_ARCGIS_VERSION=ARCGIS_PRO_3_2_OR_LATER"]):
    p = os.path.join(tempfile.mkdtemp(), "t.gdb")
    ds = ogr.GetDriverByName("OpenFileGDB").CreateDataSource(p)
    lyr = ds.CreateLayer("t", geom_type=ogr.wkbPoint, options=options)
    lyr.CreateField(ogr.FieldDefn("when", ogr.OFTDateTime))
    f = ogr.Feature(lyr.GetLayerDefn())
    f.SetField("when", "2024/01/05 10:20:30")     # no time zone
    f.SetGeometry(ogr.CreateGeometryFromWkt("POINT (1 2)"))
    lyr.CreateFeature(f)
    ds = lyr = f = None
    src = ogr.Open(p)
    g = next(iter(src.GetLayer(0)))
    print((options or ["default layout"])[0].ljust(46), g.GetFieldAsString("when"))
```

Output, as printed:

```
default layout                                 2024/01/05 10:20:30+00
TARGET_ARCGIS_VERSION=ARCGIS_PRO_3_2_OR_LATER  2024/01/05 10:20:30+00
```

## What to do

If the times are local, say so next to the data: the `+00` on reading is not a statement of the source. A check that compares values before and after should accept a time without a zone coming back with `+00` and the same clock time, and count such values.

## Sources

- No link. The driver page does not say how a time without a zone is read. We found no GDAL issue about it, so the label is ours: an unstated zone becomes a stated one.
