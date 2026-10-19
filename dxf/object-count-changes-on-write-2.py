import os, tempfile
from osgeo import ogr

p = os.path.join(tempfile.mkdtemp(), "multi.dxf")
ds = ogr.GetDriverByName("DXF").CreateDataSource(p)
lyr = ds.CreateLayer("entities", geom_type=ogr.wkbMultiPolygon)
f = ogr.Feature(lyr.GetLayerDefn())
f.SetGeometry(ogr.CreateGeometryFromWkt(
    "MULTIPOLYGON (((0 0, 1 0, 1 1, 0 0)), ((5 5, 6 5, 6 6, 5 5)), ((9 9, 10 9, 10 10, 9 9)))"))
lyr.CreateFeature(f)
ds = lyr = f = None

back = ogr.Open(p)
lyr = back.GetLayer(0)
print("features written: 1, features read back:", lyr.GetFeatureCount())
