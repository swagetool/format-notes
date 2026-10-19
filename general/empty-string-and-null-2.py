import os, tempfile
from osgeo import gdal, ogr

p = os.path.join(tempfile.mkdtemp(), "t.gml")
ds = ogr.GetDriverByName("GML").CreateDataSource(p)
lyr = ds.CreateLayer("t", geom_type=ogr.wkbPoint)
lyr.CreateField(ogr.FieldDefn("v", ogr.OFTString))
for v in ("", " lead", "trail "):
    f = ogr.Feature(lyr.GetLayerDefn())
    f.SetField("v", v)
    f.SetGeometry(ogr.CreateGeometryFromWkt("POINT (1 2)"))
    lyr.CreateFeature(f)
ds = lyr = f = None

print("in the file:", [l.strip() for l in open(p) if "<ogr:v" in l])
for opts in ([], ["EMPTY_AS_NULL=NO"]):
    src = gdal.OpenEx(p, open_options=opts)
    back = src.GetLayer(0)
    print("open options", opts or "none", "->", [r.GetField("v") for r in back])
