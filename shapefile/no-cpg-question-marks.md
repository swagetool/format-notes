# Shapefile written without an encoding stores non-Latin text as question marks

Kind: documented driver behaviour

Checked on GDAL 3.10.3, PROJ 9.6.0, Python 3.13.5.

## What happens

By default the driver writes Latin-1. Cyrillic letters become `?`. The loss is in the file and cannot be undone. GDAL prints one warning at write time. With `ENCODING=UTF-8` a `.cpg` file is created and the text is intact.

## Reproduce

Snippet file: `no-cpg-question-marks.py`

```python
import os, tempfile
from osgeo import ogr

text = "Улица Ленина, дом 5"
for opts in ([], ["ENCODING=UTF-8"]):
    d = tempfile.mkdtemp()
    ds = ogr.GetDriverByName("ESRI Shapefile").CreateDataSource(os.path.join(d, "t.shp"))
    lyr = ds.CreateLayer("t", geom_type=ogr.wkbPoint, options=opts)
    lyr.CreateField(ogr.FieldDefn("addr", ogr.OFTString))
    f = ogr.Feature(lyr.GetLayerDefn())
    f.SetField("addr", text)
    f.SetGeometry(ogr.CreateGeometryFromWkt("POINT (1 2)"))
    lyr.CreateFeature(f)
    ds = lyr = f = None
    src = ogr.Open(os.path.join(d, "t.shp"))
    got = next(iter(src.GetLayer(0))).GetField("addr")
    print("options:", opts or "none", "| files:", sorted(os.listdir(d)))
    print("  read:", got)
```

Output, as printed (standard output first, then standard error):

```
options: none | files: ['t.dbf', 't.shp', 't.shx']
  read: ????? ??????, ??? 5
options: ['ENCODING=UTF-8'] | files: ['t.cpg', 't.dbf', 't.shp', 't.shx']
  read: Улица Ленина, дом 5
[stderr] Warning 1: One or several characters couldn't be converted correctly from UTF-8 to ISO-8859-1.  This warning will not be emitted anymore.
```

## What to do

Always pass `ENCODING=UTF-8` (or another explicit encoding) when creating a Shapefile, and ship the `.cpg`.

## Sources

- [GDAL Shapefile driver page](https://gdal.org/en/stable/drivers/vector/shapefile.html), Layer creation options: `ENCODING` "Set the encoding value in the DBF file. The default value is "LDID/87"." In the Encoding section: "LDID "87 / 0x57" is treated as ISO-8859-1 which may not be appropriate."
- GDAL warns once when a character cannot be converted, as the output above shows.
- We did not find a GDAL issue about this.
