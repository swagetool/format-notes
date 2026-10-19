# GeoPackage does not keep a field named fid or geom

Kind: format limit

Checked on GDAL 3.10.3, PROJ 9.6.0, Python 3.13.5.

## What happens

A text field called `fid` or `geom` is not created. GDAL prints an error, the objects are still written, and the values of that field are gone. An integer field called `fid` is used as the feature id, so a repeated value (1, 1, 2) makes one insert fail with "UNIQUE constraint failed" and the object is lost: three written, two read back.

## Reproduce

Snippet file: `fid-and-geom-field-names.py`

```python
import os, tempfile
from osgeo import gdal, ogr

def attempt(label, field_type, name, values):
    p = os.path.join(tempfile.mkdtemp(), "t.gpkg")
    ds = ogr.GetDriverByName("GPKG").CreateDataSource(p)
    lyr = ds.CreateLayer("t", geom_type=ogr.wkbPoint)
    lyr.CreateField(ogr.FieldDefn(name, field_type))
    ok = 0
    for v in values:
        f = ogr.Feature(lyr.GetLayerDefn())
        f.SetField(name, v)
        f.SetGeometry(ogr.CreateGeometryFromWkt("POINT (1 2)"))
        if lyr.CreateFeature(f) == 0:
            ok += 1
    ds = lyr = f = None
    src = ogr.Open(p)
    back = src.GetLayer(0)
    idx = back.GetLayerDefn().GetFieldIndex(name)
    read = [r.GetField(idx) if idx >= 0 else None for r in back]
    print(label)
    print("   written:", values, "| CreateFeature succeeded:", ok, "of", len(values))
    print("   read back:", read, "| field", name, "present:", idx >= 0)

attempt("text field named fid", ogr.OFTString, "fid", ["a", "b", "c"])
attempt("integer field fid, value 1 twice", ogr.OFTInteger, "fid", [1, 1, 2])
attempt("text field named geom", ogr.OFTString, "geom", ["a", "b", "c"])
```

Output, as printed (standard output first, then standard error):

```
text field named fid
   written: ['a', 'b', 'c'] | CreateFeature succeeded: 3 of 3
   read back: [None, None, None] | field fid present: False
integer field fid, value 1 twice
   written: [1, 1, 2] | CreateFeature succeeded: 2 of 3
   read back: [None, None] | field fid present: False
text field named geom
   written: ['a', 'b', 'c'] | CreateFeature succeeded: 3 of 3
   read back: [None, None, None] | field geom present: False
[stderr] ERROR 1: Wrong field type for fid
ERROR 1: Invalid index : -1
ERROR 1: Invalid index : -1
ERROR 1: Invalid index : -1
ERROR 1: failed to execute insert : UNIQUE constraint failed: t.fid
ERROR 1: Cannot create field geom. It has the same name as the geometry field.
ERROR 1: Invalid index : -1
ERROR 1: Invalid index : -1
ERROR 1: Invalid index : -1
```

## What to do

Rename these fields before the write and keep the mapping. Check the return codes of `CreateField` and `CreateFeature`.

## Sources

- [GDAL GeoPackage driver page](https://gdal.org/en/stable/drivers/vector/gpkg.html): `FID` "Defaults to fid. Column name to use for the OGR FID (primary key in the SQLite database)." `GEOMETRY_NAME` "Defaults to geom." Both are columns of the same table as the fields, so a field of the same name collides with them. The page does not say what happens then.
- We did not find a GDAL issue about this.
