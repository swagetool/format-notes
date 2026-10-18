# Shapefile text fields hold 254 bytes, not 254 characters

Checked on GDAL 3.10.3, PROJ 9.6.0, Python 3.13.5.

## What happens

A 300-letter Latin string is cut to 254. A 200-letter Cyrillic string, which is 400 bytes in UTF-8, is cut to 127 letters, the largest number that fits in 254 bytes. GDAL does warn about the cut, the snippet silences it.

## Reproduce

```python
import os, tempfile
from osgeo import gdal, ogr

gdal.PushErrorHandler("CPLQuietErrorHandler")   # GDAL warns about the cut, here we count it ourselves

def roundtrip(text):
    d = tempfile.mkdtemp()
    ds = ogr.GetDriverByName("ESRI Shapefile").CreateDataSource(os.path.join(d, "t.shp"))
    lyr = ds.CreateLayer("t", geom_type=ogr.wkbPoint, options=["ENCODING=UTF-8"])
    fd = ogr.FieldDefn("v", ogr.OFTString)
    fd.SetWidth(254)
    lyr.CreateField(fd)
    f = ogr.Feature(lyr.GetLayerDefn())
    f.SetField("v", text)
    f.SetGeometry(ogr.CreateGeometryFromWkt("POINT (1 2)"))
    lyr.CreateFeature(f)
    ds = lyr = f = None
    src = ogr.Open(os.path.join(d, "t.shp"))
    return next(iter(src.GetLayer(0))).GetField("v")

for label, text in (("latin", "a" * 300), ("cyrillic", "ж" * 200)):
    got = roundtrip(text)
    print(label, "written:", len(text), "chars,", len(text.encode()), "bytes | read:",
          len(got), "chars,", len(got.encode()), "bytes")
```

Output, as printed (standard output first, then standard error):

```
latin written: 300 chars, 300 bytes | read: 254 chars, 254 bytes
cyrillic written: 200 chars, 400 bytes | read: 127 chars, 254 bytes
```

## What to do

Measure text in the encoding you write. Warn before the write about the objects that will be cut, or choose a format without this limit.
