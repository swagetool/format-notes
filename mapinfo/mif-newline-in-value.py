import os, tempfile
from osgeo import ogr

p = os.path.join(tempfile.mkdtemp(), "t.mif")
ds = ogr.GetDriverByName("MapInfo File").CreateDataSource(p)
lyr = ds.CreateLayer("t", geom_type=ogr.wkbPoint)
lyr.CreateField(ogr.FieldDefn("v", ogr.OFTString))
f = ogr.Feature(lyr.GetLayerDefn())
f.SetField("v", "line one\nline two")
f.SetGeometry(ogr.CreateGeometryFromWkt("POINT (1 2)"))
lyr.CreateFeature(f)
ds = lyr = f = None

print("in the .mid:", open(p[:-4] + ".mid").read().strip())
src = ogr.Open(p)
back = next(iter(src.GetLayer(0))).GetField("v")
print("read back:  ", repr(back))
print("newlines in the value read back:", back.count("\n"))
