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
