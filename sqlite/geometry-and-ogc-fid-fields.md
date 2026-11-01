# SQLite does not create a layer with a field named geometry, and drops a text field named OGC_FID

Kind: driver bug

Checked on GDAL 3.10.3, PROJ 9.6.0, Python 3.13.5.

## What happens

The SQLite driver makes its own columns: `ogc_fid` for the feature id and `GEOMETRY` for the geometry. Two field names collide with them.

1. A field named `geometry`: `CreateField` returns 0, and `CreateFeature` returns 6 with a `duplicate column name` error from SQLite. The table is never created. Reading the file gives 0 layers.
2. A text field named `OGC_FID`: `CreateField` returns 6 ("Wrong field type for OGC_FID"). The features are written without that field, and reading gives 1 feature with no fields. An integer field with that name is accepted.

In both cases the data of that column is gone, in the second one the rest of the layer survives.

## Reproduce

Snippet file: `geometry-and-ogc-fid-fields.py`

```python
import os, tempfile
from osgeo import gdal, ogr

os.chdir(tempfile.mkdtemp())
for name, kind in (("speed", ogr.OFTInteger), ("geometry", ogr.OFTString),
                   ("OGC_FID", ogr.OFTString), ("OGC_FID", ogr.OFTInteger)):
    msgs = []
    gdal.PushErrorHandler(lambda c, n, m: msgs.append(m))
    ds = ogr.GetDriverByName("SQLite").CreateDataSource("t.sqlite")
    lyr = ds.CreateLayer("t", geom_type=ogr.wkbPoint)
    field = lyr.CreateField(ogr.FieldDefn(name, kind))
    f = ogr.Feature(lyr.GetLayerDefn())
    if lyr.GetLayerDefn().GetFieldCount():
        f.SetField(0, 5 if kind == ogr.OFTInteger else "5")
    f.SetGeometry(ogr.CreateGeometryFromWkt("POINT (1 2)"))
    written = lyr.CreateFeature(f)
    ds = lyr = f = None
    back = ogr.Open("t.sqlite")
    gdal.PopErrorHandler()
    layers = back.GetLayerCount()
    count = back.GetLayer(0).GetFeatureCount() if layers else 0
    print("%s %s: CreateField %d, CreateFeature %d, layers read %d, features read %d"
          % (name, ogr.GetFieldTypeName(kind), field, written, layers, count))
    for m in msgs:
        print("   ", m)
    back = None
    os.remove("t.sqlite")
```

Output, as printed (standard output first, then standard error):

```
speed Integer: CreateField 0, CreateFeature 0, layers read 1, features read 1
geometry String: CreateField 0, CreateFeature 6, layers read 0, features read 0
    sqlite3_exec(CREATE TABLE 't' ( "ogc_fid" INTEGER PRIMARY KEY AUTOINCREMENT, 'GEOMETRY' BLOB, 'geometry' VARCHAR)) failed: duplicate column name: geometry
OGC_FID String: CreateField 6, CreateFeature 0, layers read 1, features read 1
    Wrong field type for OGC_FID
OGC_FID Integer: CreateField 0, CreateFeature 0, layers read 1, features read 1
```

## What to do

Rename these fields before writing SQLite, `geometry` and `OGC_FID`, and keep a mapping. Check the layer count and field list of the written file.

## Sources

- [GDAL SQLite driver page](https://gdal.org/en/stable/drivers/vector/sqlite.html): the `FID` layer creation option, default `OGC_FID`. The page does not say what happens when a field takes the name of a column the driver already uses. The label "driver bug" is ours: the first case reports a success for the field and fails later on the feature.
- We did not find a GDAL issue about this.
