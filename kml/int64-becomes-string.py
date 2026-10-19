import os, tempfile
from osgeo import ogr

p = os.path.join(tempfile.mkdtemp(), "t.kml")
ds = ogr.GetDriverByName("LIBKML").CreateDataSource(p)
lyr = ds.CreateLayer("t", geom_type=ogr.wkbPoint)
lyr.CreateField(ogr.FieldDefn("color", ogr.OFTInteger64))
lyr.CreateField(ogr.FieldDefn("label", ogr.OFTString))
f = ogr.Feature(lyr.GetLayerDefn())
f.SetField("color", 220)
f.SetField("label", "264 DIVER ")
f.SetGeometry(ogr.CreateGeometryFromWkt("POINT (30 50)"))
lyr.CreateFeature(f)
ds = lyr = f = None

print("in the file:", [l.strip() for l in open(p) if "264" in l or "220" in l])
src = ogr.Open(p)
back = src.GetLayer(0)
d = back.GetLayerDefn()
for i in range(d.GetFieldCount()):
    fd = d.GetFieldDefn(i)
    if fd.GetName() in ("color", "label"):
        print(fd.GetName(), "type read:", fd.GetTypeName())
g = next(iter(back))
print("values read:", repr(g.GetField("color")), repr(g.GetField("label")))
