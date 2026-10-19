import os, re, tempfile
from osgeo import ogr

p = os.path.join(tempfile.mkdtemp(), "out.dxf")
ds = ogr.GetDriverByName("DXF").CreateDataSource(p)
lyr = ds.CreateLayer("entities", geom_type=ogr.wkbPoint)
lyr.CreateField(ogr.FieldDefn("Layer", ogr.OFTString))
f = ogr.Feature(lyr.GetLayerDefn())
f.SetField("Layer", "Łódź")
f.SetGeometry(ogr.CreateGeometryFromWkt("POINT (1 2)"))
lyr.CreateFeature(f)
ds = lyr = f = None

raw = open(p, "rb").read()
print("header says:", re.search(rb"\$DWGCODEPAGE\r?\n\s*3\r?\n(\S+)", raw).group(1).decode())
print("name written as UTF-8 bytes:", "Łódź".encode("utf-8") in raw)
for l in ogr.Open(p):
    for g in l:
        print("GDAL reads back:", g.GetField("Layer"))
