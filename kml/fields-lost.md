# KML loses fields in two situations

Kind: driver bug

Checked on GDAL 3.10.3, PROJ 9.6.0, Python 3.13.5.

## What happens

1. If no feature in the layer has a value in any attribute field, none of the fields come back. One value in one feature is enough to bring them all back.
2. Some field names collide with fields the reader adds on its own. Of the names written below, `timestamp`, `begin`, `end` and `visibility` returned no usable value, and `name` is listed as `Name`. Their values are in the file, but the reader fills those fields from KML elements instead. `visibility` also produces a warning about a failed integer parse.

## Reproduce

Snippet file: `fields-lost-1.py`

```python
import os, tempfile
from osgeo import ogr

def run(set_one_value):
    p = os.path.join(tempfile.mkdtemp(), "t.kml")
    ds = ogr.GetDriverByName("LIBKML").CreateDataSource(p)
    lyr = ds.CreateLayer("t", geom_type=ogr.wkbPoint)
    lyr.CreateField(ogr.FieldDefn("height", ogr.OFTReal))
    lyr.CreateField(ogr.FieldDefn("note", ogr.OFTString))
    for i in range(3):
        f = ogr.Feature(lyr.GetLayerDefn())
        if set_one_value and i == 0:
            f.SetField("note", "x")
        f.SetGeometry(ogr.CreateGeometryFromWkt("POINT (30 50)"))
        lyr.CreateFeature(f)
    ds = lyr = f = None
    src = ogr.Open(p)
    d = src.GetLayer(0).GetLayerDefn()
    return [d.GetFieldDefn(i).GetName() for i in range(d.GetFieldCount())
            if d.GetFieldDefn(i).GetName() in ("height", "note")]

print("every value empty:      fields read back =", run(False))
print("one value on one point: fields read back =", run(True))
```

Output, as printed (standard output first, then standard error):

```
every value empty:      fields read back = []
one value on one point: fields read back = ['height', 'note']
```

Snippet file: `fields-lost-2.py`

```python
import os, tempfile
from osgeo import ogr

names = ["name", "timestamp", "visibility", "begin", "end", "street"]
p = os.path.join(tempfile.mkdtemp(), "t.kml")
ds = ogr.GetDriverByName("LIBKML").CreateDataSource(p)
lyr = ds.CreateLayer("t", geom_type=ogr.wkbPoint)
for n in names:
    lyr.CreateField(ogr.FieldDefn(n, ogr.OFTString))
f = ogr.Feature(lyr.GetLayerDefn())
for n in names:
    f.SetField(n, "v_" + n)
f.SetGeometry(ogr.CreateGeometryFromWkt("POINT (30 50)"))
lyr.CreateFeature(f)
ds = lyr = f = None

src = ogr.Open(p)
g = next(iter(src.GetLayer(0)))
d = g.GetDefnRef()
print("fields read:", [d.GetFieldDefn(i).GetName() for i in range(d.GetFieldCount())][:20])
for n in names:
    idx = d.GetFieldIndex(n)
    shown = repr(g.GetField(idx)) if idx >= 0 else "no field of that name"
    print(n.ljust(11), "written 'v_%s'" % n, "| read:", shown)
```

Output, as printed (standard output first, then standard error):

```
fields read: ['id', 'Name', 'description', 'timestamp', 'begin', 'end', 'altitudeMode', 'tessellate', 'extrude', 'visibility', 'drawOrder', 'icon', 'street']
name        written 'v_name' | read: 'v_name'
timestamp   written 'v_timestamp' | read: None
visibility  written 'v_visibility' | read: 0
begin       written 'v_begin' | read: None
end         written 'v_end' | read: None
street      written 'v_street' | read: 'v_street'
[stderr] Warning 1: Value 'v_visibility' of field t.visibility parsed incompletely to integer 0.
```

## What to do

Rename the colliding fields on write and keep the mapping. For layers whose attributes are all empty, write one empty string into a text field of one feature, or tell the user the fields will not survive.

## Sources

- [GDAL LIBKML driver page](https://gdal.org/en/stable/drivers/vector/libkml.html): lists `LIBKML_TIMESTAMP_FIELD`, `LIBKML_BEGIN_FIELD`, `LIBKML_END_FIELD`, `LIBKML_VISIBILITY_FIELD` and `LIBKML_NAME_FIELD` with the defaults `timestamp`, `begin`, `end`, `visibility` and `name`, each mapped to the KML tag of that name. That documents effect 2. Effect 1 (all fields gone when no value is set) is not described.
- [GDAL pull request 13591](https://github.com/OSGeo/gdal/pull/13591) (closes issue 13590): a related collision, a field named `ID` clashing with a core attribute, was fixed in January 2026 by adding the suffix 2 to the name. We did not test the fields of this note against that change.
