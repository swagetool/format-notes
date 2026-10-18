# GML rewrites layer and field names and merges layers whose names become equal

Checked on GDAL 3.10.3, PROJ 9.6.0, Python 3.13.5.

## What happens

`road-a` and `road_a` are two layers. GML cannot have `-` in an element name, so `road-a` becomes `road_a`, and on reading there is one layer with 6 features. The field `max-speed` becomes `max_speed`. GDAL prints warnings at write time.

## Reproduce

```python
import os, tempfile
from osgeo import ogr

p = os.path.join(tempfile.mkdtemp(), "t.gml")
ds = ogr.GetDriverByName("GML").CreateDataSource(p)
for name in ("road-a", "road_a"):
    lyr = ds.CreateLayer(name, geom_type=ogr.wkbPoint)
    lyr.CreateField(ogr.FieldDefn("max-speed", ogr.OFTInteger))
    for i in range(3):
        f = ogr.Feature(lyr.GetLayerDefn())
        f.SetField(0, 50)
        f.SetGeometry(ogr.CreateGeometryFromWkt("POINT (1 2)"))
        lyr.CreateFeature(f)
ds = lyr = f = None

back = ogr.Open(p)
print("layers written: ['road-a', 'road_a'], 6 features")
for l in back:
    d = l.GetLayerDefn()
    print("layer read:", l.GetName(), "features:", l.GetFeatureCount(),
          "fields:", [d.GetFieldDefn(i).GetName() for i in range(d.GetFieldCount())])
```

Output, as printed (standard output first, then standard error):

```
layers written: ['road-a', 'road_a'], 6 features
layer read: road_a features: 6 fields: ['gml_id', 'max_speed']
[stderr] Warning 1: Layer name 'road-a' adjusted to 'road_a' for XML validity.
Warning 1: Field name 'max-speed' adjusted to 'max_speed' to be a valid
XML element name.
Warning 1: Field name 'max-speed' adjusted to 'max_speed' to be a valid
XML element name.
```

## What to do

Clean the names yourself before writing, to the set that the format accepts, and check that they are still unique afterwards.
