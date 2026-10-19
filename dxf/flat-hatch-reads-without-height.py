import os, tempfile
from osgeo import ogr

p = os.path.join(tempfile.mkdtemp(), "hatch.dxf")
ds = ogr.GetDriverByName("DXF").CreateDataSource(p)
lyr = ds.CreateLayer("entities", geom_type=ogr.wkbPolygon25D)
wkts = ["POLYGON Z ((0 0 0, 1 0 0, 1 1 0, 0 0 0))",
        "POLYGON Z ((0 0 -1, 1 0 1, 1 1 -1, 0 0 -1))",
        "POLYGON Z ((0 0 5, 1 0 5, 1 1 5, 0 0 5))"]
for w in wkts:
    f = ogr.Feature(lyr.GetLayerDefn())
    f.SetGeometry(ogr.CreateGeometryFromWkt(w))
    lyr.CreateFeature(f)
ds = lyr = f = None

back = ogr.Open(p)
for (w, f) in zip(wkts, back.GetLayer(0)):
    print("written:", w)
    print("read:   ", f.GetGeometryRef().ExportToIsoWkt())
