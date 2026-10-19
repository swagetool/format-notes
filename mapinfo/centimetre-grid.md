# MapInfo TAB moves coordinates by up to about a centimetre

Kind: documented driver behaviour

Checked on GDAL 3.10.3, PROJ 9.6.0, Python 3.13.5.

## What happens

2000 random points in a UTM range were written to a MapInfo table and read back. The largest shift was 0.0099 with a CRS (EPSG:32610) and 0.0150 without one. GDAL prints no message about the shift (the two warnings in the output are about a dummy column). The file opens, the points are where you expect them, and only a comparison of numbers shows it.

## Reproduce

Snippet file: `centimetre-grid.py`

```python
import os, random, tempfile
from osgeo import ogr, osr

random.seed(1)
pts = [(500000 + random.random() * 100000, 5400000 + random.random() * 100000)
       for _ in range(2000)]

def roundtrip(srs):
    d = tempfile.mkdtemp()
    ds = ogr.GetDriverByName("MapInfo File").CreateDataSource(d)
    lyr = ds.CreateLayer("t", srs, ogr.wkbPoint)
    for x, y in pts:
        f = ogr.Feature(lyr.GetLayerDefn())
        pt = ogr.Geometry(ogr.wkbPoint)
        pt.AddPoint_2D(x, y)
        f.SetGeometry(pt)
        lyr.CreateFeature(f)
    ds = lyr = f = None
    src = ogr.Open(os.path.join(d, "t.tab"))
    back = src.GetLayer(0)
    worst = 0.0
    for (x, y), f in zip(pts, back):
        g = f.GetGeometryRef()
        worst = max(worst, abs(g.GetX() - x), abs(g.GetY() - y))
    return worst

utm = osr.SpatialReference()
utm.ImportFromEPSG(32610)
print("with EPSG:32610, worst shift: %.4f" % roundtrip(utm))
print("without a CRS,   worst shift: %.4f" % roundtrip(None))
```

Output, as printed (standard output first, then standard error):

```
with EPSG:32610, worst shift: 0.0099
without a CRS,   worst shift: 0.0150
[stderr] Warning 5: MapInfo tables must contain at least 1 column, adding dummy FID column.
Warning 5: MapInfo tables must contain at least 1 column, adding dummy FID column.
```

## What to do

Compare coordinates after a MapInfo round trip with a tolerance of about 2 cm, and print the largest shift instead of a yes/no. Always write the CRS, because leaving it out made the shift larger here.

## Sources

- [GDAL MapInfo driver page](https://gdal.org/en/stable/drivers/vector/mitab.html), Creation Issues: "The TAB File format requires that the bounds (geographical extents) of a new file be set before writing the first feature." For a projection other than lat/lon the default bounds are (-30000000 + false_easting, -15000000 + false_northing) to (30000000 + false_easting, 15000000 + false_northing). The `BOUNDS` layer creation option is described as "Define custom layer bounds to increase the accuracy of the coordinates."
- The page does not give the size of the shift. The numbers in this note are what we measured.
- We did not find a GDAL issue about this.
