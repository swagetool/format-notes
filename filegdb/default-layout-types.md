# File Geodatabase in its default layout breaks a time of day and changes four other value types

Kind: documented driver behaviour

Checked on GDAL 3.10.3, PROJ 9.6.0, Python 3.13.5.

## What happens

GDAL's OpenFileGDB driver writes a layer in the layout every ArcGIS opens, unless the layer creation option `TARGET_ARCGIS_VERSION=ARCGIS_PRO_3_2_OR_LATER` is given. In that default layout:

- a 64-bit integer is stored as a real number: `9007199254740993` comes back `9.00719925474099e+15`;
- a date comes back as a date and time at midnight, marked UTC: `2024/01/05 00:00:00+00`;
- a time of day is lost: `10:20:30` comes back `1969/12/31 23:59:59+00`;
- a time with a zone is moved to UTC and loses the zone: `10:20:30+03` comes back `07:20:30+00`;
- a fraction of a second is cut: `10:20:30.123` comes back `10:20:30+00`.

GDAL prints a warning for the first three when the field is created. It prints nothing about the zone or the fraction. With the option, every value comes back whole. The price is that ArcMap and ArcGIS Pro before 3.2 cannot open such a layer.

## Reproduce

Snippet file: `default-layout-types.py`

```python
import os, tempfile
from osgeo import gdal, ogr

gdal.PushErrorHandler(lambda c, n, m: print("[gdal]", m))

def run(options):
    p = os.path.join(tempfile.mkdtemp(), "t.gdb")
    ds = ogr.GetDriverByName("OpenFileGDB").CreateDataSource(p)
    lyr = ds.CreateLayer("t", geom_type=ogr.wkbPoint, options=options)
    for name, kind in (("big", ogr.OFTInteger64), ("day", ogr.OFTDate),
                       ("clock", ogr.OFTTime), ("zoned", ogr.OFTDateTime),
                       ("fine", ogr.OFTDateTime)):
        lyr.CreateField(ogr.FieldDefn(name, kind))
    f = ogr.Feature(lyr.GetLayerDefn())
    f.SetField("big", 2 ** 53 + 1)
    f.SetField("day", "2024/01/05")
    f.SetField("clock", "10:20:30")
    f.SetField("zoned", "2024/01/05 10:20:30+03")
    f.SetField("fine", "2024/01/05 10:20:30.123")
    f.SetGeometry(ogr.CreateGeometryFromWkt("POINT (1 2)"))
    lyr.CreateFeature(f)
    ds = lyr = f = None
    src = ogr.Open(p)
    g = next(iter(src.GetLayer(0)))
    print(options or "default layout")
    for name in ("big", "day", "clock", "zoned", "fine"):
        print("  ", name.ljust(6), g.GetFieldAsString(name))

print("written: big 9007199254740993, day 2024/01/05, clock 10:20:30,")
print("         zoned 2024/01/05 10:20:30+03, fine 2024/01/05 10:20:30.123")
run([])
run(["TARGET_ARCGIS_VERSION=ARCGIS_PRO_3_2_OR_LATER"])
```

Output, as printed (the `[gdal]` lines are GDAL's own warnings, caught by the handler on standard output):

```
written: big 9007199254740993, day 2024/01/05, clock 10:20:30,
         zoned 2024/01/05 10:20:30+03, fine 2024/01/05 10:20:30.123
[gdal] Field big of type Integer64 will be written as a Float64. To get Integer64, use layer creation option TARGET_ARCGIS_VERSION=ARCGIS_PRO_3_2_OR_LATER
[gdal] Field day of type Date will be written as a DateTime. To get DateTime, use layer creation option TARGET_ARCGIS_VERSION=ARCGIS_PRO_3_2_OR_LATER
[gdal] Field clock of type Time will be written as a DateTime. To get DateTime, use layer creation option TARGET_ARCGIS_VERSION=ARCGIS_PRO_3_2_OR_LATER
default layout
   big    9.00719925474099e+15
   day    2024/01/05 00:00:00+00
   clock  1969/12/31 23:59:59+00
   zoned  2024/01/05 07:20:30+00
   fine   2024/01/05 10:20:30+00
['TARGET_ARCGIS_VERSION=ARCGIS_PRO_3_2_OR_LATER']
   big    9007199254740993
   day    2024/01/05
   clock  10:20:30
   zoned  2024/01/05 10:20:30+03
   fine   2024/01/05 10:20:30.123+00
```

## What to do

Decide per layer. Where a layer holds 64-bit integers, dates, times of day, zoned times or fractions of a second, give it `TARGET_ARCGIS_VERSION=ARCGIS_PRO_3_2_OR_LATER` and tell the reader that older ArcGIS will not open it. Where every integer fits 32 bits, create the field as a 32-bit integer (`OFTInteger`): every ArcGIS reads that, and the option is not needed for it. Store a time of day as text if the layer must open in older ArcGIS.

## Sources

- GDAL documentation of the driver, layer creation option `TARGET_ARCGIS_VERSION` and the section "64-bit integer field support": https://gdal.org/en/release-3.10/drivers/vector/openfilegdb.html
- The documentation does not say that a time of day comes back as `1969/12/31 23:59:59` or that a zone and a fraction are dropped. We found no GDAL issue about it.
