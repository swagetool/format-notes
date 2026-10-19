import os, tempfile
from osgeo import ogr

p = os.path.join(tempfile.mkdtemp(), "empty.dxf")
ds = ogr.GetDriverByName("DXF").CreateDataSource(p)
lyr = ds.CreateLayer("entities", geom_type=ogr.wkbPolygon)
for wkt in ("POLYGON ((0 0, 1 0, 1 1, 0 0))", "POLYGON EMPTY", "POLYGON ((5 5, 6 5, 6 6, 5 5))"):
    f = ogr.Feature(lyr.GetLayerDefn())
    f.SetGeometry(ogr.CreateGeometryFromWkt(wkt))
    print(wkt.ljust(34), "CreateFeature returned", lyr.CreateFeature(f))
ds = lyr = f = None

n = sum(l.GetFeatureCount() for l in ogr.Open(p))
print("features written: 3, read back:", n)
