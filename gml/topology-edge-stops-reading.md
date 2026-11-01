# A GML with a topology edge that has no geometry stops reading at the first such object

Kind: documented driver behaviour

Checked on GDAL 3.10.3, PROJ 9.6.0, Python 3.13.5.

## What happens

Some GML files store a geometry as topology: a `gml:TopoCurve` or face made of `gml:directedEdge` elements. If an edge carries no geometry GDAL cannot build the object. With default settings the read raises "Failed to get geometry in directedEdge" on that object and nothing after it is returned. The message names the cure: the configuration option `GML_SKIP_CORRUPTED_FEATURES`.

With the option set to `YES` the bad object is skipped with a warning and the others are read. Skipping loses an object, and `GetFeatureCount` still counts it: the layer says 3 and 2 are read. Compare the two numbers to see how many were skipped.

The file in the snippet is built to reach this code path: an edge with only an id. We did not check it against a real topology file here.

## Reproduce

Snippet file: `topology-edge-stops-reading.py`

```python
import os, tempfile
from osgeo import gdal, ogr

def feature(i, geometry):
    return ('<gml:featureMember><ogr:road fid="r%d"><ogr:geom>%s</ogr:geom><ogr:id>%d</ogr:id>'
            '</ogr:road></gml:featureMember>\n' % (i, geometry, i))

line = "<gml:LineString><gml:coordinates>0,0 1,1</gml:coordinates></gml:LineString>"
# A topological curve whose edge carries no geometry of its own.
topo = '<gml:TopoCurve><gml:directedEdge orientation="+"><gml:Edge gml:id="e2"/></gml:directedEdge></gml:TopoCurve>'
text = ('<?xml version="1.0" encoding="UTF-8"?>\n'
        '<ogr:FeatureCollection xmlns:ogr="http://ogr.maptools.org/" xmlns:gml="http://www.opengis.net/gml">\n'
        + feature(1, line) + feature(2, topo) + feature(3, line) + '</ogr:FeatureCollection>\n')
path = os.path.join(tempfile.mkdtemp(), "t.gml")
open(path, "w").write(text)

def read(skip):
    gdal.SetConfigOption("GML_SKIP_CORRUPTED_FEATURES", skip)
    msgs = []
    gdal.PushErrorHandler(lambda c, n, m: msgs.append(m))
    try:
        ds = gdal.OpenEx(path, open_options=["WRITE_GFS=NO"])
        lyr = ds.GetLayer(0)
        n = sum(1 for _ in lyr)
        result = "read %d features, GetFeatureCount says %d" % (n, lyr.GetFeatureCount())
    except Exception as e:
        result = "no result"
        msgs.append(str(e))
    gdal.PopErrorHandler()
    print("GML_SKIP_CORRUPTED_FEATURES=%s: %s" % (skip, result))
    for m in msgs:
        print("  message:", m)

gdal.UseExceptions()
read("NO")
read("YES")
```

Output, as printed (standard output first, then standard error):

```
GML_SKIP_CORRUPTED_FEATURES=NO: no result
  message: Geometry of feature 2 r2 cannot be parsed: Failed to get geometry in directedEdge. You may set the GML_SKIP_CORRUPTED_FEATURES configuration option to YES to skip to the next feature
GML_SKIP_CORRUPTED_FEATURES=YES: read 2 features, GetFeatureCount says 3
  message: Geometry of feature 2 r2 cannot be parsed: Failed to get geometry in directedEdge. Skipping to next feature.
```

## What to do

Open topology GML with `GML_SKIP_CORRUPTED_FEATURES=YES` when the alternative is no data, and report the difference between the declared and the read count as the number of objects that were not read. Do not call the result complete.

## Sources

- [GDAL GML driver page](https://gdal.org/en/stable/drivers/vector/gml.html): `GML_SKIP_CORRUPTED_FEATURES` skips features that cannot be parsed, and with `NO` (the default) the driver fails with an error on such a feature.
- We did not find a GDAL issue about the directedEdge message.
