# The GDAL DXF writer writes UTF-8 text under an ANSI_1252 header

Checked on GDAL 3.10.3, PROJ 9.6.0, Python 3.13.5.

## What happens

Writing `Łódź` as a layer name produces a file that says `ANSI_1252` in the header while the name is stored as UTF-8 bytes. Reading the same file with GDAL gives `ÅÃ³dÅº`. The file is wrong on its own, so any reader that trusts the header will do the same.

## Reproduce

```python
import os, re, tempfile
from osgeo import ogr

p = os.path.join(tempfile.mkdtemp(), "out.dxf")
ds = ogr.GetDriverByName("DXF").CreateDataSource(p)
lyr = ds.CreateLayer("entities", geom_type=ogr.wkbPoint)
lyr.CreateField(ogr.FieldDefn("Layer", ogr.OFTString))
f = ogr.Feature(lyr.GetLayerDefn())
f.SetField("Layer", "Łódź")
f.SetGeometry(ogr.CreateGeometryFromWkt("POINT (1 2)"))
lyr.CreateFeature(f)
ds = lyr = f = None

raw = open(p, "rb").read()
print("header says:", re.search(rb"\$DWGCODEPAGE\r?\n\s*3\r?\n(\S+)", raw).group(1).decode())
print("name written as UTF-8 bytes:", "Łódź".encode("utf-8") in raw)
for l in ogr.Open(p):
    for g in l:
        print("GDAL reads back:", g.GetField("Layer"))
```

Output, as printed (standard output first, then standard error):

```
header says: ANSI_1252
name written as UTF-8 bytes: True
GDAL reads back: ÅÃ³dÅº
```

## What to do

After writing a DXF with non-Latin or accented text, read it back and compare. If you need such text to survive, re-encode the finished file into one ANSI code page that contains all the letters and keep the header in line with it. Letters outside the page need an escape such as `\U+0141`.
