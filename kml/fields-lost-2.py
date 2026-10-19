import os, tempfile
from osgeo import ogr

names = ["name", "timestamp", "visibility", "begin", "end", "street"]
p = os.path.join(tempfile.mkdtemp(), "t.kml")
ds = ogr.GetDriverByName("LIBKML").CreateDataSource(p)
lyr = ds.CreateLayer("t", geom_type=ogr.wkbPoint)
for n in names:
    lyr.CreateField(ogr.FieldDefn(n, ogr.OFTString))
f = ogr.Feature(lyr.GetLayerDefn())
for n in names:
    f.SetField(n, "v_" + n)
f.SetGeometry(ogr.CreateGeometryFromWkt("POINT (30 50)"))
lyr.CreateFeature(f)
ds = lyr = f = None

src = ogr.Open(p)
g = next(iter(src.GetLayer(0)))
d = g.GetDefnRef()
print("fields read:", [d.GetFieldDefn(i).GetName() for i in range(d.GetFieldCount())][:20])
for n in names:
    idx = d.GetFieldIndex(n)
    shown = repr(g.GetField(idx)) if idx >= 0 else "no field of that name"
    print(n.ljust(11), "written 'v_%s'" % n, "| read:", shown)
