# A MIF table with no fields is written and cannot be opened

Kind: driver bug

Checked on GDAL 3.10.3, PROJ 9.6.0, Python 3.13.5.

## What happens

GDAL accepts a layer with no attribute fields for MIF. `CreateFeature` returns 0 (success) and a `.mif` and a `.mid` are written. On closing, GDAL prints two errors saying the file must contain at least one attribute field. The files stay on disk, and opening the `.mif` afterwards returns `None` with the error "COLUMNS keyword not found or invalid number of columns".

A conversion that ends with a successful write call can leave a file nobody can read.

## Reproduce

Snippet file: `mif-table-without-fields.py`

```python
import os, tempfile
from osgeo import gdal, ogr

# Work inside a fresh directory so the messages carry a short relative path.
os.chdir(tempfile.mkdtemp())
ds = ogr.GetDriverByName("MapInfo File").CreateDataSource("nofields.mif")
lyr = ds.CreateLayer("nofields", geom_type=ogr.wkbPoint)
f = ogr.Feature(lyr.GetLayerDefn())
f.SetGeometry(ogr.CreateGeometryFromWkt("POINT (1 2)"))
print("create feature returns:", lyr.CreateFeature(f))
ds = lyr = f = None
print("files:", sorted(os.listdir(".")))
src = ogr.Open("nofields.mif")
print("open:", "None" if src is None else src.GetLayerCount())
```

Output, as printed (standard output first, then standard error):

```
create feature returns: 0
files: ['nofields.mid', 'nofields.mif']
open: None
[stderr] ERROR 6: File nofields.mif must contain at least 1 attribute field.
ERROR 6: File nofields.mif must contain at least 1 attribute field.
ERROR 6: COLUMNS keyword not found or invalid number of columns read in nofields.mif.  File may be corrupt.
```

## What to do

Before writing MIF, add one field (an integer `id`, for example) to a layer that has none. Open the file after writing to check it.

## Sources

- The [GDAL MapInfo driver page](https://gdal.org/en/stable/drivers/vector/mitab.html) does not mention layers without fields. The label "driver bug" is ours: the error text itself says a field is required, yet the write call reports success.
- We did not find a GDAL issue about this.
