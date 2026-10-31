# MIF writes a newline in a value as backslash and n, and reads it back that way

Kind: driver bug

Checked on GDAL 3.10.3, PROJ 9.6.0, Python 3.13.5.

## What happens

MIF is a text format, so the driver writes a newline inside a value as the two characters backslash and `n`, in the `.mid` file. On reading it does not turn them back. A value `line one`, newline, `line two` comes back with a literal backslash and `n` and with 0 newline characters.

We tested only the MIF and MID pair, not TAB.

## Reproduce

Snippet file: `mif-newline-in-value.py`

```python
import os, tempfile
from osgeo import ogr

p = os.path.join(tempfile.mkdtemp(), "t.mif")
ds = ogr.GetDriverByName("MapInfo File").CreateDataSource(p)
lyr = ds.CreateLayer("t", geom_type=ogr.wkbPoint)
lyr.CreateField(ogr.FieldDefn("v", ogr.OFTString))
f = ogr.Feature(lyr.GetLayerDefn())
f.SetField("v", "line one\nline two")
f.SetGeometry(ogr.CreateGeometryFromWkt("POINT (1 2)"))
lyr.CreateFeature(f)
ds = lyr = f = None

print("in the .mid:", open(p[:-4] + ".mid").read().strip())
src = ogr.Open(p)
back = next(iter(src.GetLayer(0))).GetField("v")
print("read back:  ", repr(back))
print("newlines in the value read back:", back.count("\n"))
```

Output, as printed (standard output first, then standard error):

```
in the .mid: "line one\nline two"
read back:   'line one\\nline two'
newlines in the value read back: 0
```

## What to do

After reading a MIF, replace the two characters backslash and `n` in text fields with a newline if the data is known to hold multi-line text. Do it only for MIF, since a value from another source may contain a real backslash followed by `n`.

## Sources

- The [GDAL MapInfo driver page](https://gdal.org/en/stable/drivers/vector/mitab.html) does not mention newlines in values. The label "driver bug" is ours for an undocumented limitation.
- We did not find a GDAL issue about this.
