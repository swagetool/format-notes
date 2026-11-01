# A VRT whose source cannot be reached opens fine and has no features

Kind: undocumented driver behaviour

Checked on GDAL 3.10.3, PROJ 9.6.0, Python 3.13.5.

## What happens

A `.vrt` file names its source inside the XML. `ogr.Open` on the `.vrt` does not open that source. It returns a dataset with one layer, and the source is tried only when the layer is used. If the source is unreachable, the layer has 0 features and `GetNextFeature` returns `None`.

The snippet tries two sources that cannot be read: a `/vsicurl/` address on a closed local port, and a file that does not exist. Both times the open succeeds with 1 layer and 0 features. The messages differ. The remote source gives one warning ("HTTP response code ... : 0"). The missing file gives an error ("Failed to open datasource"), and the dataset is returned anyway. A check that tests for `None` or waits for an exception sees a successful open in both cases.

An empty result like this describes the state of the source at that moment, not the data. "0 features" here does not mean the source holds none.

## Reproduce

Snippet file: `unreachable-source-opens-empty.py`

```python
import os, tempfile
from osgeo import gdal, ogr

os.chdir(tempfile.mkdtemp())
TEMPLATE = ('<OGRVRTDataSource><OGRVRTLayer name="roads"><SrcDataSource>%s</SrcDataSource>'
            '</OGRVRTLayer></OGRVRTDataSource>')
for label, source in (("remote, port closed", "/vsicurl/http://127.0.0.1:9/roads.geojson"),
                      ("local, file missing", "/nonexistent/roads.geojson")):
    open("t.vrt", "w").write(TEMPLATE % source)
    msgs = []
    gdal.PushErrorHandler(lambda c, n, m: msgs.append("%d %s" % (c, m)))
    ds = ogr.Open("t.vrt")
    if ds is None:
        print(label + ": open returned None")
    else:
        lyr = ds.GetLayer(0)
        print(label + ": opened, layers", ds.GetLayerCount(), "features", lyr.GetFeatureCount(),
              "first feature", lyr.GetNextFeature())
    gdal.PopErrorHandler()
    print("  messages:", msgs)
    ds = lyr = None
```

Output, as printed (standard output first, then standard error):

```
remote, port closed: opened, layers 1 features 0 first feature None
  messages: ['2 HTTP response code on http://127.0.0.1:9/roads.geojson: 0']
local, file missing: opened, layers 1 features 0 first feature None
  messages: ["3 Failed to open datasource `/nonexistent/roads.geojson'."]
```

## What to do

After opening a VRT, compare the feature count with what you expect, and treat any message from the open call as a failure. For a network source, test that the address answers before you convert, and say in the result that the source was not reached.

## Sources

- No link. The [GDAL VRT driver page](https://gdal.org/en/stable/drivers/vector/vrt.html) does not say when the source is opened or what happens when it cannot be. The snippet shows the behaviour on 3.10.3.
- We did not find a GDAL issue about this.
