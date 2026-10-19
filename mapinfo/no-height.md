# MapInfo TAB has no height, and drops Z with no message about it

Kind: format limit

Checked on GDAL 3.10.3, PROJ 9.6.0, Python 3.13.5.

## What happens

A `POINT Z` goes in and a 2D point comes out. GDAL prints no warning about the height (the one warning in the output is about a dummy column). In this snippet no CRS was set, so the X value also moved by 0.01, which is the effect from the neighbouring note.

## Reproduce

Snippet file: `no-height.py`

```python
import os, tempfile
from osgeo import ogr

d = tempfile.mkdtemp()
ds = ogr.GetDriverByName("MapInfo File").CreateDataSource(d)
lyr = ds.CreateLayer("t", geom_type=ogr.wkbPoint25D)
f = ogr.Feature(lyr.GetLayerDefn())
f.SetGeometry(ogr.CreateGeometryFromWkt("POINT Z (500000 5400000 12.5)"))
lyr.CreateFeature(f)
ds = lyr = f = None

src = ogr.Open(os.path.join(d, "t.tab"))
for f in src.GetLayer(0):
    print("written: POINT Z (500000 5400000 12.5)")
    print("read:   ", f.GetGeometryRef().ExportToIsoWkt())
```

Output, as printed (standard output first, then standard error):

```
written: POINT Z (500000 5400000 12.5)
read:    POINT (500000.01 5400000.0)
[stderr] Warning 5: MapInfo tables must contain at least 1 column, adding dummy FID column.
```

## What to do

If the format cannot keep Z, say so before the write and count the objects that had one. Keep the heights in an extra attribute if they matter.

## Sources

- No link. The [GDAL MapInfo driver page](https://gdal.org/en/stable/drivers/vector/mitab.html) does not mention Z. The note records what the files show.
- We did not find a GDAL issue about this.
