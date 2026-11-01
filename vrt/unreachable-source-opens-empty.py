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
