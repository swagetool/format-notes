# Empty string and NULL are different values, and most formats do not keep both

Kind: documented driver behaviour

Checked on GDAL 3.10.3, PROJ 9.6.0, Python 3.13.5.

## What happens

Row 1 has `s=''` and `n=0`. Row 2 has both NULL. After a round trip, from the output below:

- Shapefile and GML: empty string and NULL both read back as `None`.
- CSV: everything is text, empty for both.
- MapInfo: both become `''` and the NULL integer becomes 0.
- GeoPackage and GeoJSON keep the difference.
- FlatGeobuf keeps it too, but the two rows come back in the other order.

For GML the reason is on the reading side. The reader has `EMPTY_AS_NULL=YES` by default and the second snippet shows `EMPTY_AS_NULL=NO` bringing the empty string back. The same snippet shows that the GML writer drops a leading space (`' lead'` was written as `lead`).

## Reproduce

Snippet file: `empty-string-and-null-1.py`

```python
import os, tempfile
from osgeo import ogr

cases = [("ESRI Shapefile", "t.shp"), ("GML", "t.gml"), ("CSV", "t.csv"),
         ("MapInfo File", "t"), ("GPKG", "t.gpkg"), ("GeoJSON", "t.geojson"),
         ("FlatGeobuf", "t.fgb")]
print("written: row 1 s='' n=0, row 2 s=NULL n=NULL")
for drv, name in cases:
    p = os.path.join(tempfile.mkdtemp(), name)
    ds = ogr.GetDriverByName(drv).CreateDataSource(p)
    lyr = ds.CreateLayer("t", geom_type=ogr.wkbPoint)
    lyr.CreateField(ogr.FieldDefn("s", ogr.OFTString))
    lyr.CreateField(ogr.FieldDefn("n", ogr.OFTInteger))
    f = ogr.Feature(lyr.GetLayerDefn())
    f.SetField("s", "")
    f.SetField("n", 0)
    f.SetGeometry(ogr.CreateGeometryFromWkt("POINT (1 2)"))
    lyr.CreateFeature(f)
    g = ogr.Feature(lyr.GetLayerDefn())
    g.SetFieldNull("s")
    g.SetFieldNull("n")
    g.SetGeometry(ogr.CreateGeometryFromWkt("POINT (3 4)"))
    lyr.CreateFeature(g)
    ds = lyr = f = g = None
    if drv == "MapInfo File":
        p = os.path.join(p, "t.tab")
    src = ogr.Open(p)
    back = [(r.GetField("s"), r.GetField("n")) for r in src.GetLayer(0)]
    print(drv.ljust(15), back)
```

Output, as printed (standard output first, then standard error):

```
written: row 1 s='' n=0, row 2 s=NULL n=NULL
ESRI Shapefile  [(None, 0), (None, None)]
GML             [(None, 0), (None, None)]
CSV             [('', '0'), ('', '')]
MapInfo File    [('', 0), ('', 0)]
GPKG            [('', 0), (None, None)]
GeoJSON         [('', 0), (None, None)]
FlatGeobuf      [(None, None), ('', 0)]
```

Snippet file: `empty-string-and-null-2.py`

```python
import os, tempfile
from osgeo import gdal, ogr

p = os.path.join(tempfile.mkdtemp(), "t.gml")
ds = ogr.GetDriverByName("GML").CreateDataSource(p)
lyr = ds.CreateLayer("t", geom_type=ogr.wkbPoint)
lyr.CreateField(ogr.FieldDefn("v", ogr.OFTString))
for v in ("", " lead", "trail "):
    f = ogr.Feature(lyr.GetLayerDefn())
    f.SetField("v", v)
    f.SetGeometry(ogr.CreateGeometryFromWkt("POINT (1 2)"))
    lyr.CreateFeature(f)
ds = lyr = f = None

print("in the file:", [l.strip() for l in open(p) if "<ogr:v" in l])
for opts in ([], ["EMPTY_AS_NULL=NO"]):
    src = gdal.OpenEx(p, open_options=opts)
    back = src.GetLayer(0)
    print("open options", opts or "none", "->", [r.GetField("v") for r in back])
```

Output, as printed (standard output first, then standard error):

```
in the file: ['<ogr:v></ogr:v>', '<ogr:v>lead</ogr:v>', '<ogr:v>trail </ogr:v>']
open options none -> [None, 'lead', 'trail ']
open options ['EMPTY_AS_NULL=NO'] -> ['', 'lead', 'trail ']
```

## What to do

If the difference matters, choose GeoPackage, GeoJSON or FlatGeobuf. For the others, count how many values will change before the write and say it.

## Sources

- [GDAL GML driver page](https://gdal.org/en/stable/drivers/vector/gml.html): `EMPTY_AS_NULL` "Defaults to YES. If YES, fields with empty content will be reported as being NULL, instead of being an empty string."
- [GDAL CSV driver page](https://gdal.org/en/stable/drivers/vector/csv.html): `EMPTY_STRING_AS_NULL` "Defaults to NO. Whether to consider empty strings as null fields on reading". The page says nothing about writing.
- Shapefile and MapInfo behaviour is not described on their driver pages. We list only what the snippet printed.
- We did not find a GDAL issue about this.
