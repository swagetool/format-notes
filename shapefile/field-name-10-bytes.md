# Shapefile cuts field names at 10 bytes, in the middle of a letter

Checked on GDAL 3.10.3, PROJ 9.6.0, Python 3.13.5.

## What happens

The limit is bytes, not characters. `Название` (8 letters, 16 bytes in UTF-8) becomes `Назва`. `Ulica_główna` is cut after the first byte of `ó` and the result is a name with a broken byte. GDAL prints a warning about "laundered" names, which includes the broken one.

## Reproduce

```python
import os, tempfile
from osgeo import ogr

names = ("Название", "Ulica_główna", "street_name_long")
p = os.path.join(tempfile.mkdtemp(), "t.shp")
ds = ogr.GetDriverByName("ESRI Shapefile").CreateDataSource(p)
lyr = ds.CreateLayer("t", geom_type=ogr.wkbPoint, options=["ENCODING=UTF-8"])
for name in names:
    lyr.CreateField(ogr.FieldDefn(name, ogr.OFTString))
ds = lyr = None

src = ogr.Open(p)
defn = src.GetLayer(0).GetLayerDefn()
for i, written in enumerate(names):
    got = defn.GetFieldDefn(i).GetName()
    print(repr(written), "->", repr(got), "| bytes:", len(got.encode("utf-8", "surrogateescape")))
```

Output, as printed (standard output first, then standard error):

```
'Название' -> 'Назва' | bytes: 10
'Ulica_główna' -> 'Ulica_gł\udcc3' | bytes: 10
'street_name_long' -> 'street_nam' | bytes: 10
[stderr] Warning 6: Normalized/laundered field name: 'Название' to 'Назва'
Warning 6: Normalized/laundered field name: 'Ulica_główna' to 'Ulica_gł�'
Warning 6: Normalized/laundered field name: 'street_name_long' to 'street_nam'
```

## What to do

Shorten names yourself, on a letter boundary, and keep a table from the original name to the written one. Do not rely on GDAL's cut for any name that has non-ASCII letters.
