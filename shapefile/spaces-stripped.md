# Shapefile removes spaces from both ends of a text value

Checked on GDAL 3.10.3, PROJ 9.6.0, Python 3.13.5.

## What happens

DBF pads fields to a fixed width with spaces, and the reader cannot tell padding from a real trailing space, so it strips on both sides. `" lead"` becomes `"lead"`. GeoPackage keeps all of it in the same test.

## Reproduce

```python
import os, tempfile
from osgeo import ogr

def roundtrip(driver, name, text):
    p = os.path.join(tempfile.mkdtemp(), name)
    ds = ogr.GetDriverByName(driver).CreateDataSource(p)
    lyr = ds.CreateLayer("t", geom_type=ogr.wkbPoint)
    lyr.CreateField(ogr.FieldDefn("v", ogr.OFTString))
    f = ogr.Feature(lyr.GetLayerDefn())
    f.SetField("v", text)
    f.SetGeometry(ogr.CreateGeometryFromWkt("POINT (1 2)"))
    lyr.CreateFeature(f)
    ds = lyr = f = None
    src = ogr.Open(p)
    return next(iter(src.GetLayer(0))).GetField("v")

for text in (" lead", "trail ", " both "):
    print(repr(text).ljust(9), "shapefile:", repr(roundtrip("ESRI Shapefile", "t.shp", text)),
          " gpkg:", repr(roundtrip("GPKG", "t.gpkg", text)))
```

Output, as printed (standard output first, then standard error):

```
' lead'   shapefile: 'lead'  gpkg: ' lead'
'trail '  shapefile: 'trail'  gpkg: 'trail '
' both '  shapefile: 'both'  gpkg: ' both '
```

## What to do

When you check a round trip, compare the values with `strip()` on both sides for Shapefile, or you will report differences that come from padding.
