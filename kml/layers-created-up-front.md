# The plain KML driver takes features only into the layer created last

Kind: driver bug

Checked on GDAL 3.10.3, PROJ 9.6.0, Python 3.13.5.

## What happens

Three layers are created first and 5 features are written to each. The 10 features written to the first two layers fail with error 6 ("Interleaved feature adding to different layers is not supported") and only the third layer has data. GDAL prints the error for every object, and the return code is 6 each time, so a script that does not check it loses 10 of 15 features.

The LIBKML driver took all 15 when we ran the same snippet with that driver name.

## Reproduce

Snippet file: `layers-created-up-front.py`

```python
import os, tempfile
from osgeo import ogr

p = os.path.join(tempfile.mkdtemp(), "t.kml")
ds = ogr.GetDriverByName("KML").CreateDataSource(p)
layers = [ds.CreateLayer(n, geom_type=ogr.wkbPoint) for n in ("a", "b", "c")]
results = []
for lyr in layers:                        # 5 features into each of 3 layers
    for i in range(5):
        f = ogr.Feature(lyr.GetLayerDefn())
        f.SetGeometry(ogr.CreateGeometryFromWkt("POINT (30 50)"))
        results.append(lyr.CreateFeature(f))
ds = layers = lyr = f = None

print("CreateFeature return codes:", results)
src = ogr.Open(p)
print({l.GetName(): l.GetFeatureCount() for l in src}, "(15 written)")
```

Output, as printed (standard output first, then standard error):

```
CreateFeature return codes: [6, 6, 6, 6, 6, 6, 6, 6, 6, 6, 0, 0, 0, 0, 0]
{'a': 0, 'b': 0, 'c': 5} (15 written)
[stderr] ERROR 6: Interleaved feature adding to different layers is not supported
ERROR 6: Interleaved feature adding to different layers is not supported
ERROR 6: Interleaved feature adding to different layers is not supported
ERROR 6: Interleaved feature adding to different layers is not supported
ERROR 6: Interleaved feature adding to different layers is not supported
ERROR 6: Interleaved feature adding to different layers is not supported
ERROR 6: Interleaved feature adding to different layers is not supported
ERROR 6: Interleaved feature adding to different layers is not supported
ERROR 6: Interleaved feature adding to different layers is not supported
ERROR 6: Interleaved feature adding to different layers is not supported
```

## What to do

Create a layer, write all of its features, then create the next one. Check the return code of every `CreateFeature`.

## Sources

- The [GDAL KML driver page](https://gdal.org/en/stable/drivers/vector/kml.html) does not mention this limit. The error text printed by the driver is the only statement of it that we found.
- We did not find a GDAL issue about this.
