# A DXF written by GDAL cannot hold more than one layer set

Kind: documented driver behaviour

Checked on GDAL 3.10.3, PROJ 9.6.0, Python 3.13.5.

## What happens

The second `CreateLayer` returns `None`. In a DXF the drawing layer is a field called `Layer`, so several GDAL layers have to be merged into one and the original set name has to go into that field.

## Reproduce

Snippet file: `only-one-entities-layer.py`

```python
import os, tempfile
from osgeo import gdal, ogr

p = os.path.join(tempfile.mkdtemp(), "two.dxf")
ds = ogr.GetDriverByName("DXF").CreateDataSource(p)
a = ds.CreateLayer("roads", geom_type=ogr.wkbLineString)
print("first layer:", a is not None)
b = ds.CreateLayer("buildings", geom_type=ogr.wkbPolygon)
print("second layer:", b)
print("GDAL says:", gdal.GetLastErrorMsg())
```

Output, as printed (standard output first, then standard error):

```
first layer: True
second layer: None
GDAL says: Unable to have more than one OGR entities layer in a DXF file, with one options blocks layer.
[stderr] ERROR 1: Unable to have more than one OGR entities layer in a DXF file, with one options blocks layer.
```

## What to do

Write one OGR layer and fill the `Layer` attribute with the name of the set each object came from. Tell the user that sets were merged.

## Sources

- [GDAL DXF driver page](https://gdal.org/en/stable/drivers/vector/dxf.html), DXF Writer: "Only one OGR layer can be used to create the output file (but many DXF layers can be created)." The error text in the output above says the same.
- We did not find a GDAL issue about this.
