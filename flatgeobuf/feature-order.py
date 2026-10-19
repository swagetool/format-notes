import os, tempfile
from osgeo import ogr

pts = [(0, 0), (90, 90), (10, 80), (80, 10), (45, 45)]
p = os.path.join(tempfile.mkdtemp(), "t.fgb")
ds = ogr.GetDriverByName("FlatGeobuf").CreateDataSource(p)
lyr = ds.CreateLayer("t", geom_type=ogr.wkbPoint)
lyr.CreateField(ogr.FieldDefn("seq", ogr.OFTInteger))
for i, (x, y) in enumerate(pts):
    f = ogr.Feature(lyr.GetLayerDefn())
    f.SetField("seq", i)
    f.SetGeometry(ogr.CreateGeometryFromWkt("POINT (%d %d)" % (x, y)))
    lyr.CreateFeature(f)
ds = lyr = f = None

print("written order:", list(range(len(pts))))
back = ogr.Open(p)
print("read order:   ", [r.GetField("seq") for r in back.GetLayer(0)])
