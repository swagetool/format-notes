# GDAL does not open a MapInfo table whose header says Type NativeX

Kind: undocumented driver behaviour

Checked on GDAL 3.10.3, PROJ 9.6.0, Python 3.13.5.

## What happens

A MapInfo `.tab` file names the table type in its header. GDAL writes `Type NATIVE`. The snippet writes a one-point table, copies its four files under a new name, and changes only that word to `NativeX`. The original opens with 1 feature. The copy is refused with "not recognized as being in a supported file format", the message GDAL gives for a file it has never heard of. It says nothing about the table type, and the driver does read TAB files.

This shows how GDAL reacts to the declared type. The data files in the snippet are Native ones, and we have no table written by MapInfo as `NativeX` to try. A person who gets this message for a `.tab` should open the file in a text editor and read the `Type` line first, before looking for a missing companion file.

## Reproduce

Snippet file: `native-x-not-recognized.py`

```python
import os, tempfile
from osgeo import gdal, ogr

os.chdir(tempfile.mkdtemp())
ds = ogr.GetDriverByName("MapInfo File").CreateDataSource("t.tab")
lyr = ds.CreateLayer("t")
lyr.CreateField(ogr.FieldDefn("id", ogr.OFTInteger))
f = ogr.Feature(lyr.GetLayerDefn())
f.SetField(0, 1)
f.SetGeometry(ogr.CreateGeometryFromWkt("POINT (1 2)"))
lyr.CreateFeature(f)
ds = lyr = f = None

# The same four files under a second name, the only change is the table type in the .tab.
for ext in ("tab", "dat", "map", "id"):
    data = open("t." + ext, "rb").read()
    if ext == "tab":
        data = data.replace(b"Type NATIVE", b"Type NativeX")
    open("n." + ext, "wb").write(data)

gdal.UseExceptions()
for name in ("t.tab", "n.tab"):
    for line in open(name):
        if "Type" in line:
            print(name, "header:", line.strip())
    try:
        ds = ogr.Open(name)
        print(name, "opened, features:", ds.GetLayer(0).GetFeatureCount())
    except Exception as e:
        print(name, "error:", e)
```

Output, as printed (standard output first, then standard error):

```
t.tab header: Type NATIVE Charset "Neutral"
t.tab opened, features: 1
n.tab header: Type NativeX Charset "Neutral"
n.tab error: `n.tab' not recognized as being in a supported file format.
```

## What to do

Look at the `Type` line of a `.tab` that GDAL refuses. If it says `NativeX`, ask for the table exported from MapInfo as MIF/MID or as a native TAB, or convert it in MapInfo.

## Sources

- No link. The [GDAL MapInfo driver page](https://gdal.org/en/stable/drivers/vector/mitab.html) describes native TAB and MIF/MID and does not mention `NativeX`.
- We did not find a GDAL issue about this.
