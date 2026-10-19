import os, tempfile
from osgeo import ogr

wkts = ("POINT Z (1 2 5)", "POINT (3 4)")
p = os.path.join(tempfile.mkdtemp(), "t.shp")
ds = ogr.GetDriverByName("ESRI Shapefile").CreateDataSource(p)
lyr = ds.CreateLayer("t", geom_type=ogr.wkbPoint25D)
for wkt in wkts:
    f = ogr.Feature(lyr.GetLayerDefn())
    f.SetGeometry(ogr.CreateGeometryFromWkt(wkt))
    lyr.CreateFeature(f)
ds = lyr = f = None

src = ogr.Open(p)
for wkt, f in zip(wkts, src.GetLayer(0)):
    print("written:", wkt.ljust(16), "read:", f.GetGeometryRef().ExportToIsoWkt())
